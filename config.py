"""
Configuration file for Telegram Music Bot
Fill in the required values before running the bot
"""

# Bot Configuration
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8740501995:AAHKfFEddEEGx-2O5GWWEMkiPx7Qq3xJRvM")
API_ID = int(os.getenv("API_ID", "38269682"))
API_HASH = os.getenv("API_HASH", "822b916e4b3c1f9690e6aa3a8c0fbc8f")

# IMPORTANT: Run session_generator.py first to get your session string
SESSION_STRING = os.getenv("SESSION_STRING", "")  # Paste your session string here
SESSION_STRING_2 = os.getenv("SESSION_STRING_2", "")  # Optional: Second assistant
SESSION_STRING_3 = os.getenv("SESSION_STRING_3", "")  # Optional: Third assistant
SESSION_STRING_4 = os.getenv("SESSION_STRING_4", "")  # Optional: Fourth assistant
SESSION_STRING_5 = os.getenv("SESSION_STRING_5", "")  # Optional: Fifth assistant

# MongoDB Configuration
# Use MongoDB Atlas (free) or local MongoDB
MONGO_DB = os.getenv("MONGO_DB", "mongodb+srv://music_22:Nishkarsh123@music.lvdeg6f.mongodb.net/?appName=MUSIC")
MONGO_DB_NAME = "music_bot"

# Owner and Admin Configuration
# Add your Telegram user ID(s) here
# OWNER_ID can be set in .env as comma-separated values: OWNER_ID=8791884726
OWNER_ID_ENV = os.getenv("OWNER_ID", "")
OWNER_ID = [int(x.strip()) for x in OWNER_ID_ENV.split(",") if x.strip()] if OWNER_ID_ENV else [8791884726]  # Default owner
SUDOERS = []  # Example: [123456789, 987654321]

# API Configuration
API_KEY = os.getenv("API_KEY", "NxGBNexGenBots53fc88")
NEXGENBOTS_API = os.getenv("NEXGENBOTS_API", "https://pvtz.nexgenbots.xyz")
VIDEO_API_URL = os.getenv("VIDEO_API_URL", "https://pvtz.nexgenbots.xyz")

# Download Settings
DOWNLOAD_DIR = "downloads"
MAX_DURATION = 3600  # Maximum song duration in seconds (1 hour)
MAX_QUEUE_SIZE = 50  # Maximum songs in queue

# Voice Chat Settings
DEFAULT_VOLUME = 100  # Default volume (1-200)

# Logging
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID", "@music_24345")
# Try to convert to int if it's a numeric ID, otherwise keep as string (username)
try:
    if LOG_GROUP_ID and not LOG_GROUP_ID.startswith("@"):
        LOG_GROUP_ID = int(LOG_GROUP_ID)
except ValueError:
    pass
LOG_CHANNEL = None  # Log channel username (optional)
