#!/usr/bin/env python3
"""
Test script to verify audio files are valid and can be played
"""

import os
import subprocess
import sys

def test_audio_file(file_path):
    """Test if an audio file is valid using ffprobe"""
    print(f"\n{'='*60}")
    print(f"Testing: {file_path}")
    print(f"{'='*60}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File does not exist!")
        return False
    
    # Check file size
    file_size = os.path.getsize(file_path)
    print(f"📁 File size: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
    
    if file_size < 1024:
        print(f"❌ File too small, likely corrupted!")
        return False
    
    # Use ffprobe to get audio info
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ ffprobe failed: {result.stderr}")
            return False
        
        import json
        info = json.loads(result.stdout)
        
        # Print stream info
        streams = info.get('streams', [])
        if streams:
            stream = streams[0]
            print(f"✅ Audio stream found:")
            print(f"   Codec: {stream.get('codec_name', 'unknown')}")
            print(f"   Sample rate: {stream.get('sample_rate', 'unknown')} Hz")
            print(f"   Channels: {stream.get('channels', 'unknown')}")
            print(f"   Duration: {stream.get('duration', 'unknown')} seconds")
        else:
            print(f"❌ No audio streams found!")
            return False
        
        # Print format info
        fmt = info.get('format', {})
        print(f"📦 Format: {fmt.get('format_name', 'unknown')}")
        print(f"⏱️  Duration: {fmt.get('duration', 'unknown')} seconds")
        print(f"🎵 Bitrate: {fmt.get('bit_rate', 'unknown')} bps")
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"❌ ffprobe timed out!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ffmpeg():
    """Test if ffmpeg is installed and working"""
    print("\n" + "="*60)
    print("Testing FFmpeg Installation")
    print("="*60)
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg installed: {version}")
            
            # Check ffmpeg location
            location = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            print(f"📍 Location: {location.stdout.strip()}")
            return True
        else:
            print(f"❌ FFmpeg check failed")
            return False
    except Exception as e:
        print(f"❌ FFmpeg not found: {e}")
        return False


def main():
    """Main test function"""
    print("\n🎵 Audio File Validation Test")
    print("="*60)
    
    # Test ffmpeg
    ffmpeg_ok = test_ffmpeg()
    if not ffmpeg_ok:
        print("\n⚠️  FFmpeg is required! Install it with:")
        print("   brew install ffmpeg")
        sys.exit(1)
    
    # Test audio files in downloads directory
    downloads_dir = os.path.join(os.path.dirname(__file__), 'downloads')
    
    if not os.path.exists(downloads_dir):
        print(f"\n❌ Downloads directory not found: {downloads_dir}")
        sys.exit(1)
    
    # Get recent m4a files
    m4a_files = [f for f in os.listdir(downloads_dir) if f.endswith('.m4a')]
    
    if not m4a_files:
        print(f"\n❌ No .m4a files found in downloads directory")
        sys.exit(1)
    
    print(f"\n📂 Found {len(m4a_files)} audio file(s)")
    
    # Test first 3 files
    test_count = min(3, len(m4a_files))
    success_count = 0
    
    for i in range(test_count):
        file_path = os.path.join(downloads_dir, m4a_files[i])
        if test_audio_file(file_path):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Results: {success_count}/{test_count} files valid")
    print(f"{'='*60}")
    
    if success_count == test_count:
        print("✅ All tested files are valid!")
    else:
        print("⚠️  Some files may be corrupted. Try re-downloading them.")


if __name__ == "__main__":
    main()
