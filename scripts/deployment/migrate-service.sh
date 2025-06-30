#!/bin/bash
# Migration script to update existing discord-bot service to discord-message-listener
# Run this on the server to migrate from the old bot to the new message listener

set -e

echo "🔄 Migrating from Discord Bot to Discord Message Listener..."

# Stop the old service if it exists
echo "⏹️ Stopping old discord-bot service..."
sudo systemctl stop discord-bot 2>/dev/null || echo "Old service not running or doesn't exist"

# Disable the old service
echo "🚫 Disabling old discord-bot service..."
sudo systemctl disable discord-bot 2>/dev/null || echo "Old service not enabled or doesn't exist"

# Copy the new service file
echo "📋 Installing new service configuration..."
sudo cp discord-message-listener.service /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the new service
echo "✅ Enabling discord-message-listener service..."
sudo systemctl enable discord-message-listener

# Update sudoers for the new service name
echo "🔐 Updating sudoers configuration..."
sudo tee /etc/sudoers.d/discord-bot << 'SUDOERS_EOF'
# Allow discord-bot user to manage discord-message-listener service without password
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl start discord-message-listener
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl stop discord-message-listener
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl restart discord-message-listener
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl status discord-message-listener
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl is-active discord-message-listener
# Allow chown for fixing ownership issues during deployment
discord-bot ALL=(ALL) NOPASSWD: /bin/chown -R discord-bot:discord-bot /opt/discord-bot
SUDOERS_EOF

# Set proper permissions for sudoers file
sudo chmod 440 /etc/sudoers.d/discord-bot

echo "🎉 Migration completed!"
echo ""
echo "📝 Next steps:"
echo "1. Make sure your .env file is configured with the new format"
echo "2. Start the service: sudo systemctl start discord-message-listener"
echo "3. Check status: sudo systemctl status discord-message-listener"
echo "4. View logs: sudo journalctl -u discord-message-listener -f"
echo ""
echo "🗑️ To remove old service file (optional):"
echo "   sudo rm /etc/systemd/system/discord-bot.service"
