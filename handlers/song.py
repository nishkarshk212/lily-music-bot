"""
Song Download Handler - Download songs from YouTube
"""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from utils.downloader import downloader
import logging
import os

logger = logging.getLogger(__name__)


async def song_command(client: Client, message: Message):
    """Download a song from YouTube"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get query
        if len(message.command) < 2 and not message.reply_to_message:
            await message.reply_text(
                "❌ Please provide a song name or YouTube URL.\n\n"
                "**Usage:** `/song <song name or YouTube URL>`"
            )
            return
        
        if message.reply_to_message:
            query = message.reply_to_message.text or message.reply_to_message.caption
        else:
            query = message.text.split(None, 1)[1]
        
        # Search and download
        status_msg = await message.reply_text(f"🔍 **Searching:** {query}")
        
        # Get song info
        song_info = await downloader.get_song_info(query)
        if not song_info:
            await status_msg.edit_text("❌ Could not find the song.")
            return
        
        await status_msg.edit_text(f"📥 **Downloading:** {song_info['title']}")
        
        # Download audio (MP3)
        file_path = await downloader.download_audio(query)
        if not file_path:
            await status_msg.edit_text("❌ Failed to download the song.")
            return
        
        await status_msg.edit_text(f"📤 **Uploading:** {song_info['title']}")
        
        # Send the file
        await message.reply_audio(
            audio=file_path,
            title=song_info['title'],
            performer=song_info.get('uploader', 'Unknown'),
            duration=song_info.get('duration', 0),
            caption=f"🎵 **{song_info['title']}**\n\n"
                   f"⏱ Duration: {song_info.get('duration', 0)} seconds"
        )
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await status_msg.edit_text("✅ **Download complete!**")
        
    except Exception as e:
        logger.error(f"Error in song_command: {e}")
        await message.reply_text("❌ An error occurred while downloading the song.")


async def video_command(client: Client, message: Message):
    """Download a video from YouTube"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get query
        if len(message.command) < 2 and not message.reply_to_message:
            await message.reply_text(
                "❌ Please provide a video name or YouTube URL.\n\n"
                "**Usage:** `/video <video name or YouTube URL>`"
            )
            return
        
        if message.reply_to_message:
            query = message.reply_to_message.text or message.reply_to_message.caption
        else:
            query = message.text.split(None, 1)[1]
        
        # Search and download
        status_msg = await message.reply_text(f"🔍 **Searching:** {query}")
        
        # Get video info
        video_info = await downloader.get_song_info(query)
        if not video_info:
            await status_msg.edit_text("❌ Could not find the video.")
            return
        
        await status_msg.edit_text(f"📥 **Downloading:** {video_info['title']}")
        
        # Download video (MP4)
        file_path = await downloader.download_video(query)
        if not file_path:
            await status_msg.edit_text("❌ Failed to download the video.")
            return
        
        await status_msg.edit_text(f"📤 **Uploading:** {video_info['title']}")
        
        # Send the file
        await message.reply_video(
            video=file_path,
            caption=f"🎬 **{video_info['title']}**\n\n"
                   f"⏱ Duration: {video_info.get('duration', 0)} seconds"
        )
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await status_msg.edit_text("✅ **Download complete!**")
        
    except Exception as e:
        logger.error(f"Error in video_command: {e}")
        await message.reply_text("❌ An error occurred while downloading the video.")
