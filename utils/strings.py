"""
String constants for bot messages
All user-facing messages are stored here for easy customization
"""

# Owner Configuration
OWNER_ID = 8791884726

# Support Channel Configuration
SUPPORT_CHANNEL_USERNAME = "Tele_212_bots"
SUPPORT_CHANNEL_ID = -1003713225825

# Start Message
START_MESSAGE = """
╭───────────────────▣
│❍ ʜᴇʏ {user_mention}
│❍ ɪ ᴀᴍ {bot_mention}
├───────────────────▣
│❍ ʙᴇsᴛ ǫᴜɪʟɪᴛʏ ғᴇᴀᴛᴜʀᴇs •
│❍ ᴘᴏᴡᴇʀᴇᴅ ʙʏ...{support_mention}
╰───────────────────▣
"""

# Help Message
HELP_MESSAGE = """
╭───────────────────▣
│❍ **Music Bot - Command List**
├───────────────────▣
│
│🎶 **Basic Commands:**
│❍ /play <song name or URL> - Play a song
│❍ /play <reply to message> - Play from replied message
│
│📋 **Queue Commands:**
│❍ /queue - View current queue
│❍ /clearqueue - Clear the entire queue
│
│⏯️ **Playback Control:**
│❍ /skip - Skip current song
│❍ /pause - Pause playback
│❍ /resume - Resume playback
│❍ /stop - Stop playback and clear queue
│
│🔧 **Advanced Features:**
│❍ /volume <1-200> - Adjust volume
│❍ /loop <count> - Loop current song
│❍ /shuffle - Shuffle the queue
│
╰───────────────────▣
"""

# Now Playing Message (HTML format)
def build_playing_message(title, title_url, duration, requester, bot_name="Music Bot"):
    # Truncate title if too long for a cleaner look
    if len(title) > 25:
        title = title[:22] + "..."
    
    # Create clickable song title
    song_mention = f'<a href="{title_url}">{title}</a>' if title_url else title
    
    # Styled with dual blockquotes: one for header, one for details
    # Added \n between blockquotes to ensure they appear on separate lines
    return (
        "<blockquote><b>❖  𝛅ᴛᴧʀᴛєᴅ  𝛅ᴛʀєᴧϻɪηɢ</b></blockquote>"
        "\n"
        "<blockquote>"
        f"<b>❍ тɪᴛʟє :</b> {song_mention}\n"
        f"<b>❍ ᴅᴜʀᴧᴛɪση :</b> {duration} <b>ϻɪηᴜᴛєs</b>\n"
        f"<b>❍ ʙʏ :</b> {requester}"
        "</blockquote>"
    )

# For backward compatibility
NOW_PLAYING_MESSAGE = build_playing_message("{title}", "{url}", "{duration}", "{requester}")

# Queue Message
QUEUE_MESSAGE = """
❖ **ᴄᴜʀʀᴇɴᴛ ǫᴜᴇᴜᴇ** ↗

⦿ **ɴᴏᴡ ᴘʟᴀʏɪɴɢ:**
  {current_title}
  ⏱ {current_duration} | 👤 {current_requester}

⦿ **ᴜᴘᴄᴏᴍɪɴɢ ({count} sᴏɴɢs):**
{queue_list}
"""

# Error Messages
ERROR_NO_RESULTS = "❌ No results found for: `{query}`\nTry a different search term."
ERROR_QUEUE_FULL = "❌ Queue is full! Maximum {max_size} songs allowed."
ERROR_NOT_PLAYING = "❌ No song is currently playing!"
ERROR_NOT_IN_VC = "❌ I'm not in a voice chat!"

# Success Messages
SUCCESS_ADDED_TO_QUEUE = """
<blockquote>
<b>❖ ᴧᴅᴅєᴅ ᴛᴏ ǫᴜєᴜᴇ ᴧᴛ #{position} ❞</b>

<b>❍ TITLE :</b> {title} <b>❞</b>
<b>❍ DURΛTIση :</b> {duration} <b>MIηUTeS</b>
<b>❍ BY :</b> {requester}
</blockquote>
"""

# Controls Help
CONTROLS_HELP = """
**Controls:**
⏭️ /skip - Skip song
⏸️ /pause - Pause
🔊 /volume - Adjust volume
"""
