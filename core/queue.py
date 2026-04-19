"""
Queue Management System for Music Bot
Handles song queue operations for each chat
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Song:
    """Represents a song in the queue"""
    title: str
    duration: int  # in seconds
    file_path: str
    thumbnail: str
    requester: str
    video_id: str = ""
    url: str = ""
    artist: str = "Unknown"
    views: str = "0"


class Queue:
    """Queue manager for a single chat"""
    
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.queue: List[Song] = []
        self.current_song: Optional[Song] = None
        self.is_playing = False
        self.loop_count = 0  # 0 = no loop, >0 = loop count
        self.loop_queue = False
        self.volume = 100
        self.history: List[Song] = []  # Previously played songs
        self.start_time = 0.0 # Unix timestamp when current song started
    
    def add_song(self, song: Song) -> int:
        """Add song to queue, returns position"""
        self.queue.append(song)
        return len(self.queue)
    
    def get_next_song(self) -> Optional[Song]:
        """Get next song from queue"""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def skip_song(self) -> Optional[Song]:
        """Skip current song and get next"""
        if self.current_song:
            self.history.append(self.current_song)
        
        # Handle loop
        if self.loop_count > 0 and self.current_song:
            self.loop_count -= 1
            self.queue.insert(0, self.current_song)
        
        self.current_song = self.get_next_song()
        return self.current_song
    
    def clear_queue(self):
        """Clear the entire queue"""
        self.queue.clear()
        self.history.clear()
    
    def get_queue(self) -> List[Song]:
        """Get current queue"""
        return self.queue.copy()
    
    def get_position(self, video_id: str) -> int:
        """Get position of song in queue"""
        for i, song in enumerate(self.queue, 1):
            if song.video_id == video_id:
                return i
        return -1
    
    def remove_song(self, position: int) -> bool:
        """Remove song from queue by position (1-based)"""
        if 0 < position <= len(self.queue):
            self.queue.pop(position - 1)
            return True
        return False
    
    def shuffle_queue(self):
        """Shuffle the queue"""
        import random
        random.shuffle(self.queue)
    
    def size(self) -> int:
        """Get queue size"""
        return len(self.queue)
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.queue) == 0


class QueueManager:
    """Global queue manager for all chats"""
    
    def __init__(self):
        self.queues: Dict[int, Queue] = {}
    
    def get_queue(self, chat_id: int) -> Queue:
        """Get or create queue for a chat"""
        if chat_id not in self.queues:
            self.queues[chat_id] = Queue(chat_id)
        return self.queues[chat_id]
    
    def remove_queue(self, chat_id: int):
        """Remove queue for a chat"""
        if chat_id in self.queues:
            del self.queues[chat_id]
    
    def get_all_queues(self) -> Dict[int, Queue]:
        """Get all queues"""
        return self.queues.copy()


# Global queue manager instance
queue_manager = QueueManager()
