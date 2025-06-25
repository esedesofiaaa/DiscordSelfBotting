#!/bin/bash
# Prepare server for deployuser deployment
# Run this script ONCE on your server to prepare it for GitHub Actions deployment

set -e

echo "🔧 Preparing server for deployuser deployment..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root or with sudo"
    echo "Usage: sudo bash prepare-server.sh"
    exit 1
fi

# Get the actual user who ran sudo (not root)
ACTUAL_USER="${SUDO_USER:-$(whoami)}"
if [ "$ACTUAL_USER" = "root" ]; then
    echo "❌ Please run this script with sudo from your normal user account"
    echo "Don't run as root directly"
    exit 1
fi

echo "👤 Preparing for user: $ACTUAL_USER"

# Stop any existing service
echo "⏹️ Stopping any existing discord-bot service..."
systemctl stop discord-bot 2>/dev/null || echo "Service was not running"

# Create deployuser if it doesn't exist
echo "👤 Setting up deployuser..."
if ! id deployuser >/dev/null 2>&1; then
    useradd -m -s /bin/bash deployuser
    echo "✅ Created deployuser"
else
    echo "✅ deployuser already exists"
fi

# Ensure project directory exists and has correct ownership
echo "📁 Setting up project directory..."
mkdir -p /opt/discord-bot
chown -R deployuser:deployuser /opt/discord-bot

# Clone or update repository
echo "📥 Setting up repository..."
cd /opt/discord-bot
if [ ! -d ".git" ]; then
    echo "Cloning repository..."
    sudo -u deployuser git clone https://github.com/esedesofiaaa/DiscordSelfBotting.git .
else
    echo "Repository already exists"
fi

# Ensure deployuser owns everything
chown -R deployuser:deployuser /opt/discord-bot

# Set up virtual environment
echo "🐍 Setting up Python virtual environment..."
sudo -u deployuser bash -c "
    cd /opt/discord-bot
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
"

# Set up systemd service
echo "⚙️ Setting up systemd service..."
cp /opt/discord-bot/discord-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable discord-bot

# Configure passwordless sudo for deployuser
echo "🔐 Configuring passwordless sudo..."
tee /etc/sudoers.d/deployuser << 'SUDOERS_EOF'
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl start discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl stop discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl restart discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl status discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl is-active discord-bot
deployuser ALL=(ALL) NOPASSWD: /usr/bin/chown -R deployuser\:deployuser /opt/discord-bot
SUDOERS_EOF

chmod 440 /etc/sudoers.d/deployuser

# Clean up old configurations
echo "🧹 Cleaning up old configurations..."
rm -f /etc/sudoers.d/discord-bot

# Test the configuration
echo "🧪 Testing configuration..."
visudo -c || { echo "❌ Sudoers configuration error"; exit 1; }

# Test deployuser permissions
echo "🔍 Testing deployuser permissions..."
sudo -u deployuser sudo -n systemctl status discord-bot >/dev/null 2>&1 && echo "✅ systemctl permissions OK" || echo "❌ systemctl permissions failed"
sudo -u deployuser sudo -n chown -R deployuser:deployuser /opt/discord-bot --dry-run >/dev/null 2>&1 && echo "✅ chown permissions OK" || echo "❌ chown permissions failed"

# Test Python environment
echo "🐍 Testing Python environment..."
sudo -u deployuser bash -c "cd /opt/discord-bot && source venv/bin/activate && python --version" && echo "✅ Python environment OK" || echo "❌ Python environment failed"

echo ""
echo "🎉 Server preparation completed!"
echo ""
echo "📝 Next steps:"
echo "1. Configure your GitHub Secrets:"
echo "   - DISCORD_TOKEN: Your Discord bot token"
echo "   - LINODE_HOST: This server's IP address"
echo "   - LINODE_USERNAME: deployuser"
echo "   - SSH_PRIVATE_KEY: Your SSH private key"
echo ""
echo "2. You can now deploy using GitHub Actions!"
echo "3. Or test manually: sudo -u deployuser bash -c 'cd /opt/discord-bot && source venv/bin/activate && python main.py'"
echo ""
echo "🔍 Check service status: systemctl status discord-bot"
echo "📄 View logs: journalctl -u discord-bot -f"
