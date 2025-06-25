#!/bin/bash
# Setup script for Discord Bot on Linode server
# Run this script once on your Linode server to set up the environment

set -e

echo "🚀 Setting up Discord Bot environment on Linode..."

# Create dedicated user for the bot
echo "👤 Creating discord-bot user..."
sudo useradd -m -s /bin/bash discord-bot || echo "User already exists"

# Create project directory
echo "📁 Creating project directory..."
sudo mkdir -p /opt/discord-bot
sudo chown discord-bot:discord-bot /opt/discord-bot

# Switch to discord-bot user for the rest of the setup
echo "🔄 Switching to discord-bot user..."
sudo -u discord-bot bash << 'EOF'
cd /opt/discord-bot

# Clone the repository (you'll need to set up SSH keys or use HTTPS)
echo "📥 Cloning repository..."
# git clone git@github.com:your-username/your-repo.git .
# OR
# git clone https://github.com/your-username/your-repo.git .

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
# pip install -r requirements.txt  # Uncomment after cloning repo

# Create logs directory
mkdir -p logs

echo "✅ Environment setup completed for discord-bot user"
EOF

# Copy and setup systemd service
echo "⚙️ Setting up systemd service..."
sudo cp discord-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-bot

# Setup firewall (if needed)
echo "🔥 Configuring firewall..."
# sudo ufw allow ssh
# sudo ufw --force enable

echo "🎉 Setup completed!"
echo ""
echo "📝 Next steps:"
echo "1. Clone your repository to /opt/discord-bot"
echo "2. Install dependencies: sudo -u discord-bot bash -c 'cd /opt/discord-bot && source venv/bin/activate && pip install -r requirements.txt'"
echo "3. Configure your bot token and settings"
echo "4. Start the service: sudo systemctl start discord-bot"
echo "5. Check status: sudo systemctl status discord-bot"
