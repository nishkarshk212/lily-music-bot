"""
Formatter Utilities
Helper functions for formatting time, size, and text
"""


def format_time(seconds: int) -> str:
    """
    Format seconds to MM:SS or HH:MM:SS
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if not seconds:
        return "00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_views(views) -> str:
    """
    Format view count to human readable format (e.g., 1.2M, 500K)
    
    Args:
        views: View count
        
    Returns:
        Formatted view string
    """
    try:
        if not views:
            return "0 views"
        
        num = int(views)
        if num >= 1000000:
            return f"{num / 1000000:.1f}M views"
        elif num >= 1000:
            return f"{num / 1000:.1f}K views"
        else:
            return f"{num} views"
    except (ValueError, TypeError):
        return str(views) if views else "0 views"


def format_size(size_bytes: int) -> str:
    """
    Format bytes to human readable size
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to max length with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_queue_list(queue_items: list, start_position: int = 1) -> str:
    """
    Format queue items into a readable list
    
    Args:
        queue_items: List of Song objects
        start_position: Starting position number
        
    Returns:
        Formatted queue string
    """
    if not queue_items:
        return "Queue is empty!"
    
    lines = []
    for i, song in enumerate(queue_items, start_position):
        duration = format_time(song.duration)
        title = truncate_text(song.title, 40)
        lines.append(f"{i}. {title} ({duration})")
    
    return "\n".join(lines)


def format_duration_text(seconds: int) -> str:
    """
    Format duration with units
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
