import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX', '!')
OWNER_ID = '1384570203022692392'  # Replace with your Discord user ID

# Bot settings
SETTINGS = {
    'auto_reply': False,
    'log_messages': True,
    'delete_after_reply': False
}

# Message monitoring settings
MONITORING = {
    'enabled': True,
    'server_id': '1331752826082295899',  # Replace with the server ID to monitor
    'channel_ids': [],  # Empty list = monitor all channels, or specify channel IDs
    'log_file': './logs/messages.txt',
    'include_attachments': True,
    'include_embeds': True
}
