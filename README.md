# Discord Self-Bot (Python)

A Discord bot for automation and message monitoring, built with Python.

## Features

- Message monitoring and logging
- Command system with prefix support
- Message deletion
- Bot information and statistics
- Latency verification

## Setup

### For local development:

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Add your Discord token to the `.env` file:
   ```env
   DISCORD_TOKEN=your_token_here
   PREFIX=!
   ```

5. Configure bot settings in `config.py`

6. Start the bot:
   ```bash
   # Using development scripts
   ./dev/start_bot.sh          # With validations
   ./dev/start_bot_simple.sh   # Direct execution
   
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

⚠️ **Important**: This is a self-bot, which violates Discord's Terms of Service. Use at your own risk.

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

## Contributing

1. Fork the repository
2. Create a feature branch: `./branch-helper.sh feature your-feature`
3. Make your changes and commit them
4. Push to your fork and submit a pull request
5. Merge to develop first for testing

## License

This project is for educational purposes only. Use responsibly and in accordance with Discord's Terms of Service.
- **Push a `develop` o `feature/*`** → Tests automáticos
- **Pull Request** → Tests antes de merge