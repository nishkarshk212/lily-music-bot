"""
HTML Message Helper - Provides clean HTML formatting utilities
"""

from pyrogram.enums import ParseMode


def html(text: str) -> dict:
    """
    Returns a dict with text and parse_mode for HTML messages.
    Use with ** unpacking in message calls.
    
    Example:
        await message.reply_text(**html("<b>Bold text</b>"))
    """
    return {"text": text, "parse_mode": ParseMode.HTML}


def parse_mode_html() -> ParseMode:
    """
    Returns the HTML ParseMode enum.
    
    Example:
        await message.reply_text("<b>Bold</b>", parse_mode=parse_mode_html())
    """
    return ParseMode.HTML


# Common HTML formatting helpers
def bold(text: str) -> str:
    """Wrap text in bold tags"""
    return f"<b>{text}</b>"


def italic(text: str) -> str:
    """Wrap text in italic tags"""
    return f"<i>{text}</i>"


def code(text: str) -> str:
    """Wrap text in code tags"""
    return f"<code>{text}</code>"


def link(text: str, url: str) -> str:
    """Create a hyperlink"""
    return f'<a href="{url}">{text}</a>'


def blockquote(text: str) -> str:
    """Wrap text in blockquote tags"""
    return f"<blockquote>{text}</blockquote>"


def newline() -> str:
    """Return newline character"""
    return "\n"
