#!/bin/bash
# Restart script for Telegram Music Bot

echo "🔄 Restarting Telegram Music Bot..."
echo "===================================="

# Kill ALL existing bot processes (comprehensive cleanup)
echo "🛑 Stopping existing bot processes..."
pkill -9 -f "python3.*main.py" 2>/dev/null
pkill -9 -f "python.*main.py" 2>/dev/null
pkill -9 -f "python3.*start_bot.py" 2>/dev/null
pkill -9 -f "/usr/bin/python3 main.py" 2>/dev/null
sleep 2

# Verify ALL processes are killed
RETRY=0
while pgrep -f "main.py" > /dev/null && [ $RETRY -lt 3 ]; do
    echo "⚠️  Force killing remaining processes (attempt $((RETRY+1)))..."
    pkill -9 -f "main.py" 2>/dev/null
    sleep 1
    RETRY=$((RETRY+1))
done

# Final check
if pgrep -f "main.py" > /dev/null; then
    echo "❌ Failed to kill all processes. Please check manually."
    exit 1
fi

echo "✅ All previous processes stopped"

# Check if systemd service exists and is active
if systemctl is-active --quiet lily-music-bot.service 2>/dev/null; then
    echo "⚠️  Systemd service is active. Using systemd to restart..."
    systemctl restart lily-music-bot.service
    sleep 3
    if systemctl is-active --quiet lily-music-bot.service; then
        echo "✅ Bot restarted via systemd"
        echo "📝 View logs with: journalctl -u lily-music-bot.service -f"
        echo "===================================="
        echo "🎵 Restart process complete!"
        exit 0
    fi
fi

# Fallback: Start the bot manually (only if systemd is not available)
echo "🚀 Starting bot manually..."
nohup python3 main.py > bot_restart.log 2>&1 &

# Get the process ID
BOT_PID=$!
echo "✅ Bot started with PID: $BOT_PID"

# Wait a moment and check if it's running
sleep 3
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running successfully!"
    echo "📝 View logs with: tail -f bot_restart.log"
    echo "⚠️  Note: Consider using systemd service for better management"
else
    echo "❌ Bot failed to start. Check bot_restart.log for details"
    exit 1
fi

echo "===================================="
echo "🎵 Restart process complete!"