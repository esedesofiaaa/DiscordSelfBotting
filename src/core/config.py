"""
Configuration module for Discord Self Bot
"""
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class BotSettings:
    """Bot behavior settings"""
    auto_reply: bool = False
    log_messages: bool = True
    delete_after_reply: bool = False
    command_prefix: str = '!'


@dataclass
class MonitoringSettings:
    """Message monitoring configuration"""
    enabled: bool = True
    server_id: str = ''
    channel_ids: List[str] = None
    log_file: str = './logs/messages.txt'
    include_attachments: bool = True
    include_embeds: bool = True
    
    def __post_init__(self):
        if self.channel_ids is None:
            self.channel_ids = []


class Config:
    """Main configuration class"""
    
    def __init__(self):
        # Bot credentials
        self.TOKEN = os.getenv('DISCORD_TOKEN')
        self.OWNER_ID = os.getenv('OWNER_ID', '1384570203022692392')
        
        # Bot settings
        self.bot = BotSettings(
            auto_reply=os.getenv('AUTO_REPLY', 'False').lower() == 'true',
            log_messages=os.getenv('LOG_MESSAGES', 'True').lower() == 'true',
            delete_after_reply=os.getenv('DELETE_AFTER_REPLY', 'False').lower() == 'true',
            command_prefix=os.getenv('PREFIX', '!')
        )
        
        # Monitoring settings
        self.monitoring = MonitoringSettings(
            enabled=os.getenv('MONITORING_ENABLED', 'True').lower() == 'true',
            server_id=os.getenv('MONITORING_SERVER_ID', '1331752826082295899'),
            channel_ids=self._parse_channel_ids(os.getenv('MONITORING_CHANNEL_IDS', '')),
            log_file=os.getenv('LOG_FILE', './logs/messages.txt'),
            include_attachments=os.getenv('INCLUDE_ATTACHMENTS', 'True').lower() == 'true',
            include_embeds=os.getenv('INCLUDE_EMBEDS', 'True').lower() == 'true'
        )
    
    def _parse_channel_ids(self, channel_ids_str: str) -> List[str]:
        """Parse comma-separated channel IDs"""
        if not channel_ids_str.strip():
            return []
        return [cid.strip() for cid in channel_ids_str.split(',') if cid.strip()]
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        errors = []
        warnings = []
        
        # Validate token
        if not self.TOKEN:
            errors.append("Discord token is missing. Set DISCORD_TOKEN in .env file")
        elif self.TOKEN == self.OWNER_ID:
            errors.append("Invalid token! You're using your user ID instead of Discord token")
        
        # Validate monitoring settings
        if self.monitoring.enabled:
            if not self.monitoring.server_id:
                warnings.append("No server ID set for monitoring")
            
            if not os.path.exists(os.path.dirname(self.monitoring.log_file)):
                warnings.append(f"Log directory doesn't exist: {os.path.dirname(self.monitoring.log_file)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Global config instance
config = Config()
