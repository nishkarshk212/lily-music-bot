"""
Handler for when the bot is added to a new group
"""

import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from config import LOG_GROUP_ID
from utils.group_start import GROUP_START_IMAGES
import logging

logger = logging.getLogger(__name__)

async def new_group_handler(client: Client, message: Message):
    """Handle when bot is added to a new group"""
    if not message.new_chat_members:
        return
    
    bot_id = (await client.get_me()).id
    
    for member in message.new_chat_members:
        if member.id == bot_id:
            # Bot was added to the group
            chat = message.chat
            chat_name = chat.title
            chat_id = chat.id
            chat_username = f"@{chat.username}" if chat.username else "Private"
            
            # Save chat to database for broadcast
            from database.mongodb import db_manager
            try:
                await db_manager.save_chat_settings(
                    chat_id=chat_id,
                    settings={"chat_title": chat_name or "", "chat_type": chat.type}
                )
                logger.info(f"✅ Saved new group to database: {chat_id} - {chat_name}")
            except Exception as e:
                logger.error(f"Failed to save chat to database: {e}")
            
            # Try to get chat link
            try:
                chat_link = await client.export_chat_invite_link(chat_id)
            except:
                chat_link = "No Link (Bot needs admin rights)"
            
            # Get member count
            try:
                member_count = await client.get_chat_members_count(chat_id)
            except:
                member_count = "N/A"
            
            # Added by info
            added_by = message.from_user.mention if message.from_user else "Unknown"
            
            # Log message to log group
            if LOG_GROUP_ID:
                log_message = (
                    f"📝 ᴍᴜsɪᴄ ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ᴀ ɴᴇᴡ ɢʀᴏᴜᴘ \n\n"
                    f"❅─────✧❅✦❅✧─────❅ \n\n"
                    f"📌 ᴄʜᴀᴛ ɴᴀᴍᴇ: {chat_name}\n"
                    f"🍂 ᴄʜᴀᴛ ɪᴅ: `{chat_id}`\n"
                    f"🔐 ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ: {chat_username}\n"
                    f"🛰 ᴄʜᴀᴛ ʟɪɴᴋ: {chat_link}\n"
                    f"📈 ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs: {member_count}\n"
                    f"🤔 ᴀᴅᴅᴇᴅ ʙʏ: {added_by}"
                )
                
                # Use the professional train landscape image for log group
                selected_image = "https://i.ibb.co/wFwqqbjk/anime-landscape-person-traveling.jpg"
                
                try:
                    await client.send_photo(
                        LOG_GROUP_ID,
                        photo=selected_image,
                        caption=log_message
                    )
                except Exception as e:
                    print(f"Error sending log message: {e}")
            break
