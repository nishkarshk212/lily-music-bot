"""
YouTube Search Handler using NexGen API
Handles /search command to find songs
"""

import logging
import aiohttp
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from utils.decorators import admin_check

logger = logging.getLogger(__name__)

# NexGen API configuration
import os
NEXGEN_API_URL = os.getenv("NEXGENBOTS_API", "https://pvtz.nexgenbots.xyz")
API_KEY = os.getenv("API_KEY")


async def search_youtube(query: str) -> list:
    """
    Search YouTube using yt-dlp
    
    Args:
        query: Search query
        
    Returns:
        List of search results
    """
    try:
        import yt_dlp
        import asyncio
        
        search_url = f"ytsearch5:{query}"
        
        loop = asyncio.get_event_loop()
        
        def _search():
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'format': 'bestaudio/best',
                'default_search': 'ytsearch',
                'ignoreerrors': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(search_url, download=False)
        
        info = await loop.run_in_executor(None, _search)
        
        if not info or 'entries' not in info or not info['entries']:
            return []
        
        results = []
        for entry in info['entries']:
            results.append({
                "title": entry.get("title", "Unknown"),
                "duration": format_duration(entry.get("duration", 0)),
                "views": format_views(entry.get("view_count", 0)),
                "channel": entry.get("channel", entry.get("uploader", "Unknown")),
                "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                "thumbnail": entry.get("thumbnail", "")
            })
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        return []


def format_duration(seconds: int) -> str:
    """Format duration from seconds to MM:SS or HH:MM:SS"""
    if not seconds:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def format_views(count: int) -> str:
    """Format view count"""
    if not count:
        return "0"
    
    if count >= 1000000000:
        return f"{count / 1000000000:.1f}B"
    elif count >= 1000000:
        return f"{count / 1000000:.1f}M"
    elif count >= 1000:
        return f"{count / 1000:.1f}K"
    else:
        return str(count)



@admin_check
async def search_command(client: Client, message: Message):
    """Handle /search command - Search for songs on YouTube"""
    try:
        # Send typing action
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Check if query is provided
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide a search query.\n\n"
                "**Usage:** `/search <song name>`\n"
                "**Example:** `/shape of you`"
            )
            return
        
        # Get search query
        query = message.text.split(None, 1)[1]
        
        # Send searching message
        searching_msg = await message.reply_text(f"🔍 **Searching for:** `{query}`")
        
        # Search using yt-dlp
        results = await search_youtube(query)
        
        # Check if we got any results
        if not results:
            await searching_msg.edit_text(
                f"❌ No results found for: `{query}`\n\n"
                "Try a different search term."
            )
            return
        
        # Format results
        text = f"🔍 **Search Results for:** `{query}`\n\n"
        
        for i, result in enumerate(results[:5], 1):
            title = result.get("title", "Unknown")
            duration = result.get("duration", "Unknown")
            views = result.get("views", "Unknown")
            channel = result.get("channel", "Unknown")
            url = result.get("url", "")
            
            text += f"**{i}. {title}**\n"
            text += f"   ⏱ Duration: {duration}\n"
            text += f"   👁 Views: {views}\n"
            text += f"   📺 Channel: {channel}\n"
            text += f"   🔗 [Watch on YouTube]({url})\n\n"
        
        text += f"**Use /play to play any of these songs!**"
        
        # Edit the searching message with results
        await searching_msg.edit_text(
            text,
            disable_web_page_preview=True
        )
        
        logger.info(f"✅ Search completed for: {query}")
        
    except Exception as e:
        logger.error(f"❌ Search command error: {e}", exc_info=True)
        await message.reply_text(
            "❌ An error occurred while searching. Please try again."
        )


@admin_check
async def csearch_command(client: Client, message: Message):
    """Handle /csearch command - Search for songs (channel version)"""
    # Same as search command, can be used for channel play
    await search_command(client, message)
