"""
Control Command Handlers
Handles skip, pause, resume, stop, and volume commands
"""

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import asyncio
from core.queue import queue_manager
from core.call_manager import call_manager
from utils.formatter import format_time
from utils.decorators import admin_check
from utils.strings import SUPPORT_CHANNEL_USERNAME
import logging

logger = logging.getLogger(__name__)


@admin_check
async def skip_command(client: Client, message: Message):
    """Handle /skip command"""
    try:
        chat_id = message.chat.id
        queue = queue_manager.get_queue(chat_id)
        
        if not call_manager or not call_manager.is_playing(chat_id):
            await message.reply_text("❌ No song is currently playing!")
            return
        
        # Skip the song
        next_song = await call_manager.skip(chat_id)
        
        # Get user mention
        user_mention = message.from_user.mention
        
        if next_song:
            # Send simple skip message
            await message.reply_text(
                f"<blockquote>"
                f"<b>⏭️ δᴋɪᴩᴩєᴅ! ❞</b>"
                f"</blockquote>",
                parse_mode=ParseMode.HTML
            )
            
            # Send the Now Playing message of the current (next) song
            from handlers.play import send_playing_message
            asyncio.create_task(
                send_playing_message(
                    client=client,
                    chat_id=chat_id,
                    song=next_song
                )
            )
        else:
            # Create keyboard with close button
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")
                ]
            ])
            
            await message.reply_text(
                f"➻ 𝖲𝗍𝗋𝖾𝖺𝗆 𝖲𝗄𝗂𝗉𝗉𝖾𝖽 🎄\n"
                f"│\n"
                f"└𝖡𝗗 : {user_mention}🥀\n\n"
                f"𝖭𝗈 𝖬𝗈𝗋𝖾 𝖰𝗎𝖾𝗎𝖾𝖽 𝖳𝗋𝖺𝖼𝗄𝗌 𝖨𝗇 ᴛɪᴛᴀɴɪᴄ ʟᴇɢᴀᴄʏ , 𝖫𝖾𝖺𝗏𝗂𝗇𝗀 𝖵𝗂𝖽𝖾𝗈𝖢𝗁𝖺𝗍 .",
                reply_markup=keyboard
            )
        
        logger.info(f"Song skipped by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Skip command error: {e}")
        await message.reply_text("❌ Failed to skip song. Please try again.")


@admin_check
async def pause_command(client: Client, message: Message):
    """Handle /pause command"""
    try:
        chat_id = message.chat.id
        
        if not call_manager or not call_manager.is_playing(chat_id):
            await message.reply_text("❌ No song is currently playing!")
            return
        
        await call_manager.pause(chat_id)
        
        await message.reply_text(
            f"<blockquote>"
            f"<b>⏸️ ᴘʟᴧʏʙᴧᴄᴋ ᴘᴧᴜꜱєᴅ! ❞</b>\n\n"
            f"<b>Use /resume to continue playing.</b>"
            f"</blockquote>",
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Playback paused by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Pause command error: {e}")
        await message.reply_text("❌ Failed to pause. Please try again.")


@admin_check
async def resume_command(client: Client, message: Message):
    """Handle /resume command"""
    try:
        chat_id = message.chat.id
        queue = queue_manager.get_queue(chat_id)
        
        if not call_manager:
            await message.reply_text("❌ Call manager not initialized!")
            return
        
        if not queue.is_playing and queue.current_song:
            await call_manager.resume(chat_id)
            
            await message.reply_text(
                f"<blockquote>"
                f"<b>▶️ ᴘʟᴧʏʙᴧᴄᴋ ʀєꜱᴜϻєᴅ! ❞</b>\n\n"
                f"<b>❍ TITLE :</b> {queue.current_song.title} <b>❞</b>\n"
                f"<b>❍ DURΛTIση :</b> {format_time(queue.current_song.duration)} <b>MIηUTeS</b>\n"
                f"<b>❍ BY :</b> {queue.current_song.requester}"
                f"</blockquote>",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply_text("❌ No paused song to resume!")
        
        logger.info(f"Playback resumed by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Resume command error: {e}")
        await message.reply_text("❌ Failed to resume. Please try again.")


@admin_check
async def stop_command(client: Client, message: Message):
    """Handle /stop command"""
    try:
        chat_id = message.chat.id
        
        if not call_manager or not call_manager.is_playing(chat_id):
            await message.reply_text("❌ No song is currently playing!")
            return
        
        # Stop playback (this also clears queue and leaves voice chat)
        await call_manager.stop(chat_id)
        
        # Get user mention
        user_mention = message.from_user.mention
        
        # Create keyboard with close button
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")
            ]
        ])
        
        await message.reply_text(
            f"<blockquote>"
            f"<b>❖ δᴛʀєᴧϻ єηᴅєᴅ / δᴛσᴘᴘєᴅ ❞</b>\n\n"
            f"<b>❍ BY :</b> {user_mention}"
            f"</blockquote>",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Playback stopped by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Stop command error: {e}")
        await message.reply_text("❌ Failed to stop. Please try again.")


@admin_check
async def volume_command(client: Client, message: Message):
    """Handle /volume command"""
    try:
        chat_id = message.chat.id
        
        if not call_manager or not call_manager.is_playing(chat_id):
            await message.reply_text("❌ No song is currently playing!")
            return
        
        # Check if volume level is provided
        if len(message.command) < 2:
            queue = queue_manager.get_queue(chat_id)
            await message.reply_text(
                f"🔊 **Current Volume:** {queue.volume}%\n\n"
                "**Usage:** `/volume <1-200>`\n"
                "• 1-50: Low\n"
                "• 51-100: Normal\n"
                "• 101-150: High\n"
                "• 151-200: Very High"
            )
            return
        
        # Parse volume level
        try:
            volume = int(message.command[1])
            if volume < 1 or volume > 200:
                await message.reply_text(
                    "❌ Volume must be between 1 and 200!"
                )
                return
        except ValueError:
            await message.reply_text(
                "❌ Invalid volume level! Please provide a number."
            )
            return
        
        # Set volume
        await call_manager.set_volume(chat_id, volume)
        
        volume_level = "🔇" if volume == 0 else "🔈" if volume < 50 else "🔉" if volume < 100 else "🔊"
        
        await message.reply_text(
            f"<blockquote>"
            f"{volume_level} <b>ᴠσʟᴜϻє ꜱєᴛ ᴛσ {volume}%! ❞</b>"
            f"</blockquote>",
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Volume set to {volume} by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Volume command error: {e}")
        await message.reply_text("❌ Failed to set volume. Please try again.")
