"""
Voice Chat Manager using PyTGCalls
Handles all voice chat operations
"""

import asyncio
import os
from typing import Optional, Dict
from pyrogram import Client
from pyrogram.types import Chat
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality, MediaStream, Update, StreamAudioEnded
from pytgcalls.types import ChatUpdate
from core.queue import queue_manager, Song
from config import DEFAULT_VOLUME
import logging

logger = logging.getLogger(__name__)


class CallManager:
    """Manages voice calls for all chats"""
    
    def __init__(self, app: Client, user_session: str = None):
        self.app = app
        self.user_session = user_session
        self.user_client = None
        self.calls: Dict[int, PyTgCalls] = {}
        self.active_chats: Dict[int, bool] = {}
        
    async def initialize_user_client(self):
        """Initialize user account client for voice chats"""
        if self.user_session and not self.user_client:
            logger.info("Initializing user account for voice chats...")
            self.user_client = Client(
                "music_assistant",
                api_id=self.app.api_id,
                api_hash=self.app.api_hash,
                session_string=self.user_session,
            )
            await self.user_client.start()
            logger.info("✅ User account initialized for voice chats")
    
    def get_call(self, chat_id: int) -> PyTgCalls:
        """Get or create PyTgCalls instance for a chat"""
        if chat_id not in self.calls:
            # Try to use assistant manager first, fallback to user_client or app
            from core.userbot import assistant_manager
            
            client = None
            if assistant_manager.assistants:
                # Use the first available assistant
                client = assistant_manager.get_next_assistant()
                logger.info(f"Using assistant: {client.me.first_name} (ID: {client.me.id})")
            
            if not client:
                client = self.user_client if self.user_client else self.app
                logger.info(f"Using fallback client: {'user_client' if self.user_client else 'bot_app'}")
            
            logger.info(f"Creating PyTgCalls instance for chat {chat_id}")
            self.calls[chat_id] = PyTgCalls(client)
            
            # Register event handler for stream ended
            @self.calls[chat_id].on_update()
            async def stream_ended_handler(client: PyTgCalls, update: Update):
                await self.handle_stream_ended(chat_id, update)
            
        return self.calls[chat_id]
    
    async def join_voice_chat(self, chat_id: int, chat_username: str = None) -> bool:
        """Join voice chat in a group or channel. Returns True if assistant was invited, False if already present"""
        try:
            from core.userbot import assistant_manager
            from pytgcalls.exceptions import PyTgCallsAlreadyRunning
            
            logger.info(f"Joining voice chat in {chat_id}...")
            
            # Check if assistant is already in chat before joining
            assistant_already_present = await assistant_manager.is_assistant_in_chat(chat_id)
            logger.info(f"Assistant already present: {assistant_already_present}")
            
            # Ensure assistant is in the chat before joining
            await assistant_manager.ensure_assistant_in_chat(chat_id, chat_username)
            
            call = self.get_call(chat_id)
            logger.info(f"active_chats status for {chat_id}: {self.active_chats.get(chat_id, False)}")
            
            if not self.active_chats.get(chat_id, False):
                # For channels (IDs starting with -100), ensure user client is used
                if str(chat_id).startswith('-100'):
                    if not self.user_client and not assistant_manager.assistants:
                        raise RuntimeError("User account session is required to play in channels. Please set SESSION_STRING in .env")
                    logger.info(f"Channel detected ({chat_id}), using user account for voice chat")
                
                try:
                    logger.info(f"Starting PyTgCalls for {chat_id}...")
                    await call.start()
                    self.active_chats[chat_id] = True
                    logger.info(f"✅ PyTgCalls started for {chat_id} (will join voice chat when playing)")
                except PyTgCallsAlreadyRunning:
                    # Client is already running, just mark as active
                    logger.info(f"PyTgCalls already running for {chat_id}, marking as active")
                    self.active_chats[chat_id] = True
            else:
                logger.info(f"PyTgCalls already active for {chat_id}")
            
            # Return whether assistant was already present
            return assistant_already_present
        except Exception as e:
            logger.error(f"Failed to join voice chat in {chat_id}: {e}")
            logger.exception("Full traceback:")
            raise
    
    async def leave_voice_chat(self, chat_id: int):
        """Leave voice chat in a group"""
        try:
            logger.info(f"Leaving voice chat in {chat_id}...")
            
            # Reset queue state
            queue = queue_manager.get_queue(chat_id)
            queue.is_playing = False
            queue.current_song = None
            
            if chat_id in self.calls:
                call = self.calls[chat_id]
                # PyTgCalls v2.x: leave the call
                try:
                    await call.leave_call(chat_id)
                    self.active_chats[chat_id] = False
                    logger.info(f"✅ Left voice chat in {chat_id}")
                except Exception as leave_error:
                    # If already not in a call, just mark as inactive
                    if "not in a call" in str(leave_error).lower():
                        logger.info(f"Already not in a call for {chat_id}")
                        self.active_chats[chat_id] = False
                    else:
                        raise
            else:
                logger.info(f"No call instance for {chat_id}")
                self.active_chats[chat_id] = False
        except Exception as e:
            logger.error(f"Failed to leave voice chat in {chat_id}: {e}")
    
    async def play_song(self, chat_id: int, song: Song):
        """Play a song in voice chat"""
        try:
            logger.info(f"Starting to play song in {chat_id}: {song.title}")
            
            call = self.get_call(chat_id)
            queue = queue_manager.get_queue(chat_id)
            
            # Check if it's a URL or a file
            is_url = song.file_path.startswith(("http://", "https://"))
            
            if not is_url:
                # Check if file exists
                if not os.path.exists(song.file_path):
                    raise FileNotFoundError(f"Audio file not found: {song.file_path}")
                
                file_size = os.path.getsize(song.file_path)
                logger.info(f"File exists: {song.file_path}")
                logger.info(f"File size: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
                
                # Validate file is not empty or corrupted
                if file_size < 1024:  # Less than 1KB is likely corrupted
                    raise ValueError(f"Audio file too small ({file_size} bytes), likely corrupted")
            else:
                logger.info(f"Playing from URL: {song.file_path}")
            
            # Small delay to ensure file is fully written (prevents audio breaking)
            # Reduced for ultra-fast playback
            if not is_url:
                if not os.path.exists(song.file_path):
                     await asyncio.sleep(0.1) # Reduced from 0.3s
                else:
                     pass # Removed 0.1s delay if file already exists
            
            # Create media stream - HIGH quality is often more stable for voice chats than STUDIO
            stream = MediaStream(
                song.file_path,
                audio_parameters=AudioQuality.HIGH
            )
            
            logger.info(f"Stream created for {chat_id}, calling play()...")
            logger.info(f"Stream details: file={song.file_path}, audio_quality=HIGH")
            
            # PyTgCalls v2: play() will automatically join the voice chat if not already in one
            await call.play(chat_id, stream)
            
            # Send playing message if this was an automatic play (not from play_command)
            # We check if it's the current song in queue
            # Actually, play_command handles its own send_playing_message for the first song
            # But for auto-playing next song, we need to send it here or in handle_stream_ended
            
            logger.info(f"✅ play() successful for {chat_id} - assistant should now be in voice chat")
            logger.info(f"PyTgCalls active: {call}, Chat active: {self.active_chats.get(chat_id, False)}")
            
            # Set volume
            await self.set_volume(chat_id, queue.volume)
            
            # Mark as playing (song is already added to queue in play.py)
            queue.is_playing = True
            
            logger.info(f"✅ Playing '{song.title}' in {chat_id}")
            
        except Exception as e:
            logger.error(f"Failed to play song in {chat_id}: {e}")
            logger.exception("Full traceback:")
            raise
    
    async def pause(self, chat_id: int):
        """Pause playback"""
        try:
            call = self.get_call(chat_id)
            await call.pause(chat_id)
            queue = queue_manager.get_queue(chat_id)
            queue.is_playing = False
            logger.info(f"Paused playback in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to pause in {chat_id}: {e}")
            raise
    
    async def resume(self, chat_id: int):
        """Resume playback"""
        try:
            call = self.get_call(chat_id)
            await call.resume(chat_id)
            queue = queue_manager.get_queue(chat_id)
            queue.is_playing = True
            logger.info(f"Resumed playback in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to resume in {chat_id}: {e}")
            raise
    
    async def stop(self, chat_id: int):
        """Stop playback"""
        try:
            call = self.get_call(chat_id)
            # PyTgCalls v2.x doesn't have stop() method
            # We need to clear the queue and leave voice chat instead
            queue = queue_manager.get_queue(chat_id)
            queue.is_playing = False
            queue.clear_queue()
            queue.current_song = None
            logger.info(f"Stopped playback in {chat_id}")
            
            # Leave voice chat after stop
            await self.leave_voice_chat(chat_id)
            # Reset active_chats flag
            self.active_chats[chat_id] = False
        except Exception as e:
            logger.error(f"Failed to stop in {chat_id}: {e}")
            raise
    
    async def skip(self, chat_id: int):
        """Skip current song"""
        try:
            queue = queue_manager.get_queue(chat_id)
            next_song = queue.skip_song()
            
            if next_song:
                await self.play_song(chat_id, next_song)
                return next_song
            else:
                # Queue is empty, leave voice chat after delay
                await self.auto_leave_voice_chat(chat_id)
                return None
        except Exception as e:
            logger.error(f"Failed to skip in {chat_id}: {e}")
            raise
    
    async def auto_leave_voice_chat(self, chat_id: int):
        """Auto leave voice chat when queue is empty"""
        try:
            queue = queue_manager.get_queue(chat_id)
            
            # Wait 30 seconds to see if new songs are added (increased from 10s)
            logger.info(f"Queue empty in {chat_id}, will auto-leave in 30 seconds if no songs added")
            await asyncio.sleep(30)
            
            # Check if queue is still empty
            if queue.is_empty() and not queue.current_song:
                await self.leave_voice_chat(chat_id)
                queue.clear_queue()
                logger.info(f"✅ Auto-left voice chat in {chat_id} (no songs playing)")
        except Exception as e:
            logger.error(f"Error in auto_leave for {chat_id}: {e}")
    
    async def set_volume(self, chat_id: int, volume: int):
        """Set volume (1-200)"""
        try:
            call = self.get_call(chat_id)
            volume = max(1, min(200, volume))  # Clamp between 1-200
            await call.change_volume_call(chat_id, volume)
            queue = queue_manager.get_queue(chat_id)
            queue.volume = volume
            logger.info(f"Volume set to {volume} in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to set volume in {chat_id}: {e}")
            raise
    
    async def mute(self, chat_id: int):
        """Mute playback"""
        await self.set_volume(chat_id, 0)
    
    async def unmute(self, chat_id: int):
        """Unmute playback"""
        queue = queue_manager.get_queue(chat_id)
        await self.set_volume(chat_id, queue.volume if queue.volume > 0 else DEFAULT_VOLUME)
    
    def is_playing(self, chat_id: int) -> bool:
        """Check if bot is playing in a chat"""
        queue = queue_manager.get_queue(chat_id)
        # Check if assistant is actually in the active_chats map and if a song is playing
        is_active = self.active_chats.get(chat_id, False)
        return queue.is_playing and is_active and queue.current_song is not None
    
    def get_current_song(self, chat_id: int) -> Optional[Song]:
        """Get currently playing song"""
        queue = queue_manager.get_queue(chat_id)
        return queue.current_song
    
    async def handle_stream_ended(self, chat_id: int, update: Update):
        """Handle stream ended event or voice chat closed event"""
        try:
            queue = queue_manager.get_queue(chat_id)
            
            # Handle Voice Chat Closed
            if isinstance(update, ChatUpdate):
                if update.status == ChatUpdate.Status.CLOSED_VOICE_CHAT:
                    logger.info(f"Voice chat closed in {chat_id}, clearing queue")
                    queue.clear_queue()
                    queue.current_song = None
                    queue.is_playing = False
                    self.active_chats[chat_id] = False
                    return

            # Only handle if the stream actually ended
            if not isinstance(update, StreamAudioEnded):
                return
            
            # Skip current song and get next
            next_song = queue.skip_song()
            
            if next_song:
                logger.info(f"Stream ended for {chat_id}, playing next song: {next_song.title}")
                await self.play_song(chat_id, next_song)
                
                # Notify about the next song
                from core.bot import bot_app
                from handlers.play import send_playing_message
                
                asyncio.create_task(
                    send_playing_message(
                        client=bot_app.app,
                        chat_id=chat_id,
                        song=next_song
                    )
                )
            else:
                # If queue is empty and no more songs, leave voice chat
                logger.info(f"Queue empty for chat {chat_id}, auto-leaving voice chat")
                
                # Mark as not playing IMMEDIATELY to allow new songs to play
                queue.is_playing = False
                queue.current_song = None
                
                # Wait 5 seconds before leaving to prevent rapid join/leave
                await asyncio.sleep(5)
                
                # Double check queue is still empty
                if queue.is_empty() and not queue.current_song:
                    await self.leave_voice_chat(chat_id)
                    logger.info(f"Auto-left voice chat in {chat_id}")
                    
                    # Log message about auto-leaving
                    from config import LOG_GROUP_ID
                    from core.bot import bot_app
                    if LOG_GROUP_ID:
                        try:
                            await bot_app.app.send_message(
                                LOG_GROUP_ID,
                                f"👋 **Assistant auto-left voice chat in `{chat_id}`** (Queue ended)"
                            )
                        except:
                            pass
                    
        except Exception as e:
            logger.error(f"Error handling stream ended in {chat_id}: {e}")
            logger.exception("Traceback:")


# Global call manager instance (will be initialized in bot.py)
call_manager: Optional[CallManager] = None
