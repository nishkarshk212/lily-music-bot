"""
MongoDB Database Layer
Handles persistent storage for bot settings
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Global database client
db_client: Optional[AsyncIOMotorClient] = None
db = None


async def init_db(mongo_uri: str, db_name: str = "music_bot"):
    """Initialize MongoDB connection"""
    global db_client, db
    
    try:
        import ssl
        # Create SSL context that's compatible with MongoDB Atlas
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Clean up URI - remove existing TLS params
        if "mongodb+srv://" in mongo_uri:
            if "?" in mongo_uri:
                base_uri = mongo_uri.split("?")[0]
                params = mongo_uri.split("?")[1]
                # Remove tls-related params to avoid conflicts
                params = "&".join([p for p in params.split("&") if not p.lower().startswith("tls")])
                mongo_uri = f"{base_uri}?{params}" if params else base_uri
        
        db_client = AsyncIOMotorClient(
            mongo_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=10000
        )
        db = db_client[db_name]
        
        # Test connection
        await db_client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        logger.warning("Bot will run without database persistence")
        db = None


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.settings_collection = None
        self.queue_collection = None
        self.user_collection = None
        self.auth_collection = None
        self.gban_collection = None
        self.blacklist_collection = None
        
        if db is not None:
            self.settings_collection = db['chat_settings']
            self.queue_collection = db['active_queues']
            self.user_collection = db['users']
            self.auth_collection = db['auth_users']
            self.gban_collection = db['gban_users']
            self.blacklist_collection = db['blacklisted_chats']
    
    async def get_chat_settings(self, chat_id: int) -> Dict:
        """Get settings for a chat"""
        if not self.settings_collection:
            return {}
        
        try:
            settings = await self.settings_collection.find_one({"chat_id": chat_id})
            return settings or {}
        except Exception as e:
            logger.error(f"Failed to get chat settings: {e}")
            return {}
    
    async def save_chat_settings(self, chat_id: int, settings: Dict):
        """Save settings for a chat"""
        if not self.settings_collection:
            return
        
        try:
            await self.settings_collection.update_one(
                {"chat_id": chat_id},
                {"$set": settings},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to save chat settings: {e}")
    
    async def get_loop_setting(self, chat_id: int) -> int:
        """Get loop count for a chat"""
        settings = await self.get_chat_settings(chat_id)
        return settings.get("loop_count", 0)
    
    async def set_loop_setting(self, chat_id: int, loop_count: int):
        """Set loop count for a chat"""
        await self.save_chat_settings(chat_id, {"loop_count": loop_count})
    
    async def get_volume_setting(self, chat_id: int) -> int:
        """Get volume for a chat"""
        settings = await self.get_chat_settings(chat_id)
        return settings.get("volume", 100)
    
    async def set_volume_setting(self, chat_id: int, volume: int):
        """Set volume for a chat"""
        await self.save_chat_settings(chat_id, {"volume": volume})
    
    async def save_queue(self, chat_id: int, queue_data: Dict):
        """Save queue state"""
        if not self.queue_collection:
            return
        
        try:
            await self.queue_collection.update_one(
                {"chat_id": chat_id},
                {"$set": queue_data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to save queue: {e}")
    
    async def get_queue(self, chat_id: int) -> Optional[Dict]:
        """Get queue state"""
        if not self.queue_collection:
            return None
        
        try:
            return await self.queue_collection.find_one({"chat_id": chat_id})
        except Exception as e:
            logger.error(f"Failed to get queue: {e}")
            return None
    
    async def delete_queue(self, chat_id: int):
        """Delete queue state"""
        if not self.queue_collection:
            return
        
        try:
            await self.queue_collection.delete_one({"chat_id": chat_id})
        except Exception as e:
            logger.error(f"Failed to delete queue: {e}")
    
    async def add_user(self, user_id: int, username: str = ""):
        """Add or update user in database"""
        if not self.user_collection:
            return
        
        try:
            await self.user_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "username": username,
                        "last_active": None  # You can add timestamp here
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to add user: {e}")
    
    async def get_user_count(self) -> int:
        """Get total user count"""
        if not self.user_collection:
            return 0
        
        try:
            return await self.user_collection.count_documents({})
        except Exception as e:
            logger.error(f"Failed to get user count: {e}")
            return 0
    
    async def get_chat_count(self) -> int:
        """Get total chat count"""
        if not self.settings_collection:
            return 0
        
        try:
            return await self.settings_collection.count_documents({})
        except Exception as e:
            logger.error(f"Failed to get chat count: {e}")
            return 0
    
    async def get_all_chats(self) -> list:
        """Get all chats"""
        if not self.settings_collection:
            return []
        
        try:
            chats = []
            cursor = self.settings_collection.find({})
            async for chat in cursor:
                chats.append(chat)
            return chats
        except Exception as e:
            logger.error(f"Failed to get all chats: {e}")
            return []
    
    # Auth User Methods
    async def add_auth_user(self, chat_id: int, user_id: int, user_name: str):
        """Add user to auth list"""
        if not self.auth_collection:
            return
        
        try:
            await self.auth_collection.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {"name": user_name}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to add auth user: {e}")
    
    async def remove_auth_user(self, chat_id: int, user_id: int):
        """Remove user from auth list"""
        if not self.auth_collection:
            return
        
        try:
            await self.auth_collection.delete_one(
                {"chat_id": chat_id, "user_id": user_id}
            )
        except Exception as e:
            logger.error(f"Failed to remove auth user: {e}")
    
    async def get_auth_users(self, chat_id: int) -> list:
        """Get auth users for a chat"""
        if not self.auth_collection:
            return []
        
        try:
            users = []
            cursor = self.auth_collection.find({"chat_id": chat_id})
            async for user in cursor:
                users.append({"id": user["user_id"], "name": user["name"]})
            return users
        except Exception as e:
            logger.error(f"Failed to get auth users: {e}")
            return []
    
    async def is_auth_user(self, chat_id: int, user_id: int) -> bool:
        """Check if user is auth user"""
        if not self.auth_collection:
            return False
        
        try:
            count = await self.auth_collection.count_documents(
                {"chat_id": chat_id, "user_id": user_id}
            )
            return count > 0
        except Exception as e:
            logger.error(f"Failed to check auth user: {e}")
            return False
    
    # GBAN Methods
    async def gban_user(self, user_id: int, user_name: str, admin_id: int):
        """Globally ban a user"""
        if not self.gban_collection:
            return
        
        try:
            await self.gban_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "name": user_name,
                        "banned_by": admin_id,
                        "reason": "No reason provided"
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to gban user: {e}")
    
    async def ungban_user(self, user_id: int):
        """Remove user from GBAN list"""
        if not self.gban_collection:
            return
        
        try:
            await self.gban_collection.delete_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Failed to ungban user: {e}")
    
    async def is_gbanned(self, user_id: int) -> bool:
        """Check if user is globally banned"""
        if not self.gban_collection:
            return False
        
        try:
            count = await self.gban_collection.count_documents({"user_id": user_id})
            return count > 0
        except Exception as e:
            logger.error(f"Failed to check gban: {e}")
            return False
    
    async def get_gbanned_users(self) -> list:
        """Get all globally banned users"""
        if not self.gban_collection:
            return []
        
        try:
            users = []
            cursor = self.gban_collection.find({})
            async for user in cursor:
                users.append({"id": user["user_id"], "name": user["name"]})
            return users
        except Exception as e:
            logger.error(f"Failed to get gbanned users: {e}")
            return []
    
    # Blacklist Methods
    async def blacklist_chat(self, chat_id: int):
        """Blacklist a chat"""
        if not self.blacklist_collection:
            return
        
        try:
            await self.blacklist_collection.update_one(
                {"chat_id": chat_id},
                {"$set": {"chat_id": chat_id}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to blacklist chat: {e}")
    
    async def whitelist_chat(self, chat_id: int):
        """Remove chat from blacklist"""
        if not self.blacklist_collection:
            return
        
        try:
            await self.blacklist_collection.delete_one({"chat_id": chat_id})
        except Exception as e:
            logger.error(f"Failed to whitelist chat: {e}")
    
    async def is_blacklisted(self, chat_id: int) -> bool:
        """Check if chat is blacklisted"""
        if not self.blacklist_collection:
            return False
        
        try:
            count = await self.blacklist_collection.count_documents({"chat_id": chat_id})
            return count > 0
        except Exception as e:
            logger.error(f"Failed to check blacklist: {e}")
            return False
    
    async def get_blacklisted_chats(self) -> list:
        """Get all blacklisted chats"""
        if not self.blacklist_collection:
            return []
        
        try:
            chats = []
            cursor = self.blacklist_collection.find({})
            async for chat in cursor:
                chats.append(chat)
            return chats
        except Exception as e:
            logger.error(f"Failed to get blacklisted chats: {e}")
            return []
    
    # Channel Play Methods
    async def set_channel_play(self, chat_id: int, channel_id: int):
        """Set channel for a chat"""
        await self.save_chat_settings(chat_id, {"channel_id": channel_id})
    
    async def get_channel_play(self, chat_id: int) -> int:
        """Get channel for a chat"""
        settings = await self.get_chat_settings(chat_id)
        return settings.get("channel_id")
    
    # General Settings Methods
    async def set_setting(self, key: str, value):
        """Set a general setting"""
        if not self.settings_collection:
            return
        
        try:
            await self.settings_collection.update_one(
                {"key": key},
                {"$set": {"value": value}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to set setting: {e}")
    
    async def get_setting(self, key: str, default=None):
        """Get a general setting"""
        if not self.settings_collection:
            return default
        
        try:
            setting = await self.settings_collection.find_one({"key": key})
            return setting["value"] if setting else default
        except Exception as e:
            logger.error(f"Failed to get setting: {e}")
            return default


# Global database manager instance
db_manager = DatabaseManager()
