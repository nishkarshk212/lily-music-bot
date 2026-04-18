"""
Local File Play Handler
Handles playing local audio/video files from Telegram messages
"""

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction, ParseMode
from core.queue import queue_manager, Song
from core.call_manager import call_manager
from utils.thumbnail_generator import create_thumbnail
from utils.formatter import format_time, format_views
from utils.decorators import bot_can_manage_vc, admin_check
from utils.strings import build_playing_message, ERROR_QUEUE_FULL, SUPPORT_CHANNEL_USERNAME
from config import MAX_QUEUE_SIZE, DOWNLOAD_DIR
from core.bot import bot_app
import os
import random
import asyncio
import logging
import hashlib
import re

logger = logging.getLogger(__name__)

# Processing messages
PROCESSING_MESSAGES = [
    "ᴘʟᴀʏɪɴɢ ꜰɪʟᴇ......"
]


async def send_playing_message(client: Client, chat_id: int, song):
    """Send playing message in background after playback has started"""
    try:
        # Generate thumbnail if available
        thumb_path = None
        
        if song.thumbnail:
            thumb_path = create_thumbnail(
                title=song.title,
                artist=song.artist,
                views=format_views(song.views) if song.views else "0",
                duration=format_time(song.duration),
                cover_url=song.thumbnail,
                output=f"assets/thumb_{chat_id}_{song.video_id}.png"
            )
        
        # Get bot info
        bot_info = await client.get_me()
        bot_name = bot_info.first_name
        bot_username = bot_info.username
        
        # Build the playing message
        playing_caption = build_playing_message(
            title=song.title,
            title_url=None,
            duration=format_time(song.duration),
            requester=song.requester,
            bot_name=bot_name
        )
        
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="✦ ᴧᴅᴅ ϻє ✦",
                        url=f"https://t.me/{bot_username}?startgroup=true"
                    ),
                    InlineKeyboardButton(
                        text="ꜱᴜᴘᴘσʀᴛ",
                        url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="ᴄʟσꜱє",
                        callback_data="close_playing"
                    )
                ]
            ]
        )
        
        # Send message with thumbnail if available
        if thumb_path and os.path.exists(thumb_path):
            await client.send_photo(
                chat_id=chat_id,
                photo=thumb_path,
                caption=playing_caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            # Clean up thumbnail
            try:
                os.remove(thumb_path)
            except:
                pass
        else:
            # Send as text
            await client.send_message(
                chat_id=chat_id,
                text=playing_caption,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Failed to send playing message: {e}")


def get_file_id(message: Message):
    """Get file ID and type from message"""
    if message.audio:
        return message.audio.file_id, 'audio', message.audio
    elif message.voice:
        return message.voice.file_id, 'voice', message.voice
    elif message.video:
        return message.video.file_id, 'video', message.video
    elif message.document:
        # Check if document is audio/video
        mime_type = message.document.mime_type or ''
        if mime_type.startswith(('audio/', 'video/')):
            return message.document.file_id, 'document', message.document
    return None, None, None


def get_file_info(file_obj, file_type: str) -> dict:
    """Extract file information"""
    info = {
        'file_name': 'Unknown',
        'duration': 0,
        'mime_type': '',
        'file_size': 0,
        'title': 'Unknown',
        'performer': '',
    }
    
    if hasattr(file_obj, 'file_name'):
        info['file_name'] = file_obj.file_name or 'Unknown'
    
    if hasattr(file_obj, 'duration'):
        info['duration'] = file_obj.duration or 0
    
    if hasattr(file_obj, 'mime_type'):
        info['mime_type'] = file_obj.mime_type or ''
    
    if hasattr(file_obj, 'file_size'):
        info['file_size'] = file_obj.file_size or 0
    
    if hasattr(file_obj, 'title'):
        info['title'] = file_obj.title or 'Unknown'
    
    if hasattr(file_obj, 'performer'):
        info['performer'] = file_obj.performer or ''
    
    return info


@admin_check
@bot_can_manage_vc
async def play_local_file(client: Client, message: Message):
    """Handle playing local audio/video files from Telegram"""
    try:
        chat_id = message.chat.id
        queue = queue_manager.get_queue(chat_id)
        
        # Get file from message
        file_id, file_type, file_obj = get_file_id(message)
        
        if not file_id:
            await message.reply_text(
                "❌ ᴘʟєᴧꜱє ʀєᴘʟʏ ᴛσ **ᴧᴜᴅɪσ**, **ᴠσɪᴄє**, σʀ **ᴠɪᴅєσ** ꜰɪʟє ᴛσ ᴘʟᴧʏ ɪᴛ."
            )
            return
        
        # Get file information
        file_info = get_file_info(file_obj, file_type)
        
        # Check queue size
        if queue.size() >= MAX_QUEUE_SIZE:
            await message.reply_text(ERROR_QUEUE_FULL.format(max_size=MAX_QUEUE_SIZE))
            return
        
        # Send processing message
        status_msg = await message.reply_text("📥 **ᴅσᴡηʟσᴧᴅɪηɢ ꜰɪʟє...**")
        
        # Create unique filename
        file_extension = file_info['mime_type'].split('/')[-1] if file_info['mime_type'] else 'mp3'
        unique_hash = hashlib.md5(f"{chat_id}_{file_id}".encode()).hexdigest()[:8]
        local_file_path = os.path.join(DOWNLOAD_DIR, f"local_{unique_hash}.{file_extension}")
        
        # Download file
        try:
            await message.download(file_name=local_file_path)
        except Exception as download_error:
            await status_msg.edit_text("❌ ꜰᴧɪʟєᴅ ᴛσ ᴅσᴡηʟσᴧᴅ ꜰɪʟє. ᴘʟєᴧꜱє ᴛʀʏ ᴧɢᴧɪη.")
            logger.error(f"Failed to download file: {download_error}")
            return
        
        # Verify file was downloaded
        if not os.path.exists(local_file_path):
            await status_msg.edit_text("❌ ꜰɪʟє ησᴛ ꜰσᴜηᴅ ᴧꜰᴛєʀ ᴅσᴡηʟσᴧᴅ.")
            return
        
        file_size = os.path.getsize(local_file_path)
        if file_size < 1024:
            await status_msg.edit_text("❌ ꜰɪʟє ɪꜱ ᴛσσ ꜱϻᴧʟʟ σʀ ᴄσʀʀᴜᴘᴛєᴅ.")
            try:
                os.remove(local_file_path)
            except:
                pass
            return
        
        # Create Song object
        title = file_info['title'] if file_info['title'] != 'Unknown' else file_info['file_name']
        artist = file_info['performer'] if file_info['performer'] else "Telegram File"
        duration = file_info['duration'] if file_info['duration'] > 0 else 0
        
        song = Song(
            title=title,
            duration=duration,
            file_path=local_file_path,
            thumbnail="",  # Local files don't have thumbnails
            requester=message.from_user.first_name,
            video_id=f"local_{unique_hash}",
            url="",
            artist=artist,
            views="0"
        )
        
        # Check if already playing
        is_already_playing = call_manager and call_manager.is_playing(chat_id)
        
        if is_already_playing:
            # Add to queue
            position = queue.add_song(song)
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")]])
            
            msg_text = (
                f"✅ **{title}**\n\n"
                f"ᴅᴜʀᴧᴛɪση: {format_time(duration)}\n"
                f"ʀєϫᴜєꜱᴛєᴅ ʙʏ: {song.requester}\n"
                f"📍 ᴘσꜱɪᴛɪση: #{position}\n\n"
                f"ᴧᴅᴅєᴅ ᴛσ ϙᴜєᴜє!"
            )
            
            await status_msg.edit_text(msg_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            # Play immediately
            if not call_manager:
                await status_msg.edit_text("❌ Call manager not initialized!")
                return
            
            try:
                # Set as current song
                queue.current_song = song
                queue.is_playing = True
                
                # Delete status message
                try:
                    await status_msg.delete()
                except:
                    pass
                
                # Play the file
                await call_manager.play_song(chat_id, song)
                
                # Send playing message in background
                asyncio.create_task(send_playing_message(client=client, chat_id=chat_id, song=song))
                
            except Exception as play_error:
                # Reset state
                queue.current_song = None
                queue.is_playing = False
                
                error_msg = str(play_error)
                try:
                    if "CHANNEL_INVALID" in error_msg or "ChannelInvalid" in error_msg:
                        error_response = (
                            "❌ **ᴄʜᴧηηєʟ ɪηᴠᴧʟɪᴅ**\n\n"
                            "ᴛʜє ʙσᴛ ᴅσєꜱ ησᴛ ʜᴧᴠє ᴧᴄᴄєꜱꜱ ᴛσ ᴛʜɪꜱ ᴄʜᴧηηєʟ/ɢʀσᴜᴘ.\n"
                            "ᴘʟєᴧꜱє ᴧᴅᴅ ᴛʜє ʙσᴛ ᴧηᴅ ϻᴧᴋє ɪᴛ **ᴧᴅϻɪη** ᴡɪᴛʜ ᴠσɪᴄє ᴄʜᴧᴛ ᴘєʀϻɪꜱꜱɪσηꜱ."
                        )
                    else:
                        error_response = f"❌ ꜰᴧɪʟєᴅ ᴛσ ᴘʟᴧʏ: {error_msg[:200]}"
                    
                    await status_msg.edit_text(error_response)
                except:
                    await message.reply_text("❌ ꜰᴧɪʟєᴅ ᴛσ ᴘʟᴧʏ ᴛʜє ꜰɪʟє. ᴘʟєᴧꜱє ᴛʀʏ ᴧɢᴧɪη.")
                raise
        
        logger.info(f"Local file played by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Play local file error: {e}", exc_info=True)
        
        # Send error log
        if bot_app:
            await bot_app.send_error_log(f"Play Local File Error in {message.chat.id}: {str(e)}")
        
        # Send sorry message
        sorry_text = (
            "ꜱᴏʀʀʏ ʙᴧʙᴜ ! ᴛʀʏ ᴘʟᴧʏɪηɢ σᴛʜєʀ \n\n"
            "ᴛʜɪꜱ ꜰɪʟє ᴄσᴜʟᴅη'ᴛ ʙє ᴘʟᴧʏєᴅ. \n"
            "ᴘʟєᴧꜱє ᴛʀʏ ᴧησᴛʜєʀ ꜰɪʟє. 🥀"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⊜ ꜱᴜᴘᴘσʀᴛ ⊜", url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}")]
        ])
        
        await message.reply_text(sorry_text, reply_markup=keyboard)


# Register the handler
def get_local_file_handler():
    """Return handler for local files"""
    from pyrogram import filters
    
    # Handle audio, voice, video, and document (audio/video) files
    local_file_filter = (
        filters.audio | 
        filters.voice | 
        filters.video | 
        (filters.document & filters.regex(r'.*\.(mp3|mp4|wav|ogg|m4a|flac|mkv|avi|mov)$', re.IGNORECASE))
    )
    
    return MessageHandler(
        play_local_file,
        local_file_filter & filters.reply
    )
