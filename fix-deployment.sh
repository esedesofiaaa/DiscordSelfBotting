#!/bin/bash
# Quick fix script for existing Discord Bot deployment
# Run this on your Linode server to fix current issues

echo "🔧 Fixing Discord Bot deployment issues..."

# Fix 1: Configure passwordless sudo for discord-bot user
echo "🔐 Configuring passwordless sudo..."
sudo tee /etc/sudoers.d/discord-bot << 'EOF'
# Allow discord-bot user to manage discord-bot service without password
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl start discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl stop discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl restart discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl status discord-bot
discord-bot ALL=(ALL) NOPASSWD: /bin/systemctl is-active discord-bot
EOF
sudo chmod 440 /etc/sudoers.d/discord-bot

# Fix 2: Fix git ownership issues
echo "📁 Fixing git ownership issues..."
sudo -u discord-bot bash << 'USEREOF'
cd /opt/discord-bot
git config --global --add safe.directory /opt/discord-bot
USEREOF

# Fix 3: Ensure proper ownership of the project directory
echo "👤 Fixing directory ownership..."
sudo chown -R discord-bot:discord-bot /opt/discord-bot

# Test the fixes
echo "🧪 Testing fixes..."

# Test sudo configuration
echo "Testing sudo configuration..."
sudo -u discord-bot sudo -n systemctl is-active discord-bot >/dev/null 2>&1 && echo "✅ Sudo configuration working" || echo "❌ Sudo configuration failed"

# Test git repository
echo "Testing git repository..."
sudo -u discord-bot bash -c "cd /opt/discord-bot && git status >/dev/null 2>&1" && echo "✅ Git repository working" || echo "❌ Git repository has issues"

echo "🎉 Fixes applied!"
echo ""
echo "📝 You can now:"
echo "1. Test the deployment again from GitHub Actions"
echo "2. Manually start the bot: sudo systemctl start discord-bot"
echo "3. Check status: sudo systemctl status discord-bot"
