"""
Loop Command Handler
Handles /loop command for looping songs
"""

from pyrogram import Client
from pyrogram.types import Message
from core.queue import queue_manager
from core.call_manager import call_manager
import logging

logger = logging.getLogger(__name__)


async def loop_command(client: Client, message: Message):
    """Handle /loop command"""
    try:
        chat_id = message.chat.id
        queue = queue_manager.get_queue(chat_id)
        
        # Check if bot is playing
        if not call_manager or not call_manager.is_playing(chat_id):
            await message.reply_text("❌ No song is currently playing!")
            return
        
        # Check if loop parameter is provided
        if len(message.command) < 2:
            # Show current loop status
            if queue.loop_count > 0:
                await message.reply_text(
                    f"<blockquote>"
                    f"<b>🔁 ʟσσᴘ ɪꜱ єηᴧʙʟєᴅ! ❞</b>\n\n"
                    f"Current song will loop <b>{queue.loop_count}</b> more times.\n\n"
                    "<b>Usage:</b>\n"
                    "• /loop &lt;number&gt; - Set loop count\n"
                    "• /loop off - Disable loop"
                    f"</blockquote>",
                    parse_mode="HTML"
                )
            else:
                await message.reply_text(
                    f"<blockquote>"
                    f"<b>🔁 ʟσσᴘ ɪꜱ ᴅɪꜱᴧʙʟєᴅ ❞</b>\n\n"
                    "<b>Usage:</b>\n"
                    "• /loop &lt;number&gt; - Loop current song N times\n"
                    "• /loop off - Disable loop\n\n"
                    "<b>Example:</b> /loop 3 will play the song 4 times total"
                    f"</blockquote>",
                    parse_mode="HTML"
                )
            return
        
        # Parse loop parameter
        loop_param = message.command[1].lower()
        
        if loop_param in ["off", "0", "disable"]:
            # Disable loop
            queue.loop_count = 0
            queue.loop_queue = False
            
            await message.reply_text(
                f"<blockquote>"
                f"<b>🔁 ʟσσᴘ ᴅɪꜱᴧʙʟєᴅ! ❞</b>\n\n"
                f"Song will play normally."
                f"</blockquote>",
                parse_mode="HTML"
            )
            
            logger.info(f"Loop disabled by {message.from_user.id} in {chat_id}")
            
        else:
            try:
                loop_count = int(loop_param)
                
                if loop_count < 1 or loop_count > 50:
                    await message.reply_text(
                        "❌ Loop count must be between 1 and 50!"
                    )
                    return
                
                # Set loop count
                queue.loop_count = loop_count
                queue.loop_queue = False
                
                await message.reply_text(
                    f"<blockquote>"
                    f"<b>🔁 ʟσσᴘ єηᴧʙʟєᴅ! ❞</b>\n\n"
                    f"Current song will loop <b>{loop_count}</b> times.\n"
                    f"Total plays: <b>{loop_count + 1}</b> (including current)"
                    f"</blockquote>",
                    parse_mode="HTML"
                )
                
                logger.info(f"Loop set to {loop_count} by {message.from_user.id} in {chat_id}")
                
            except ValueError:
                await message.reply_text(
                    "❌ Invalid loop count! Please provide a number.\n\n"
                    "**Example:** `/loop 3`"
                )
                return
        
    except Exception as e:
        logger.error(f"Loop command error: {e}")
        await message.reply_text("❌ Failed to set loop. Please try again.")
