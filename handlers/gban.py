"""
Global Ban Handler - GBAN users
"""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from database.mongodb import db_manager
from utils.decorators import sudo_check
import logging

logger = logging.getLogger(__name__)


@sudo_check
async def gban_command(client: Client, message: Message):
    """Globally ban a user"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get user to ban
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
                "**Usage:** `/gban [username/user_id]`"
            )
            return
        
        # Check if already banned
        is_banned = await db_manager.is_gbanned(user_id)
        if is_banned:
            await message.reply_text(f"❌ **{user_name}** is already globally banned!")
            return
        
        # Add to GBAN list
        await db_manager.gban_user(user_id, user_name, message.from_user.id)
        
        await message.reply_text(
            f"✅ **{user_name}** has been globally banned!\n\n"
            f"They are now banned from all served chats."
        )
        
    except Exception as e:
        logger.error(f"Error in gban_command: {e}")
        await message.reply_text("❌ An error occurred while banning user.")


@sudo_check
async def ungban_command(client: Client, message: Message):
    """Globally unban a user"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get user to unban
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
                "**Usage:** `/ungban [username/user_id]`"
            )
            return
        
        # Check if banned
        is_banned = await db_manager.is_gbanned(user_id)
        if not is_banned:
            await message.reply_text(f"❌ **{user_name}** is not globally banned!")
            return
        
        # Remove from GBAN list
        await db_manager.ungban_user(user_id)
        
        await message.reply_text(
            f"✅ **{user_name}** has been globally unbanned!\n\n"
            f"They can now use the bot again."
        )
        
    except Exception as e:
        logger.error(f"Error in ungban_command: {e}")
        await message.reply_text("❌ An error occurred while unbanning user.")


@sudo_check
async def gbannedusers_command(client: Client, message: Message):
    """Show list of globally banned users"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get GBAN users
        gbanned_users = await db_manager.get_gbanned_users()
        
        if not gbanned_users:
            await message.reply_text(
                "📋 **No globally banned users.**\n\n"
                "All users can use the bot."
            )
            return
        
        # Build GBAN users list
        gban_list = "**Globally Banned Users:**\n\n"
        for i, user in enumerate(gbanned_users, 1):
            gban_list += f"{i}. [{user['name']}](tg://user?id={user['id']}) (`{user['id']}`)\n"
        
        gban_list += f"\n**Total:** {len(gbanned_users)} users"
        
        await message.reply_text(gban_list)
        
    except Exception as e:
        logger.error(f"Error in gbannedusers_command: {e}")
        await message.reply_text("❌ An error occurred while fetching banned users.")
