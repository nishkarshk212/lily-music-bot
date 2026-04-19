"""
YouTube/Audio Downloader using NexGen API
Handles downloading and extracting metadata
"""

import os
import yt_dlp
import asyncio
import aiohttp
from typing import Optional, Dict
from youtubesearchpython.__future__ import VideosSearch
from config import DOWNLOAD_DIR, MAX_DURATION
import logging

logger = logging.getLogger(__name__)

# NexGen API configuration
NEXGEN_API_URL = os.getenv("NEXGENBOTS_API", "https://pvtz.nexgenbots.xyz")
API_KEY = os.getenv("API_KEY")


class SongInfo:
    """Container for song information"""
    
    def __init__(self):
        self.title: str = ""
        self.duration: int = 0  # in seconds
        self.thumbnail: str = ""
        self.channel: str = ""
        self.video_id: str = ""
        self.url: str = ""
        self.file_path: str = ""


class Downloader:
    """Handles downloading audio from various sources using NexGen API"""
    
    def __init__(self):
        self.download_dir = DOWNLOAD_DIR
        os.makedirs(self.download_dir, exist_ok=True)
        self._session = None
        self._search_cache = {} # Cache for search results: {query: SongInfo}

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    def get_ydl_opts(self, output_path: str) -> Dict:
        """Get yt-dlp options"""
        return {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'prefer_ffmpeg': True,
            'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # macOS Homebrew default
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    
    async def extract_info(self, url: str) -> Optional[SongInfo]:
        """Extract information from URL using NexGen API"""
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                return None
            
            # FASTEST: Use yt-dlp metadata extraction without full download
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Fast extraction
                'skip_download': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'socket_timeout': 3,  # Reduced timeout
            }
            
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Use a smaller thread pool or direct executor for faster response
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            
            if not info:
                return None
            
            song = SongInfo()
            song.title = info.get('title', 'Unknown')
            song.duration = int(info.get('duration', 0))
            song.thumbnail = info.get('thumbnail', '')
            song.channel = info.get('uploader', 'Unknown')
            song.video_id = video_id
            song.url = url
            
            return song
            
        except Exception as e:
            logger.error(f"Failed to extract info: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        if "v=" in url:
            return url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[-1].split("?")[0]
        return url
    
    async def download_song(self, url: str, song_info: SongInfo) -> Optional[str]:
        """
        Download song using NexGen API
        
        Args:
            url: Video URL
            song_info: Song information
            
        Returns:
            Path to downloaded file or None
        """
        try:
            # Check duration limit
            if song_info.duration > MAX_DURATION:
                logger.error(f"Song too long: {song_info.duration}s")
                return None
            
            video_id = song_info.video_id
            # Use m4a format for better compatibility with PyTgCalls
            file_path = os.path.join(self.download_dir, f"{video_id}.m4a")
            
            # Check if already downloaded
            if os.path.exists(file_path):
                logger.info(f"✅ [NEXGEN] File already exists: {file_path}")
                song_info.file_path = file_path
                return file_path
            
            # Use NexGen API to download
            logger.info(f"🎵 [NEXGEN] Using API: {NEXGEN_API_URL}/song/{video_id}")
            
            session = await self._get_session()
            # Step 1: Get the stream URL
            api_url = f"{NEXGEN_API_URL}/song/{video_id}"
            params = {"api": API_KEY} if API_KEY else {}
            
            async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            status = data.get("status")
                            stream_link = data.get("link")
                            
                            if status == "done" and stream_link:
                                logger.info(f"✅ [NEXGEN] Got stream link, using for immediate playback")
                                song_info.file_path = stream_link
                                return stream_link
                            elif status == "downloading":
                                logger.info("⏳ [NEXGEN] Still processing, waiting...")
                                await asyncio.sleep(5)
                                # Retry once
                                return await self.download_song(url, song_info)
                            else:
                                logger.warning(f"⚠️ [NEXGEN] Unexpected status: {status}")
                                return None
                        else:
                            logger.warning(f"⚠️ [NEXGEN] Empty response")
                            return None
                    else:
                        logger.warning(f"⚠️ [NEXGEN] API returned status {response.status}")
                        return None
                
        except Exception as e:
            logger.error(f"❌ [NEXGEN] Failed to download song: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def search_and_download(self, query: str) -> Optional[SongInfo]:
        """Search for a song and download it using youtube-search-python (ULTRA FAST)"""
        try:
            # ⚡ Check cache first (aggressive caching for faster playback)
            if query in self._search_cache:
                logger.info(f"⚡ [CACHE HIT] Using cached result for: {query}")
                return self._search_cache[query]

            # ⚡ ULTRA-FAST: Use youtube-search-python instead of yt-dlp
            # yt-dlp takes 0.5-1.5s for search, VideosSearch takes 0.1-0.3s
            search = VideosSearch(query, limit=1)
            result = await search.next()
            
            if not result or not result.get("result"):
                return None
            
            video_info = result["result"][0]
            video_id = video_info.get('id')
            if not video_id:
                return None
                
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Create SongInfo directly from search result (FASTEST)
            song_info = SongInfo()
            song_info.title = video_info.get('title', 'Unknown')
            # Handle duration (format: '3:45')
            duration_str = video_info.get('duration', '0')
            if duration_str and isinstance(duration_str, str):
                parts = duration_str.split(':')
                if len(parts) == 2:
                    try:
                        song_info.duration = int(parts[0]) * 60 + int(parts[1])
                    except (ValueError, IndexError):
                        song_info.duration = 0
                elif len(parts) == 3:
                    try:
                        song_info.duration = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                    except (ValueError, IndexError):
                        song_info.duration = 0
            elif isinstance(duration_str, (int, float)):
                song_info.duration = int(duration_str)
            
            # Handle thumbnail (get maxres if available)
            thumbnails = video_info.get('thumbnails', [])
            song_info.thumbnail = thumbnails[-1].get('url') if thumbnails else f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            song_info.channel = video_info.get('channel', {}).get('name', 'Unknown') if video_info.get('channel') else 'Unknown'
            song_info.views = video_info.get('viewCount', {}).get('short', '0') if video_info.get('viewCount') else '0'
            song_info.video_id = video_id
            song_info.url = video_url
            
            # ⚡ Use direct stream for fastest possible playback
            api_url = f"{NEXGEN_API_URL}/song/{video_id}"
            params = {"api": API_KEY} if API_KEY else {}
            
            try:
                session = await self._get_session()
                # ⚡ Reduced timeout to 3 seconds for faster response
                async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and data.get("status") == "done" and data.get("link"):
                            song_info.file_path = data.get("link")
                            self._search_cache[query] = song_info
                            logger.info(f"⚡ Got stream link for: {query}")
                            return song_info
            except Exception as e:
                logger.warning(f"NexGen fast-link fetch failed: {e}")
            
            # Fallback to standard download if stream link not immediately available
            file_path = await self.download_song(video_url, song_info)
            if file_path:
                song_info.file_path = file_path
                self._search_cache[query] = song_info
                return song_info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to search and download: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def cleanup_file(self, file_path: str):
        """Delete downloaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file: {e}")
    
    async def download_thumbnail(self, thumbnail_url: str, output_path: str) -> Optional[str]:
        """
        Download thumbnail from URL
        
        Args:
            thumbnail_url: URL of the thumbnail
            output_path: Path to save the thumbnail
            
        Returns:
            Path to downloaded thumbnail or None
        """
        try:
            if not thumbnail_url:
                return None
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(thumbnail_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            logger.info(f"✅ Downloaded thumbnail: {output_path}")
                            return output_path
                        else:
                            logger.error(f"❌ Thumbnail file is empty")
                            return None
                    else:
                        logger.error(f"❌ Failed to download thumbnail: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Failed to download thumbnail: {e}")
            return None
    
    def cleanup_all(self):
        """Clean up all downloaded files"""
        try:
            for filename in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            logger.info("Cleaned up all downloads")
        except Exception as e:
            logger.error(f"Failed to cleanup all: {e}")


# Global downloader instance
downloader = Downloader()
