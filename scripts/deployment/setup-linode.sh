#!/bin/bash
# Setup script for Discord Message Listener on Linode server
# Run this script once on your Linode server to set up the environment

set -e

echo "🚀 Setting up Discord Message Listener environment on Linode..."

# Create dedicated user for the listener
echo "👤 Creating deployuser user..."
sudo useradd -m -s /bin/bash deployuser || echo "User already exists"

# Create project directory (use existing directory structure for compatibility)
echo "📁 Creating project directory..."
sudo mkdir -p /opt/discord-bot
sudo chown deployuser:deployuser /opt/discord-bot

# Switch to deployuser user for the rest of the setup
echo "🔄 Switching to deployuser user..."
sudo -u deployuser bash << 'EOF'
cd /opt/discord-bot

# Clone the repository
echo "📥 Cloning repository..."
git clone https://github.com/esedesofiaaa/DiscordSelfBotting.git .

# Configure git safe directory
git config --global --add safe.directory /opt/discord-bot

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

echo "✅ Environment setup completed for deployuser user"
EOF

# Copy and setup systemd service
echo "⚙️ Setting up systemd service..."
sudo cp discord-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-bot

# Configure passwordless sudo for deployuser user for systemctl commands
echo "🔐 Configuring passwordless sudo for systemctl commands..."
<<<<<<< HEAD
sudo tee /etc/sudoers.d/discord-bot << 'SUDOERS_EOF'
# Allow discord-bot user to manage discord-bot service without password
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl start discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl stop discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl restart discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl status discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl is-active discord-bot
=======
sudo tee /etc/sudoers.d/deployuser << 'SUDOERS_EOF'
# Allow deployuser user to manage discord-bot service without password
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl start discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl stop discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl restart discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl status discord-bot
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl is-active discord-bot
>>>>>>> 97e4673 (refactor: Update service user references from 'discord-bot' to 'deployuser' and fix log file environment variable typo)
# Allow chown for fixing ownership issues during deployment
deployuser ALL=(ALL) NOPASSWD: /bin/chown -R deployuser:deployuser /opt/discord-bot
# Allow copying service files
deployuser ALL=(ALL) NOPASSWD: /bin/cp /opt/discord-bot/discord-bot.service /etc/systemd/system/
deployuser ALL=(ALL) NOPASSWD: /bin/systemctl daemon-reload
SUDOERS_EOF

# Set proper permissions for sudoers file
sudo chmod 440 /etc/sudoers.d/deployuser

# Setup firewall (if needed)
echo "🔥 Configuring firewall..."
# sudo ufw allow ssh
# sudo ufw --force enable

echo "🎉 Setup completed!"
echo ""
echo "📝 Next steps:"
echo "1. Configure your Discord token in .env file"
echo "2. Start the service: sudo systemctl start discord-bot"
echo "3. Check status: sudo systemctl status discord-bot"
echo "4. View logs: sudo journalctl -u discord-bot -f"
