# Email Notification System

This system monitors Discord bot activity and sends email alerts when the bot has not received or processed any messages for more than 8 hours.

## Features

- **Inactivity Detection**: Monitors bot activity and detects when no messages have been processed for a configurable period (default: 8 hours)
- **Email Alerts**: Sends HTML-formatted email notifications when inactivity is detected
- **Recovery Notifications**: Sends confirmation email when bot resumes processing messages
- **Activity Tracking**: Persistent tracking of bot activity across restarts
- **Configurable Thresholds**: Customize inactivity threshold and check intervals

## Components

### 1. Activity Tracker (`activity_tracker.py`)
Tracks when the bot processes messages and stores activity data persistently.

- Records timestamp of every processed message
- Stores data in `./logs/bot_activity.json`
- Provides methods to check time since last activity

### 2. Email Notifier (`email_notifier.py`)
Handles sending email notifications via SMTP.

- Supports HTML and plain text emails
- Configurable SMTP server and credentials
- Pre-formatted inactivity alert templates
- Recovery notification templates

### 3. Inactivity Monitor (`inactivity_monitor.py`)
Periodically checks bot activity and triggers email alerts.

- Runs as independent process
- Checks activity at configurable intervals (default: 30 minutes)
- Sends alerts only once per inactivity period
- Auto-detects recovery and sends confirmation

## Setup

### 1. Configure Email Settings

Edit your `.env` file with email configuration:

```bash
# SMTP Server Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Email Credentials
SMTP_SENDER_EMAIL=your_email@gmail.com
SMTP_SENDER_PASSWORD=your_app_password

# Alert Recipients (comma-separated)
ALERT_RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com

# Inactivity Threshold (hours)
INACTIVITY_THRESHOLD_HOURS=8.0

# Check Interval (minutes)
INACTIVITY_CHECK_INTERVAL_MINUTES=30.0
```

### 2. Gmail App Password Setup

If using Gmail, you need to create an **App Password**:

1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification (if not already enabled)
4. Go to App passwords: https://myaccount.google.com/apppasswords
5. Select "Mail" and your device
6. Generate password and copy it
7. Use this password in `SMTP_SENDER_PASSWORD`

**Important**: Do NOT use your regular Gmail password!

### 3. Other Email Providers

**Outlook/Hotmail**:
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo Mail**:
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Custom SMTP Server**:
```bash
SMTP_SERVER=your.smtp.server
SMTP_PORT=587  # or 465 for SSL
```

## Usage

### Testing Email Configuration

Before starting the monitor, test your email configuration:

```bash
python email_notifier.py
```

This will send a test email to verify your SMTP settings are correct.

### Running the Inactivity Monitor

Start the inactivity monitor as a separate process:

```bash
python inactivity_monitor.py
```

The monitor will:
1. Check bot activity every 30 minutes (configurable)
2. Send email alert if bot inactive for 8+ hours (configurable)
3. Send recovery notification when bot becomes active again

### Running as Background Service

For production, run the monitor in the background:

```bash
# Using nohup
nohup python inactivity_monitor.py > logs/monitor.log 2>&1 &

# Or using screen
screen -dmS inactivity_monitor python inactivity_monitor.py

# Or using systemd (recommended for servers)
# See systemd service example below
```

### Systemd Service (Linux)

Create `/etc/systemd/system/discord-inactivity-monitor.service`:

```ini
[Unit]
Description=Discord Bot Inactivity Monitor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/DiscordSelfBotting
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python inactivity_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable discord-inactivity-monitor
sudo systemctl start discord-inactivity-monitor
sudo systemctl status discord-inactivity-monitor
```

## Email Alert Examples

### Inactivity Alert Email

Subject: `⚠️ Discord Bot Inactivity Alert - 8.5 hours`

The email includes:
- Duration of inactivity
- Last activity timestamp
- Possible issues
- Recommended troubleshooting steps

### Recovery Notification Email

Subject: `✅ Discord Bot Activity Resumed`

Sent when bot starts processing messages again after an inactivity period.

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP server address |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_SENDER_EMAIL` | - | Sender email address (required) |
| `SMTP_SENDER_PASSWORD` | - | Sender email password (required) |
| `ALERT_RECIPIENT_EMAILS` | - | Comma-separated recipient emails (required) |
| `INACTIVITY_THRESHOLD_HOURS` | `8.0` | Hours before sending alert |
| `INACTIVITY_CHECK_INTERVAL_MINUTES` | `30.0` | Minutes between checks |
| `ACTIVITY_TRACKER_FILE` | `./logs/bot_activity.json` | Activity data file location |

### Customizing Thresholds

**Check more frequently (every 15 minutes)**:
```bash
INACTIVITY_CHECK_INTERVAL_MINUTES=15.0
```

**Alert after 4 hours instead of 8**:
```bash
INACTIVITY_THRESHOLD_HOURS=4.0
```

**Alert after 24 hours (daily check)**:
```bash
INACTIVITY_THRESHOLD_HOURS=24.0
INACTIVITY_CHECK_INTERVAL_MINUTES=60.0
```

## Activity Tracking

The bot automatically tracks activity when:
- Bot starts (`on_ready` event)
- Each message is processed successfully

Activity data is stored in `./logs/bot_activity.json`:

```json
{
  "last_activity_time": "2026-01-02T10:30:45.123456",
  "bot_start_time": "2026-01-02T08:00:00.000000",
  "total_messages_processed": 1234,
  "last_updated": "2026-01-02T10:30:45.123456"
}
```

## Troubleshooting

### Email Not Sending

**Problem**: Test email fails with authentication error

**Solutions**:
- Verify email and password are correct
- For Gmail: Use App Password, not regular password
- Check 2-Factor Authentication is enabled
- Verify SMTP server and port are correct

**Problem**: Connection timeout

**Solutions**:
- Check firewall allows outbound connections on port 587/465
- Try alternative SMTP server
- Verify internet connectivity

### Inactivity Not Detected

**Problem**: No alerts even though bot is inactive

**Solutions**:
- Check inactivity monitor is running: `ps aux | grep inactivity_monitor`
- Verify activity tracker file exists: `cat ./logs/bot_activity.json`
- Check monitor logs for errors
- Ensure threshold hours is set correctly

### False Alerts

**Problem**: Receiving alerts even though bot is active

**Solutions**:
- Verify bot is actually processing messages
- Check if activity tracker is being called in `on_message`
- Review `./logs/bot_activity.json` for recent timestamps
- Check system clock is correct

## Monitoring Multiple Bots

To monitor multiple bots, run separate monitor instances with different activity files:

```bash
# Bot 1
ACTIVITY_TRACKER_FILE=./logs/bot1_activity.json python inactivity_monitor.py &

# Bot 2
ACTIVITY_TRACKER_FILE=./logs/bot2_activity.json python inactivity_monitor.py &
```

## Security Notes

- **Never commit** `.env` file with real credentials to git
- Use App Passwords for Gmail (more secure than regular passwords)
- Consider using environment variables or secrets manager in production
- Restrict file permissions on activity tracker files
- Use encrypted connections (TLS/SSL) for SMTP

## Architecture

```
┌─────────────────────┐
│  Discord Bot        │
│  (main process)     │
│                     │
│  - Processes msgs   │
│  - Calls            │
│    activity_tracker │
│    .record_activity()│
└──────────┬──────────┘
           │
           │ writes to
           ▼
┌─────────────────────┐
│  bot_activity.json  │
│  (shared file)      │
│                     │
│  - last_activity    │
│  - message_count    │
└──────────┬──────────┘
           │
           │ reads from
           ▼
┌─────────────────────┐
│ Inactivity Monitor  │
│ (separate process)  │
│                     │
│  - Checks activity  │
│  - Sends emails     │
└─────────────────────┘
```

## License

Same as parent project.

## Support

For issues or questions:
1. Check logs in `./logs/` directory
2. Verify environment configuration
3. Test email settings with `python email_notifier.py`
4. Review this documentation
