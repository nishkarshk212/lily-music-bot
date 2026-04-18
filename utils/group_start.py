"""
Group Start Message Handler
Handles the message when bot is added to a group
"""

import random
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.strings import SUPPORT_CHANNEL_USERNAME

# Group start images (same as start images)
GROUP_START_IMAGES = [
    "https://i.ibb.co/PzYnJRB7/anime-girl-autumn-scenery.jpg",
    "https://i.ibb.co/Fv79FW1/anime-girl-kimono-bamboo-forest.jpg",
    "https://i.ibb.co/LhBbppvL/anime-girl-kimono-misty-lake.jpg",
    "https://i.ibb.co/nqPYXqLh/anime-girl-plays-guitar-by-water-night.jpg",
    "https://i.ibb.co/mVmRx517/anime-girl-rock-by-river-autumn-sunset-scenery.jpg",
    "https://i.ibb.co/wFwqqbjk/anime-landscape-person-traveling.jpg",
    "https://i.ibb.co/gM5B48Br/anime-like-illustration-girl-by-sea.jpg",
    "https://i.ibb.co/LXGTZNhc/anime-like-illustration-girl-portrait.jpg",
    "https://i.ibb.co/s9CGyfYK/anime-style-couple-characters-with-fire.jpg",
    "https://i.ibb.co/xStZGy0J/anime-style-scene-with-people-showing-affection-outdoors-street.jpg",
    "https://i.ibb.co/prj9V4vz/anime-character-traveling-2.jpg",
]

# Group Start Message Template
GROUP_START_MESSAGE = """<b>𝖧𝖾𝗒 {user_mention}</b>
<b>𝖳𝗁𝗂𝗌 𝖨𝗌 {bot_mention}</b>

𝖳𝗁𝖺𝗇𝗄𝗌 𝖥𝗈𝗋 𝖠𝖽𝖽𝗂𝗇𝗀 𝖬𝖾 𝖨𝗇 {chat_name}!

🎵 𝖨 𝖢𝖺𝗇 𝖯𝗅𝖺𝗒 𝖲𝗈𝗇𝗀𝗌 𝖨𝗇 𝖵𝗈𝗂𝖼𝖾 𝖢𝗁𝖺𝗍𝗌
🎧 𝖧𝗂𝗀𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒 𝖲𝗈𝗎𝗇𝖽
⚡ 𝖥𝖺𝗌𝗍 & 𝖱𝖾𝗅𝗂𝖺𝖻𝗅𝖾

<b>𝖴𝗌𝖾 /play 𝗍𝗈 𝗌𝗍𝖺𝗋𝗍 𝗅𝗂𝗌𝗍𝖾𝗇𝗂𝗇𝗀 𝗍𝗈 𝗆𝗎𝗌𝗂𝖼!</b>
𝖴𝗌𝖾 /help 𝖿𝗈𝗋 𝖺𝗅𝗅 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌."""


def get_group_start_keyboard(bot_username: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for group start message"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✦ ᴧᴅᴅ ϻє ✦",
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                "⊜ ꜱᴜᴘᴘσʀᴛ ⊜",
                url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}"
            )
        ]
    ])


def get_random_group_start_image() -> str:
    """Get a random group start image"""
    return random.choice(GROUP_START_IMAGES)


def format_group_start_message(user_mention: str, bot_mention: str, chat_name: str) -> str:
    """Format the group start message with variables"""
    return GROUP_START_MESSAGE.format(
        user_mention=user_mention,
        bot_mention=bot_mention,
        chat_name=chat_name
    )
