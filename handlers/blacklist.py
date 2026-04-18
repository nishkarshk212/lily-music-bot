"""
Chat Blacklist Handler - Manage blacklisted chats
"""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from database.mongodb import db_manager
from utils.decorators import sudo_check
import logging

logger = logging.getLogger(__name__)


@sudo_check
async def blacklistchat_command(client: Client, message: Message):
    """Blacklist a chat from using the bot"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get chat ID
        if len(message.command) > 1:
            chat_id = int(message.command[1])
        elif message.chat.type != 'private':
            chat_id = message.chat.id
        else:
            await message.reply_text(
                "❌ Please provide a chat ID or use this command in a group.\n\n"
                "**Usage:** `/blacklistchat [chat_id]`"
            )
            return
        
        # Add to blacklist
        await db_manager.blacklist_chat(chat_id)
        
        # Get chat info
        try:
            chat = await client.get_chat(chat_id)
            chat_name = chat.title
        except:
            chat_name = "Unknown Chat"
        
        await message.reply_text(
            f"✅ **Chat Blacklisted!**\n\n"
            f"Chat: {chat_name}\n"
            f"ID: `{chat_id}`\n\n"
            f"This chat can no longer use the bot."
        )
        
    except Exception as e:
        logger.error(f"Error in blacklistchat_command: {e}")
        await message.reply_text("❌ An error occurred while blacklisting chat.")


@sudo_check
async def whitelistchat_command(client: Client, message: Message):
    """Whitelist a blacklisted chat"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get chat ID
        if len(message.command) > 1:
            chat_id = int(message.command[1])
        else:
            await message.reply_text(
                "❌ Please provide a chat ID.\n\n"
                "**Usage:** `/whitelistchat [chat_id]`"
            )
            return
        
        # Remove from blacklist
        await db_manager.whitelist_chat(chat_id)
        
        # Get chat info
        try:
            chat = await client.get_chat(chat_id)
            chat_name = chat.title
        except:
            chat_name = "Unknown Chat"
        
        await message.reply_text(
            f"✅ **Chat Whitelisted!**\n\n"
            f"Chat: {chat_name}\n"
            f"ID: `{chat_id}`\n\n"
            f"This chat can now use the bot again."
        )
        
    except Exception as e:
        logger.error(f"Error in whitelistchat_command: {e}")
        await message.reply_text("❌ An error occurred while whitelisting chat.")


@sudo_check
async def blacklistedchat_command(client: Client, message: Message):
    """Show list of blacklisted chats"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get blacklisted chats
        blacklisted = await db_manager.get_blacklisted_chats()
        
        if not blacklisted:
            await message.reply_text(
                "📋 **No blacklisted chats.**\n\n"
                "All chats can use the bot."
            )
            return
        
        # Build blacklisted chats list
        bl_list = "**Blacklisted Chats:**\n\n"
        for i, chat in enumerate(blacklisted, 1):
            bl_list += f"{i}. `{chat['chat_id']}`\n"
        
        bl_list += f"\n**Total:** {len(blacklisted)} chats"
        
        await message.reply_text(bl_list)
        
    except Exception as e:
        logger.error(f"Error in blacklistedchat_command: {e}")
        await message.reply_text("❌ An error occurred while fetching blacklisted chats.")
