"""
Callback Query Handlers - Inline button callbacks
"""

import asyncio
import random
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InputMediaPhoto
from pyrogram.enums import ParseMode
from utils.strings import HELP_MESSAGE

# Help panel images (same as start images)
HELP_IMAGES = [
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


async def help_callback(client: Client, callback_query: CallbackQuery):
    """Handle help button callback from start message"""
    try:
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
        selected_image = random.choice(HELP_IMAGES)
        
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
                InlineKeyboardButton("• ꜱєᴛᴛɪηɢꜱ •", callback_data="settings_main"),
                InlineKeyboardButton("• ꜱᴛᴀᴛꜱ •", callback_data="overall_stats")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_start")
            ]
        ])
        
        # Edit the same message instead of sending new one
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=help_text,
            reply_markup=keyboard
        )
        
        # Answer the callback query to remove the loading state
        await callback_query.answer("📚 Help & Commands", show_alert=False)
        
    except Exception as e:
        # Fallback if something goes wrong
        await callback_query.answer("Error loading help", show_alert=True)


async def back_to_start_callback(client: Client, callback_query: CallbackQuery):
    """Handle back button from help panel"""
    try:
        # Get user mention - use the one who clicked the button
        user_mention = callback_query.from_user.mention
        
        # Get bot info
        bot_info = await client.get_me()
        bot_username = bot_info.username
        bot_name = bot_info.first_name
        bot_mention = f"<a href='https://t.me/{bot_username}'>{bot_name}</a>"
        
        # Get support channel mention
        from utils.strings import SUPPORT_CHANNEL_USERNAME
        support_mention = f"<a href='https://t.me/{SUPPORT_CHANNEL_USERNAME}'>Support Channel</a>"
        
        # Format the start message
        from utils.strings import START_MESSAGE
        start_text = START_MESSAGE.format(
            user_mention=user_mention,
            bot_mention=bot_mention,
            support_mention=support_mention
        )
        
        # Randomly select a start image
        selected_image = random.choice(HELP_IMAGES)
        
        # Create inline keyboard with buttons - VERTICAL for mobile
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
        
        # Edit the same message in one call with correct parse mode
        await callback_query.message.edit_media(
            media=InputMediaPhoto(
                media=selected_image,
                caption=start_text,
                parse_mode=ParseMode.HTML
            ),
            reply_markup=keyboard
        )
        
        await callback_query.answer("Back to Home Panel", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error returning to start", show_alert=True)


async def admin_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin button callback"""
    try:
        # Admin commands message
        admin_text = """
╭───────────────────▣
│❍ **ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs :**
├───────────────────▣
│
│ᴊᴜsᴛ ᴀᴅᴅ ᴄ ɪɴ ᴛʜᴇ sᴛᴀʀᴛɪɴɢ ᴏғ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs
│ᴛᴏ ᴜsᴇ ᴛʜᴇᴍ ғᴏʀ ᴄʜᴀɴɴᴇʟ.
│
│❍ /pause : ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ.
│❍ /resume : ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ.
│❍ /skip : sᴋɪᴩ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ
│   sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ.
│❍ /end ᴏʀ /stop : ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ
│   ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ.
│❍ /player : ɢᴇᴛ ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴩʟᴀʏᴇʀ ᴩᴀɴᴇʟ.
│❍ /queue : sʜᴏᴡs ᴛʜᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs ʟɪsᴛ.
│
╰───────────────────▣
"""
        
        # Randomly select an image
        selected_image = random.choice(HELP_IMAGES)
        
        # Create back button
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        # Edit the same message
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=admin_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Admin Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading admin commands", show_alert=True)


async def back_to_help_callback(client: Client, callback_query: CallbackQuery):
    """Handle back button from admin/other panels to help"""
    try:
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
        selected_image = random.choice(HELP_IMAGES)
        
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
        
        # Edit the same message
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=help_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Back to Help", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error", show_alert=True)


# Additional callback handlers for each category
async def auth_callback(client: Client, callback_query: CallbackQuery):
    """Handle auth button callback"""
    try:
        auth_text = """
╭───────────────────▣
│❍ **ᴀᴜᴛʜ ᴜsᴇʀs :**
├───────────────────▣
│
│ᴀᴜᴛʜ ᴜsᴇʀs ᴄᴀɴ ᴜsᴇ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ɪɴ ᴛʜᴇ ʙᴏᴛ
│ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ.
│
│❍ /auth [ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ_ɪᴅ] : ᴀᴅᴅ ᴀ ᴜsᴇʀ ᴛᴏ
│   ᴀᴜᴛʜ ʟɪsᴛ ᴏғ ᴛʜᴇ ʙᴏᴛ.
│❍ /unauth [ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ_ɪᴅ] : ʀᴇᴍᴏᴠᴇ ᴀ ᴀᴜᴛʜ
│   ᴜsᴇʀs ғʀᴏᴍ ᴛʜᴇ ᴀᴜᴛʜ ᴜsᴇʀs ʟɪsᴛ.
│❍ /authusers : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ᴀᴜᴛʜ ᴜsᴇʀs
│   ᴏғ ᴛʜᴇ ɢʀᴏᴜᴩ.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=auth_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Auth Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading auth commands", show_alert=True)


async def gcast_callback(client: Client, callback_query: CallbackQuery):
    """Handle broadcast button callback"""
    try:
        gcast_text = """
╭───────────────────▣
│❍ **ʙʀᴏᴀᴅᴄᴀsᴛ ғᴇᴀᴛᴜʀᴇ [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :**
├───────────────────▣
│
│❍ /broadcast [ᴍᴇssᴀɢᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ]
│   : ʙʀᴏᴀᴅᴄᴀsᴛ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴏғ
│   ᴛʜᴇ ʙᴏᴛ.
│
│**ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴍᴏᴅᴇs :**
│❍ -pin : ᴩɪɴs ʏᴏᴜʀ ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇs ɪɴ
│   sᴇʀᴠᴇᴅ ᴄʜᴀᴛs.
│❍ -pinloud : ᴩɪɴs ʏᴏᴜʀ ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ
│   ɪɴ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴀɴᴅ sᴇɴᴅ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ.
│❍ -user : ʙʀᴏᴀᴅᴄᴀsᴛs ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴛʜᴇ
│   ᴜsᴇʀs ᴡʜᴏ ʜᴀᴠᴇ sᴛᴀʀᴛᴇᴅ ʏᴏᴜʀ ʙᴏᴛ.
│❍ -assistant : ʙʀᴏᴀᴅᴄᴀsᴛ ғʀᴏᴍ ᴛʜᴇ ᴀssɪᴛᴀɴᴛ
│   ᴀᴄᴄᴏᴜɴᴛ ᴏғ ᴛʜᴇ ʙᴏᴛ.
│❍ -nobot : ғᴏʀᴄᴇs ᴛʜᴇ ʙᴏᴛ ᴛᴏ ɴᴏᴛ ʙʀᴏᴀᴅᴄᴀsᴛ.
│
│**ᴇxᴀᴍᴩʟᴇ:** /broadcast -user -assistant -pin
│ᴛᴇsᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=gcast_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Broadcast Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading broadcast commands", show_alert=True)


async def blchat_callback(client: Client, callback_query: CallbackQuery):
    """Handle blacklist chat button callback"""
    try:
        blchat_text = """
╭───────────────────▣
│❍ **ᴄʜᴀᴛ ʙʟᴀᴄᴋʟɪsᴛ ғᴇᴀᴛᴜʀᴇ : [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs]**
├───────────────────▣
│
│ʀᴇsᴛʀɪᴄᴛ sʜɪᴛ ᴄʜᴀᴛs ᴛᴏ ᴜsᴇ ᴏᴜʀ ᴘʀᴇᴄɪᴏᴜs ʙᴏᴛ.
│
│❍ /blacklistchat [ᴄʜᴀᴛ ɪᴅ] : ʙʟᴀᴄᴋʟɪsᴛ ᴀ ᴄʜᴀᴛ
│   ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.
│❍ /whitelistchat [ᴄʜᴀᴛ ɪᴅ] : ᴡʜɪᴛᴇʟɪsᴛ ᴛʜᴇ
│   ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴄʜᴀᴛ.
│❍ /blacklistedchat : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ
│   ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴄʜᴀᴛs.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=blchat_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Blacklist Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading blacklist commands", show_alert=True)


async def cplay_callback(client: Client, callback_query: CallbackQuery):
    """Handle channel play button callback"""
    try:
        cplay_text = """
╭───────────────────▣
│❍ **ᴄʜᴀɴɴᴇʟ ᴩʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs:**
├───────────────────▣
│
│ʏᴏᴜ ᴄᴀɴ sᴛʀᴇᴀᴍ ᴀᴜᴅɪᴏ/ᴠɪᴅᴇᴏ ɪɴ ᴄʜᴀɴɴᴇʟ.
│
│❍ /cplay : sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ
│   ᴀᴜᴅɪᴏ ᴛʀᴀᴄᴋ ᴏɴ ᴄʜᴀɴɴᴇʟ's ᴠɪᴅᴇᴏᴄʜᴀᴛ.
│❍ /cvplay : sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ
│   ᴠɪᴅᴇᴏ ᴛʀᴀᴄᴋ ᴏɴ ᴄʜᴀɴɴᴇʟ's ᴠɪᴅᴇᴏᴄʜᴀᴛ.
│❍ /cplayforce or /cvplayforce : sᴛᴏᴩs ᴛʜᴇ
│   ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ.
│❍ /channelplay [ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ] ᴏʀ
│   [ᴅɪsᴀʙʟᴇ] : ᴄᴏɴɴᴇᴄᴛ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀ ɢʀᴏᴜᴩ.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=cplay_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Channel Play Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading channel play commands", show_alert=True)


async def gban_callback(client: Client, callback_query: CallbackQuery):
    """Handle gban button callback"""
    try:
        gban_text = """
╭───────────────────▣
│❍ **ɢʟᴏʙᴀʟ ʙᴀɴ ғᴇᴀᴛᴜʀᴇ [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :**
├───────────────────▣
│
│❍ /gban [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ] :
│   ɢʟᴏʙᴀʟʟʏ ʙᴀɴs ᴛʜᴇ ᴜsᴇʀ ғʀᴏᴍ ᴀʟʟ ᴛʜᴇ
│   sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴀɴᴅ ʙʟᴀᴄᴋʟɪsᴛ ʜɪᴍ.
│❍ /ungban [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ] :
│   ɢʟᴏʙᴀʟʟʏ ᴜɴʙᴀɴs ᴛʜᴇ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ ᴜsᴇʀ.
│❍ /gbannedusers : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ɢʟᴏʙᴀʟʟʏ
│   ʙᴀɴɴᴇᴅ ᴜsᴇʀs.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=gban_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("GBAN Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading gban commands", show_alert=True)


async def loop_callback(client: Client, callback_query: CallbackQuery):
    """Handle loop button callback"""
    try:
        loop_text = """
╭───────────────────▣
│❍ **ʟᴏᴏᴘ sᴛʀᴇᴀᴍ :**
├───────────────────▣
│
│sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ ɪɴ ʟᴏᴏᴘ
│
│❍ /loop [enable/disable] : ᴇɴᴀʙʟᴇs/ᴅɪsᴀʙʟᴇs
│   ʟᴏᴏᴘ ғᴏʀ ᴛʜᴇ ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ
│❍ /loop [1, 2, 3, ...] : ᴇɴᴀʙʟᴇs ᴛʜᴇ ʟᴏᴏᴘ
│   ғᴏʀ ᴛʜᴇ ɢɪᴠᴇɴ ᴠᴀʟᴜᴇ.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=loop_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Loop Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading loop commands", show_alert=True)


async def log_callback(client: Client, callback_query: CallbackQuery):
    """Handle log button callback"""
    try:
        log_text = """
╭───────────────────▣
│❍ **ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :**
├───────────────────▣
│
│❍ /logs : ɢᴇᴛ ʟᴏɢs ᴏғ ᴛʜᴇ ʙᴏᴛ.
│❍ /logger [ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ] : ʙᴏᴛ ᴡɪʟʟ sᴛᴀʀᴛ
│   ʟᴏɢɢɪɴɢ ᴛʜᴇ ᴀᴄᴛɪᴠɪᴛɪᴇs ʜᴀᴩᴩᴇɴ ᴏɴ ʙᴏᴛ.
│❍ /maintenance [ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ] : ᴇɴᴀʙʟᴇ ᴏʀ
│   ᴅɪsᴀʙʟᴇ ᴛʜᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=log_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Log Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading log commands", show_alert=True)


async def ping_callback(client: Client, callback_query: CallbackQuery):
    """Handle ping button callback"""
    try:
        ping_text = """
╭───────────────────▣
│❍ **ᴘɪɴɢ & sᴛᴀᴛs :**
├───────────────────▣
│
│❍ /start : sᴛᴀʀᴛs ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ.
│❍ /help : ɢᴇᴛ ʜᴇʟᴩ ᴍᴇɴᴜ ᴡɪᴛʜ ᴇxᴩʟᴀɴᴀᴛɪᴏɴ.
│❍ /ping : sʜᴏᴡs ᴛʜᴇ ᴩɪɴɢ ᴀɴᴅ sʏsᴛᴇᴍ sᴛᴀᴛs.
│❍ /stats : sʜᴏᴡs ᴛʜᴇ ᴏᴠᴇʀᴀʟʟ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=ping_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Ping Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading ping commands", show_alert=True)


async def play_callback(client: Client, callback_query: CallbackQuery):
    """Handle play button callback"""
    try:
        play_text = """
╭───────────────────▣
│❍ **ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs :**
├───────────────────▣
│
│v : sᴛᴀɴᴅs ғᴏʀ ᴠɪᴅᴇᴏ ᴩʟᴀʏ.
│force : sᴛᴀɴᴅs ғᴏʀ ғᴏʀᴄᴇ ᴩʟᴀʏ.
│fplay : sᴛᴀɴᴅs ғᴏʀ ғɪʟᴇ ᴩʟᴀʏ.
│
│❍ /play ᴏʀ /vplay : sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ
│   ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.
│❍ /playforce ᴏʀ /vplayforce : sᴛᴏᴩs ᴛʜᴇ
│   ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ.
│❍ /fplay : ᴘʟᴀʏs ʟᴏᴄᴀʟ ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇs
│   (ʀᴇᴘʟʏ ᴛᴏ ᴀᴜᴅɪᴏ/ᴠɪᴅᴇᴏ ғɪʟᴇ)
│
│**sᴜᴘᴘᴏʀᴛᴇᴅ ғᴏʀᴍᴀᴛs:**
│ ᴀᴜᴅɪᴏ: ᴍᴘ3, ᴍ4ᴀ, ᴡᴀᴠ, ᴏɢɢ, ғʟᴀᴄ,
│        ᴡᴍᴀ, ᴀᴀᴄ, ᴏᴘᴜs, ᴀᴍʀ
│ ᴠɪᴅᴇᴏ: ᴍᴘ4, ᴍᴋᴠ, ᴀᴠɪ, ᴍᴏᴠ, ᴡᴇʙᴍ, 3ɢᴘ
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=play_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Play Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading play commands", show_alert=True)


async def shuffle_callback(client: Client, callback_query: CallbackQuery):
    """Handle shuffle button callback"""
    try:
        shuffle_text = """
╭───────────────────▣
│❍ **sʜᴜғғʟᴇ ᴏ̨ᴜᴇᴜᴇ :**
├───────────────────▣
│
│❍ /shuffle : sʜᴜғғʟᴇ's ᴛʜᴇ ᴏ̨ᴜᴇᴜᴇ.
│❍ /queue : sʜᴏᴡs ᴛʜᴇ sʜᴜғғʟᴇᴅ ᴏ̨ᴜᴇᴜᴇ.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=shuffle_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Shuffle Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading shuffle commands", show_alert=True)


async def seek_callback(client: Client, callback_query: CallbackQuery):
    """Handle seek button callback"""
    try:
        seek_text = """
╭───────────────────▣
│❍ **sᴇᴇᴋ sᴛʀᴇᴀᴍ :**
├───────────────────▣
│
│❍ /seek [ᴅᴜʀᴀᴛɪᴏɴ ɪɴ sᴇᴄᴏɴᴅs] : sᴇᴇᴋ ᴛʜᴇ
│   sᴛʀᴇᴀᴍ ᴛᴏ ᴛʜᴇ ɢɪᴠᴇɴ ᴅᴜʀᴀᴛɪᴏɴ.
│❍ /seekback [ᴅᴜʀᴀᴛɪᴏɴ ɪɴ sᴇᴄᴏɴᴅs] : ʙᴀᴄᴋᴡᴀʀᴅ
│   sᴇᴇᴋ ᴛʜᴇ sᴛʀᴇᴀᴍ ᴛᴏ ᴛʜᴇ ɢɪᴠᴇɴ ᴅᴜʀᴀᴛɪᴏɴ.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=seek_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Seek Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading seek commands", show_alert=True)


async def song_callback(client: Client, callback_query: CallbackQuery):
    """Handle song button callback"""
    try:
        song_text = """
╭───────────────────▣
│❍ **sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ**
├───────────────────▣
│
│❍ /song [sᴏɴɢ ɴᴀᴍᴇ/ʏᴛ ᴜʀʟ] : ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴʏ
│   ᴛʀᴀᴄᴋ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ɪɴ ᴍᴘ3 ᴏʀ ᴍᴘ4 ғᴏʀᴍᴀᴛs.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=song_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Song Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading song commands", show_alert=True)


async def speed_callback(client: Client, callback_query: CallbackQuery):
    """Handle speed button callback"""
    try:
        speed_text = """
╭───────────────────▣
│❍ **sᴘᴇᴇᴅ ᴄᴏᴍᴍᴀɴᴅs :**
├───────────────────▣
│
│ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛʀᴏʟ ᴛʜᴇ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ ᴏғ ᴛʜᴇ
│ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ. [ᴀᴅᴍɪɴs ᴏɴʟʏ]
│
│❍ /speed or /playback : ғᴏʀ ᴀᴅᴊᴜsᴛɪɴɢ ᴛʜᴇ
│   ᴀᴜᴅɪᴏ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ ɪɴ ɢʀᴏᴜᴘ.
│❍ /cspeed or /cplayback : ғᴏʀ ᴀᴅᴊᴜsᴛɪɴɢ ᴛʜᴇ
│   ᴀᴜᴅɪᴏ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ ɪɴ ᴄʜᴀɴɴᴇʟ.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=speed_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Speed Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading speed commands", show_alert=True)


async def bl_users_callback(client: Client, callback_query: CallbackQuery):
    """Handle BL users button callback"""
    try:
        bl_users_text = """
╭───────────────────▣
│❍ **ʙʟ-ᴜsᴇʀs ғᴇᴀᴛᴜʀᴇ :**
├───────────────────▣
│
│ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs ʟɪsᴛ - ᴍᴀɴᴀɢᴇ ᴜsᴇʀs
│ᴡʜᴏ ᴀʀᴇ ʙʟᴏᴄᴋᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.
│
│❍ /block [ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ_ɪᴅ] : ʙʟᴏᴄᴋ ᴀ ᴜsᴇʀ
│   ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.
│❍ /unblock [ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ_ɪᴅ] : ᴜɴʙʟᴏᴄᴋ ᴀ
│   ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ ʙʟᴏᴄᴋ ʟɪsᴛ.
│❍ /blockedusers : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ
│   ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs.
│
╰───────────────────▣
"""
        
        selected_image = random.choice(HELP_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_help")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=bl_users_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("BL Users Commands", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading BL users commands", show_alert=True)


async def close_playing_callback(client: Client, callback_query: CallbackQuery):
    """Handle close button callback from playing message"""
    try:
        # Get user mention
        user_mention = callback_query.from_user.mention
        
        # Edit the message to show who closed it
        await callback_query.message.edit_caption(
            caption=f"<b>Cʟᴏsᴇᴅ ʙʏ :</b> {user_mention}",
            reply_markup=None,
            parse_mode=ParseMode.HTML
        )
        
        # Delete after 3 seconds
        await asyncio.sleep(3)
        await callback_query.message.delete()
        
        await callback_query.answer("Message closed", show_alert=False)
    except Exception as e:
        # If edit fails, try to delete directly
        try:
            await callback_query.message.delete()
            await callback_query.answer("Message closed", show_alert=False)
        except:
            await callback_query.answer("Cannot close this message", show_alert=True)


async def queue_list_callback(client: Client, callback_query: CallbackQuery):
    """Handle queue list button callback"""
    try:
        from core.queue import queue_manager
        from utils.formatter import format_time, truncate_text
        
        chat_id = callback_query.message.chat.id
        queue = queue_manager.get_queue(chat_id)
        queue_list = queue.get_queue()
        
        if not queue_list:
            await callback_query.answer("Queue is empty!", show_alert=True)
            return
        
        # Build queue list message
        queue_text = "<b>𝖰𝗎𝖾𝗎𝖾 𝖫𝗂𝗌𝗍:</b>\n\n"
        for i, song in enumerate(queue_list[:20], 1):
            queue_text += f"{i}. {truncate_text(song.title, 50)}\n"
            queue_text += f"   ⏱ {format_time(song.duration)} | 👤 {song.requester}\n\n"
        
        if len(queue_list) > 20:
            queue_text += f"... ᴀɴᴅ {len(queue_list) - 20} ᴍᴏʀᴇ sᴏɴɢs"
        
        await callback_query.answer("Showing queue list", show_alert=False)
        await callback_query.message.edit_caption(
            caption=queue_text,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await callback_query.answer("Error loading queue", show_alert=True)
