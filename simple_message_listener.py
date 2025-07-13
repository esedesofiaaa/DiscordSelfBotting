"""
Discord Message Listener - Simple Version with Notion integration
A bot that listens and logs all messages from a specific server or channel.
Saves information directly to a Notion database.
Includes heartbeat monitoring system with Healthchecks.io.
"""
import discord
import os
import datetime
import asyncio
from typing import Optional, List
from dotenv import load_dotenv
from notion_client import Client
from heartbeat_system import HeartbeatSystem

# Load environment variables
load_dotenv()


class SimpleMessageListener:
    """Simple bot to listen and log Discord messages"""
    
    def __init__(self):
        # Basic configuration
        self.token = os.getenv('DISCORD_TOKEN')
        self.target_server_id = os.getenv('MONITORING_SERVER_ID')
        self.target_channel_ids = self._parse_channel_ids(os.getenv('MONITORING_CHANNEL_IDS', ''))
        self.log_file = os.getenv('LOG_FILE', './logs/messages.txt')
        
        # Notion configuration
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.notion_client = None
        
        # Heartbeat configuration
        self.heartbeat_url = os.getenv('HEALTHCHECKS_PING_URL', 'https://hc-ping.com/f679a27c-8a41-4ae2-9504-78f1b260e71d')
        self.heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', '300'))  # Default: 5 minutes
        self.heartbeat_system = None
        
        # Initialize heartbeat system
        if self.heartbeat_url:
            self.heartbeat_system = HeartbeatSystem(self.heartbeat_url, self.heartbeat_interval)
            print(f"✅ Heartbeat system configured (interval: {self.heartbeat_interval}s)")
        
        # Initialize Notion client if configured
        if self.notion_token and self.notion_database_id:
            try:
                self.notion_client = Client(auth=self.notion_token)
                print("✅ Notion client initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing Notion: {e}")
                self.notion_client = None
        
        # Discord client (self-bot)
        self.client = discord.Client()
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Configure events
        self._setup_events()
    
    def _parse_channel_ids(self, channel_ids_str: str) -> List[str]:
        """Parse comma-separated channel IDs, ignoring comments"""
        if not channel_ids_str.strip():
            return []
        
        # Remove comments (everything after #)
        clean_str = channel_ids_str.split('#')[0].strip()
        
        if not clean_str:
            return []
            
        return [cid.strip() for cid in clean_str.split(',') if cid.strip()]
    
    def _setup_events(self):
        """Configure Discord event handlers"""
        
        @self.client.event
        async def on_ready():
            if self.client.user:
                print(f"🤖 Bot connected as: {self.client.user}")
                print(f"🆔 User ID: {self.client.user.id}")
            print(f"📝 Monitoring server: {self.target_server_id}")
            
            if self.target_channel_ids:
                print(f"📋 Specific channels: {', '.join(self.target_channel_ids)}")
            else:
                print("📋 Monitoring ALL channels in the server")
            
            print(f"📁 Saving messages to: {self.log_file}")
            
            # Start heartbeat system
            if self.heartbeat_system:
                print("💓 Starting heartbeat system...")
                asyncio.create_task(self.heartbeat_system.start_heartbeat())
            
            print("-" * 60)
            
            # Check if target server exists
            target_server = self._get_target_server()
            if target_server:
                print(f"✅ Server found: {target_server.name}")
                if hasattr(target_server, 'member_count'):
                    print(f"👥 Members: {target_server.member_count}")
            else:
                print(f"❌ Server not found! Check the server ID.")
            print("-" * 60)
        
        @self.client.event
        async def on_message(message):
            # Log all messages matching monitoring criteria
            if self._should_monitor_message(message):
                await self._log_message(message)
        
        @self.client.event
        async def on_error(event, *args, **kwargs):
            print(f"❌ Error in event {event}: {args}")
            
            # Send error ping to heartbeat system
            if self.heartbeat_system:
                await self.heartbeat_system.send_ping("fail", f"Error in event {event}: {str(args)[:100]}")
        
        @self.client.event
        async def on_disconnect():
            print("🔌 Bot disconnected")
            
            # Send disconnect ping
            if self.heartbeat_system:
                await self.heartbeat_system.send_ping("fail", "Bot disconnected from Discord")
        
        @self.client.event
        async def on_resumed():
            print("🔄 Connection resumed")
            
            # Send reconnect ping
            if self.heartbeat_system:
                await self.heartbeat_system.send_ping("success", "Connection resumed successfully")
    
    def _should_monitor_message(self, message: discord.Message) -> bool:
        """Determine if the message should be logged"""
        # Ignore messages without guild (DMs) unless specifically configured
        if not message.guild:
            return False
            
        # Check if message is from the target server
        if str(message.guild.id) != self.target_server_id:
            return False
        
        # If specific channels are configured, check if message is from one of them
        if self.target_channel_ids:
            return str(message.channel.id) in self.target_channel_ids
        
        # If no specific channels, monitor all channels in the server
        return True
    
    def _get_target_server(self) -> Optional[discord.Guild]:
        """Get the target server for monitoring"""
        if not self.target_server_id or not self.target_server_id.isdigit():
            return None
        return discord.utils.get(self.client.guilds, id=int(self.target_server_id))
    
    async def _find_message_in_notion(self, message_id: str) -> Optional[str]:
        """
        Search for a message in Notion by its ID and return the Notion page URL
        """
        if not self.notion_client or not self.notion_database_id:
            return None
        
        try:
            # Search Notion database using message ID
            query_filter = {
                "property": "Message ID",
                "title": {
                    "equals": message_id
                }
            }
            
            print(f"🔍 Searching message in Notion: {message_id}")
            
            # Query in a thread to avoid blocking the event loop
            response = await asyncio.to_thread(
                self.notion_client.databases.query,
                database_id=self.notion_database_id,
                filter=query_filter
            )
            
            # Access results directly (notion-client 2.2.1 returns a dict)
            results = response['results']  # type: ignore
            
            if results and len(results) > 0:
                page_id = results[0]['id']
                # Generate Notion page URL
                page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
                print(f"✅ Message found in Notion: {page_url}")
                return page_url
            else:
                print(f"❌ Message not found in Notion: {message_id}")
                return None
            
        except Exception as e:
            print(f"❌ Error searching message in Notion: {e}")
            return None
    
    async def _save_message_to_notion(self, message: discord.Message):
        """Save message to Notion database with support for replies"""
        if not self.notion_client or not self.notion_database_id:
            return False
        
        try:
            # Get message info
            server_name = message.guild.name if message.guild else 'DM'
            
            try:
                channel_name = getattr(message.channel, 'name', 'DM')
            except:
                channel_name = 'DM'
            
            # Get author name
            author_name = f"@{message.author.name}"
            
            content = message.content or '[No text content]'
            
            # Discord message ID
            message_id = str(message.id)
            
            # Check for attachments
            has_attachment = len(message.attachments) > 0
            
            # Prepare attachments for Notion (only file URLs)
            attachment_files = []
            if has_attachment:
                for attachment in message.attachments:
                    attachment_files.append({
                        "name": attachment.filename,
                        "external": {
                            "url": attachment.url
                        }
                    })
            
            # Check for URLs in content
            import re
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, content)
            has_url = len(urls) > 0
            url_adjunta = urls[0] if urls else ""
            
            # Original message URL
            message_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else ""
            
            # ISO formatted date
            fecha_mensaje = message.created_at.isoformat()
            
            # Check if message is a reply
            replied_message_notion_url = None
            if message.reference and message.reference.message_id:
                replied_message_id = str(message.reference.message_id)
                replied_message_notion_url = await self._find_message_in_notion(replied_message_id)
                
                if replied_message_notion_url:
                    print(f"🔗 Message is a reply to: {replied_message_id}")
                else:
                    print(f"⚠️  Original message not found in Notion: {replied_message_id}")
            
            # Create Notion page object
            notion_page = {
                "parent": {"database_id": self.notion_database_id},
                "properties": {
                    "Message ID": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": message_id
                                }
                            }
                        ]
                    },
                    "Author": {
                        "title": [
                            {
                                "text": {
                                    "content": author_name
                                }
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": fecha_mensaje
                        }
                    },
                    "Server": {
                        "select": {
                            "name": server_name
                        }
                    },
                    "Channel": {
                        "select": {
                            "name": channel_name
                        }
                    },
                    "Content": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": content[:2000]  # Notion character limit
                                }
                            }
                        ]
                    },
                    "Attached URL": {
                        "url": url_adjunta if has_url else None
                    },
                    "Message URL": {
                        "url": message_url if message_url else None
                    }
                }
            }
            
            # Add attachments if present
            if attachment_files:
                notion_page["properties"]["Attached File"] = {
                    "files": attachment_files
                }
            
            # Add original message URL if reply
            if replied_message_notion_url:
                notion_page["properties"]["Original Message"] = {
                    "url": replied_message_notion_url
                }
            
            # Create Notion page in a thread to avoid blocking
            response = await asyncio.to_thread(
                self.notion_client.pages.create,
                **notion_page
            )
            
            reply_info = " (reply)" if replied_message_notion_url else ""
            print(f"✅ Message saved in Notion: {author_name} in #{channel_name}{reply_info}")
            return response
            
        except Exception as e:
            print(f"❌ Error saving message in Notion: {e}")
            return None
        
    async def _log_message(self, message: discord.Message):
        """Log message in Notion and as backup in text file"""
        try:
            # Try saving to Notion first
            notion_success = False
            if self.notion_client:
                notion_response = await self._save_message_to_notion(message)
                notion_success = bool(notion_response)
            
            # If Notion fails or is not configured, use text file as backup
            if not notion_success:
                self._log_message_to_file(message)
                
        except Exception as e:
            print(f"❌ Error logging message: {e}")
            # As last resort, try saving to file
            try:
                self._log_message_to_file(message)
            except:
                print(f"❌ Critical error: Could not save message by any method")
    
    def _log_message_to_file(self, message: discord.Message):
        """Log message to text file (backup method)"""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            # Get server and channel name
            server_name = message.guild.name if message.guild else 'DM'
            
            try:
                channel_name = getattr(message.channel, 'name', 'DM')
            except:
                channel_name = 'DM'
            
            # Get author name
            author_name = f"@{message.author.name}"
            
            content = message.content or '[No text content]'
            
            # Attachment info
            attachments_info = ""
            if message.attachments:
                attachments_info = f" [Attachments: {len(message.attachments)}]"
            
            # Embed info
            embeds_info = ""
            if message.embeds:
                embeds_info = f" [Embeds: {len(message.embeds)}]"
            
            # Log format
            log_entry = f"[{timestamp}] {server_name} > #{channel_name} | {author_name}: {content}{attachments_info}{embeds_info}\n"
            log_separator = "-" * 80 + "\n"
            
            # Write to file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.write(log_separator)
            
            # Show in console
            print(f"📝 [BACKUP FILE] [{server_name}] #{channel_name} | {author_name}: {content[:50]}{'...' if len(content) > 50 else ''}")
            
        except Exception as e:
            print(f"❌ Error logging message to file: {e}")
    
    def validate_config(self) -> bool:
        """Validate bot configuration"""
        if not self.token:
            print("❌ Discord token not found. Set DISCORD_TOKEN in the .env file")
            return False
        
        if not self.target_server_id:
            print("❌ Server ID not configured. Set MONITORING_SERVER_ID in the .env file")
            return False
        
        # Notion configuration validation (optional but recommended)
        if not self.notion_token or not self.notion_database_id:
            print("⚠️  Notion configuration not found. Messages will be saved only to text file.")
            print("   To use Notion, set NOTION_TOKEN and NOTION_DATABASE_ID in the .env file")
        else:
            print("✅ Notion configuration found. Messages will be saved in Notion.")
        
        # Heartbeat configuration validation
        if not self.heartbeat_url:
            print("⚠️  Heartbeat URL not configured. Set HEALTHCHECKS_PING_URL in the .env file")
        else:
            print(f"✅ Heartbeat system configured: {self.heartbeat_url[:50]}...")
        
        return True
    
    def run(self):
        """Start the bot"""
        if not self.validate_config():
            return
        
        print("🚀 Starting Discord Message Listener...")
        print("📋 Configuration:")
        print(f"   - Server: {self.target_server_id}")
        print(f"   - Channels: {'Specific' if self.target_channel_ids else 'All'}")
        print(f"   - Notion: {'✅ Configured' if self.notion_client else '❌ Not configured'}")
        print(f"   - Heartbeats: {'✅ Configured' if self.heartbeat_system else '❌ Not configured'}")
        print(f"   - Backup file: {self.log_file}")
        print("-" * 60)
        
        try:
            if self.token:
                self.client.run(self.token)
            else:
                print("❌ Invalid token")
        except KeyboardInterrupt:
            print("\n⏹️ Stopping bot...")
            # Stop heartbeat system
            if self.heartbeat_system:
                asyncio.run(self.heartbeat_system.stop_heartbeat())
        except Exception as error:
            print(f"❌ Error starting bot: {error}")
            if "Improper token" in str(error):
                print("🔑 Make sure to use a valid Discord token")
            
            # Send critical error ping
            if self.heartbeat_system:
                asyncio.run(self.heartbeat_system.send_ping("fail", f"Critical error: {str(error)[:100]}"))
    
    async def get_heartbeat_status(self) -> dict:
        """Get heartbeat system status"""
        if not self.heartbeat_system:
            return {"status": "not_configured"}
        
        return self.heartbeat_system.get_status()
    
    async def send_manual_heartbeat(self, message: str = "Manual ping from bot"):
        """Send manual heartbeat"""
        if not self.heartbeat_system:
            return False
        
        return await self.heartbeat_system.send_manual_ping(message)

def main():
    """Main entry point"""
    listener = SimpleMessageListener()
    listener.run()

if __name__ == "__main__":
    main()
