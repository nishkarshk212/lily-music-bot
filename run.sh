#!/bin/bash
# Quick launcher script for the Telegram Music Bot

echo "🎵 Telegram Music Bot - Quick Launcher"
echo "========================================"
echo ""

# Check if diagnostic has been run
if [ ! -f "diagnostic.py" ]; then
    echo "❌ diagnostic.py not found!"
    exit 1
fi

# Run diagnostic first
echo "🔍 Running diagnostic check..."
python diagnostic.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Diagnostic failed! Please fix the issues above."
    exit 1
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 Starting bot with auto-restart..."
echo "   Press Ctrl+C to stop"
echo ""

# Start the bot
python start_bot.py
