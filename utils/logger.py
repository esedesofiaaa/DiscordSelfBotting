import os
import datetime
from typing import Optional
import discord


class MessageLogger:
    def __init__(self, log_file_path: str):
        self.log_file = log_file_path
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def format_message(self, message: discord.Message) -> str:
        """Format message for logging"""
        timestamp = datetime.datetime.now().isoformat()
        server = message.guild.name if message.guild else 'DM'
        channel = message.channel.name if hasattr(message.channel, 'name') else 'Unknown'
        
        # Handle both old and new Discord username formats
        if message.author.discriminator == '0':
            author = f"@{message.author.name}"  # New username format
        else:
            author = f"{message.author.name}#{message.author.discriminator}"  # Old format
            
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
    
    def log_message(self, message: discord.Message):
        """Log a message to the file"""
        try:
            formatted_message = self.format_message(message)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_message)
            print(f"✅ Message logged: {message.author.name} in #{message.channel.name}")
        except Exception as error:
            print(f"❌ Error logging message: {error}")
    
    def get_log_stats(self) -> dict:
        """Get statistics about the log file"""
        try:
            if not os.path.exists(self.log_file):
                return {'exists': False, 'size': 0, 'lines': 0}
            
            stats = os.stat(self.log_file)
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            return {
                'exists': True,
                'size': stats.st_size,
                'lines': lines,
                'last_modified': datetime.datetime.fromtimestamp(stats.st_mtime)
            }
        except Exception as error:
            print(f"Error getting log stats: {error}")
            return {'exists': False, 'size': 0, 'lines': 0}
