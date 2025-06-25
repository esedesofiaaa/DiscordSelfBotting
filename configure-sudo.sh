#!/bin/bash
# Script to configure passwordless sudo for discord-bot user
# Run this on your Linode server if you already have the environment set up

echo "🔐 Configuring passwordless sudo for discord-bot user..."

# Create sudoers file for discord-bot user
sudo tee /etc/sudoers.d/discord-bot << 'EOF'
# Allow discord-bot user to manage discord-bot service without password
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl start discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl stop discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl restart discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl status discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl is-active discord-bot
EOF

# Set proper permissions
sudo chmod 440 /etc/sudoers.d/discord-bot

# Test the configuration
echo "🧪 Testing sudo configuration..."
sudo -u discord-bot sudo -n systemctl is-active discord-bot && echo "✅ Sudo configuration working" || echo "❌ Sudo configuration failed"

echo "✅ Passwordless sudo configuration completed!"
echo ""
echo "📝 The discord-bot user can now run these commands without password:"
echo "  - sudo systemctl start discord-bot"
echo "  - sudo systemctl stop discord-bot"
echo "  - sudo systemctl restart discord-bot"
echo "  - sudo systemctl status discord-bot"
echo "  - sudo systemctl is-active discord-bot"
