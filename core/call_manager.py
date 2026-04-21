"""
Voice Chat Manager using PyTGCalls
Handles all voice chat operations
"""

import asyncio
import os
import time
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
        self.calls: Dict[int, PyTgCalls] = {} # Map chat_id to PyTgCalls instance
        self.assistant_calls: Dict[int, PyTgCalls] = {} # Map assistant_id to PyTgCalls instance
        self.active_chats: Dict[int, bool] = {}
        self.chat_assistants: Dict[int, int] = {} # Map chat_id to assistant_id
        
    async def initialize_user_client(self):
        """Initialize user account client and PyTgCalls instances for all assistants"""
        # ... legacy support ...
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

        # Initialize PyTgCalls for all assistants and start them
        from core.userbot import assistant_manager
        for assistant in assistant_manager.assistants:
            assistant_id = assistant.me.id
            if assistant_id not in self.assistant_calls:
                logger.info(f"Initializing PyTgCalls for assistant {assistant_id}")
                call = PyTgCalls(assistant)
                self.assistant_calls[assistant_id] = call
                
                # Start the call instance immediately
                try:
                    await call.start()
                    logger.info(f"✅ Started PyTgCalls for assistant {assistant_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to start PyTgCalls for assistant {assistant_id}: {e}")

                # Register event handler for stream ended
                @call.on_update()
                async def stream_ended_handler(client: PyTgCalls, update: Update, assistant_id=assistant_id):
                    # We need to find which chat_id this update belongs to
                    # PyTgCalls update usually has chat_id
                    if isinstance(update, StreamAudioEnded):
                        await self.handle_stream_ended(update.chat_id, update)
    
    def get_call(self, chat_id: int) -> PyTgCalls:
        """Get or create PyTgCalls instance for a chat (reusing assistant instances)"""
        # If we already have an assistant assigned to this chat, use its call instance
        if chat_id in self.chat_assistants:
            assistant_id = self.chat_assistants[chat_id]
            if assistant_id in self.assistant_calls:
                return self.assistant_calls[assistant_id]

        # Otherwise, pick an assistant and assign it to this chat
        from core.userbot import assistant_manager
        
        client = None
        if assistant_manager.assistants:
            client = assistant_manager.get_next_assistant()
            assistant_id = client.me.id
            self.chat_assistants[chat_id] = assistant_id
            
            # Ensure PyTgCalls is initialized for this assistant
            if assistant_id not in self.assistant_calls:
                logger.info(f"Initializing PyTgCalls for assistant {assistant_id}")
                call = PyTgCalls(client)
                self.assistant_calls[assistant_id] = call
                # Note: We should ideally start it in initialize_user_client, 
                # but if an assistant is added later, we start it here.
                # However, start() is blocking, so we should be careful.
                # We'll try to start it if not already running.
                
            return self.assistant_calls[assistant_id]
            
        # Fallback to user_client or app
        client = self.user_client if self.user_client else self.app
        assistant_id = client.me.id if hasattr(client, 'me') else 0
        self.chat_assistants[chat_id] = assistant_id
        
        if assistant_id not in self.assistant_calls:
            self.assistant_calls[assistant_id] = PyTgCalls(client)
            
        return self.assistant_calls[assistant_id]
    
    async def join_voice_chat(self, chat_id: int, chat_username: str = None) -> bool:
        """Join voice chat in a group or channel. Returns True if assistant was invited, False if already present"""
        try:
            from core.userbot import assistant_manager
            from pytgcalls.exceptions import PyTgCallsAlreadyRunning
            
            logger.info(f"⚡ Joining voice chat in {chat_id}...")
            
            # ⚡ FAST SKIP: Check if already active and playing
            if self.active_chats.get(chat_id, False):
                logger.info(f"✅ Voice chat already active for {chat_id}")
                return True
            
            # ⚡ OPTIMIZED: Check membership with reduced cache time (5 min instead of 1 hour)
            assistant_already_present = await assistant_manager.is_assistant_in_chat(chat_id)
            
            # ⚡ FAST: Ensure assistant is in the chat (non-blocking if already present)
            if not assistant_already_present:
                await assistant_manager.ensure_assistant_in_chat(chat_id, chat_username)
            
            call = self.get_call(chat_id)
            
            # ⚡ Start PyTgCalls immediately
            try:
                logger.info(f"⚡ Starting PyTgCalls for {chat_id}...")
                await call.start()
                self.active_chats[chat_id] = True
                logger.info(f"✅ PyTgCalls started for {chat_id}")
            except PyTgCallsAlreadyRunning:
                logger.info(f"PyTgCalls already running for {chat_id}")
                self.active_chats[chat_id] = True
            
            return assistant_already_present
        except Exception as e:
            error_str = str(e)
            logger.error(f"Failed to join voice chat in {chat_id}: {error_str}")
            logger.exception("Full traceback:")
            
            # Provide better error messages for common issues
            if "CHANNEL_INVALID" in error_str or "ChannelInvalid" in error_str:
                raise ValueError(
                    f"Bot does not have access to this chat/channel (ID: {chat_id}). "
                    f"Please ensure the bot and assistant are added as admins with voice chat permissions."
                ) from e
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
            
            # ⚡ REMOVED delay - file should be ready from API stream
            # No sleep needed for URL streams
            
            # Create media stream - HIGH quality for stability
            # Add ffmpeg parameters for better stream handling
            stream = MediaStream(
                song.file_path,
                audio_parameters=AudioQuality.HIGH,
                ffmpeg_parameters='-reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 2'
            )
            
            logger.info(f"⚡ Stream created for {chat_id}, calling play()...")
            
            # ⚡ PyTgCalls v2: play() will automatically join the voice chat if not already in one
            # Add timeout to prevent hanging
            try:
                await asyncio.wait_for(call.play(chat_id, stream), timeout=30.0)
            except asyncio.TimeoutError:
                logger.error(f"Play operation timed out for {chat_id}")
                raise TimeoutError(f"Failed to play song: operation timed out. The stream might be unreachable.")
            
            logger.info(f"✅ play() successful for {chat_id}")
            
            # Set volume
            await self.set_volume(chat_id, queue.volume)
            
            # Mark as playing (song is already added to queue in play.py)
            queue.is_playing = True
            queue.start_time = time.time()
            
            logger.info(f"✅ Playing '{song.title}' in {chat_id}")
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Failed to play song in {chat_id}: {error_str}")
            logger.exception("Full traceback:")
            
            # Handle GROUPCALL_INVALID - reset state and re-raise with helpful message
            if "GROUPCALL_INVALID" in error_str or "GroupcallInvalid" in error_str:
                # Reset the active chat state since the voice chat is invalid
                self.active_chats[chat_id] = False
                logger.warning(f"Voice chat in {chat_id} is invalid. State reset. User should start a new voice chat.")
                raise ValueError(
                    f"The voice chat in this group has ended or is invalid. "
                    f"Please start a new voice chat and try again."
                ) from e
            
            # Handle timeout errors
            if "TimeoutError" in error_str or "timed out" in error_str.lower():
                logger.warning(f"Stream timeout for {chat_id}. The audio source might be slow or unreachable.")
                raise ValueError(
                    f"Failed to play: The audio stream timed out. "
                    f"This usually means the audio source is slow or unreachable. "
                    f"Please try again or try a different song."
                ) from e
            
            # Re-raise with better context for specific errors
            if "CHANNEL_INVALID" in error_str or "ChannelInvalid" in error_str:
                raise ValueError(f"Bot does not have access to this chat (ID: {chat_id}). Please add the bot as admin.") from e
            # Don't raise FLOOD_WAIT - it's temporary and will be retried by user
            if "FLOOD_WAIT" in error_str:
                raise ValueError(f"Telegram rate limit reached. Please wait a few seconds and try again.") from e
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
        """Stop playback - immediately clear queue and leave voice chat"""
        try:
            call = self.get_call(chat_id)
            queue = queue_manager.get_queue(chat_id)
            
            # Immediately clear all queue data
            queue.is_playing = False
            queue.current_song = None
            queue.clear_queue()
            
            logger.info(f"Stopped playback in {chat_id}, leaving voice chat immediately")
            
            # Leave voice chat immediately
            await self.leave_voice_chat(chat_id)
            
            # Reset active_chats flag
            self.active_chats[chat_id] = False
            
            logger.info(f"✅ Successfully stopped and left voice chat in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to stop in {chat_id}: {e}")
            # Even if there's an error, try to reset the state
            queue = queue_manager.get_queue(chat_id)
            queue.is_playing = False
            queue.current_song = None
            queue.clear_queue()
            self.active_chats[chat_id] = False
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
        """Auto leave voice chat when queue is empty after skipping"""
        try:
            queue = queue_manager.get_queue(chat_id)
            
            # Wait 5 seconds to see if new songs are added
            logger.info(f"Queue empty in {chat_id} after skip, will auto-leave in 5 seconds if no songs added")
            await asyncio.sleep(5)
            
            # Check if queue is still empty and no song is playing
            if queue.is_empty() and not queue.current_song:
                logger.info(f"Queue still empty in {chat_id}, leaving voice chat")
                await self.leave_voice_chat(chat_id)
                
                # Reset state
                queue.clear_queue()
                self.active_chats[chat_id] = False
                
                logger.info(f"✅ Auto-left voice chat in {chat_id} (no songs playing)")
                
                # Send notification to the chat
                try:
                    from core.bot import bot_app
                    if bot_app and bot_app.app:
                        await bot_app.app.send_message(
                            chat_id,
                            "🎵 **Queue is empty!**\n\n"
                            "The assistant has left the voice chat.\n"
                            "Use /play to start playing again. 🎤"
                        )
                except Exception as e:
                    logger.warning(f"Failed to send auto-leave message: {e}")
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
    
    async def seek(self, chat_id: int, seconds: int) -> bool:
        """Seek to a specific position in the current stream"""
        try:
            call = self.get_call(chat_id)
            queue = queue_manager.get_queue(chat_id)
            
            if not queue.current_song:
                return False
                
            # PyTgCalls v2.x seek: play the same stream but with seek_offset
            from pytgcalls.types import MediaStream
            from pytgcalls.types import AudioQuality
            
            stream = MediaStream(
                queue.current_song.file_path,
                audio_parameters=AudioQuality.HIGH,
                ffmpeg_parameters=f"-ss {seconds}"
            )
            
            await call.play(chat_id, stream)
            
            # Update start time for position estimation
            queue.start_time = time.time() - seconds
            
            logger.info(f"Seeked to {seconds}s in {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to seek in {chat_id}: {e}")
            return False
    
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
                
                # Wait 3 seconds before leaving to give users time to add more songs
                await asyncio.sleep(3)
                
                # Double check queue is still empty before leaving
                if queue.is_empty() and not queue.current_song:
                    logger.info(f"Queue still empty after 3s, leaving voice chat in {chat_id}")
                    
                    # Send notification BEFORE leaving
                    try:
                        from core.bot import bot_app
                        if bot_app and bot_app.app:
                            await bot_app.app.send_message(
                                chat_id,
                                "🎵 **Queue completed!**\n\n"
                                "All songs have been played. The assistant will now leave the voice chat.\n"
                                "Use /play to start playing again. 🎤"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to send queue completion message: {e}")
                    
                    # Now leave the voice chat
                    await self.leave_voice_chat(chat_id)
                    
                    # Reset state
                    self.active_chats[chat_id] = False
                    
                    logger.info(f"✅ Auto-left voice chat in {chat_id} (queue completed)")
                    
        except Exception as e:
            logger.error(f"Error handling stream ended in {chat_id}: {e}")
            logger.exception("Traceback:")


# Global call manager instance (will be initialized in bot.py)
call_manager: Optional[CallManager] = None
