"""
Speed Handler - Control playback speed
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
async def speed_command(client: Client, message: Message):
    """Adjust audio playback speed in group"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get speed value
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide a speed value.\n\n"
                "**Usage:** `/speed [value]`\n"
                "**Examples:**\n"
                "- `/speed 1.0` - Normal speed\n"
                "- `/speed 1.5` - 1.5x speed\n"
                "- `/speed 2.0` - 2x speed\n"
                "- `/speed 0.5` - Half speed"
            )
            return
        
        try:
            speed = float(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid speed. Please provide a number (e.g., 1.5).")
            return
        
        # Validate speed range
        if speed < 0.5 or speed > 2.0:
            await message.reply_text("❌ Speed must be between 0.5 and 2.0")
            return
        
        # Check if playing
        if not call_manager.current_call or not call_manager.current_call.is_playing:
            await message.reply_text("❌ No song is currently playing!")
            return
        
        # Set speed
        success = await call_manager.current_call.set_speed(speed)
        
        if success:
            await message.reply_text(
                f"✅ **Playback speed updated!**\n\n"
                f"🎵 Speed: {speed}x"
            )
        else:
            await message.reply_text("❌ Failed to change playback speed.")
        
    except Exception as e:
        logger.error(f"Error in speed_command: {e}")
        await message.reply_text("❌ An error occurred while changing speed.")


@admin_check
@bot_can_manage_vc
async def cspeed_command(client: Client, message: Message):
    """Adjust audio playback speed in channel"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get speed value
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide a speed value.\n\n"
                "**Usage:** `/cspeed [value]`\n"
                "**Examples:**\n"
                "- `/cspeed 1.0` - Normal speed\n"
                "- `/cspeed 1.5` - 1.5x speed\n"
                "- `/cspeed 2.0` - 2x speed\n"
                "- `/cspeed 0.5` - Half speed"
            )
            return
        
        try:
            speed = float(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid speed. Please provide a number (e.g., 1.5).")
            return
        
        # Validate speed range
        if speed < 0.5 or speed > 2.0:
            await message.reply_text("❌ Speed must be between 0.5 and 2.0")
            return
        
        # Check if playing
        if not call_manager.current_call or not call_manager.current_call.is_playing:
            await message.reply_text("❌ No song is currently playing!")
            return
        
        # Set speed
        success = await call_manager.current_call.set_speed(speed)
        
        if success:
            await message.reply_text(
                f"✅ **Channel playback speed updated!**\n\n"
                f"🎵 Speed: {speed}x"
            )
        else:
            await message.reply_text("❌ Failed to change playback speed.")
        
    except Exception as e:
        logger.error(f"Error in cspeed_command: {e}")
        await message.reply_text("❌ An error occurred while changing speed.")


# Aliases for playback commands
playback_command = speed_command
cplayback_command = cspeed_command
