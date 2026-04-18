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
        await message.reply_chat_action(ChatAction.TYPING)
        
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
        
        # Check if playing
        if not call_manager.current_call or not call_manager.current_call.is_playing:
            await message.reply_text("❌ No song is currently playing!")
            return
        
        # Seek forward
        current_position = call_manager.current_call.position
        new_position = current_position + duration
        
        # Perform seek
        success = await call_manager.current_call.seek(new_position)
        
        if success:
            await message.reply_text(
                f"✅ **Seeked forward!**\n\n"
                f"⏱ Duration: {duration} seconds\n"
                f"📍 New position: {new_position} seconds"
            )
        else:
            await message.reply_text("❌ Failed to seek. The duration may be beyond the track length.")
        
    except Exception as e:
        logger.error(f"Error in seek_command: {e}")
        await message.reply_text("❌ An error occurred while seeking.")


@admin_check
@bot_can_manage_vc
async def seekback_command(client: Client, message: Message):
    """Seek backward in the current stream"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
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
        
        # Check if playing
        if not call_manager.current_call or not call_manager.current_call.is_playing:
            await message.reply_text("❌ No song is currently playing!")
            return
        
        # Seek backward
        current_position = call_manager.current_call.position
        new_position = max(0, current_position - duration)
        
        # Perform seek
        success = await call_manager.current_call.seek(new_position)
        
        if success:
            await message.reply_text(
                f"✅ **Seeked backward!**\n\n"
                f"⏱ Duration: {duration} seconds\n"
                f"📍 New position: {new_position} seconds"
            )
        else:
            await message.reply_text("❌ Failed to seek.")
        
    except Exception as e:
        logger.error(f"Error in seekback_command: {e}")
        await message.reply_text("❌ An error occurred while seeking backward.")
