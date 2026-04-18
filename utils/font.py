"""
Font styling utilities for bot messages
Provides various text style transformations for Telegram messages
"""


class FontStyles:
    """Text style transformations for bot messages"""
    
    # Small Caps (ᴛᴇxᴛ style)
    SMALL_CAPS_MAP = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }
    
    @classmethod
    def small_caps(cls, text: str) -> str:
        """Convert text to small caps style (ᴇxᴀᴍᴘʟᴇ)"""
        result = []
        for char in text.lower():
            result.append(cls.SMALL_CAPS_MAP.get(char, char))
        return ''.join(result)
    
    @classmethod
    def bold(cls, text: str) -> str:
        """Convert text to bold using Telegram markdown"""
        return f"**{text}**"
    
    @classmethod
    def italic(cls, text: str) -> str:
        """Convert text to italic using Telegram markdown"""
        return f"__{text}__"
    
    @classmethod
    def code(cls, text: str) -> str:
        """Convert text to code/monospace using Telegram markdown"""
        return f"`{text}`"
    
    @classmethod
    def strikethrough(cls, text: str) -> str:
        """Convert text to strikethrough using Telegram markdown"""
        return f"~~{text}~~"
    
    @classmethod
    def underline(cls, text: str) -> str:
        """Convert text to underline using HTML"""
        return f"<u>{text}</u>"
    
    @classmethod
    def link(cls, text: str, url: str) -> str:
        """Create a clickable link using HTML"""
        return f"<a href='{url}'>{text}</a>"
    
    @classmethod
    def mention(cls, user_id: int, name: str) -> str:
        """Create a user mention link"""
        return f"<a href='tg://user?id={user_id}'>{name}</a>"


# Convenience functions for direct use
def to_small_caps(text: str) -> str:
    """Convert text to small caps style"""
    return FontStyles.small_caps(text)

def to_bold(text: str) -> str:
    """Convert text to bold"""
    return FontStyles.bold(text)

def to_italic(text: str) -> str:
    """Convert text to italic"""
    return FontStyles.italic(text)

def to_code(text: str) -> str:
    """Convert text to monospace code"""
    return FontStyles.code(text)


# Example usage and testing
if __name__ == "__main__":
    # Test the font styles
    test_text = "Hello World"
    
    print("Original:", test_text)
    print("Small Caps:", to_small_caps(test_text))
    print("Bold:", to_bold(test_text))
    print("Italic:", to_italic(test_text))
    print("Code:", to_code(test_text))
    
    # Example: Convert entire messages
    sample_message = "Welcome to Music Bot"
    print("\nSample message:", sample_message)
    print("Styled:", to_small_caps(sample_message))
