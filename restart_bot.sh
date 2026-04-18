#!/bin/bash
# Restart script for Telegram Music Bot

echo "🔄 Restarting Telegram Music Bot..."
echo "===================================="

# Kill any existing bot processes
echo "🛑 Stopping existing bot processes..."
pkill -f "python3.*main.py" 2>/dev/null
pkill -f "python3.*start_bot.py" 2>/dev/null
sleep 2

# Verify processes are killed
if pgrep -f "python3.*main.py" > /dev/null || pgrep -f "python3.*start_bot.py" > /dev/null; then
    echo "⚠️  Force killing processes..."
    pkill -9 -f "python3.*main.py" 2>/dev/null
    pkill -9 -f "python3.*start_bot.py" 2>/dev/null
    sleep 1
fi

echo "✅ Previous processes stopped"

# Start the bot in the background
echo "🚀 Starting bot..."
nohup python3 main.py > bot_restart.log 2>&1 &

# Get the process ID
BOT_PID=$!
echo "✅ Bot started with PID: $BOT_PID"

# Wait a moment and check if it's running
sleep 3
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running successfully!"
    echo "📝 View logs with: tail -f bot_restart.log"
else
    echo "❌ Bot failed to start. Check bot_restart.log for details"
fi

echo "===================================="
echo "🎵 Restart process complete!"