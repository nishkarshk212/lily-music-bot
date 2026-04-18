"""
Channel Play Handler - Play music in channels
"""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from core.queue import queue_manager, Song
from core.call_manager import call_manager
from utils.downloader import downloader
from utils.thumbnail_generator import create_thumbnail
from utils.formatter import format_time
from utils.decorators import admin_check, bot_can_manage_vc
from utils.strings import NOW_PLAYING_MESSAGE, SUCCESS_ADDED_TO_QUEUE, CONTROLS_HELP, ERROR_NO_RESULTS, ERROR_QUEUE_FULL
from config import MAX_QUEUE_SIZE
import logging

logger = logging.getLogger(__name__)


@admin_check
@bot_can_manage_vc
async def cplay_command(client: Client, message: Message):
    """Play audio in channel"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get query
        if len(message.command) < 2 and not message.reply_to_message:
            await message.reply_text(
                "❌ Please provide a song name or URL.\n\n"
                "**Usage:** `/cplay <song name or URL>`"
            )
            return
        
        if message.reply_to_message:
            query = message.reply_to_message.text or message.reply_to_message.caption
        else:
            query = message.text.split(None, 1)[1]
        
        # Download and process song
        status_msg = await message.reply_text(f"🔍 **Searching:** {query}")
        
        # Search and download
        result = await downloader.search_and_download(query)
        if not result:
            await status_msg.edit_text(ERROR_NO_RESULTS.format(query=query))
            return
        
        # Create song object
        song = Song(
            title=result['title'],
            duration=result['duration'],
            file_path=result['file_path'],
            requester=message.from_user.mention,
            chat_id=message.chat.id
        )
        
        # Add to queue
        queue = queue_manager.get_queue(message.chat.id)
        position = queue.add_song(song)
        
        if position == 1:
            # Start playing
            queue.current_song = song
            queue.is_playing = True
            
            await status_msg.edit_text(
                NOW_PLAYING_MESSAGE.format(
                    title=song.title,
                    duration=format_time(song.duration),
                    requester=song.requester
                )
            )
            
            # Join channel voice chat and play
            # Note: This requires channel configuration
            await message.reply_text(
                "⚠️ **Channel Play**\n\n"
                "Please configure channel using `/channelplay` first."
            )
        else:
            await status_msg.edit_text(
                SUCCESS_ADDED_TO_QUEUE.format(
                    title=song.title,
                    duration=format_time(song.duration),
                    requester=song.requester,
                    position=position
                ) + "\n\n" + CONTROLS_HELP
            )
        
    except Exception as e:
        logger.error(f"Error in cplay_command: {e}")
        await message.reply_text("❌ An error occurred while processing your request.")


@admin_check
@bot_can_manage_vc
async def cvplay_command(client: Client, message: Message):
    """Play video in channel"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get query
        if len(message.command) < 2 and not message.reply_to_message:
            await message.reply_text(
                "❌ Please provide a video name or URL.\n\n"
                "**Usage:** `/cvplay <video name or URL>`"
            )
            return
        
        if message.reply_to_message:
            query = message.reply_to_message.text or message.reply_to_message.caption
        else:
            query = message.text.split(None, 1)[1]
        
        # Download and process video
        status_msg = await message.reply_text(f"🔍 **Searching:** {query}")
        
        # Search and download video
        result = await downloader.search_and_download_video(query)
        if not result:
            await status_msg.edit_text(ERROR_NO_RESULTS.format(query=query))
            return
        
        # Create song object
        song = Song(
            title=result['title'],
            duration=result['duration'],
            file_path=result['file_path'],
            requester=message.from_user.mention,
            chat_id=message.chat.id
        )
        
        # Add to queue
        queue = queue_manager.get_queue(message.chat.id)
        position = queue.add_song(song)
        
        if position == 1:
            # Start playing
            queue.current_song = song
            queue.is_playing = True
            
            await status_msg.edit_text(
                NOW_PLAYING_MESSAGE.format(
                    title=song.title,
                    duration=format_time(song.duration),
                    requester=song.requester
                )
            )
            
            await message.reply_text(
                "⚠️ **Channel Video Play**\n\n"
                "Please configure channel using `/channelplay` first."
            )
        else:
            await status_msg.edit_text(
                SUCCESS_ADDED_TO_QUEUE.format(
                    title=song.title,
                    duration=format_time(song.duration),
                    requester=song.requester,
                    position=position
                ) + "\n\n" + CONTROLS_HELP
            )
        
    except Exception as e:
        logger.error(f"Error in cvplay_command: {e}")
        await message.reply_text("❌ An error occurred while processing your request.")


@admin_check
async def channelplay_command(client: Client, message: Message):
    """Connect channel to a group"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide a channel username/ID or `disable`.\n\n"
                "**Usage:** `/channelplay [channel username or ID]` or `/channelplay disable`"
            )
            return
        
        action = message.command[1].lower()
        
        if action == 'disable':
            # Disable channel play
            from database.mongodb import db_manager
            await db_manager.set_channel_play(message.chat.id, None)
            
            await message.reply_text(
                "✅ **Channel play disabled for this chat.**"
            )
        else:
            # Enable channel play
            channel_input = message.command[1]
            
            # Get channel info
            try:
                if channel_input.startswith('@'):
                    channel = await client.get_chat(channel_input)
                else:
                    channel = await client.get_chat(int(channel_input))
                
                # Verify it's a channel
                if channel.type != 'channel':
                    await message.reply_text("❌ Please provide a valid channel.")
                    return
                
                # Save channel configuration
                from database.mongodb import db_manager
                await db_manager.set_channel_play(message.chat.id, channel.id)
                
                await message.reply_text(
                    f"✅ **Channel connected!**\n\n"
                    f"Channel: {channel.title}\n"
                    f"Username: @{channel.username if channel.username else 'None'}\n\n"
                    f"You can now use `/cplay` and `/cvplay` commands."
                )
                
            except Exception as e:
                await message.reply_text(f"❌ Could not find channel: {channel_input}")
                return
        
    except Exception as e:
        logger.error(f"Error in channelplay_command: {e}")
        await message.reply_text("❌ An error occurred while configuring channel play.")
