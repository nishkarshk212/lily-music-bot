"""
Play Command Handler
Handles /play command for playing songs
"""

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction, ParseMode
from core.queue import queue_manager, Song
from core.call_manager import call_manager
from utils.downloader import downloader
from utils.thumbnail_generator import create_thumbnail
from utils.formatter import format_time, format_views
from utils.decorators import bot_can_manage_vc, admin_check
from utils.strings import build_playing_message, SUCCESS_ADDED_TO_QUEUE, ERROR_NO_RESULTS, ERROR_QUEUE_FULL, SUPPORT_CHANNEL_USERNAME
from utils.html_helper import blockquote
from config import MAX_QUEUE_SIZE
from core.bot import bot_app
import os
import random
import asyncio
import logging

logger = logging.getLogger(__name__)

# Processing messages - Single clean searching message
AYU = [
    "ᴘʟᴀʏɪɴɢ ꜱσηɢ......"
]


async def send_playing_message(client: Client, chat_id: int, song, song_info=None):
    """Send playing message in background after playback has started"""
    try:
        # Generate thumbnail asynchronously
        thumb_path = None
        
        # Get metadata from song_info or song object
        thumbnail_url = getattr(song_info, 'thumbnail', song.thumbnail) if song_info else song.thumbnail
        artist = getattr(song_info, 'channel', song.artist) if song_info else song.artist
        views = format_views(getattr(song_info, 'views', song.views)) if song_info else format_views(song.views)
        
        if thumbnail_url:
            thumb_path = create_thumbnail(
                title=song.title,
                artist=artist,
                views=views,
                duration=format_time(song.duration),
                cover_url=thumbnail_url,
                output=f"assets/thumb_{chat_id}_{song.video_id}.png"
            )
        
        # Get bot info
        bot_info = await client.get_me()
        bot_name = bot_info.first_name
        bot_username = bot_info.username
        
        # Build the playing message with clickable title
        playing_caption = build_playing_message(
            title=song.title,
            title_url=song.url if hasattr(song, 'url') else None,
            duration=format_time(song.duration),
            requester=song.requester,
            bot_name=bot_name
        )
        
        # Create inline keyboard with buttons
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
            # Send as text if no thumbnail
            await client.send_message(
                chat_id=chat_id,
                text=playing_caption,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Failed to send playing message: {e}")


@admin_check
@bot_can_manage_vc
async def play_command(client: Client, message: Message):
    """Handle /play command"""
    try:
        chat_id = message.chat.id
        chat_username = message.chat.username  # Get chat username if available
        queue = queue_manager.get_queue(chat_id)
        
        # Check if reply to a message with URL
        if message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text.strip()
        elif len(message.command) > 1:
            query = " ".join(message.command[1:])
        else:
            # Show usage message with image and buttons
            from utils.group_start import GROUP_START_IMAGES
            
            play_usage_text = """
╭───────────────────▣
│❍ **ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅ ᴜsᴀɢᴇ :**
├───────────────────▣
│
│𝖴𝗌𝖺𝗀𝖾 : /play [ 𝖲𝗈𝗇𝗀 𝖭𝖺𝗆𝖾 / 𝖸𝗈𝗎𝖳𝗎𝖻𝖾 𝖴𝗋𝗅 / 𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖠 𝖠𝗎𝖽𝗂𝗈 / 𝖵𝗂𝖽𝖾𝗈 𝖥𝗂𝗅𝖾 ]
│
╰───────────────────▣
"""
            
            # Randomly select an image
            selected_image = random.choice(GROUP_START_IMAGES)
            
            # Create inline keyboard with support and close buttons only
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⊜ ꜱᴜᴘᴘσʀᴛ ⊜", url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}"),
                    InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")
                ]
            ])
            
            await message.reply_photo(
                photo=selected_image,
                caption=play_usage_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # ⚡ ULTRA-FAST: Join voice chat FIRST (highest priority)
        # Start joining voice chat IMMEDIATELY - this is the bottleneck
        join_task = asyncio.create_task(call_manager.join_voice_chat(chat_id, chat_username))
        
        # Then start search in parallel
        is_url = query.startswith(("http://", "https://"))
        if is_url:
            search_task = asyncio.create_task(downloader.extract_info(query))
        else:
            search_task = asyncio.create_task(downloader.search_and_download(query))

        # Wait for search with very short timeout
        try:
            song_info = await asyncio.wait_for(asyncio.shield(search_task), timeout=1.0)
            status_msg = None
        except asyncio.TimeoutError:
            # Only show searching message if it takes longer than 1 second
            status_msg = await message.reply_text("🔍 **δєᴧʀᴄʜɪηɢ...**")
            song_info = await search_task
            
        if not song_info:
            if status_msg:
                await status_msg.edit_text(ERROR_NO_RESULTS.format(query=query))
            else:
                await message.reply_text(ERROR_NO_RESULTS.format(query=query))
            return
        
        # Check song duration limit
        from config import MAX_DURATION
        if song_info.duration > MAX_DURATION:
            duration_minutes = song_info.duration // 60
            max_minutes = MAX_DURATION // 60
            error_msg = (
                f"❌ **ꜱσηɢ ᴛσσ ʟσηɢ!**\n\n"
                f"**Duration:** {duration_minutes} minutes\n"
                f"**Maximum allowed:** {max_minutes} minutes\n\n"
                f"ᴘʟєᴧꜱє ᴄʜσσꜱє ᴀ ꜱʜσʀᴛєʀ ꜱσηɢ. 🎵"
            )
            if status_msg:
                await status_msg.edit_text(error_msg)
            else:
                await message.reply_text(error_msg)
            return
        
        # Check queue size
        if queue.size() >= MAX_QUEUE_SIZE:
            if status_msg:
                await status_msg.edit_text(ERROR_QUEUE_FULL.format(max_size=MAX_QUEUE_SIZE))
            else:
                await message.reply_text(ERROR_QUEUE_FULL.format(max_size=MAX_QUEUE_SIZE))
            return
        
        # Create Song object
        song = Song(
            title=song_info.title,
            duration=song_info.duration,
            file_path=song_info.file_path,
            thumbnail=song_info.thumbnail,
            requester=message.from_user.first_name,
            video_id=song_info.video_id,
            url=song_info.url,
            artist=getattr(song_info, 'channel', 'Unknown'),
            views=str(getattr(song_info, 'views', '0'))
        )
        
        # FINAL CHECK: Has the bot started playing something else in the last 2 seconds?
        # This prevents duplicate messages if multiple commands were sent rapidly
        is_already_playing = call_manager and call_manager.is_playing(chat_id)
        
        if is_already_playing:
            # ALREADY PLAYING - Add to queue and show "Queued" message
            position = queue.add_song(song)
            
            # Create keyboard with close button
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")]])
            
            msg_text = SUCCESS_ADDED_TO_QUEUE.format(
                title=song.title,
                duration=format_time(song.duration),
                requester=song.requester,
                position=position
            )
            
            if status_msg:
                try:
                    await status_msg.edit_text(msg_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                except Exception as e:
                    # Ignore MESSAGE_NOT_MODIFIED error (message already has same content)
                    if "MESSAGE_NOT_MODIFIED" not in str(e):
                        logger.warning(f"Failed to edit status message: {e}")
                        # Don't send duplicate - just log the warning
            else:
                await message.reply_text(msg_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            # NOT PLAYING - Join VC and play IMMEDIATELY
            if not call_manager:
                if status_msg:
                    await status_msg.edit_text("❌ Call manager not initialized!")
                else:
                    await message.reply_text("❌ Call manager not initialized!")
                return
            
            try:
                # ⚡ CRITICAL: Set as current song IMMEDIATELY to prevent race conditions
                queue.current_song = song
                queue.is_playing = True
                
                # Delete the status message if it exists (before playing)
                if status_msg:
                    try:
                        await status_msg.delete()
                    except:
                        pass
                
                # ⚡ Play IMMEDIATELY - PyTgCalls will auto-join if needed
                # Don't wait for join_task, play_song handles it
                await call_manager.play_song(chat_id, song)
                
                # Ensure join completed in background (usually already done)
                if not join_task.done():
                    try:
                        await asyncio.wait_for(join_task, timeout=2.0)
                    except:
                        pass  # Join might already be done via play_song
                
                # Send playing message in background (non-blocking)
                asyncio.create_task(send_playing_message(client=client, chat_id=chat_id, song=song, song_info=song_info))
                
            except Exception as play_error:
                # Reset state if playback failed
                queue.current_song = None
                queue.is_playing = False
                
                # Check for specific admin required error
                error_msg = str(play_error)
                error_sent = False
                
                try:
                    if "CHAT_ADMIN_REQUIRED" in error_msg:
                        error_response = (
                            "❌ **ᴛєʟєɢʀᴧϻ ꜱᴧʏꜱ: [400 CHAT_ADMIN_REQUIRED]**\n\n"
                            "ᴛʜє ᴧꜱꜱɪꜱᴛᴧηᴛ ηєєᴅꜱ ᴛσ ʙє ᴧη **ᴧᴅϻɪη** ᴡɪᴛʜ ᴘєʀϻɪꜱꜱɪση ᴛσ **ϻᴧηᴧɢє ᴠσɪᴄє ᴄʜᴧᴛꜱ** ᴛσ ꜱᴛᴧʀᴛ ᴛʜє ꜱᴛʀєᴧϻ!"
                        )
                    elif "CHANNEL_INVALID" in error_msg or "ChannelInvalid" in error_msg:
                        error_response = (
                            "❌ **ᴄʜᴧηηєʟ ɪηᴠᴧʟɪᴅ**\n\n"
                            "ᴛʜє ʙσᴛ ᴅσєꜱ ησᴛ ʜᴧᴠє ᴧᴄᴄєꜱꜱ ᴛσ ᴛʜɪꜱ ᴄʜᴧηηєʟ/ɢʀσᴜᴘ.\n"
                            "ᴘʟєᴧꜱє ᴧᴅᴅ ᴛʜє ʙσᴛ ᴀηᴅ ᴧꜱꜱɪꜱᴛᴀηᴛ, ᴛʜєη ϻᴀᴋє ᴛʜєϻ **ᴀᴅϻɪη** ᴡɪᴛʜ ᴠσɪᴄє ᴄʜᴀᴛ ᴘєʀϻɪꜱꜱɪσηꜱ."
                        )
                    elif "GROUPCALL_INVALID" in error_msg or "GroupcallInvalid" in error_msg or "voice chat has ended" in error_msg.lower():
                        error_response = (
                            "❌ **ᴠσɪᴄє ᴄʜᴧᴛ єηᴅєᴅ σʀ ɪηᴠᴧʟɪᴅ**\n\n"
                            "ᴛʜє ᴠσɪᴄє ᴄʜᴧᴛ ɪη ᴛʜɪꜱ ɢʀσᴜᴘ ʜᴧꜱ єηᴅєᴅ σʀ ɪꜱ ɪηᴠᴧʟɪᴅ.\n"
                            "ᴘʟєᴧꜱє **ꜱᴛᴧʀᴛ ᴀ ηєᴡ ᴠσɪᴄє ᴄʜᴧᴛ** ᴀηᴅ ᴛʀʏ ᴧɢᴧɪη. 🎤"
                        )
                    elif "FLOOD_WAIT" in error_msg:
                        error_response = (
                            "⏳ **ᴛєʟєɢʀᴧϻ ʀᴧᴛє ʟɪϻɪᴛ**\n\n"
                            "ᴘʟєᴧꜱє ᴡᴧɪᴛ ᴀ ꜰєᴡ ꜱєᴄσηᴅꜱ ᴀηᴅ ᴛʀʏ ᴀɢᴀɪη.\n"
                            "ᴛʜɪꜱ ʜᴧᴘᴘєηꜱ ᴡʜєη ᴛσσ ϻᴧηʏ ᴄσϻϻᴧηᴅꜱ ᴧʀє ꜱєηᴛ ϙᴜɪᴄᴋʟʏ."
                        )
                    else:
                        error_response = f"❌ ꜰᴀɪʟєᴅ ᴛσ ᴘʟᴀʏ: {error_msg[:200]}"
                    
                    # Only edit status_msg if it exists and is valid
                    if status_msg:
                        await status_msg.edit_text(error_response)
                        error_sent = True
                    else:
                        await message.reply_text(error_response)
                        error_sent = True
                except Exception as edit_error:
                    # If editing fails with a real error (not MESSAGE_NOT_MODIFIED)
                    if "MESSAGE_NOT_MODIFIED" not in str(edit_error):
                        logger.warning(f"Failed to edit status message: {edit_error}")
                        # Don't send duplicate message - the edit likely succeeded or user already sees something
                    # If it was MESSAGE_NOT_MODIFIED, that's fine - user already sees the message
                
                # Don't raise expected errors (CHANNEL_INVALID, ADMIN_REQUIRED, FLOOD_WAIT, GROUPCALL_INVALID) to prevent log spam
                if "CHANNEL_INVALID" not in error_msg and "CHAT_ADMIN_REQUIRED" not in error_msg and "FLOOD_WAIT" not in error_msg and "GROUPCALL_INVALID" not in error_msg and "GroupcallInvalid" not in error_msg:
                    raise
        
        logger.info(f"Play command executed by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        # Don't log/send error if it's an expected error that was already handled
        error_str = str(e)
        if "CHANNEL_INVALID" in error_str or "CHAT_ADMIN_REQUIRED" in error_str or "FLOOD_WAIT" in error_str:
            return  # Already handled above
        
        logger.error(f"Play command error: {e}", exc_info=True)
        
        # Send error log to log group
        if bot_app:
            await bot_app.send_error_log(f"Play Command Error in {message.chat.id}: {str(e)}")
            
        # Send sorry message to the group
        sorry_text = (
            "ꜱᴏʀʀʏ ʙᴀʙᴜ ! ᴛʀʏ ᴘʟᴀʏɪɴɢ ᴏᴛʜᴇʀ \n\n"
            "ᴛʜɪs ᴛʀᴀᴄᴋ ᴄᴏᴜʟᴅɴ'ᴛ ʙᴇ ᴘʟᴀʏᴇᴅ. \n"
            "ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɴᴏᴛʜᴇʀ sᴏɴɢ. 🥀"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⊜ ꜱᴜᴘᴘσʀᴛ ⊜", url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}")]
        ])
        
        await message.reply_text(sorry_text, reply_markup=keyboard)
        
        # Restart the bot service (Only if it's a fatal error, not just a playback issue)
        # if bot_app:
        #     await bot_app.restart()
