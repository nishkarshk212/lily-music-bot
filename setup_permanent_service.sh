#!/bin/bash
# Create systemd service for permanent bot execution

SERVER_IP="161.118.250.195"
USERNAME="root"
PORT="22"
BOT_DIR="/root/lily-music-bot"

echo "🔧 Setting up permanent bot service..."
echo "========================================"

ssh -p ${PORT} ${USERNAME}@${SERVER_IP} << ENDSSH
echo "📡 Connected to server"

# Create systemd service file
cat > /etc/systemd/system/lily-music-bot.service << 'EOF'
[Unit]
Description=Lily Music Bot - Telegram Music Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${BOT_DIR}
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"

# Reload systemd to recognize the new service
systemctl daemon-reload
echo "✅ Systemd reloaded"

# Enable service to start on boot
systemctl enable lily-music-bot.service
echo "✅ Service enabled to start on boot"

# Stop any running bot processes
pkill -f "python.*main.py" 2>/dev/null || pkill -f "python3.*main.py" 2>/dev/null
sleep 2

# Start the service
systemctl start lily-music-bot.service
echo "✅ Service started"

# Show service status
sleep 3
systemctl status lily-music-bot.service --no-pager

echo ""
echo "========================================"
echo "🎵 Bot service setup complete!"
echo ""
echo "Useful commands:"
echo "  Check status: systemctl status lily-music-bot.service"
echo "  View logs: journalctl -u lily-music-bot.service -f"
echo "  Stop service: systemctl stop lily-music-bot.service"
echo "  Restart service: systemctl restart lily-music-bot.service"
ENDSSH

echo "✅ Permanent service setup completed!"
