"""
Settings Panel Handler
Manages bot settings and configuration with category sub-menus
Adapted from Annie Music style UI
"""

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, Message
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import MessageNotModified
from database.mongodb import db_manager
from config import OWNER_ID, SUDOERS

# Settings panel images
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

async def is_admin_check(callback_query: CallbackQuery):
    """Utility to check if user is admin or owner/sudoer"""
    user_id = callback_query.from_user.id
    if user_id in OWNER_ID or user_id in SUDOERS:
        return True
    if callback_query.message.chat.type == ChatType.PRIVATE:
        return user_id in OWNER_ID or user_id in SUDOERS
    try:
        member = await callback_query.message.chat.get_member(user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

async def get_settings_markup(chat_id: int):
    """Generate main settings markup with status indicators"""
    settings = await db_manager.get_chat_settings(chat_id)
    clean_mode = settings.get("clean_mode", "enable")
    logging = settings.get("logging", "enable")
    
    cm_icon = "✅" if clean_mode == "enable" else "❌"
    lg_icon = "✅" if logging == "enable" else "❌"

    keyboard = [
        [
            InlineKeyboardButton("ᴘʟᴧʏ ϻσᴅє", callback_data="set_pm"),
            InlineKeyboardButton("ꜱᴋɪᴘ ϻσᴅє", callback_data="set_sm")
        ],
        [
            InlineKeyboardButton("ꜱᴛσᴘ ϻσᴅє", callback_data="set_st"),
            InlineKeyboardButton("ǫᴜᴧʟɪᴛʏ", callback_data="set_quality")
        ],
        [
            InlineKeyboardButton("ᴠσʟᴜϻє", callback_data="set_volume"),
            InlineKeyboardButton("ᴠɪᴅєσ ϻσᴅє", callback_data="set_videomode")
        ],
        [
            InlineKeyboardButton(f"ᴄʟєᴧη ϻσᴅє {cm_icon}", callback_data="toggle_cleanmode"),
            InlineKeyboardButton(f"ʟσɢɢɪηɢ {lg_icon}", callback_data="toggle_logging")
        ],
        [
            InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_start"),
            InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def settings_callback(client: Client, callback_query: CallbackQuery):
    """Handle settings main panel"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ɢʀσᴜᴩ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        markup = await get_settings_markup(chat_id)
        
        settings_text = f"""
╭───────────────────▣
│❍ **ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ ᴘᴀɴᴇʟ :**
├───────────────────▣
│
│⚙️ **ᴄᴏɴꜰɪɢᴜʀᴇ ʏᴏᴜʀ ʙᴏᴛ ʜᴇʀᴇ.**
│   **ᴄʟɪᴄᴋ ᴏɴ ʙᴜᴛᴛᴏɴꜱ ᴛᴏ ᴛᴏɢɢʟᴇ.**
│
╰───────────────────▣
"""
        selected_image = random.choice(SETTINGS_IMAGES)
        
        try:
            await callback_query.message.edit_media(
                media=InputMediaPhoto(media=selected_image, caption=settings_text),
                reply_markup=markup
            )
        except MessageNotModified:
            pass
        await callback_query.answer("Settings Menu")
        
    except Exception as e:
        await callback_query.answer(f"Error: {e}", show_alert=True)

# --- Category Sub-Panels ---

async def playmode_panel(client: Client, callback_query: CallbackQuery):
    """Sub-menu for Play Mode"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    
    current_type = settings.get("play_mode", "everyone")
    current_status = settings.get("play_status", "enable")
    
    keyboard = [
        [InlineKeyboardButton("🔍 **ᴡʜᴏ ᴄᴀɴ ᴘʟᴀʏ:**", callback_data="none")],
        [
            InlineKeyboardButton(f"{'✅ ' if current_type == 'admins' else ''}ᴧᴅϻɪηꜱ", callback_data="update_pm_admins"),
            InlineKeyboardButton(f"{'✅ ' if current_type == 'everyone' else ''}єᴠєʀʏσηє", callback_data="update_pm_everyone")
        ],
        [InlineKeyboardButton("⚙️ **ꜱᴛᴀᴛᴜꜱ:**", callback_data="none")],
        [
            InlineKeyboardButton(f"{'✅ ' if current_status == 'enable' else ''}єηᴧʙʟє", callback_data="update_ps_enable"),
            InlineKeyboardButton(f"{'✅ ' if current_status == 'disable' else ''}ᴅɪꜱᴧʙʟє", callback_data="update_ps_disable")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="🎵 **ᴘʟᴀʏ ᴍᴏᴅᴇ sᴇᴛᴛɪɴɢs**\n\nConfigure who can play music and toggle feature status.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    await callback_query.answer("Play Mode Settings")

async def skipmode_panel(client: Client, callback_query: CallbackQuery):
    """Sub-menu for Skip Mode"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    
    current_type = settings.get("skip_mode", "admins")
    current_status = settings.get("skip_status", "enable")
    
    keyboard = [
        [InlineKeyboardButton("🔍 **ᴡʜᴏ ᴄᴀɴ sᴋɪᴘ:**", callback_data="none")],
        [
            InlineKeyboardButton(f"{'✅ ' if current_type == 'admins' else ''}ᴧᴅϻɪηꜱ", callback_data="update_sm_admins"),
            InlineKeyboardButton(f"{'✅ ' if current_type == 'everyone' else ''}єᴠєʀʏσηє", callback_data="update_sm_everyone")
        ],
        [InlineKeyboardButton("⚙️ **ꜱᴛᴀᴛᴜꜱ:**", callback_data="none")],
        [
            InlineKeyboardButton(f"{'✅ ' if current_status == 'enable' else ''}єηᴧʙʟє", callback_data="update_ss_enable"),
            InlineKeyboardButton(f"{'✅ ' if current_status == 'disable' else ''}ᴅɪꜱᴧʙʟє", callback_data="update_ss_disable")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="⏭️ **sᴋɪᴘ ᴍᴏᴅᴇ sᴇᴛᴛɪɴɢs**\n\nConfigure who can skip music and toggle feature status.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    await callback_query.answer("Skip Mode Settings")

async def stopmode_panel(client: Client, callback_query: CallbackQuery):
    """Sub-menu for Stop Mode"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    
    current_type = settings.get("stop_mode", "admins")
    current_status = settings.get("stop_status", "enable")
    
    keyboard = [
        [InlineKeyboardButton("🔍 **ᴡʜᴏ ᴄᴀɴ sᴛᴏᴘ:**", callback_data="none")],
        [
            InlineKeyboardButton(f"{'✅ ' if current_type == 'admins' else ''}ᴧᴅϻɪηꜱ", callback_data="update_st_admins"),
            InlineKeyboardButton(f"{'✅ ' if current_type == 'everyone' else ''}єᴠєʀʏσηє", callback_data="update_st_everyone")
        ],
        [InlineKeyboardButton("⚙️ **ꜱᴛᴀᴛᴜꜱ:**", callback_data="none")],
        [
            InlineKeyboardButton(f"{'✅ ' if current_status == 'enable' else ''}єηᴧʙʟє", callback_data="update_st_status_enable"),
            InlineKeyboardButton(f"{'✅ ' if current_status == 'disable' else ''}ᴅɪꜱᴧʙʟє", callback_data="update_st_status_disable")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="⏹️ **sᴛᴏᴘ ᴍᴏᴅᴇ sᴇᴛᴛɪɴɢs**\n\nConfigure who can stop the stream and toggle feature status.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    await callback_query.answer("Stop Mode Settings")

# --- Update Handlers ---

async def set_mode_callback(client: Client, callback_query: CallbackQuery):
    """Handle all toggle and setting updates"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ Admin Only!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        data = callback_query.data
        settings = await db_manager.get_chat_settings(chat_id)
        
        # 1. Main Panel Toggles
        if data == "toggle_cleanmode":
            new_mode = "disable" if settings.get("clean_mode", "enable") == "enable" else "enable"
            await db_manager.save_chat_settings(chat_id, {"clean_mode": new_mode})
            markup = await get_settings_markup(chat_id)
            try:
                await callback_query.message.edit_reply_markup(reply_markup=markup)
            except MessageNotModified:
                pass
            await callback_query.answer(f"✅ Clean mode: {new_mode}d")
            
        elif data == "toggle_logging":
            new_mode = "disable" if settings.get("logging", "enable") == "enable" else "enable"
            await db_manager.save_chat_settings(chat_id, {"logging": new_mode})
            markup = await get_settings_markup(chat_id)
            try:
                await callback_query.message.edit_reply_markup(reply_markup=markup)
            except MessageNotModified:
                pass
            await callback_query.answer(f"✅ Logging: {new_mode}d")
            
        # 2. Play Mode Updates
        elif data.startswith("update_pm_"):
            mode = data.replace("update_pm_", "")
            await db_manager.save_chat_settings(chat_id, {"play_mode": mode})
            await playmode_panel(client, callback_query)
        elif data.startswith("update_ps_"):
            status = data.replace("update_ps_", "")
            await db_manager.save_chat_settings(chat_id, {"play_status": status})
            await playmode_panel(client, callback_query)
            
        # 3. Skip Mode Updates
        elif data.startswith("update_sm_"):
            mode = data.replace("update_sm_", "")
            await db_manager.save_chat_settings(chat_id, {"skip_mode": mode})
            await skipmode_panel(client, callback_query)
        elif data.startswith("update_ss_"):
            status = data.replace("update_ss_", "")
            await db_manager.save_chat_settings(chat_id, {"skip_status": status})
            await skipmode_panel(client, callback_query)
            
        # 4. Stop Mode Updates
        elif data.startswith("update_st_admins") or data.startswith("update_st_everyone"):
            mode = data.replace("update_st_", "")
            await db_manager.save_chat_settings(chat_id, {"stop_mode": mode})
            await stopmode_panel(client, callback_query)
        elif data.startswith("update_st_status_"):
            status = data.replace("update_st_status_", "")
            await db_manager.save_chat_settings(chat_id, {"stop_status": status})
            await stopmode_panel(client, callback_query)
        
    except Exception as e:
        await callback_query.answer(f"Update failed: {e}", show_alert=True)

# --- Other Sub-menus ---

async def quality_callback(client: Client, callback_query: CallbackQuery):
    """Handle quality settings sub-menu"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    current = settings.get("quality", "high")
    
    keyboard = [
        [
            InlineKeyboardButton(f"{'✅ ' if current == 'low' else ''}Low", callback_data="set_q_low"),
            InlineKeyboardButton(f"{'✅ ' if current == 'medium' else ''}Medium", callback_data="set_q_medium")
        ],
        [
            InlineKeyboardButton(f"{'✅ ' if current == 'high' else ''}High", callback_data="set_q_high"),
            InlineKeyboardButton(f"{'✅ ' if current == 'studio' else ''}Studio", callback_data="set_q_studio")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="📡 **ꜱєʟєᴄᴛ ᴧᴜᴅɪσ ǫᴜᴧʟɪᴛʏ:**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    await callback_query.answer("Quality Settings")

async def volume_callback(client: Client, callback_query: CallbackQuery):
    """Handle volume settings sub-menu"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    current = settings.get("volume", 100)
    
    keyboard = [
        [
            InlineKeyboardButton(f"{'✅ ' if current == 50 else ''}50%", callback_data="set_v_50"),
            InlineKeyboardButton(f"{'✅ ' if current == 100 else ''}100%", callback_data="set_v_100")
        ],
        [
            InlineKeyboardButton(f"{'✅ ' if current == 150 else ''}150%", callback_data="set_v_150"),
            InlineKeyboardButton(f"{'✅ ' if current == 200 else ''}200%", callback_data="set_v_200")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="🔊 **ꜱєʟєᴄᴛ ᴅєꜰᴧᴜʟᴛ ᴠσʟᴜϻє:**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    await callback_query.answer("Volume Settings")

async def videomode_callback(client: Client, callback_query: CallbackQuery):
    """Handle video mode settings sub-menu"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    current = settings.get("video_mode", "720p")
    
    keyboard = [
        [
            InlineKeyboardButton(f"{'✅ ' if current == '480p' else ''}480p", callback_data="set_vid_480p"),
            InlineKeyboardButton(f"{'✅ ' if current == '720p' else ''}720p", callback_data="set_vid_720p")
        ],
        [
            InlineKeyboardButton(f"{'✅ ' if current == '1080p' else ''}1080p", callback_data="set_vid_1080p"),
            InlineKeyboardButton(f"{'✅ ' if current == 'hd' else ''}HD", callback_data="set_vid_hd")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="📹 **ꜱєʟєᴄᴛ ᴠɪᴅєσ ǫᴜᴧʟɪᴛʏ:**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    await callback_query.answer("Video Mode Settings")

async def update_sub_setting(client: Client, callback_query: CallbackQuery):
    """Update settings from sub-menus (Quality, Volume, Video)"""
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    
    if data.startswith("set_q_"):
        val = data.replace("set_q_", "")
        await db_manager.save_chat_settings(chat_id, {"quality": val})
        await quality_callback(client, callback_query)
    elif data.startswith("set_v_"):
        val = int(data.replace("set_v_", ""))
        await db_manager.save_chat_settings(chat_id, {"volume": val})
        await volume_callback(client, callback_query)
    elif data.startswith("set_vid_"):
        val = data.replace("set_vid_", "")
        await db_manager.save_chat_settings(chat_id, {"video_mode": val})
        await videomode_callback(client, callback_query)
