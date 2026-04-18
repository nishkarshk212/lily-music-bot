"""
Admin Handlers - Start and Help commands
"""

import os
import random
import time
import logging
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction, ParseMode
from utils.strings import START_MESSAGE, HELP_MESSAGE, OWNER_ID, SUPPORT_CHANNEL_USERNAME

# Get logger
logger = logging.getLogger(__name__)

# Start command images (URLs)
START_IMAGES = [
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

# Cache for bot info to avoid repeated API calls
_bot_info_cache = None

# Bot start time for uptime calculation
_bot_start_time = time.time()


def get_uptime():
    """Calculate bot uptime"""
    current_time = time.time()
    uptime_seconds = int(current_time - _bot_start_time)
    
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    if days > 0:
        return f"{days}ᴅᴀʏs, {hours}ʜ:{minutes}ᴍ:{seconds}s"
    elif hours > 0:
        return f"{hours}ʜ:{minutes}ᴍ:{seconds}s"
    elif minutes > 0:
        return f"{minutes}ᴍ:{seconds}s"
    else:
        return f"{seconds}s"


async def start_command(client: Client, message: Message):
    """Handle /start command - Separate messages for group and private"""
    try:
        # Send typing action immediately for better UX
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Save user to database for broadcast
        from database.mongodb import db_manager
        try:
            await db_manager.add_user(
                user_id=message.from_user.id,
                username=message.from_user.username or ""
            )
        except:
            pass  # Don't fail if DB save fails
        
        # Save chat to database for broadcast
        if message.chat.type in ['group', 'supergroup', 'channel']:
            try:
                await db_manager.save_chat_settings(
                    chat_id=message.chat.id,
                    settings={"chat_title": message.chat.title or "", "chat_type": message.chat.type}
                )
            except:
                pass  # Don't fail if DB save fails
        
        # Get bot info from cache or fetch it
        global _bot_info_cache
        if _bot_info_cache is None:
            _bot_info_cache = await client.get_me()
        
        bot_info = _bot_info_cache
        bot_username = bot_info.username
        bot_name = bot_info.first_name
        bot_mention = f"<a href='https://t.me/{bot_username}'>{bot_name}</a>"
        
        # Randomly select a start image
        selected_image = random.choice(START_IMAGES)
        
        # Check if in group, supergroup or channel
        if message.chat.type in ['group', 'supergroup', 'channel']:
            # GROUP START MESSAGE - When bot is added to group
            from utils.group_start import (
                format_group_start_message,
                get_group_start_keyboard,
                get_random_group_start_image
            )
            
            user_mention = message.from_user.mention
            chat_name = message.chat.title
            
            # Format group start message
            group_start_text = format_group_start_message(
                user_mention=user_mention,
                bot_mention=bot_mention,
                chat_name=chat_name
            )
            
            # Create inline keyboard with support and add to group buttons
            keyboard = get_group_start_keyboard(bot_username)
            
            # Get random start image
            selected_image = get_random_group_start_image()
            
            # Send photo with caption and buttons
            await message.reply_photo(
                photo=selected_image,
                caption=group_start_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        else:
            # PRIVATE CHAT START MESSAGE - Full welcome
            user_mention = message.from_user.mention
            bot_mention = f"<a href='https://t.me/{bot_username}'>{bot_name}</a>"
            
            private_start_text = f"""✦ ʜєʟʟᴏ {user_mention} 🥀 
 
 ⊚ ᴛʜɪꜱ ɪꜱ {bot_mention} 
 
 ➻ ᴧ ᴘʀєᴍɪᴜᴍ ᴅєꜱɪɢηєᴅ ϻᴜꜱɪᴄ ᴘʟᴧʏєʀ ʙσᴛ ꜰσʀ ᴛєʟєɢʀᴧϻ ɢʀσᴜᴘ & ᴄʜᴧηηєʟ. 
 
 » ɪғ ᴧηʏ ʜєʟᴘ ᴛᴧᴘ ᴛᴏ ʜєʟᴘ ʙᴜᴛᴛση. 
 
 •── ⋅ ⋅  ────── ⋅᯽⋅ ────── ⋅ ⋅ ⋅──•"""
            
            # Create inline keyboard for private chat
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✦ ᴧᴅᴅ ϻє ✦",
                        url=f"https://t.me/{bot_username}?startgroup=true"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "❖ ʜєʟᴘ ᴧηᴅ ᴄσϻϻᴧηᴅ ❖",
                        callback_data="help_commands"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⊜ ꜱᴜᴘᴘσʀᴛ ⊜",
                        url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}"
                    )
                ]
            ])
            
            # Use the specific train landscape image for start
            selected_image = "https://i.ibb.co/wFwqqbjk/anime-landscape-person-traveling.jpg"
            
            # Send photo with caption and buttons
            await message.reply_photo(
                photo=selected_image,
                caption=private_start_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Start command error: {e}", exc_info=True)
        
        # Try to send a simple text message as fallback
        try:
            # Get bot info for fallback
            bot_info = await client.get_me()
            bot_username = bot_info.username
            bot_mention = f"<a href='https://t.me/{bot_username}'>{bot_info.first_name}</a>"
            
            if message.chat.type in ['group', 'supergroup', 'channel']:
                # Simple group fallback
                await message.reply_text(
                    f"<b>{bot_mention} 𝖨𝗌 𝖠𝗅𝗂𝖛𝖊 .</b>\n\n"
                    f"Use /help to see all commands.",
                    disable_web_page_preview=True
                )
            else:
                # Simple private fallback
                await message.reply_text(
                    f"🎵 **Welcome to Music Bot!**\n\n"
                    f"Hey {message.from_user.mention}!\n"
                    f"I can play music in voice chats with amazing features.\n\n"
                    f"Use /help to see all commands.",
                    disable_web_page_preview=True
                )
        except Exception as fallback_error:
            # Ultimate fallback if even simple text fails
            logger.error(f"Fallback message also failed: {fallback_error}")
            await message.reply_text("🎵 Music Bot is ready! Use /help for commands.")


async def help_command(client: Client, message: Message):
    """Handle /help command"""
    try:
        # Send typing action
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Help message text
        help_text = """
╭───────────────────▣
│❍ **𝖢𝗁𝗈𝗌𝖾 𝖳𝗁𝖾 𝖢𝖺𝗍𝖾𝗀𝗈𝗋𝗒 𝖥𝗈𝗋 𝖶𝗁𝗂𝖼𝗁 𝖸𝗈𝗎 𝖶𝖺𝗇𝗇𝖺 𝖦𝖾𝗍 𝖧𝖾𝗅𝗉 .**
│❍ **𝖠𝗌𝗄 𝖸𝗈𝗎𝗋 𝖣𝗈𝗎𝖻𝗍𝗌 𝖠𝗍 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖢𝗁𝖺𝗍**
│❍ **𝖠𝗅𝗅 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖢𝖺𝗇 𝖡𝖾 𝖴𝗌𝖾𝖽 𝖶𝗂𝗍𝗁 : /**
├───────────────────▣
╰───────────────────▣
"""
        
        # Randomly select an image
        selected_image = random.choice(START_IMAGES)
        
        # Create 3x3 grid of command buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴧᴅϻɪη •", callback_data="cmd_admin"),
                InlineKeyboardButton("• ᴧᴜᴛʜ •", callback_data="cmd_auth"),
                InlineKeyboardButton("• ɢ-ᴄᴧꜱᴛ •", callback_data="cmd_gcast")
            ],
            [
                InlineKeyboardButton("• ʙʟ-ᴄʜᴧᴛ •", callback_data="cmd_blchat"),
                InlineKeyboardButton("• ʙʟ-ᴜꜱєʀꜱ •", callback_data="bl_user"),
                InlineKeyboardButton("• ᴄ-ᴘʟᴧʏ •", callback_data="cmd_cplay")
            ],
            [
                InlineKeyboardButton("• ɢ-ʙᴧη •", callback_data="cmd_gban"),
                InlineKeyboardButton("• ʟσσᴘ •", callback_data="cmd_loop"),
                InlineKeyboardButton("• ʟσɢ •", callback_data="cmd_log")
            ],
            [
                InlineKeyboardButton("• ᴘɪηɢ •", callback_data="cmd_ping"),
                InlineKeyboardButton("• ᴘʟᴧʏ •", callback_data="cmd_play"),
                InlineKeyboardButton("• ꜱʜᴜꜰꜰʟє •", callback_data="cmd_shuffle")
            ],
            [
                InlineKeyboardButton("• ꜱєєᴋ •", callback_data="cmd_seek"),
                InlineKeyboardButton("• ꜱσηɢ •", callback_data="cmd_song"),
                InlineKeyboardButton("• ꜱᴘєєᴅ •", callback_data="cmd_speed")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_start")
            ]
        ])
        
        # Send photo with caption and buttons
        await message.reply_photo(
            photo=selected_image,
            caption=help_text,
            reply_markup=keyboard
        )
        
    except Exception as e:
        # Fallback message
        await message.reply_text(HELP_MESSAGE)
