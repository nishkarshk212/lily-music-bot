"""
Custom Decorators for Bot Handlers
"""

from functools import wraps
from pyrogram.types import Message
from config import OWNER_ID, SUDOERS
from database.mongodb import db_manager
import logging
import time

logger = logging.getLogger(__name__)

# Cache for admin checks and settings to reduce API/DB calls
_admin_cache = {}
_settings_cache = {}
CACHE_TTL = 300  # 5 minutes cache


def admin_check(func):
    """Decorator to check if user is admin in the chat, with settings override"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            # Check if it's a private message
            if message.chat.type == "private":
                return await func(client, message, *args, **kwargs)
            
            # Get user ID and chat ID
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            # Check if user is owner or sudoer - they bypass everything
            if user_id in OWNER_ID or user_id in SUDOERS:
                return await func(client, message, *args, **kwargs)
            
            # Determine command type for setting check
            # Skip commands use /skip, /next, etc.
            # Play commands use /play, /vplay, etc.
            command = message.command[0].lower() if message.command else ""
            is_skip_cmd = command in ["skip", "next"]
            is_play_cmd = command in ["play", "vplay", "playlist"]
            
            # Check settings for "Everyone" mode
            settings = await db_manager.get_chat_settings(chat_id)
            
            if is_skip_cmd:
                skip_mode = settings.get("skip_mode", "admins")
                if skip_mode == "everyone":
                    return await func(client, message, *args, **kwargs)
            
            if is_play_cmd:
                play_mode = settings.get("play_mode", "everyone") # Default play mode is everyone
                if play_mode == "everyone":
                    return await func(client, message, *args, **kwargs)
            
            # If not "everyone" mode, proceed with admin check
            # Check cache first
            cache_key = f"{chat_id}:{user_id}"
            current_time = time.time()
            if cache_key in _admin_cache:
                cached_time, is_admin = _admin_cache[cache_key]
                if current_time - cached_time < CACHE_TTL:
                    if is_admin:
                        return await func(client, message, *args, **kwargs)
                    # Don't return if not admin from cache, re-check once just in case status changed
            
            # Get user status in the chat
            member = await message.chat.get_member(user_id)
            # Log the status for debugging
            logger.info(f"User {user_id} status in {chat_id}: {member.status}")
            
            from pyrogram.enums import ChatMemberStatus
            is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            
            # Update cache
            _admin_cache[cache_key] = (current_time, is_admin)
            
            if is_admin:
                return await func(client, message, *args, **kwargs)
            else:
                await message.reply_text(
                    "❌ ᴛʜɪꜱ ᴄσϻϻᴧηᴅ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ɢʀσᴜᴩ ᴧᴅϻɪηꜱ σηʟʏ!"
                )
                return
                
        except Exception as e:
            logger.error(f"Admin check error: {e}")
            await message.reply_text("❌ An error occurred while checking permissions.")
            return
    
    return wrapper


def user_in_vc(func):
    """Decorator to check if user is in voice chat"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            # This is a simplified check - in production, you'd check actual VC membership
            # For now, we'll allow all users in group chats
            if message.chat.type in ["group", "supergroup"]:
                return await func(client, message, *args, **kwargs)
            else:
                await message.reply_text(
                    "❌ This command can only be used in group voice chats!"
                )
                return
        except Exception as e:
            logger.error(f"VC check error: {e}")
            await message.reply_text("❌ An error occurred.")
            return
    
    return wrapper


def bot_can_manage_vc(func):
    """Decorator to check if bot has voice chat permissions"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            # In groups, bot should be admin with appropriate permissions
            if message.chat.type in ["group", "supergroup"]:
                bot_member = await message.chat.get_member(client.me.id)
                
                # Bot should be admin
                # In Pyrogram 2.x, status is a string
                if bot_member.status not in ['administrator', 'creator']:
                    await message.reply_text(
                        "❌ I need to be an admin to manage voice chats!\n"
                        "Please promote me to admin with voice chat permissions."
                    )
                    return
            
            return await func(client, message, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Bot permission check error: {e}")
            await message.reply_text("❌ An error occurred while checking permissions.")
            return
    
    return wrapper


def sudo_only(func):
    """Decorator to restrict command to sudo users only"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        
        if user_id in OWNER_ID or user_id in SUDOERS:
            return await func(client, message, *args, **kwargs)
        else:
            await message.reply_text(
                "❌ This command is restricted to authorized users only!"
            )
            return
    
    return wrapper


def owner_only(func):
    """Decorator to restrict command to owner only"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        
        if user_id in OWNER_ID:
            return await func(client, message, *args, **kwargs)
        else:
            await message.reply_text(
                "❌ This command is restricted to the bot owner only!"
            )
            return
    
    return wrapper


def sudo_check(func):
    """Decorator to check if user is sudoer (alias for sudo_only)"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        
        if user_id in OWNER_ID or user_id in SUDOERS:
            return await func(client, message, *args, **kwargs)
        else:
            await message.reply_text(
                "❌ This command is restricted to authorized users only!"
            )
            return
    
    return wrapper
