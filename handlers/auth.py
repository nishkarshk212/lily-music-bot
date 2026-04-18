"""
Auth User Handlers - Manage authorized users
"""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from database.mongodb import db_manager
from utils.decorators import sudo_check
import logging

logger = logging.getLogger(__name__)


@sudo_check
async def auth_command(client: Client, message: Message):
    """Add a user to auth list"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get user to auth
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
        elif len(message.command) > 1:
            user_input = message.command[1]
            # Try to get user by username or ID
            try:
                if user_input.startswith('@'):
                    user = await client.get_users(user_input)
                    user_id = user.id
                    user_name = user.first_name
                else:
                    user = await client.get_users(int(user_input))
                    user_id = user.id
                    user_name = user.first_name
            except Exception as e:
                await message.reply_text(f"❌ Could not find user: {user_input}")
                return
        else:
            await message.reply_text(
                "❌ Please provide a username/user ID or reply to a user's message.\n\n"
                "**Usage:** `/auth [username/user_id]`"
            )
            return
        
        # Add to auth users
        await db_manager.add_auth_user(message.chat.id, user_id, user_name)
        
        await message.reply_text(
            f"✅ **{user_name}** has been added to auth users!\n\n"
            f"They can now use admin commands in this chat."
        )
        
    except Exception as e:
        logger.error(f"Error in auth_command: {e}")
        await message.reply_text("❌ An error occurred while adding auth user.")


@sudo_check
async def unauth_command(client: Client, message: Message):
    """Remove a user from auth list"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get user to unauth
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
        elif len(message.command) > 1:
            user_input = message.command[1]
            try:
                if user_input.startswith('@'):
                    user = await client.get_users(user_input)
                    user_id = user.id
                    user_name = user.first_name
                else:
                    user = await client.get_users(int(user_input))
                    user_id = user.id
                    user_name = user.first_name
            except Exception as e:
                await message.reply_text(f"❌ Could not find user: {user_input}")
                return
        else:
            await message.reply_text(
                "❌ Please provide a username/user ID or reply to a user's message.\n\n"
                "**Usage:** `/unauth [username/user_id]`"
            )
            return
        
        # Remove from auth users
        await db_manager.remove_auth_user(message.chat.id, user_id)
        
        await message.reply_text(
            f"✅ **{user_name}** has been removed from auth users!\n\n"
            f"They can no longer use admin commands in this chat."
        )
        
    except Exception as e:
        logger.error(f"Error in unauth_command: {e}")
        await message.reply_text("❌ An error occurred while removing auth user.")


async def authusers_command(client: Client, message: Message):
    """Show list of auth users"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get auth users for this chat
        auth_users = await db_manager.get_auth_users(message.chat.id)
        
        if not auth_users:
            await message.reply_text(
                "📋 **No auth users in this chat.**\n\n"
                "Auth users can use admin rights without being admins."
            )
            return
        
        # Build auth users list
        auth_list = "**Auth Users in this Chat:**\n\n"
        for i, user in enumerate(auth_users, 1):
            auth_list += f"{i}. [{user['name']}](tg://user?id={user['id']}) (`{user['id']}`)\n"
        
        auth_list += "\n**Note:** Auth users can use admin commands in this chat."
        
        await message.reply_text(auth_list)
        
    except Exception as e:
        logger.error(f"Error in authusers_command: {e}")
        await message.reply_text("❌ An error occurred while fetching auth users.")
