"""
Broadcast Handler - Broadcast messages to served chats
"""

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from database.mongodb import db_manager
from utils.decorators import owner_only
import logging

logger = logging.getLogger(__name__)

# Broadcast state management
# user_id: {"text": str, "media": Message, "buttons": List[Dict], "state": str}
broadcast_state = {}

@owner_only
async def broadcast_command(client: Client, message: Message):
    """Initial broadcast command - shows menu"""
    user_id = message.from_user.id
    
    # Reset state for this user
    broadcast_state[user_id] = {
        "text": None,
        "media": None,
        "buttons": [],
        "state": None
    }
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 δєᴛ ᴛєxᴛ", callback_data="bc_set_text"),
            InlineKeyboardButton("🖼️ δєᴛ ϻєᴅɪᴧ", callback_data="bc_set_media")
        ],
        [
            InlineKeyboardButton("🔘 ᴧᴅᴅ ʙᴜᴛᴛση", callback_data="bc_add_button")
        ],
        [
            InlineKeyboardButton("📢 ʙʀσᴧᴅᴄᴧꜱᴛ", callback_data="bc_start_broadcast")
        ]
    ])
    
    await message.reply_text(
        "📢 **ʙʀσᴧᴅᴄᴧꜱᴛ ϻєηᴜ**\n\n"
        "ᴄσηꜰɪɢᴜʀє ʏσᴜʀ ʙʀσᴧᴅᴄᴧꜱᴛ ϻєꜱꜱᴧɢє ᴜꜱɪηɢ ᴛʜє ʙᴜᴛᴛσηꜱ ʙєʟσᴡ:",
        reply_markup=keyboard
    )

async def broadcast_callback_handler(client: Client, callback_query: CallbackQuery):
    """Handle broadcast menu callbacks"""
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if user_id not in broadcast_state:
        broadcast_state[user_id] = {"text": None, "media": None, "buttons": [], "state": None}
    
    if data == "bc_set_text":
        broadcast_state[user_id]["state"] = "waiting_for_text"
        await callback_query.message.edit_text("📝 **δєηᴅ ᴛʜє ᴛєxᴛ ʏσᴜ ᴡᴧηᴛ ᴛσ ʙʀσᴧᴅᴄᴧꜱᴛ.**")
    
    elif data == "bc_set_media":
        broadcast_state[user_id]["state"] = "waiting_for_media"
        await callback_query.message.edit_text("🖼️ **δєηᴅ ᴛʜє ϻєᴅɪᴧ (ᴘʜσᴛσ/ᴠɪᴅєσ) ʏσᴜ ᴡᴧηᴛ ᴛσ ʙʀσᴧᴅᴄᴧꜱᴛ.**")
        
    elif data == "bc_add_button":
        broadcast_state[user_id]["state"] = "waiting_for_button"
        await callback_query.message.edit_text(
            "🔘 **δєηᴅ ᴛʜє ʙᴜᴛᴛση ᴅєᴛᴧɪʟꜱ.**\n\n"
            "ꜰσʀϻᴧᴛ: `ᴛєxᴛ | ᴜʀʟ`\n"
            "єxᴧϻᴘʟє: `δᴜᴘᴘσʀᴛ | ʜᴛᴛᴘꜱ://ᴛ.ϻє/ϻᴜꜱɪᴄ_24345`"
        )
        
    elif data == "bc_start_broadcast":
        # Check if we have at least text or media
        if not broadcast_state[user_id]["text"] and not broadcast_state[user_id]["media"]:
            await callback_query.answer("❌ δєᴛ ᴧᴛ ʟєᴧꜱᴛ ᴛєxᴛ σʀ ϻєᴅɪᴧ ꜰɪʀꜱᴛ!", show_alert=True)
            return
            
        await execute_broadcast(client, callback_query.message, user_id)

async def broadcast_message_handler(client: Client, message: Message):
    """Handle text/media/button input for broadcast"""
    user_id = message.from_user.id
    if user_id not in broadcast_state or not broadcast_state[user_id]["state"]:
        return
        
    state = broadcast_state[user_id]["state"]
    
    if state == "waiting_for_text":
        broadcast_state[user_id]["text"] = message.text.html if message.text else message.caption.html if message.caption else None
        broadcast_state[user_id]["state"] = None
        await message.reply_text("✅ **ᴛєxᴛ δєᴛ δᴜᴄᴄєꜱꜱꜰᴜʟʟʏ!**")
        await broadcast_command(client, message)
        
    elif state == "waiting_for_media":
        if message.photo or message.video or message.document:
            broadcast_state[user_id]["media"] = message
            broadcast_state[user_id]["state"] = None
            await message.reply_text("✅ **ϻєᴅɪᴧ δєᴛ δᴜᴄᴄєꜱ份ᴜʟʟʏ!**")
            await broadcast_command(client, message)
        else:
            await message.reply_text("❌ **ɪηᴠᴧʟɪᴅ ϻєᴅɪᴧ! ᴘʟєᴧδє δєηᴅ ᴧ ᴘʜσᴛσ, ᴠɪᴅєσ, σʀ ᴅσᴄᴜϻєηᴛ.**")
            
    elif state == "waiting_for_button":
        if "|" in message.text:
            text, url = message.text.split("|", 1)
            broadcast_state[user_id]["buttons"].append({"text": text.strip(), "url": url.strip()})
            broadcast_state[user_id]["state"] = None
            await message.reply_text(f"✅ **ʙᴜᴛᴛση '{text.strip()}' ᴧᴅᴅєᴅ!**")
            await broadcast_command(client, message)
        else:
            await message.reply_text("❌ **ɪηᴠᴧʟɪᴅ ꜰσʀϻᴧᴛ! ᴜδє: ᴛєxᴛ | ᴜʀʟ**")

async def execute_broadcast(client: Client, message: Message, user_id: int):
    """Execute the actual broadcast"""
    try:
        data = broadcast_state[user_id]
        text = data["text"]
        media = data["media"]
        buttons = data["buttons"]
        
        # Build keyboard
        keyboard = None
        if buttons:
            keyboard_list = []
            for btn in buttons:
                keyboard_list.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
            keyboard = InlineKeyboardMarkup(keyboard_list)
            
        # Get all chats and users
        all_chats = await db_manager.get_all_chats()
        all_users = await db_manager.user_collection.find({}).to_list(length=None) if db_manager.user_collection else []
        
        broadcast_targets = []
        for chat in all_chats:
            broadcast_targets.append(chat.get('chat_id'))
        for user in all_users:
            broadcast_targets.append(user.get('user_id'))
            
        broadcast_targets = list(set(broadcast_targets)) # Unique targets
        
        if not broadcast_targets:
            await message.edit_text("❌ No targets found to broadcast to.")
            return
            
        sent_count = 0
        failed_count = 0
        
        status_msg = await message.edit_text(
            f"📢 **ʙʀσᴧᴅᴄᴧꜱᴛɪηɢ...**\n\n"
            f"ᴛσᴛᴧʟ ᴛᴧʀɢєᴛꜱ: {len(broadcast_targets)}\n"
            f"δєηᴛ: 0 | ꜰᴧɪʟєᴅ: 0"
        )
        
        for target_id in broadcast_targets:
            try:
                if media:
                    await media.copy(target_id, caption=text, reply_markup=keyboard)
                else:
                    await client.send_message(target_id, text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                
                sent_count += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                # Try again after sleep
                try:
                    if media:
                        await media.copy(target_id, caption=text, reply_markup=keyboard)
                    else:
                        await client.send_message(target_id, text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                    sent_count += 1
                except:
                    failed_count += 1
            except (UserIsBlocked, InputUserDeactivated):
                failed_count += 1
            except Exception as e:
                failed_count += 1
                logger.debug(f"Failed to send to {target_id}: {e}")
            
            # Update status every 20 messages
            if (sent_count + failed_count) % 20 == 0:
                try:
                    await status_msg.edit_text(
                        f"📢 **ʙʀσᴧᴅᴄᴧꜱᴛɪηɢ...**\n\n"
                        f"ᴛσᴛᴧʟ ᴛᴧʀɢєᴛꜱ: {len(broadcast_targets)}\n"
                        f"δєηᴛ: {sent_count} | ꜰᴧɪʟєᴅ: {failed_count}"
                    )
                except:
                    pass
        
        # Final status
        await status_msg.edit_text(
            f"✅ **ʙʀσᴧᴅᴄᴧꜱᴛ ᴄσϻᴘʟєᴛє!**\n\n"
            f"📊 **δᴛᴧᴛɪδᴛɪᴄδ:**\n"
            f"├ ᴛσᴛᴧʟ: {len(broadcast_targets)}\n"
            f"├ δєηᴛ: {sent_count}\n"
            f"└ ꜰᴧɪʟєᴅ: {failed_count}"
        )
        
        # Clear state
        if user_id in broadcast_state:
            del broadcast_state[user_id]
            
    except Exception as e:
        logger.error(f"Error in execute_broadcast: {e}")
        await message.edit_text("❌ An error occurred during broadcast.")
