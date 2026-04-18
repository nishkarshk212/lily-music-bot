#!/bin/bash
# Remote bot deployment and restart script

SERVER_IP="161.118.250.195"
USERNAME="root"
PORT="22"
GIT_REPO="https://github.com/nishkarshk212/lily-music-bot.git"
BOT_DIR="/root/lily-music-bot"  # Directory on the server where the bot will be deployed

echo "🚀 Deploying and restarting bot on remote server..."
echo "===================================================="

# SSH into the server and execute commands
ssh -p ${PORT} ${USERNAME}@${SERVER_IP} << ENDSSH
echo "📡 Connected to server"

# Navigate to bot directory or clone if it doesn't exist
if [ -d "${BOT_DIR}" ]; then
    echo "📁 Bot directory exists, pulling latest changes..."
    cd ${BOT_DIR}
    git pull origin main || git pull origin master
else
    echo "📦 Cloning repository..."
    git clone ${GIT_REPO} ${BOT_DIR}
    cd ${BOT_DIR}
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Kill existing bot processes
echo "🛑 Stopping existing bot processes..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "python.*start_bot.py" 2>/dev/null
sleep 2

# Verify processes are killed
if pgrep -f "python.*main.py" > /dev/null || pgrep -f "python.*start_bot.py" > /dev/null; then
    echo "⚠️  Force killing processes..."
    pkill -9 -f "python.*main.py" 2>/dev/null
    pkill -9 -f "python.*start_bot.py" 2>/dev/null
    sleep 1
fi

echo "✅ Previous processes stopped"

# Start the bot in the background
echo "🚀 Starting bot..."
nohup python main.py > bot.log 2>&1 &

# Get the process ID
BOT_PID=$!
echo "✅ Bot started with PID: $BOT_PID"

# Wait a moment and check if it's running
sleep 3
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running successfully!"
    echo "📝 View logs with: tail -f ${BOT_DIR}/bot.log"
else
    echo "❌ Bot failed to start. Check ${BOT_DIR}/bot.log for details"
fi

echo "===================================================="
echo "🎵 Deployment and restart process complete!"
ENDSSH

echo "✅ Remote deployment completed!"
