"""
Base command handler for Discord Self Bot
"""
from abc import ABC, abstractmethod
from typing import List
import discord


class BaseCommand(ABC):
    """Base class for all commands"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Command description"""
        pass
    
    @property
    def aliases(self) -> List[str]:
        """Command aliases"""
        return []
    
    @property
    def usage(self) -> str:
        """Command usage format"""
        return f"{self.name}"
    
    @abstractmethod
    async def execute(self, message: discord.Message, args: List[str]):
        """Execute the command"""
        pass
    
    async def send_error(self, message: discord.Message, error_msg: str):
        """Send error message"""
        try:
            await message.reply(f"❌ {error_msg}")
        except Exception as e:
            print(f"Error sending error message: {e}")
    
    async def send_success(self, message: discord.Message, success_msg: str):
        """Send success message"""
        try:
            await message.reply(f"✅ {success_msg}")
        except Exception as e:
            print(f"Error sending success message: {e}")


class CommandRegistry:
    """Registry for managing commands"""
    
    def __init__(self):
        self.commands = {}
        self.aliases = {}
    
    def register(self, command: BaseCommand):
        """Register a command"""
        self.commands[command.name.lower()] = command
        
        # Register aliases
        for alias in command.aliases:
            self.aliases[alias.lower()] = command.name.lower()
    
    def get_command(self, name: str) -> BaseCommand:
        """Get command by name or alias"""
        name = name.lower()
        
        # Check direct command name
        if name in self.commands:
            return self.commands[name]
        
        # Check aliases
        if name in self.aliases:
            return self.commands[self.aliases[name]]
        
        return None
    
    def get_all_commands(self) -> List[BaseCommand]:
        """Get all registered commands"""
        return list(self.commands.values())
