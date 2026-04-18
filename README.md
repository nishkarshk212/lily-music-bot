# 🎵 Telegram Music Bot

A full-featured Telegram music bot that plays songs in voice chats with support for queue management, loop, shuffle, and more!

## ✨ Features

- 🎶 **Play Music** - Play songs from YouTube via URL or search query
- 📋 **Queue System** - Add, view, and manage song queues
- ⏭️ **Playback Controls** - Skip, pause, resume, and stop playback
- 🔁 **Loop Mode** - Loop current song multiple times
- 🔀 **Shuffle** - Shuffle the queue for random playback
- 🔊 **Volume Control** - Adjust volume from 1-200%
- 🖼️ **Thumbnail Generation** - Beautiful custom thumbnails with song info
- 👥 **Multi-Chat Support** - Run in multiple groups simultaneously
- 💾 **Persistent Settings** - MongoDB integration for settings storage
- 👑 **Admin Controls** - Admin-only commands for better management

## 📋 Prerequisites

Before running the bot, ensure you have:

1. **Python 3.8+** installed
2. **FFmpeg** installed (required for audio processing)
3. **MongoDB** (optional, for persistent settings)
4. A **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
cd /Users/nishkarshkr/Desktop/BOT
```

### Step 2: Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Generate Session String

**IMPORTANT:** You must generate a session string before running the bot!

```bash
python session_generator.py
```

This will:
1. Ask for your phone number
2. Send a verification code to your Telegram account
3. Generate a session string
4. Copy the session string

### Step 5: Configure the Bot

Edit `config.py` and paste your session string:

```python
SESSION_STRING = "your_session_string_here"
```

Optionally configure:
- `OWNER_ID` - Your Telegram user ID
- `SUDOERS` - Additional admin user IDs
- `MONGO_DB` - MongoDB connection string (optional)

### Step 6: Run the Bot

```bash
python main.py
```

## 📖 Usage

### Basic Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/help` | Show detailed help and command list |
| `/play <song>` | Play a song (search or URL) |
| `/queue` | View current queue |
| `/skip` | Skip current song |
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/stop` | Stop and clear queue |
| `/volume <1-200>` | Set volume level |
| `/loop <count>` | Loop current song |
| `/shuffle` | Shuffle the queue |
| `/clearqueue` | Clear the entire queue |

### Examples

```bash
# Play by search
/play Despacito

# Play by URL
/play https://www.youtube.com/watch?v=kJQP7kiw5Fk

# Set volume to 150%
/volume 150

# Loop song 3 times
/loop 3

# Disable loop
/loop off
```

## ⚙️ Configuration

### config.py

```python
# Required
BOT_TOKEN = "your_bot_token"
API_ID = 123456
API_HASH = "your_api_hash"
SESSION_STRING = "your_session_string"

# Optional
MONGO_DB = "mongodb://localhost:27017"
OWNER_ID = [your_user_id]
SUDOERS = [admin_user_ids]
MAX_DURATION = 3600  # Max song duration (seconds)
MAX_QUEUE_SIZE = 50  # Max songs in queue
DEFAULT_VOLUME = 100  # Default volume (1-200)
```

## 🗄️ Database Setup (Optional)

### Using MongoDB Atlas (Free)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get your connection string
4. Update `MONGO_DB` in config.py

### Using Local MongoDB

```bash
# Install MongoDB (macOS)
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Default connection
MONGO_DB = "mongodb://localhost:27017"
```

## 🏗️ Project Structure

```
BOT/
├── config.py                    # Configuration file
├── requirements.txt             # Python dependencies
├── session_generator.py         # Session string generator
├── main.py                      # Bot entry point
├── core/
│   ├── bot.py                   # Bot initialization
│   ├── call_manager.py          # Voice chat management
│   └── queue.py                 # Queue system
├── handlers/
│   ├── admin.py                 # Start/Help commands
│   ├── play.py                  # Play command
│   ├── queue.py                 # Queue commands
│   ├── control.py               # Playback controls
│   ├── loop.py                  # Loop command
│   └── shuffle.py               # Shuffle command
├── utils/
│   ├── thumbnail.py             # Thumbnail generator
│   ├── downloader.py            # YouTube downloader
│   ├── formatter.py             # Text formatters
│   └── decorators.py            # Custom decorators
├── database/
│   └── mongodb.py               # MongoDB integration
├── assets/                      # Thumbnails and assets
└── downloads/                   # Downloaded songs
```

## 🔧 Troubleshooting

### Common Issues

**1. "SESSION_STRING is not set" error**
- Run `python session_generator.py` to generate a session string
- Paste it in `config.py`

**2. "FFmpeg not found" error**
- Install FFmpeg (see Installation step 2)
- Ensure it's in your system PATH

**3. Bot doesn't join voice chat**
- Make sure bot is admin in the group
- Give bot permission to manage voice chats
- Start a voice chat in the group first

**4. Songs not downloading**
- Check your internet connection
- yt-dlp may need updating: `pip install --upgrade yt-dlp`

**5. MongoDB connection error**
- Bot will run without database (settings won't persist)
- Install MongoDB or use MongoDB Atlas

### Logs

Check `bot.log` file for detailed logs and error messages.

## 📝 Notes

- Bot must be **admin** in groups with voice chat permissions
- Maximum song duration: **1 hour** (configurable)
- Maximum queue size: **50 songs** (configurable)
- Supports **YouTube** URLs and search queries
- Volume range: **1-200%**
- Session string is **sensitive** - keep it secret!

## 🔄 Updates

To update the bot:

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart bot
python main.py
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is open-source and available under the MIT License.

## 🆘 Support

If you need help:
1. Check the `/help` command in bot
2. Review this README
3. Check `bot.log` for errors
4. Contact the bot owner

## ⚠️ Disclaimer

- This bot is for **educational purposes** only
- Respect **copyright laws** in your country
- Don't use this bot to violate YouTube's Terms of Service
- You are responsible for how you use this bot

---

**Made with ❤️ for the Telegram community**

Enjoy your music! 🎶
# lily-music-bot
