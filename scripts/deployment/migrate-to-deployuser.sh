#!/bin/bash
# Migration script: discord-bot user to deployuser
# Run this on your Linode server to migrate from discord-bot to deployuser

set -e

echo "🔄 Migrating from discord-bot user to deployuser..."

# Stop the service
echo "⏹️ Stopping discord-bot service..."
sudo systemctl stop discord-bot || echo "Service was not running"

# Remove old sudoers configuration
echo "🧹 Cleaning old configuration..."
sudo rm -f /etc/sudoers.d/discord-bot

# Create deployuser if it doesn't exist
echo "👤 Ensuring deployuser exists..."
sudo useradd -m -s /bin/bash deployuser || echo "User already exists"

# Fix ownership of project directory
echo "📁 Fixing ownership..."
sudo chown -R deployuser:deployuser /opt/discord-bot

# Update systemd service
echo "⚙️ Updating systemd service..."
sudo cp discord-bot.service /etc/systemd/system/
sudo systemctl daemon-reload

# Create new sudoers configuration
echo "🔐 Configuring passwordless sudo for deployuser..."
sudo tee /etc/sudoers.d/deployuser << 'EOF'
# Allow deployuser to manage discord-bot service without password
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl start discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl stop discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl restart discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl status discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl is-active discord-bot
# Allow chown for fixing ownership issues during deployment
deployuser ALL=(ALL) NOPASSWD: /usr/bin/chown -R deployuser\:deployuser /opt/discord-bot
EOF

sudo chmod 440 /etc/sudoers.d/deployuser

# Test configuration
echo "🧪 Testing configuration..."
sudo visudo -c

# Test deployuser permissions
echo "🔍 Testing deployuser permissions..."
sudo -u deployuser sudo -n systemctl status discord-bot >/dev/null 2>&1 && echo "✅ systemctl permissions working" || echo "❌ systemctl permissions failed"

sudo -u deployuser sudo -n chown -R deployuser:deployuser /opt/discord-bot --dry-run >/dev/null 2>&1 && echo "✅ chown permissions working" || echo "❌ chown permissions failed"

# Test that deployuser can run the bot
echo "🐍 Testing bot execution..."
sudo -u deployuser bash -c "cd /opt/discord-bot && source venv/bin/activate && python --version" && echo "✅ Python environment working" || echo "❌ Python environment failed"

# Create .env file if it doesn't exist
echo "📄 Checking .env file..."
if [ ! -f /opt/discord-bot/.env ]; then
    echo "⚠️  .env file not found. You need to create it manually with your Discord token."
    echo "📝 Create it with: cp .env.example .env && nano .env"
else
    echo "✅ .env file exists"
fi

# Start the service
echo "▶️ Starting discord-bot service..."
sudo systemctl start discord-bot

# Check status
echo "🔍 Checking service status..."
sudo systemctl status discord-bot --no-pager -l

echo "🎉 Migration completed!"
echo ""
echo "📝 Service is now running as deployuser"
echo "🔍 Check logs with: sudo journalctl -u discord-bot -f"
