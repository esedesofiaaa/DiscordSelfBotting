"""
Legacy configuration compatibility
This maintains compatibility for any old imports while using the new organized config
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the new config
from core.config import config

# Maintain backward compatibility with old variable names
TOKEN = config.TOKEN
PREFIX = config.bot.command_prefix
OWNER_ID = config.OWNER_ID

# Old SETTINGS dictionary for compatibility
SETTINGS = {
    'auto_reply': config.bot.auto_reply,
    'log_messages': config.bot.log_messages,
    'delete_after_reply': config.bot.delete_after_reply
}

# Old MONITORING dictionary for compatibility  
MONITORING = {
    'enabled': config.monitoring.enabled,
    'server_id': config.monitoring.server_id,
    'channel_ids': config.monitoring.channel_ids,
    'log_file': config.monitoring.log_file,
    'include_attachments': config.monitoring.include_attachments,
    'include_embeds': config.monitoring.include_embeds
}
