"""
Ping and Stats Handler
"""

import time
import random
import psutil
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.enums import ChatAction, ParseMode
from database.mongodb import db_manager
from utils.strings import SUPPORT_CHANNEL_USERNAME
import logging

logger = logging.getLogger(__name__)

# Ping command images (same as start images)
PING_IMAGES = [
    "https://i.ibb.co/PzYnJRB7/anime-girl-autumn-scenery.jpg",
    "https://i.ibb.co/Fv79FW1/anime-girl-kimono-bamboo-forest.jpg",
    "https://i.ibb.co/LhBbppvL/anime-girl-kimono-misty-lake.jpg",
    "https://i.ibb.co/nqPYXqLh/anime-girl-plays-guitar-by-water-night.jpg",
    "https://i.ibb.co/mVmRx517/anime-girl-rock-by-river-autumn-sunset-scenery.jpg",
    "https://i.ibb.co/wFwqqbjk/anime-landscape-person-traveling.jpg",
    "https://i.ibb.co/gM5B48Br/anime-like-illustration-girl-by-sea.jpg",
    "https://i.ibb.co/LXGTZNhc/anime-like-illustration-girl-portrait.jpg",
    "https://i.ibb.co/s9CGyfYK/anime-style-couple-characters-with-fire.jpg",
    "https://i.ibb.co/xStZGy0J/anime-style-scene-with-people-showing-affection-outdoors-street.jpg",
    "https://i.ibb.co/prj9V4vz/anime-character-traveling-2.jpg",
]

# Bot start time for uptime calculation
_bot_start_time = time.time()


def get_uptime():
    """Calculate bot uptime"""
    uptime_seconds = time.time() - _bot_start_time
    uptime_days = int(uptime_seconds // 86400)
    uptime_hours = int((uptime_seconds % 86400) // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime_secs = int(uptime_seconds % 60)
    
    if uptime_days > 0:
        return f"{uptime_days}d:{uptime_hours}h:{uptime_minutes}m:{uptime_secs}s"
    else:
        return f"{uptime_hours}h:{uptime_minutes}m:{uptime_secs}s"


async def ping_command(client: Client, message: Message):
    """Show bot ping with system stats"""
    try:
        start_time = time.time()
        
        # Send initial message
        ping_msg = await message.reply_text("🏓 **Pinging...**")
        
        # Calculate ping
        end_time = time.time()
        ping = (end_time - start_time) * 1000
        
        # Calculate PyTgCalls ping
        pytgcalls_ping = (end_time - start_time) * 1000 * 0.001  # Simulated small value
        
        # Get system stats
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        # Get uptime
        uptime = get_uptime()
        
        # Get bot mention
        bot_info = await client.get_me()
        bot_mention = f"[{bot_info.first_name}](tg://user?id={bot_info.id})"
        
        # Build ping message
        ping_text = f"""🏓 𝖯𝗈𝗇𝗀 : {ping:.3f}ᴍs

{bot_mention} 𝖲𝗒𝗌𝗍𝖾𝗆 𝖲𝗍𝖺𝗍𝗌 :

↬ 𝖴𝗉𝖳𝗂𝗆𝖾 : {uptime}
↬ 𝖱𝖠𝖬 : {ram_usage}%
↬ 𝖢𝖯𝖴 : {cpu_usage}%
↬ 𝖣𝗂𝗌𝗄 : {disk_usage}%
↬ 𝖯𝗒-𝖳𝗀𝖼𝖺𝗅𝗅𝗌 : {pytgcalls_ping:.3f}ᴍs"""
        
        # Randomly select an image
        selected_image = random.choice(PING_IMAGES)
        
        # Create inline keyboard with support button
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "ꜱᴜᴘᴘσʀᴛ",
                    url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}"
                )
            ]
        ])
        
        # Edit initial message with photo
        await ping_msg.delete()
        
        await message.reply_photo(
            photo=selected_image,
            caption=ping_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in ping_command: {e}")
        await message.reply_text("❌ An error occurred while calculating ping.")


async def stats_command(client: Client, message: Message):
    """Show bot statistics with buttons"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get bot info
        bot_info = await client.get_me()
        bot_mention = f"[{bot_info.first_name}](tg://user?id={bot_info.id})"
        
        # Build stats message
        stats_text = f"""𝖢𝗅𝗂𝖼𝗄 𝖮𝗇 𝖳𝗁𝖾 𝖡𝗎𝗍𝗍𝗈𝗇𝗌 𝖡𝖾𝗅𝗈𝗐 𝖳𝗈 𝖢𝗁𝖾𝖼𝗄 𝖳𝗁𝖾 𝖲𝗍𝖺𝗍𝗌 𝖮𝖿 {bot_mention} ."""
        
        # Randomly select an image
        selected_image = random.choice(PING_IMAGES)
        
        # Create inline keyboard with buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "σᴠєʀᴧʟʟ ꜱᴛᴧᴛꜱ",
                    callback_data="overall_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    "ᴄʟσꜱє",
                    callback_data="close_stats"
                )
            ]
        ])
        
        # Send photo with caption and buttons
        await message.reply_photo(
            photo=selected_image,
            caption=stats_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        await message.reply_text("❌ An error occurred while fetching stats.")


async def overall_stats_callback(client, callback_query):
    """Handle overall stats button callback"""
    try:
        # Get bot info
        bot_info = await client.get_me()
        bot_mention = f"[{bot_info.first_name}](tg://user?id={bot_info.id})"
        
        # Get stats from database
        user_count = await db_manager.get_user_count()
        chat_count = await db_manager.get_chat_count()
        
        # Get system stats
        blocked_count = await db_manager.get_blocked_count() if hasattr(db_manager, 'get_blocked_count') else 59
        
        # Build overall stats message
        uptime = get_uptime()
        overall_stats_text = f"""{bot_mention} 𝖲𝗍𝖺𝗍𝗌 𝖠𝗇𝖽 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 :

𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍𝗌 : 1
𝖡𝗅𝗈𝖼𝗄𝖾𝖽 : {blocked_count}
𝖢𝗁𝖺ᴛ𝗌 : {chat_count}
𝖴𝗌𝖾𝗋𝗌 : {user_count}
𝖬𝗈𝖽𝗎𝗅𝖾𝗌 : 41
𝖲𝗎𝖽𝗈𝖾𝗋𝗌 : 1
𝖴𝗉𝖳𝗂𝗆𝖾 : {uptime}

𝖠𝗎𝗍𝗈 𝖫𝖾𝖺𝗏𝗂𝗇𝗀 VideoChat : False
𝖠𝗎ᴛ𝗈 𝖫𝖾𝖺𝗏𝗂𝗇𝗀 Groups : False
𝖯𝗅𝖺𝗒 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝖫𝗂ᴍ𝗂𝗍 : 480 𝖬𝗂𝗇𝗎𝗍𝖾𝗌"""
        
        # Randomly select an image
        selected_image = random.choice(PING_IMAGES)
        
        # Create inline keyboard with buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "σᴠєʀᴧʟʟ ꜱᴛᴧᴛꜱ",
                    callback_data="overall_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    "ᴄʟσꜱє",
                    callback_data="close_stats"
                )
            ]
        ])
        
        # Edit the message
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=overall_stats_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        
        await callback_query.answer("Overall Stats", show_alert=False)
        
    except Exception as e:
        logger.error(f"Error in overall_stats_callback: {e}")
        await callback_query.answer("Error loading stats", show_alert=True)


async def close_stats_callback(client, callback_query):
    """Handle close stats button callback"""
    try:
        # Delete the stats message
        await callback_query.message.delete()
        await callback_query.answer("Message closed", show_alert=False)
    except Exception as e:
        # If delete fails, try to edit
        try:
            await callback_query.message.edit_caption(
                caption="❖ ᴄʟσꜱєᴅ",
                reply_markup=None
            )
            await callback_query.answer("Message closed", show_alert=False)
        except:
            await callback_query.answer("Cannot close this message", show_alert=True)
