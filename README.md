# Discord Self-Bot (Python)

A professional Discord self-bot for automation and message monitoring, built with Python and organized with a modular architecture.

## ✨ Features

- 📝 **Message monitoring and logging** with JSON/text output options
- 🎯 **Modular command system** with easy extensibility  
- 🗑️ **Message management** (purge, clean by content)
- 📊 **Bot information and statistics**
- 🏓 **Latency verification and health checks**
- ⚙️ **Environment-based configuration**
- 🔧 **Professional project structure**

## 📁 Project Structure

```
DiscordSelfBotting/
├── src/                          # Main source code
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Configuration management
│   │   └── logger.py            # Enhanced message logger
│   ├── bot/                     # Bot client
│   │   └── client.py            # Main bot class
│   └── commands/                # Command modules
│       ├── base.py              # Base command classes
│       ├── utility.py           # Utility commands
│       ├── moderation.py        # Moderation commands
│       └── monitoring.py        # Monitoring commands
├── scripts/                     # Organized scripts
│   ├── development/             # Development scripts
│   └── deployment/              # Deployment scripts
├── logs/                        # Log files
├── run.py                       # Main entry point
├── start_bot.sh                 # Startup script
├── requirements.txt             # Dependencies
└── .env.example                 # Environment configuration template
```

## 🚀 Quick Start

### For local development:

1. **Clone and setup environment:**
   ```bash
   git clone <repository>
   cd DiscordSelfBotting
   cp .env.example .env
   ```

2. **Configure your bot:**
   Edit `.env` file with your settings:
   ```env
   DISCORD_TOKEN=your_discord_token_here
   OWNER_ID=your_discord_user_id_here
   PREFIX=!
   MONITORING_SERVER_ID=server_id_to_monitor
   ```

3. **Start the bot:**
   ```bash
   ./start_bot.sh
   ```

   Or for simple startup:
   ```bash
   python3 run.py
   ```
   
   # Or manually
   python main.py
   ```

### For server deployment:

1. **First time - Prepare the server:**
   ```bash
   # Connect to server
   ssh your_user@your_server
   
   # Clone the repository
   cd /opt
   sudo git clone https://github.com/your_username/DiscordSelfBotting.git discord-bot
   cd discord-bot
   
   # Run preparation script
   sudo bash prepare-server.sh
   ```

2. **Configure GitHub Secrets** (see section below)

3. **Deployment is automatic** - Runs when you push to main branch

### Migration from discord-bot to deployuser:

If you already had the bot configured with the `discord-bot` user:

```bash
# On the server
cd /opt/discord-bot
sudo bash migrate-to-deployuser.sh
```

## GitHub Secrets

For automatic deployment, configure these secrets in your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

- `DISCORD_TOKEN`: Your Discord bot token
- `LINODE_HOST`: Your server's IP address
- `LINODE_USERNAME`: `deployuser` (user configured by the script)
- `SSH_PRIVATE_KEY`: Your SSH private key

### How to get your SSH private key?

```bash
# On your local machine
cat ~/.ssh/id_rsa
# Copy all content (including -----BEGIN and -----END)
```

Edit `config.py` to configure:
- Bot settings
- Message monitoring options
- Server and channel IDs

## Project Structure

```
├── main.py              # Main bot file
├── config.py            # Bot configuration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment file example
├── dev/
│   ├── start_bot.sh    # Development start script (with validations)
│   └── start_bot_simple.sh # Simple start script
├── utils/
│   └── logger.py       # Message logger
├── logs/               # Logs directory
└── venv/               # Python virtual environment
```

## 🌿 Development Workflow with Branches

### Branch Strategy:

- **`main`** → Production (automatic deployment to server)
- **`develop`** → Development/staging (automatic testing)
- **`feature/*`** → New features
- **`hotfix/*`** → Critical fixes

### Recommended workflow:

#### **1. Initial setup:**
```bash
# Initialize development workflow
./branch-helper.sh init
```

#### **2. Develop new feature:**
```bash
# Create feature branch
./branch-helper.sh feature feature-name

# Make your changes
git add .
git commit -m "Add new functionality"
git push

# When ready, merge to develop
./branch-helper.sh finish feature-name
```

#### **3. Release to production:**
```bash
# Merge develop to main (triggers deployment)
./branch-helper.sh release
```

#### **4. Critical hotfix:**
```bash
# For critical bugs in production
./branch-helper.sh hotfix fix-name
# Make changes and manually merge to main and develop
```

### Useful commands:

```bash
# View current status
./branch-helper.sh status

# View complete help
./branch-helper.sh help
```

### Automatic workflows:

- **Push to `main`** → Automatic deployment to production
- **Push to `develop`** → Automatic testing and validation
- **Pull Request to `main`** → Code review and testing

## Commands

The bot supports the following commands:

- `!ping` - Check bot latency
- `!info` - Display bot information and statistics  
- `!clear [amount]` - Delete messages (default: 1)
- `!help` - Show available commands

## Security Considerations

- Bot token is stored securely using GitHub Secrets
- Environment variables are used for sensitive configuration
- Local `.env` files are excluded from version control

## Monitoring

### Server monitoring:

```bash
# Check service status
sudo systemctl status discord-bot

# View real-time logs
sudo journalctl -u discord-bot -f

# Restart service
sudo systemctl restart discord-bot
```

### Local monitoring:

```bash
# Check environment
./check_env.sh

# View logs
tail -f logs/messages.txt
```