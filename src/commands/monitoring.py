"""
Monitoring commands for Discord Self Bot
"""
from typing import List
import discord
from .base import BaseCommand


class MonitorCommand(BaseCommand):
    """Monitor command to control message monitoring"""
    
    def __init__(self, config, message_logger):
        self.config = config
        self.logger = message_logger
    
    @property
    def name(self) -> str:
        return "monitor"
    
    @property
    def description(self) -> str:
        return "Control message monitoring (start/stop/status)"
    
    @property
    def aliases(self) -> List[str]:
        return ["mon", "monitoring"]
    
    @property
    def usage(self) -> str:
        return "monitor <start|stop|status>"
    
    async def execute(self, message: discord.Message, args: List[str]):
        try:
            if not args:
                await self.send_error(message, f"Usage: `!{self.usage}`")
                return
            
            subcommand = args[0].lower()
            
            if subcommand == 'start':
                self.config.monitoring.enabled = True
                await self.send_success(message, 'Message monitoring started')
                
            elif subcommand == 'stop':
                self.config.monitoring.enabled = False
                await self.send_success(message, 'Message monitoring stopped')
                
            elif subcommand == 'status':
                await self._show_status(message)
                
            else:
                await self.send_error(message, f"Unknown subcommand. Usage: `!{self.usage}`")
                
        except Exception as error:
            print(f"Error in monitor command: {error}")
            await self.send_error(message, 'Error executing monitor command')
    
    async def _show_status(self, message: discord.Message):
        """Show monitoring status"""
        try:
            target_server = None
            if self.config.monitoring.server_id.isdigit():
                target_server = discord.utils.get(message.author.mutual_guilds, 
                                                 id=int(self.config.monitoring.server_id))
            
            server_name = target_server.name if target_server else 'Server not found'
            
            channels_text = ('All channels' if not self.config.monitoring.channel_ids 
                           else f"{len(self.config.monitoring.channel_ids)} specific channels")
            
            status = f"""**📊 Monitoring Status:**
🔧 **Enabled:** {'✅ Yes' if self.config.monitoring.enabled else '❌ No'}
🏠 **Server:** {server_name}
📁 **Log file:** `{self.config.monitoring.log_file}`
📊 **Channels:** {channels_text}
📎 **Include attachments:** {'✅' if self.config.monitoring.include_attachments else '❌'}
📋 **Include embeds:** {'✅' if self.config.monitoring.include_embeds else '❌'}"""
            
            await message.reply(status)
            
        except Exception as error:
            print(f"Error showing monitor status: {error}")
            await self.send_error(message, 'Error getting monitor status')


class LogsCommand(BaseCommand):
    """Logs command to show log file statistics"""
    
    def __init__(self, message_logger):
        self.logger = message_logger
    
    @property
    def name(self) -> str:
        return "logs"
    
    @property
    def description(self) -> str:
        return "Show log file statistics and information"
    
    @property
    def aliases(self) -> List[str]:
        return ["log", "loginfo"]
    
    async def execute(self, message: discord.Message, args: List[str]):
        try:
            stats = self.logger.get_log_stats()
            
            if not stats['exists']:
                await message.reply('📝 No log file found. Start monitoring to create logs.')
                return
            
            size_kb = stats['size'] / 1024
            size_mb = size_kb / 1024
            
            last_modified = stats.get('last_modified', 'Unknown')
            last_modified_str = (last_modified.strftime('%Y-%m-%d %H:%M:%S') 
                               if last_modified != 'Unknown' else 'Unknown')
            
            # Format file size appropriately
            if size_mb >= 1:
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = f"{size_kb:.2f} KB"
            
            log_info = f"""**📊 Log File Statistics:**
📁 **File:** `{stats.get('path', 'Unknown')}`
📊 **Size:** {size_str}
📝 **Lines:** {stats['lines']:,}
🕒 **Last modified:** {last_modified_str}
📈 **Status:** {'🟢 Active' if stats['exists'] else '🔴 Inactive'}"""
            
            await message.reply(log_info)
            
        except Exception as error:
            print(f"Error in logs command: {error}")
            await self.send_error(message, 'Error getting log information')
