"""
Queue Command Handlers
Handles /queue and /clearqueue commands
"""

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from core.queue import queue_manager
from utils.formatter import format_time, truncate_text
from utils.decorators import admin_check
from utils.strings import QUEUE_MESSAGE, SUPPORT_CHANNEL_USERNAME
from utils.group_start import GROUP_START_IMAGES
import random
import logging

logger = logging.getLogger(__name__)


async def queue_command(client: Client, message: Message):
    """Handle /queue command"""
    try:
        chat_id = message.chat.id
        queue = queue_manager.get_queue(chat_id)
        
        # Get current song
        current_song = queue.current_song
        queue_list = queue.get_queue()
        
        if not current_song and not queue_list:
            await message.reply_text(
                "📋 **Queue is Empty!**\n\n"
                "Use /play to add songs to the queue."
            )
            return
        
        # Get bot info for mention
        bot_info = await client.get_me()
        bot_name = bot_info.first_name
        bot_mention = f"<a href='https://t.me/{bot_info.username}'>{bot_name}</a>"
        
        # Build queue player message
        queue_text = f"""
<b>{bot_mention} 𝖯𝗅𝖺𝗒𝖾𝗋</b>

🎄 𝖲𝗍𝗋𝖾𝖺𝗆𝗂𝗇𝗀 : {truncate_text(current_song.title, 60) if current_song else "None"}
🔗 𝖲𝗍𝗋𝖾𝖺𝗆 𝖳𝗒𝗉𝖾 : Audio
🥀  𝖱𝖾𝗊𝗎𝖾𝗌𝗍𝖾𝖽 𝖡𝗒 : {current_song.requester if current_song else "None"}
"""
        
        # Add queue list if exists
        if queue_list:
            queue_text += f"\n<b>𝖰𝗎𝖾𝗎𝖾 ({len(queue_list)} sᴏɴɢs):</b>\n"
            for i, song in enumerate(queue_list[:10], 1):
                queue_text += f"\n{i}. {truncate_text(song.title, 50)}\n"
                queue_text += f"   ⏱ {format_time(song.duration)} | 👤 {song.requester}"
            
            if len(queue_list) > 10:
                queue_text += f"\n\n... ᴀɴᴅ {len(queue_list) - 10} ᴍᴏʀᴇ sᴏɴɢs"
        
        # Add loop status
        if queue.loop_count > 0:
            queue_text += f"\n\n🔁 Loop: {queue.loop_count} ᴛɪᴍᴇs ʀᴇᴍᴀɪɴɪɴɢ"
        elif queue.loop_queue:
            queue_text += "\n\n🔁 Queue Loop: Eɴᴀʙʟᴇᴅ"
        
        # Create keyboard with queue and close buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ǫᴜєᴜє •", callback_data="queue_list"),
                InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")
            ],
            [
                InlineKeyboardButton("⊜ ꜱᴜᴘᴘσʀᴛ ⊜", url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}")
            ]
        ])
        
        # Send with random image
        selected_image = random.choice(GROUP_START_IMAGES)
        
        await message.reply_photo(
            photo=selected_image,
            caption=queue_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Queue command error: {e}")
        await message.reply_text("❌ Failed to get queue. Please try again.")


@admin_check
async def clear_queue_command(client: Client, message: Message):
    """Handle /clearqueue command"""
    try:
        chat_id = message.chat.id
        queue = queue_manager.get_queue(chat_id)
        
        queue.clear_queue()
        
        await message.reply_text(
            "✅ **Queue Cleared!**\n\n"
            "All songs have been removed from the queue."
        )
        
        logger.info(f"Queue cleared by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Clear queue command error: {e}")
        await message.reply_text("❌ Failed to clear queue. Please try again.")
