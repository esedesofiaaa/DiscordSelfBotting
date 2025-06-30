"""
Enhanced message logger for Discord Self Bot
"""
import os
import datetime
import json
from typing import Optional, Dict, Any
from pathlib import Path
import discord


class MessageLogger:
    """Enhanced message logger with multiple output formats"""
    
    def __init__(self, log_file_path: str, json_output: bool = False):
        self.log_file = Path(log_file_path)
        self.json_output = json_output
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def format_message_text(self, message: discord.Message) -> str:
        """Format message for text logging"""
        timestamp = datetime.datetime.now().isoformat()
        server = message.guild.name if message.guild else 'DM'
        channel = message.channel.name if hasattr(message.channel, 'name') else 'Unknown'
        
        # Handle both old and new Discord username formats
        if hasattr(message.author, 'discriminator') and message.author.discriminator == '0':
            author = f"@{message.author.name}"  # New username format
        else:
            author = f"{message.author.name}#{getattr(message.author, 'discriminator', '0000')}"  # Old format
            
        content = message.content or '[No text content]'
        
        log_entry = f"[{timestamp}] {server} > #{channel} | {author}: {content}"
        
        # Add attachment info
        if message.attachments:
            attachments = ', '.join([f"{att.filename} ({att.url})" for att in message.attachments])
            log_entry += f"\n  📎 Attachments: {attachments}"
        
        # Add embed info
        if message.embeds:
            embed_info = []
            for i, embed in enumerate(message.embeds):
                title = embed.title or 'No title'
                desc = embed.description[:100] if embed.description else 'No description'
                embed_info.append(f"Embed {i + 1}: {title} - {desc}")
            log_entry += f"\n  📋 Embeds: {', '.join(embed_info)}"
        
        # Add reaction info
        if message.reactions:
            reactions = ', '.join([f"{reaction.emoji}:{reaction.count}" for reaction in message.reactions])
            log_entry += f"\n  😀 Reactions: {reactions}"
        
        return log_entry + '\n' + '-' * 80 + '\n'
    
    def format_message_json(self, message: discord.Message) -> Dict[str, Any]:
        """Format message for JSON logging"""
        # Handle both old and new Discord username formats
        if hasattr(message.author, 'discriminator') and message.author.discriminator == '0':
            author_name = f"@{message.author.name}"
        else:
            author_name = f"{message.author.name}#{getattr(message.author, 'discriminator', '0000')}"
        
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'message_id': str(message.id),
            'server': {
                'id': str(message.guild.id) if message.guild else None,
                'name': message.guild.name if message.guild else 'DM'
            },
            'channel': {
                'id': str(message.channel.id),
                'name': getattr(message.channel, 'name', 'Unknown')
            },
            'author': {
                'id': str(message.author.id),
                'name': author_name,
                'display_name': getattr(message.author, 'display_name', message.author.name)
            },
            'content': message.content,
            'attachments': [
                {
                    'filename': att.filename,
                    'url': att.url,
                    'size': att.size
                } for att in message.attachments
            ],
            'embeds': [
                {
                    'title': embed.title,
                    'description': embed.description,
                    'url': embed.url
                } for embed in message.embeds
            ],
            'reactions': [
                {
                    'emoji': str(reaction.emoji),
                    'count': reaction.count
                } for reaction in message.reactions
            ]
        }
    
    def log_message(self, message: discord.Message):
        """Log a message to the file"""
        try:
            if self.json_output:
                formatted_message = json.dumps(self.format_message_json(message), indent=2, ensure_ascii=False)
                formatted_message += '\n'
            else:
                formatted_message = self.format_message_text(message)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_message)
            
            print(f"✅ Message logged: {message.author.name} in #{getattr(message.channel, 'name', 'Unknown')}")
        except Exception as error:
            print(f"❌ Error logging message: {error}")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about the log file"""
        try:
            if not self.log_file.exists():
                return {'exists': False, 'size': 0, 'lines': 0}
            
            stats = self.log_file.stat()
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            return {
                'exists': True,
                'size': stats.st_size,
                'lines': lines,
                'last_modified': datetime.datetime.fromtimestamp(stats.st_mtime),
                'path': str(self.log_file)
            }
        except Exception as error:
            print(f"Error getting log stats: {error}")
            return {'exists': False, 'size': 0, 'lines': 0}
    
    def rotate_log(self, max_size_mb: int = 10):
        """Rotate log file if it gets too large"""
        try:
            if not self.log_file.exists():
                return
            
            size_mb = self.log_file.stat().st_size / (1024 * 1024)
            if size_mb > max_size_mb:
                backup_path = self.log_file.with_suffix(f'.{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
                self.log_file.rename(backup_path)
                print(f"📁 Log rotated: {backup_path}")
        except Exception as error:
            print(f"❌ Error rotating log: {error}")
