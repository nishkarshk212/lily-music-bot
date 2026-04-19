"""
Seek Handler - Seek within a playing stream
"""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from core.call_manager import call_manager
from utils.decorators import admin_check, bot_can_manage_vc
import logging

logger = logging.getLogger(__name__)


@admin_check
@bot_can_manage_vc
async def seek_command(client: Client, message: Message):
    """Seek forward in the current stream"""
    try:
        chat_id = message.chat.id
        from core.queue import queue_manager
        queue = queue_manager.get_queue(chat_id)
        
        # Check if playing
        if not queue.current_song or not queue.is_playing:
            await message.reply_text("❌ No song is currently playing!")
            return
            
        # Get duration to seek
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide duration in seconds.\n\n"
                "**Usage:** `/seek [duration in seconds]`\n"
                "**Example:** `/seek 60` (seek forward 60 seconds)"
            )
            return
        
        try:
            duration = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid duration. Please provide a number.")
            return
        
        # Estimate current position
        import time
        current_position = int(time.time() - queue.start_time)
        new_position = current_position + duration
        
        # Check if new position is within bounds
        if new_position >= queue.current_song.duration:
            await message.reply_text("❌ Cannot seek beyond the end of the song!")
            return
        
        # Perform seek
        success = await call_manager.seek(chat_id, new_position)
        
        if success:
            await message.reply_text(
                f"✅ **δєєᴋєᴅ ꜰσʀᴡᴧʀᴅ!**\n\n"
                f"⏱ ᴅᴜʀᴧᴛɪση: {duration} ꜱєᴄσηᴅꜱ\n"
                f"📍 ηєᴡ ᴘσꜱɪᴛɪση: {new_position} ꜱєᴄσηᴅꜱ"
            )
        else:
            await message.reply_text("❌ Failed to seek.")
        
    except Exception as e:
        logger.error(f"Error in seek_command: {e}")
        await message.reply_text("❌ An error occurred while seeking.")


@admin_check
@bot_can_manage_vc
async def seekback_command(client: Client, message: Message):
    """Seek backward in the current stream"""
    try:
        chat_id = message.chat.id
        from core.queue import queue_manager
        queue = queue_manager.get_queue(chat_id)
        
        # Check if playing
        if not queue.current_song or not queue.is_playing:
            await message.reply_text("❌ No song is currently playing!")
            return
            
        # Get duration to seek back
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide duration in seconds.\n\n"
                "**Usage:** `/seekback [duration in seconds]`\n"
                "**Example:** `/seekback 30` (seek backward 30 seconds)"
            )
            return
        
        try:
            duration = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid duration. Please provide a number.")
            return
        
        # Estimate current position
        import time
        current_position = int(time.time() - queue.start_time)
        new_position = max(0, current_position - duration)
        
        # Perform seek
        success = await call_manager.seek(chat_id, new_position)
        
        if success:
            await message.reply_text(
                f"✅ **δєєᴋєᴅ ʙᴧᴄᴋᴡᴧʀᴅ!**\n\n"
                f"⏱ ᴅᴜʀᴧᴛɪση: {duration} ꜱєᴄσηᴅꜱ\n"
                f"📍 ηєᴡ ᴘσδɪᴛɪση: {new_position} ꜱєᴄσηᴅꜱ"
            )
        else:
            await message.reply_text("❌ Failed to seek.")
        
    except Exception as e:
        logger.error(f"Error in seekback_command: {e}")
        await message.reply_text("❌ An error occurred while seeking.")
