"""
Utility commands for Discord Self Bot
"""
import time
from typing import List
import discord
from .base import BaseCommand


class PingCommand(BaseCommand):
    """Ping command to check bot latency"""
    
    @property
    def name(self) -> str:
        return "ping"
    
    @property
    def description(self) -> str:
        return "Check bot latency and response time"
    
    @property
    def aliases(self) -> List[str]:
        return ["p", "latency"]
    
    async def execute(self, message: discord.Message, args: List[str]):
        try:
            start_time = time.time()
            sent = await message.reply('🏓 Pinging...')
            end_time = time.time()
            
            latency = round((end_time - start_time) * 1000)
            ws_ping = round(message.guild.get_member(message.author.id).guild.ws.latency * 1000) if message.guild else 0
            
            await sent.edit(content=f"🏓 Pong! Latency: {latency}ms | WebSocket: {ws_ping}ms")
        except Exception as error:
            print(f"Error in ping command: {error}")
            await self.send_error(message, f"Failed to ping: {error}")


class InfoCommand(BaseCommand):
    """Info command to show bot information"""
    
    def __init__(self, bot_client):
        self.client = bot_client
    
    @property
    def name(self) -> str:
        return "info"
    
    @property
    def description(self) -> str:
        return "Show bot information and statistics"
    
    @property
    def aliases(self) -> List[str]:
        return ["information", "stats", "status"]
    
    async def execute(self, message: discord.Message, args: List[str]):
        try:
            uptime = time.time() - getattr(self.client, 'start_time', time.time())
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            
            guild_count = len(self.client.guilds)
            user_count = len(self.client.users)
            
            info = f"""**🤖 Self-Bot Information**
⏰ **Uptime:** {hours}h {minutes}m {seconds}s
🌐 **Servers:** {guild_count}
👥 **Users:** {user_count}
🔧 **Prefix:** `!`
📝 **Commands:** Available
🟢 **Status:** Online"""
            
            await message.reply(info)
        except Exception as error:
            print(f"Error in info command: {error}")
            await self.send_error(message, f"Failed to get info: {error}")


class HelpCommand(BaseCommand):
    """Help command to show available commands"""
    
    def __init__(self, command_registry):
        self.registry = command_registry
    
    @property
    def name(self) -> str:
        return "help"
    
    @property
    def description(self) -> str:
        return "Show available commands and their usage"
    
    @property
    def aliases(self) -> List[str]:
        return ["h", "commands", "cmd"]
    
    async def execute(self, message: discord.Message, args: List[str]):
        try:
            if args and len(args) > 0:
                # Show help for specific command
                command_name = args[0]
                command = self.registry.get_command(command_name)
                
                if command:
                    help_text = f"""**📖 Command Help: {command.name}**
📝 **Description:** {command.description}
💡 **Usage:** `!{command.usage}`"""
                    
                    if command.aliases:
                        help_text += f"\n🔄 **Aliases:** {', '.join(command.aliases)}"
                    
                    await message.reply(help_text)
                else:
                    await self.send_error(message, f"Command '{command_name}' not found")
            else:
                # Show all commands
                commands = self.registry.get_all_commands()
                commands_text = []
                
                for cmd in commands:
                    commands_text.append(f"`!{cmd.name}` - {cmd.description}")
                
                help_text = f"""**📚 Available Commands:**
{chr(10).join(commands_text)}

💡 Use `!help <command>` for detailed help on a specific command"""
                
                await message.reply(help_text)
        except Exception as error:
            print(f"Error in help command: {error}")
            await self.send_error(message, f"Failed to show help: {error}")
