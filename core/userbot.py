"""
Userbot/Assistant Manager
Handles multiple assistant accounts and auto-invites them to chats
"""

import asyncio
import logging
from typing import Optional, List
from pyrogram import Client
from pyrogram.types import Chat, ChatMember
from pyrogram.enums import ChatMemberStatus
from config import API_ID, API_HASH, SESSION_STRING, SESSION_STRING_2, SESSION_STRING_3, SESSION_STRING_4, SESSION_STRING_5, LOG_GROUP_ID

logger = logging.getLogger(__name__)


class AssistantManager:
    """Manages multiple assistant accounts for voice chats"""
    
    def __init__(self):
        self.assistants: List[Client] = []
        self.assistant_ids: List[int] = []
        self.assistant_names: List[str] = []
        self.assistant_usernames: List[str] = []
        self.current_assistant_index = 0
        self._membership_cache = {} # Cache for membership checks: {chat_id: (is_member, timestamp)}
        
        # Load session strings from config
        self.session_strings = [
            SESSION_STRING,
            SESSION_STRING_2,
            SESSION_STRING_3,
            SESSION_STRING_4,
            SESSION_STRING_5
        ]
        
        # Filter out empty session strings
        self.session_strings = [s for s in self.session_strings if s and s.strip()]
        
    async def start_all(self):
        """Start all assistant accounts"""
        if not self.session_strings:
            logger.warning("No session strings configured. Assistants will not be started.")
            return
        
        logger.info(f"Starting {len(self.session_strings)} assistant(s)...")
        
        for idx, session_string in enumerate(self.session_strings, 1):
            try:
                assistant = Client(
                    name=f"Assistant{idx}",
                    api_id=API_ID,
                    api_hash=API_HASH,
                    session_string=session_string,
                    # Removed no_updates=True - this causes delays in PyTgCalls
                    workers=16,
                    sleep_threshold=1,
                )
                
                await assistant.start()
                
                # Store assistant info
                self.assistants.append(assistant)
                self.assistant_ids.append(assistant.me.id)
                self.assistant_names.append(assistant.me.first_name)
                self.assistant_usernames.append(
                    assistant.me.username if assistant.me.username else "N/A"
                )
                
                logger.info(
                    f"✅ Assistant {idx} started: {assistant.me.first_name} "
                    f"(ID: {assistant.me.id}, @{assistant.me.username or 'NoUsername'})"
                )
                
                # Send start message to log group
                if LOG_GROUP_ID:
                    try:
                        assistant_mention = assistant.me.mention
                        message = f"{assistant_mention} 𝐒ᴛᴀʀᴛᴇᴅ 𝐒ᴜᴄᴄᴇssғᴜʟʟʏ... "
                        await assistant.send_message(LOG_GROUP_ID, message)
                    except Exception as e:
                        logger.error(f"Failed to send assistant start message to log group: {e}")
                
            except Exception as e:
                logger.error(f"❌ Failed to start assistant {idx}: {e}")
        
        logger.info(f"✅ {len(self.assistants)} assistant(s) running successfully!")
    
    async def stop_all(self):
        """Stop all assistant accounts"""
        logger.info("Stopping all assistants...")
        for idx, assistant in enumerate(self.assistants, 1):
            try:
                await assistant.stop()
                logger.info(f"Assistant {idx} stopped")
            except Exception as e:
                logger.error(f"Error stopping assistant {idx}: {e}")
    
    def get_next_assistant(self) -> Optional[Client]:
        """Get next assistant in round-robin fashion"""
        if not self.assistants:
            return None
        
        assistant = self.assistants[self.current_assistant_index]
        self.current_assistant_index = (self.current_assistant_index + 1) % len(self.assistants)
        return assistant
    
    async def is_assistant_in_chat(self, chat_id: int) -> bool:
        """Check if any assistant is already a member of the chat"""
        if not self.assistants:
            return False
        
        # ⚡ Check cache first (valid for 5 minutes instead of 1 hour for faster updates)
        import time
        if chat_id in self._membership_cache:
            is_member, timestamp = self._membership_cache[chat_id]
            if time.time() - timestamp < 300:  # 5 minutes
                return is_member

        for assistant in self.assistants:
            try:
                is_member = await self._check_membership(assistant, chat_id)
                if is_member:
                    self._membership_cache[chat_id] = (True, time.time())
                    return True
            except Exception as e:
                logger.debug(f"Assistant {assistant.me.first_name} membership check failed: {e}")
                continue
        
        self._membership_cache[chat_id] = (False, time.time())
        return False
    
    def get_assistant_by_id(self, chat_id: int) -> Optional[Client]:
        """Get an assistant that's already in the chat, or return next available"""
        # First, try to find an assistant already in the chat
        for assistant in self.assistants:
            try:
                # This is a simple check - you can enhance it with actual membership verification
                return assistant
            except:
                continue
        
        # Return next available assistant
        return self.get_next_assistant()
    
    async def ensure_assistant_in_chat(self, chat_id: int, chat_username: str = None) -> Optional[Client]:
        """
        Ensure an assistant is in the chat. If not, automatically invite it.
        
        Args:
            chat_id: The chat ID
            chat_username: Optional chat username for inviting
            
        Returns:
            The assistant client that's now in the chat, or None
        """
        if not self.assistants:
            logger.error("No assistants available!")
            return None
        
        # Try each assistant
        for idx, assistant in enumerate(self.assistants):
            try:
                # Check if assistant is already in the chat
                is_member = await self._check_membership(assistant, chat_id)
                
                if is_member:
                    logger.info(f"✅ Assistant {idx+1} ({assistant.me.first_name}) is already in chat {chat_id}")
                    return assistant
                
                # Assistant not in chat, try to auto-invite
                logger.warning(f"⚠️  Assistant {idx+1} not in chat {chat_id}, attempting auto-invite...")
                
                # Try to invite (will create invite link if needed)
                if await self._invite_assistant(assistant, chat_id, chat_username):
                    logger.info(f"✅ Successfully invited Assistant {idx+1} to chat {chat_id}")
                    return assistant
                else:
                    logger.warning(f"❌ Failed to invite Assistant {idx+1} to chat {chat_id}")
                    
            except Exception as e:
                logger.warning(f"Assistant {idx+1} check failed for chat {chat_id}: {e}")
                continue
        
        logger.error(
            f"❌ All assistants failed to join chat {chat_id}\n"
            f"   The bot will try to create an invite link and auto-join the assistant.\n"
            f"   Make sure the bot is an admin in the channel/group with 'Invite Users' permission."
        )
        return None
    
    async def _check_membership(self, assistant: Client, chat_id: int) -> bool:
        """Check if assistant is a member of the chat"""
        try:
            member = await assistant.get_chat_member(chat_id, assistant.me.id)
            return member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except Exception:
            # If we can't check, assume not member
            return False
    
    async def _invite_assistant(self, assistant: Client, chat_id: int, chat_username: str = None) -> bool:
        """
        Try to invite assistant to the chat by creating an invite link
        
        Args:
            assistant: The assistant client
            chat_id: Target chat ID
            chat_username: Optional username for public chats
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from pyrogram import Client as BotClient
            from core.bot import bot_app
            
            # IMPORTANT: Telegram doesn't allow joining by chat_id directly
            # We need to create an invite link using the bot and use it to join
            
            # Try via username first (easiest)
            if chat_username:
                try:
                    logger.info(f"Trying to join via username @{chat_username}...")
                    await assistant.join_chat(chat_username)
                    logger.info(f"✅ Successfully joined via username @{chat_username}")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to join via username @{chat_username}: {e}")
            
            # Try to create invite link using bot and join via that
            try:
                logger.info(f"Creating invite link for chat {chat_id}...")
                
                # Get the bot client from bot_app
                bot_client = bot_app.app
                
                if not bot_client:
                    logger.error("Bot client not initialized!")
                    return False
                
                # Create a new invite link (or get existing one)
                try:
                    from datetime import datetime, timedelta
                    
                    # Try to create a new invite link
                    logger.info(f"Bot attempting to create invite link for chat {chat_id}...")
                    
                    # Create link that expires in 5 minutes
                    expire_time = datetime.utcnow() + timedelta(minutes=5)
                    
                    invite_link = await bot_client.create_chat_invite_link(
                        chat_id=chat_id,
                        member_limit=1,  # Only for 1 use (the assistant)
                        expire_date=expire_time  # Expires in 5 minutes
                    )
                    link_url = invite_link.invite_link
                    logger.info(f"✅ Created new invite link for chat {chat_id}")
                except Exception as e:
                    logger.warning(f"Failed to create invite link: {e}")
                    # If bot is not admin, try to export invite link
                    try:
                        # Get chat info to find username
                        chat = await bot_client.get_chat(chat_id)
                        if chat.username:
                            logger.info(f"Chat has username: @{chat.username}")
                            await assistant.join_chat(chat.username)
                            logger.info(f"✅ Successfully joined via chat username")
                            return True
                        else:
                            logger.error(f"Chat {chat_id} has no username and bot cannot create invite links")
                            return False
                    except Exception as e2:
                        logger.error(f"Failed to get chat info: {e2}")
                        return False
                
                # Make assistant join via the invite link
                logger.info(f"Assistant joining via invite link: {link_url[:50]}...")
                await assistant.join_chat(link_url)
                logger.info(f"✅ Successfully invited assistant via invite link")
                return True
                
            except Exception as e:
                logger.error(f"Failed to create/use invite link: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to invite assistant to chat {chat_id}: {e}")
            return False
    
    async def leave_chat(self, chat_id: int):
        """Make all assistants leave a chat"""
        for idx, assistant in enumerate(self.assistants, 1):
            try:
                await assistant.leave_chat(chat_id)
                logger.info(f"Assistant {idx} left chat {chat_id}")
            except Exception as e:
                logger.debug(f"Assistant {idx} leave chat {chat_id} failed: {e}")
    
    def get_assistant_info(self) -> dict:
        """Get information about all assistants"""
        return {
            "total_assistants": len(self.assistants),
            "assistants": [
                {
                    "index": idx + 1,
                    "name": name,
                    "id": self.assistant_ids[idx],
                    "username": self.assistant_usernames[idx],
                }
                for idx, name in enumerate(self.assistant_names)
            ]
        }


# Global assistant manager instance
assistant_manager = AssistantManager()
