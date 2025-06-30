"""
Discord Self Bot - Main bot class
"""
import discord
import time
from typing import Optional
from src.core.config import config
from src.core.logger import MessageLogger
from src.commands.base import CommandRegistry
from src.commands.utility import PingCommand, InfoCommand, HelpCommand
from src.commands.moderation import PurgeCommand, CleanCommand
from src.commands.monitoring import MonitorCommand, LogsCommand


class DiscordSelfBot:
    """Main Discord Self Bot class"""
    
    def __init__(self):
        self.client = discord.Client()
        self.config = config
        self.start_time = time.time()
        
        # Initialize logger
        self.message_logger = MessageLogger(
            self.config.monitoring.log_file,
            json_output=False
        )
        
        # Initialize command registry
        self.command_registry = CommandRegistry()
        self._register_commands()
        
        # Setup event handlers
        self._setup_events()
    
    def _register_commands(self):
        """Register all bot commands"""
        # Utility commands
        self.command_registry.register(PingCommand())
        self.command_registry.register(InfoCommand(self.client))
        self.command_registry.register(HelpCommand(self.command_registry))
        
        # Moderation commands
        self.command_registry.register(PurgeCommand())
        self.command_registry.register(CleanCommand())
        
        # Monitoring commands
        self.command_registry.register(MonitorCommand(self.config, self.message_logger))
        self.command_registry.register(LogsCommand(self.message_logger))
    
    def _setup_events(self):
        """Setup Discord event handlers"""
        
        @self.client.event
        async def on_ready():
            await self._on_ready()
        
        @self.client.event
        async def on_message(message):
            await self._on_message(message)
        
        @self.client.event
        async def on_error(event, *args, **kwargs):
            await self._on_error(event, *args, **kwargs)
    
    async def _on_ready(self):
        """Handle bot ready event"""
        print(f"🤖 {self.client.user.name} is ready!")
        print(f"👤 Logged in as: {self.client.user}")
        print(f"🆔 User ID: {self.client.user.id}")
        print(f"🔧 Command prefix: {self.config.bot.command_prefix}")
        
        # Log monitoring status
        if self.config.monitoring.enabled:
            print(f"📝 Message monitoring enabled for server: {self.config.monitoring.server_id}")
            print(f"📁 Log file: {self.config.monitoring.log_file}")
            
            # Check if server exists
            target_server = self._get_target_server()
            if target_server:
                print(f"✅ Target server found: {target_server.name}")
            else:
                print(f"❌ Target server not found! Check server ID in config.")
        else:
            print("📝 Message monitoring disabled")
        
        print("-" * 50)
    
    async def _on_message(self, message: discord.Message):
        """Handle message events"""
        # Monitor messages in target server
        if self.config.monitoring.enabled and self._should_monitor_message(message):
            self.message_logger.log_message(message)
        
        # Ignore messages from other users and bots for commands
        if message.author.id != self.client.user.id:
            return
        
        # Log own messages if enabled
        if self.config.bot.log_messages:
            guild_name = message.guild.name if message.guild else 'DM'
            print(f"[{guild_name}] {message.author}: {message.content}")
        
        # Check if message starts with prefix
        if not message.content.startswith(self.config.bot.command_prefix):
            return
        
        # Parse command and arguments
        content = message.content[len(self.config.bot.command_prefix):].strip()
        if not content:
            return
        
        args = content.split()
        command_name = args[0].lower()
        command_args = args[1:]
        
        # Get and execute command
        command = self.command_registry.get_command(command_name)
        if command:
            try:
                await command.execute(message, command_args)
            except Exception as e:
                print(f"❌ Error executing command {command_name}: {e}")
                try:
                    await message.reply(f"❌ Error executing command: {e}")
                except:
                    pass
        else:
            print(f"❓ Unknown command: {command_name}")
    
    async def _on_error(self, event: str, *args, **kwargs):
        """Handle Discord errors"""
        print(f"❌ Error in event {event}: {args}")
    
    def _should_monitor_message(self, message: discord.Message) -> bool:
        """Determine if message should be monitored"""
        # Check if message is from target server
        if not message.guild or str(message.guild.id) != self.config.monitoring.server_id:
            return False
        
        # Check if specific channels are configured
        if self.config.monitoring.channel_ids:
            return str(message.channel.id) in self.config.monitoring.channel_ids
        
        # Monitor all channels if no specific channels configured
        return True
    
    def _get_target_server(self) -> Optional[discord.Guild]:
        """Get the target server for monitoring"""
        if not self.config.monitoring.server_id.isdigit():
            return None
        
        return discord.utils.get(self.client.guilds, id=int(self.config.monitoring.server_id))
    
    def validate_config(self) -> bool:
        """Validate bot configuration"""
        validation = self.config.validate()
        
        if validation['errors']:
            print("❌ Configuration errors:")
            for error in validation['errors']:
                print(f"  - {error}")
            return False
        
        if validation['warnings']:
            print("⚠️ Configuration warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        return True
    
    def run(self):
        """Start the bot"""
        if not self.validate_config():
            return
        
        print("🚀 Starting Discord Self Bot...")
        
        try:
            self.client.run(self.config.TOKEN)
        except Exception as error:
            print(f"❌ Error starting bot: {error}")
            if "Improper token" in str(error):
                print("🔑 Make sure you're using a valid Discord token, not your user ID")


def main():
    """Main entry point"""
    bot = DiscordSelfBot()
    bot.run()


if __name__ == "__main__":
    main()
