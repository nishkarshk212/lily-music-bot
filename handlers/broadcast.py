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
        # Fix: Use message.text directly, not .html attribute
        broadcast_state[user_id]["text"] = message.text or message.caption or None
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
        
        logger.info(f"Starting broadcast from user {user_id}: text={bool(text)}, media={bool(media)}, buttons={len(buttons)}")
        
        # Build keyboard
        keyboard = None
        if buttons:
            keyboard_list = []
            for btn in buttons:
                keyboard_list.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
            keyboard = InlineKeyboardMarkup(keyboard_list)
            
        # Get all chats and users
        all_chats = await db_manager.get_all_chats()
        logger.info(f"Found {len(all_chats)} chats in database")
        
        # Fix: Properly query users collection
        all_users = []
        if hasattr(db_manager, 'user_collection') and db_manager.user_collection:
            try:
                all_users = await db_manager.user_collection.find({}).to_list(length=None)
                logger.info(f"Found {len(all_users)} users in database")
            except Exception as e:
                logger.error(f"Failed to query users: {e}")
        else:
            logger.warning("User collection not available")
        
        broadcast_targets = []
        for chat in all_chats:
            chat_id = chat.get('chat_id')
            if chat_id:
                broadcast_targets.append(chat_id)
        for user in all_users:
            user_id_target = user.get('user_id')
            if user_id_target:
                broadcast_targets.append(user_id_target)
            
        # Remove duplicates and the broadcaster's own ID
        broadcast_targets = list(set(broadcast_targets))
        broadcast_targets = [tid for tid in broadcast_targets if tid != user_id]
        
        logger.info(f"Total broadcast targets: {len(broadcast_targets)}")
        
        if not broadcast_targets:
            await message.edit_text("❌ **ησ ᴛᴧʀɢєᴛꜱ ꜰσᴜηᴅ ᴛσ ʙʀσᴧᴅᴄᴧꜱᴛ ᴛσ.**\n\nᴍᴧᴋє ꜱᴜʀє ᴛʜє ʙσᴛ ɪꜱ ᴧᴅᴅєᴅ ᴛσ ɢʀσᴜᴘꜱ σʀ ᴄʜᴧηηєʟꜱ.")
            return
            
        sent_count = 0
        failed_count = 0
        
        status_msg = await message.edit_text(
            f"📢 **ʙʀσᴧᴅᴄᴧδᴛɪηɢ...**\n\n"
            f"ᴛσᴛᴧʟ ᴛᴧʀɢєᴛδ: {len(broadcast_targets)}\n"
            f"δєηᴛ: 0 | ꜰᴧɪʟєᴅ: 0"
        )
        
        for target_id in broadcast_targets:
            try:
                if media:
                    # media is the original Message object, copy it to target
                    await media.copy(target_id, caption=text, reply_markup=keyboard)
                else:
                    if not text:
                        continue
                    await client.send_message(target_id, text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                
                sent_count += 1
            except FloodWait as e:
                logger.warning(f"FloodWait: {e.value}s for target {target_id}")
                await asyncio.sleep(e.value)
                try:
                    if media:
                        await media.copy(target_id, caption=text, reply_markup=keyboard)
                    else:
                        await client.send_message(target_id, text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                    sent_count += 1
                except Exception as retry_error:
                    failed_count += 1
                    logger.debug(f"Retry failed for {target_id}: {retry_error}")
            except (UserIsBlocked, InputUserDeactivated):
                failed_count += 1
            except Exception as e:
                failed_count += 1
                # Log only unexpected errors
                if "CHAT_WRITE_FORBIDDEN" not in str(e) and "peer_flood" not in str(e).lower():
                    logger.error(f"Failed to send to {target_id}: {e}")
            
            # Update status every 10 messages (increased frequency for better UX)
            if (sent_count + failed_count) % 10 == 0:
                try:
                    await status_msg.edit_text(
                        f"📢 **ʙʀσᴧᴅᴄᴧδᴛɪηɢ...**\n\n"
                        f"ᴛσᴛᴧʟ ᴛᴧʀɢєᴛδ: {len(broadcast_targets)}\n"
                        f"δєηᴛ: {sent_count} | ꜰᴧɪʟєᴅ: {failed_count}"
                    )
                except:
                    pass
        
        # Final status
        final_message = (
            f"✅ **ʙʀσᴧᴅᴄᴧꜱᴛ ᴄσϻᴘʟєᴛє!**\n\n"
            f"📊 **ꜱᴛᴧᴛɪꜱᴛɪᴄꜱ:**\n"
            f"├ ᴛσᴛᴧʟ: {len(broadcast_targets)}\n"
            f"├ δєηᴛ: {sent_count}\n"
            f"└ ꜰᴧɪʟєᴅ: {failed_count}"
        )
        await status_msg.edit_text(final_message)
        logger.info(f"Broadcast completed: {sent_count} sent, {failed_count} failed out of {len(broadcast_targets)} targets")
        
        # Clear state
        if user_id in broadcast_state:
            del broadcast_state[user_id]
            
    except Exception as e:
        logger.error(f"Error in execute_broadcast: {e}", exc_info=True)
        await message.edit_text(f"❌ **ᴧη єʀʀσʀ σᴄᴄᴜʀʀєᴅ ᴅᴜʀɪηɢ ʙʀσᴧᴅᴄᴧꜱᴛ.**\n\n`{str(e)[:200]}`")
