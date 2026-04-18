"""
Maintenance Handler - Maintenance mode and logging
"""

import logging
import os
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from database.mongodb import db_manager
from utils.decorators import owner_only
from config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)


async def clean_bot_data():
    """Logic to clean cache and temporary files"""
    try:
        # Clear download directory
        if os.path.exists(DOWNLOAD_DIR):
            for file in os.listdir(DOWNLOAD_DIR):
                file_path = os.path.join(DOWNLOAD_DIR, file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}. Reason: {e}")
        
        # Clear thumbnail cache (assets)
        assets_dir = "assets"
        if os.path.exists(assets_dir):
            for file in os.listdir(assets_dir):
                if file.startswith("thumb_") and file.endswith(".png"):
                    try:
                        os.remove(os.path.join(assets_dir, file))
                    except:
                        pass
        
        # Clear bot logs if too large (optional)
        # with open("bot.log", "w") as f:
        #     f.write("")
            
        return True
    except Exception as e:
        logger.error(f"Error during cleaning: {e}")
        return False


@owner_only
async def clean_command(client: Client, message: Message):
    """Manually clear bot data"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        status = await clean_bot_data()
        if status:
            await message.reply_text("✅ **Bot maintenance complete!**\n\n- Cleared download cache\n- Removed temporary thumbnails\n- Optimized storage.")
        else:
            await message.reply_text("❌ Failed to perform full maintenance.")
            
    except Exception as e:
        logger.error(f"Error in clean_command: {e}")
        await message.reply_text("❌ An error occurred during cleaning.")


@owner_only
async def restart_command(client: Client, message: Message):
    """Manually restart the bot"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        await message.reply_text("🔄 **Restarting...**\n\nThe bot will be back online in a few seconds.")
        
        from core.bot import bot_app
        if bot_app:
            await bot_app.restart()
            
    except Exception as e:
        logger.error(f"Error in restart_command: {e}")
        await message.reply_text("❌ Failed to initiate restart.")


@owner_only
async def logs_command(client: Client, message: Message):
    """Get bot logs"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Send the log file
        if message.chat.type == 'private':
            await message.reply_document(
                document="bot.log",
                caption="📜 **Bot Logs**"
            )
        else:
            # Send in private chat for security
            await message.reply_text(
                "📜 Logs have been sent to your private chat."
            )
            # Try to send to user's PM
            try:
                await client.send_document(
                    chat_id=message.from_user.id,
                    document="bot.log",
                    caption="📜 **Bot Logs**"
                )
            except:
                pass
        
    except Exception as e:
        logger.error(f"Error in logs_command: {e}")
        await message.reply_text("❌ An error occurred while fetching logs.")


@owner_only
async def logger_command(client: Client, message: Message):
    """Toggle logging"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide enable/disable.\n\n"
                "**Usage:** `/logger [enable/disable]`"
            )
            return
        
        action = message.command[1].lower()
        
        if action in ['enable', 'on']:
            await db_manager.set_setting('logging_enabled', True)
            await message.reply_text("✅ **Logging enabled!**")
        elif action in ['disable', 'off']:
            await db_manager.set_setting('logging_enabled', False)
            await message.reply_text("✅ **Logging disabled!**")
        else:
            await message.reply_text("❌ Invalid action. Use `enable` or `disable`.")
        
    except Exception as e:
        logger.error(f"Error in logger_command: {e}")
        await message.reply_text("❌ An error occurred while toggling logging.")


@owner_only
async def maintenance_command(client: Client, message: Message):
    """Toggle maintenance mode"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide enable/disable.\n\n"
                "**Usage:** `/maintenance [enable/disable]`"
            )
            return
        
        action = message.command[1].lower()
        
        if action in ['enable', 'on']:
            await db_manager.set_setting('maintenance_mode', True)
            await message.reply_text(
                "⚠️ **Maintenance mode enabled!**\n\n"
                "The bot is now in maintenance mode.\n"
                "Only sudoers can use the bot."
            )
        elif action in ['disable', 'off']:
            await db_manager.set_setting('maintenance_mode', False)
            await message.reply_text(
                "✅ **Maintenance mode disabled!**\n\n"
                "The bot is now available for all users."
            )
        else:
            await message.reply_text("❌ Invalid action. Use `enable` or `disable`.")
        
    except Exception as e:
        logger.error(f"Error in maintenance_command: {e}")
        await message.reply_text("❌ An error occurred while toggling maintenance mode.")
