"""
Bot Initialization and Setup
"""

import asyncio
import logging
from pyrogram import Client, idle, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command
from pyrogram.types import BotCommand
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, MONGO_DB, LOG_GROUP_ID
from core.call_manager import CallManager
from core.userbot import assistant_manager
from database.mongodb import init_db
import handlers

# Configure logging - optimized for performance
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramLogHandler(logging.Handler):
    """Logging handler to send error logs to Telegram log group"""
    def __init__(self, bot_app):
        super().__init__()
        self.bot_app = bot_app
        self.setLevel(logging.ERROR)

    def emit(self, record):
        if not self.bot_app.app or not self.bot_app.app.is_connected:
            return
            
        log_entry = self.format(record)
        asyncio.create_task(self.bot_app.send_error_log(log_entry))


class BotApp:
    """Main Bot Application"""
    
    def __init__(self):
        self.app = None
        self.call_manager = None
        
    async def initialize(self):
        """Initialize bot and all components"""
        logger.info("Initializing Music Bot...")
        
        # Initialize Pyrogram Bot Client (for commands and messages)
        self.app = Client(
            "music_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            sleep_threshold=0,  # No delay for fastest responses
            workers=200,  # Maximum workers for high concurrency
            in_memory=True,  # Faster session storage
            max_concurrent_transmissions=100,  # Faster file transfers
        )
        
        # Initialize Call Manager with user session for voice chats
        self.call_manager = CallManager(self.app, SESSION_STRING)
        
        # Set the global call_manager instance
        from core.call_manager import call_manager as global_call_manager
        import core.call_manager as call_manager_module
        call_manager_module.call_manager = self.call_manager
        
        # Initialize Database
        await init_db(MONGO_DB)
        
        # Add Telegram log handler
        tg_handler = TelegramLogHandler(self)
        tg_handler.setFormatter(logging.Formatter('%(name)s: %(message)s'))
        logging.getLogger().addHandler(tg_handler)
        
        logger.info("Bot initialized successfully!")
    
    async def start_services(self):
        """Start bot and user client"""
        await self.initialize()
        self.setup_handlers()
        
        logger.info("Starting bot...")
        await self.app.start()
        
        # Set bot commands for suggestion
        await self.set_bot_commands()
        
        # Initialize assistant manager (multiple userbots)
        await assistant_manager.start_all()
        
        # Initialize user account for voice chats (legacy support)
        if self.call_manager:
            await self.call_manager.initialize_user_client()
        
        # Send start message to log group
        if LOG_GROUP_ID:
            try:
                bot_mention = self.app.me.mention
                message = (
                    f"{bot_mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ : \n\n"
                    f"ɪᴅ : {self.app.me.id}\n"
                    f"ɴᴀᴍᴇ : {self.app.me.first_name}\n"
                    f"ᴜsᴇʀɴᴀᴍᴇ : @{self.app.me.username}"
                )
                await self.app.send_message(LOG_GROUP_ID, message)
            except Exception as e:
                logger.error(f"Failed to send start message to log group: {e}")
        
        logger.info("Bot is now running!")
        
        # Start auto-restart timer (24 hours = 86400 seconds)
        asyncio.create_task(self.auto_restart_timer())
        
        # Start auto-maintenance timer (24 hours)
        asyncio.create_task(self.auto_maintenance_timer())
        
    async def auto_restart_timer(self):
        """Timer for 24-hour auto-restart"""
        await asyncio.sleep(86400)
        if LOG_GROUP_ID:
            try:
                await self.app.send_message(
                    LOG_GROUP_ID, 
                    "🔄 **24-Hour Scheduled Restart...**\n\n"
                    "The bot is restarting to maintain performance."
                )
            except Exception as e:
                logger.error(f"Failed to send restart message: {e}")
        
        await self.restart()

    async def auto_maintenance_timer(self):
        """Timer for 24-hour auto-maintenance"""
        from handlers.maintenance import clean_bot_data
        while True:
            await asyncio.sleep(86400)
            logger.info("Starting scheduled maintenance...")
            status = await clean_bot_data()
            if status and LOG_GROUP_ID:
                try:
                    await self.app.send_message(
                        LOG_GROUP_ID,
                        "🧹 **Scheduled Maintenance Complete!**\n\n"
                        "Automatically cleared cache and optimized storage."
                    )
                except Exception as e:
                    logger.error(f"Failed to send maintenance message: {e}")

    def setup_handlers(self):
        """Setup all command handlers"""
        logger.info("Setting up handlers...")
        
        # Import and register all handlers
        from handlers.play import play_command
        from handlers.queue import queue_command, clear_queue_command
        from handlers.control import skip_command, pause_command, resume_command, stop_command, volume_command
        from handlers.loop import loop_command
        from handlers.shuffle import shuffle_command
        from handlers.admin import start_command, help_command
        from handlers.callback import help_callback, back_to_start_callback, admin_callback, back_to_help_callback
        from handlers.auth import auth_command, unauth_command, authusers_command
        from handlers.broadcast import broadcast_command, broadcast_callback_handler, broadcast_message_handler
        from handlers.blacklist import blacklistchat_command, whitelistchat_command, blacklistedchat_command
        from handlers.channel import cplay_command, cvplay_command, channelplay_command
        from handlers.gban import gban_command, ungban_command, gbannedusers_command
        from handlers.seek import seek_command, seekback_command
        from handlers.song import song_command, video_command
        from handlers.speed import speed_command, cspeed_command
        from handlers.stats import ping_command, stats_command
        from handlers.maintenance import logs_command, logger_command, maintenance_command
        from handlers.ytsearch import search_command, csearch_command
        from handlers.settings_command import settings_command
        from handlers.new_group import new_group_handler
        from handlers.maintenance import clean_command, restart_command
        from handlers.local_file import get_local_file_handler
        
        # New group handler
        self.app.add_handler(MessageHandler(new_group_handler, filters.new_chat_members))
        
        # Local file handler (for playing Telegram audio/video files)
        self.app.add_handler(get_local_file_handler())
        
        # Maintenance commands
        self.app.add_handler(MessageHandler(clean_command, command("clean")))
        self.app.add_handler(MessageHandler(restart_command, command("restart")))
        
        # Settings command
        self.app.add_handler(MessageHandler(settings_command, command("settings")))
        
        # Register handlers
        self.app.add_handler(MessageHandler(start_command, command("start")))
        self.app.add_handler(MessageHandler(help_command, command("help")))
        self.app.add_handler(MessageHandler(play_command, command("play")))
        self.app.add_handler(MessageHandler(queue_command, command("queue")))
        self.app.add_handler(MessageHandler(clear_queue_command, command("clearqueue")))
        self.app.add_handler(MessageHandler(skip_command, command("skip")))
        self.app.add_handler(MessageHandler(pause_command, command("pause")))
        self.app.add_handler(MessageHandler(resume_command, command("resume")))
        self.app.add_handler(MessageHandler(stop_command, command("stop")))
        self.app.add_handler(MessageHandler(volume_command, command("volume")))
        self.app.add_handler(MessageHandler(loop_command, command("loop")))
        self.app.add_handler(MessageHandler(shuffle_command, command("shuffle")))
        
        # Auth commands
        self.app.add_handler(MessageHandler(auth_command, command("auth")))
        self.app.add_handler(MessageHandler(unauth_command, command("unauth")))
        self.app.add_handler(MessageHandler(authusers_command, command("authusers")))
        
        # Broadcast command
        self.app.add_handler(MessageHandler(broadcast_command, command("broadcast")))
        self.app.add_handler(MessageHandler(broadcast_message_handler, filters.private & ~command(["broadcast"])))
        
        # Blacklist commands
        self.app.add_handler(MessageHandler(blacklistchat_command, command("blacklistchat")))
        self.app.add_handler(MessageHandler(whitelistchat_command, command("whitelistchat")))
        self.app.add_handler(MessageHandler(blacklistedchat_command, command("blacklistedchat")))
        
        # Channel play commands
        self.app.add_handler(MessageHandler(cplay_command, command("cplay")))
        self.app.add_handler(MessageHandler(cvplay_command, command("cvplay")))
        self.app.add_handler(MessageHandler(channelplay_command, command("channelplay")))
        
        # GBAN commands
        self.app.add_handler(MessageHandler(gban_command, command("gban")))
        self.app.add_handler(MessageHandler(ungban_command, command("ungban")))
        self.app.add_handler(MessageHandler(gbannedusers_command, command("gbannedusers")))
        
        # Seek commands
        self.app.add_handler(MessageHandler(seek_command, command("seek")))
        self.app.add_handler(MessageHandler(seekback_command, command("seekback")))
        
        # Song download commands
        self.app.add_handler(MessageHandler(song_command, command("song")))
        self.app.add_handler(MessageHandler(video_command, command("video")))
        
        # Speed commands
        from handlers.speed import speed_command, cspeed_command, playback_command, cplayback_command
        self.app.add_handler(MessageHandler(speed_command, command("speed")))
        self.app.add_handler(MessageHandler(cspeed_command, command("cspeed")))
        self.app.add_handler(MessageHandler(playback_command, command("playback")))
        self.app.add_handler(MessageHandler(cplayback_command, command("cplayback")))
        
        # Ping and stats
        self.app.add_handler(MessageHandler(ping_command, command("ping")))
        self.app.add_handler(MessageHandler(stats_command, command("stats")))
        
        # Maintenance commands
        self.app.add_handler(MessageHandler(logs_command, command("logs")))
        self.app.add_handler(MessageHandler(logger_command, command("logger")))
        self.app.add_handler(MessageHandler(maintenance_command, command("maintenance")))
        
        # Search commands
        self.app.add_handler(MessageHandler(search_command, command("search")))
        self.app.add_handler(MessageHandler(csearch_command, command("csearch")))
        
        # Register callback handlers
        from pyrogram.filters import regex
        from handlers.callback import (
            help_callback, back_to_start_callback, admin_callback, back_to_help_callback,
            auth_callback, gcast_callback, blchat_callback, cplay_callback,
            gban_callback, loop_callback, log_callback, ping_callback,
            play_callback, shuffle_callback, seek_callback, song_callback, speed_callback,
            bl_users_callback, close_playing_callback, queue_list_callback
        )
        from handlers.stats import overall_stats_callback, close_stats_callback
        from handlers.settings import (
            settings_callback, quality_callback, volume_callback,
            videomode_callback, set_mode_callback, update_sub_setting,
            playmode_panel, skipmode_panel, stopmode_panel
        )
        
        self.app.add_handler(CallbackQueryHandler(help_callback, regex("^help_commands$")))
        self.app.add_handler(CallbackQueryHandler(back_to_start_callback, regex("^back_to_start$")))
        self.app.add_handler(CallbackQueryHandler(admin_callback, regex("^cmd_admin$")))
        self.app.add_handler(CallbackQueryHandler(back_to_help_callback, regex("^back_to_help$")))
        self.app.add_handler(CallbackQueryHandler(broadcast_callback_handler, regex("^bc_")))
        
        # Mode settings callbacks
        self.app.add_handler(CallbackQueryHandler(playmode_panel, regex("^set_pm$")))
        self.app.add_handler(CallbackQueryHandler(skipmode_panel, regex("^set_sm$")))
        self.app.add_handler(CallbackQueryHandler(stopmode_panel, regex("^set_st$")))
        self.app.add_handler(CallbackQueryHandler(set_mode_callback, regex("^(toggle_|update_)")))
        
        # Category callback handlers
        self.app.add_handler(CallbackQueryHandler(auth_callback, regex("^cmd_auth$")))
        self.app.add_handler(CallbackQueryHandler(gcast_callback, regex("^cmd_gcast$")))
        self.app.add_handler(CallbackQueryHandler(blchat_callback, regex("^cmd_blchat$")))
        self.app.add_handler(CallbackQueryHandler(bl_users_callback, regex("^bl_user$")))
        self.app.add_handler(CallbackQueryHandler(cplay_callback, regex("^cmd_cplay$")))
        self.app.add_handler(CallbackQueryHandler(gban_callback, regex("^cmd_gban$")))
        self.app.add_handler(CallbackQueryHandler(loop_callback, regex("^cmd_loop$")))
        self.app.add_handler(CallbackQueryHandler(log_callback, regex("^cmd_log$")))
        self.app.add_handler(CallbackQueryHandler(ping_callback, regex("^cmd_ping$")))
        self.app.add_handler(CallbackQueryHandler(play_callback, regex("^cmd_play$")))
        self.app.add_handler(CallbackQueryHandler(shuffle_callback, regex("^cmd_shuffle$")))
        self.app.add_handler(CallbackQueryHandler(seek_callback, regex("^cmd_seek$")))
        self.app.add_handler(CallbackQueryHandler(song_callback, regex("^cmd_song$")))
        self.app.add_handler(CallbackQueryHandler(speed_callback, regex("^cmd_speed$")))
        
        # Playing message callbacks
        self.app.add_handler(CallbackQueryHandler(close_playing_callback, regex("^close_playing$")))
        self.app.add_handler(CallbackQueryHandler(queue_list_callback, regex("^queue_list$")))
        
        # Stats callbacks
        self.app.add_handler(CallbackQueryHandler(overall_stats_callback, regex("^overall_stats$")))
        self.app.add_handler(CallbackQueryHandler(close_stats_callback, regex("^close_stats$")))
        
        # Settings callbacks
        self.app.add_handler(CallbackQueryHandler(settings_callback, regex("^settings_main$")))
        self.app.add_handler(CallbackQueryHandler(quality_callback, regex("^set_quality$")))
        self.app.add_handler(CallbackQueryHandler(volume_callback, regex("^set_volume$")))
        self.app.add_handler(CallbackQueryHandler(videomode_callback, regex("^set_videomode$")))
        self.app.add_handler(CallbackQueryHandler(update_sub_setting, regex("^set_(q|v|vid)_")))
        
        logger.info("Handlers setup complete!")
    
    async def set_bot_commands(self):
        """Set bot commands for Telegram suggestion"""
        try:
            commands = [
                BotCommand("start", "Start the bot"),
                BotCommand("help", "Get help message"),
                BotCommand("settings", "Open bot settings"),
                BotCommand("play", "Play a song from YouTube/URL"),
                BotCommand("fplay", "Play local Telegram audio/video file"),
                BotCommand("skip", "Skip current song"),
                BotCommand("pause", "Pause playback"),
                BotCommand("resume", "Resume playback"),
                BotCommand("stop", "Stop playback"),
                BotCommand("volume", "Set volume"),
                BotCommand("queue", "View queue"),
                BotCommand("clearqueue", "Clear queue"),
                BotCommand("shuffle", "Shuffle queue"),
                BotCommand("loop", "Loop song"),
                BotCommand("ping", "Check bot ping"),
                BotCommand("stats", "Bot statistics"),
                BotCommand("search", "Search YouTube"),
                BotCommand("song", "Download song"),
                BotCommand("video", "Download video"),
                BotCommand("speed", "Set playback speed"),
                BotCommand("seek", "Seek forward"),
                BotCommand("seekback", "Seek backward"),
                BotCommand("auth", "Add auth user"),
                BotCommand("unauth", "Remove auth user"),
                BotCommand("authusers", "List auth users"),
            ]
            
            await self.app.set_bot_commands(commands)
            logger.info("✅ Bot commands set successfully!")
            
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")
    
    async def send_error_log(self, error_msg: str):
        """Send error message to log group"""
        if LOG_GROUP_ID:
            try:
                # Truncate if too long for Telegram
                if len(error_msg) > 4000:
                    error_msg = error_msg[:4000] + "..."
                await self.app.send_message(LOG_GROUP_ID, f"❌ **Error Log:**\n\n`{error_msg}`")
            except Exception as e:
                # Don't use logger.error here as it will cause recursion
                print(f"Failed to send error log to Telegram: {e}")

    async def restart(self):
        """Restart the bot process"""
        import sys
        import os
        logger.info("Restarting bot process...")
        # Give some time for messages to be sent
        await asyncio.sleep(2)
        os.execl(sys.executable, sys.executable, *sys.argv)

    async def run(self):
        """Run the bot"""
        await self.start_services()
        
        # Keep the bot running
        try:
            await idle()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot stopping...")
        finally:
            await self.app.stop()
            
            # Stop all assistants
            await assistant_manager.stop_all()
            
            if self.call_manager and self.call_manager.user_client:
                await self.call_manager.user_client.stop()
            logger.info("Bot stopped.")


# Global bot instance
bot_app = BotApp()
