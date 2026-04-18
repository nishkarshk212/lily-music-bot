"""
Shuffle Command Handler
Handles /shuffle command for shuffling the queue
"""

from pyrogram import Client
from pyrogram.types import Message
from core.queue import queue_manager
from core.call_manager import call_manager
from utils.decorators import admin_check
import logging

logger = logging.getLogger(__name__)


@admin_check
async def shuffle_command(client: Client, message: Message):
    """Handle /shuffle command"""
    try:
        chat_id = message.chat.id
        queue = queue_manager.get_queue(chat_id)
        
        # Check if there are songs in queue
        if queue.size() < 2:
            await message.reply_text(
                "❌ Need at least 2 songs in queue to shuffle!\n\n"
                f"Current queue size: {queue.size()}"
            )
            return
        
        # Get queue before shuffle
        queue_before = queue.get_queue()
        
        # Shuffle the queue
        queue.shuffle_queue()
        
        # Get queue after shuffle
        queue_after = queue.get_queue()
        
        await message.reply_text(
            f"🔀 **Queue Shuffled!**\n\n"
            f"📊 **Total songs:** {queue.size()}\n\n"
            f"**Next 3 songs:**\n"
            f"1. {queue_after[0].title[:40]}\n"
            f"2. {queue_after[1].title[:40]}\n"
            f"{'3. ' + queue_after[2].title[:40] if len(queue_after) > 2 else ''}"
        )
        
        logger.info(f"Queue shuffled by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Shuffle command error: {e}")
        await message.reply_text("❌ Failed to shuffle queue. Please try again.")
