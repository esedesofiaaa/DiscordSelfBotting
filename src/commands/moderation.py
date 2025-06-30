"""
Moderation commands for Discord Self Bot
"""
import asyncio
from typing import List
import discord
from .base import BaseCommand


class PurgeCommand(BaseCommand):
    """Purge command to delete user's own messages"""
    
    @property
    def name(self) -> str:
        return "purge"
    
    @property
    def description(self) -> str:
        return "Delete your own messages from current channel"
    
    @property
    def aliases(self) -> List[str]:
        return ["clear", "delete", "del"]
    
    @property
    def usage(self) -> str:
        return "purge <amount>"
    
    async def execute(self, message: discord.Message, args: List[str]):
        try:
            if not args or not args[0].isdigit():
                await self.send_error(message, 'Please provide a number between 1 and 100')
                return
            
            amount = int(args[0])
            if amount < 1 or amount > 100:
                await self.send_error(message, 'Please provide a number between 1 and 100')
                return
            
            # Get messages from the channel
            messages = []
            async for msg in message.channel.history(limit=amount + 1):
                if msg.author.id == message.author.id:
                    messages.append(msg)
            
            if not messages:
                await self.send_error(message, 'No messages found to delete')
                return
            
            deleted = 0
            for msg in messages:
                try:
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(1)  # Rate limit protection
                except Exception as err:
                    print(f"Failed to delete message: {err}")
            
            print(f"✅ Deleted {deleted} messages")
            
            # Send a temporary confirmation that will also be deleted
            if deleted > 0:
                confirmation = await message.channel.send(f"🗑️ Deleted {deleted} messages")
                await asyncio.sleep(3)
                try:
                    await confirmation.delete()
                except:
                    pass
                    
        except Exception as error:
            print(f"Error in purge command: {error}")
            await self.send_error(message, f"Failed to purge messages: {error}")


class CleanCommand(BaseCommand):
    """Clean command to delete messages with specific content"""
    
    @property
    def name(self) -> str:
        return "clean"
    
    @property
    def description(self) -> str:
        return "Delete your messages containing specific text"
    
    @property
    def usage(self) -> str:
        return "clean <text_to_match>"
    
    async def execute(self, message: discord.Message, args: List[str]):
        try:
            if not args:
                await self.send_error(message, 'Please provide text to search for')
                return
            
            search_text = ' '.join(args).lower()
            
            # Get messages from the channel
            messages = []
            async for msg in message.channel.history(limit=100):
                if (msg.author.id == message.author.id and 
                    msg.content and 
                    search_text in msg.content.lower()):
                    messages.append(msg)
            
            if not messages:
                await self.send_error(message, f'No messages found containing "{search_text}"')
                return
            
            deleted = 0
            for msg in messages:
                try:
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(1)  # Rate limit protection
                except Exception as err:
                    print(f"Failed to delete message: {err}")
            
            print(f"✅ Deleted {deleted} messages containing '{search_text}'")
            
        except Exception as error:
            print(f"Error in clean command: {error}")
            await self.send_error(message, f"Failed to clean messages: {error}")
