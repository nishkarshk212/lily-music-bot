"""
Settings Command Handler
Opens the settings panel
"""

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction
from utils.decorators import admin_check
import random
import logging

logger = logging.getLogger(__name__)

# Settings images
SETTINGS_IMAGES = [
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


@admin_check
async def settings_command(client: Client, message: Message):
    """Handle /settings command"""
    try:
        await message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
        
        # Settings message text
        settings_text = """
╭───────────────────▣
│❍ **ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ ᴘᴀɴᴇʟ :**
├───────────────────▣
│
│⚙️ ᴄᴏɴꜰɪɢᴜʀᴇ ʏᴏᴜʀ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ
│   ꜰʀᴏᴍ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ.
│
╰───────────────────▣
"""
        
        # Randomly select an image
        selected_image = random.choice(SETTINGS_IMAGES)
        
        # Create settings keyboard with proper symbols
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴘʟᴀʏ ϻσᴅє •", callback_data="set_playmode"),
                InlineKeyboardButton("• ꜱᴋɪᴘ ϻσᴅє •", callback_data="set_skipmode")
            ],
            [
                InlineKeyboardButton("• ǫᴜᴀʟɪᴛʏ •", callback_data="set_quality"),
                InlineKeyboardButton("• ʟᴀηɢᴜᴀɢє •", callback_data="set_language")
            ],
            [
                InlineKeyboardButton("• ᴠσʟᴜϻє •", callback_data="set_volume"),
                InlineKeyboardButton("• ᴠɪᴅєσ ϻσᴅє •", callback_data="set_videomode")
            ],
            [
                InlineKeyboardButton("• ᴄʟєᴀη ϻσᴅє •", callback_data="set_cleanmode"),
                InlineKeyboardButton("• ʟσɢɢɪηɢ •", callback_data="set_logging")
            ],
            [
                InlineKeyboardButton("⊶ ᴄʟσꜱє ⊶", callback_data="close_playing")
            ]
        ])
        
        # Send photo with caption and buttons
        await message.reply_photo(
            photo=selected_image,
            caption=settings_text,
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in settings_command: {e}")
        await message.reply_text("❌ An error occurred while opening settings.")
