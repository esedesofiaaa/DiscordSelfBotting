import discord
import os
import datetime
import asyncio
import aiohttp
import tempfile
import mimetypes
import json
import re
import random
import requests
from typing import Optional, List
from dotenv import load_dotenv
from notion_client import Client
from heartbeat_system import HeartbeatSystem
from google_drive_manager import GoogleDriveManager

# Import the quickUpload function for official Notion file uploads
def quickUpload(filePath: str, pageId: str, notionToken: str) -> Optional[dict]:
    """
    Official Notion file upload function using the Direct Upload API (3-step process).
    
    Args:
        filePath: Path to the local file to upload
        pageId: ID of the Notion page where the file will be attached (unused in upload step)
        notionToken: Notion API token
    
    Returns:
        Dict with file upload ID for Notion properties if successful, None if failed
    """
    import requests
    import os
    
    try:
        filename = os.path.basename(filePath)
        
        headers = {
            'Authorization': f'Bearer {notionToken}',
            'Notion-Version': '2022-06-28'
        }
        
        # Step 1: Create a file upload object (empty body)
        print(f"📁 Step 1: Creating file upload object for {filename}...")
        response = requests.post(
            'https://api.notion.com/v1/file_uploads',
            headers={**headers, 'Content-Type': 'application/json'},
            json={}  # Empty body as per official docs
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create file upload: {response.status_code} - {response.text}")
            return None
        
        upload_data = response.json()
        upload_id = upload_data.get('id')
        upload_url = upload_data.get('upload_url')
        
        if not upload_id or not upload_url:
            print("❌ No upload ID or upload URL in response")
            return None
        
        print(f"✅ File upload object created with ID: {upload_id}")
        
        # Step 2: Upload file content using multipart/form-data
        print(f"📁 Step 2: Uploading file content...")
        with open(filePath, 'rb') as f:
            files = {'file': (filename, f, mimetypes.guess_type(filename)[0] or 'application/octet-stream')}
            
            # Note: Don't set Content-Type header, let requests handle multipart boundary
            upload_response = requests.post(
                upload_url,  # This should be something like /v1/file_uploads/{id}/send
                headers={k: v for k, v in headers.items() if k != 'Content-Type'},  # Remove Content-Type
                files=files
            )
        
        if upload_response.status_code not in [200, 201]:
            print(f"❌ File upload failed: {upload_response.status_code} - {upload_response.text}")
            return None
        
        upload_result = upload_response.json()
        print(f"✅ File uploaded successfully: {filename}")
        
        # Step 3: Return file upload object for Notion properties
        # The file can now be attached using the upload_id
        file_info = {
            "type": "file_upload",
            "file_upload": {
                "id": upload_id
            },
            "name": filename
        }
        
        print(f"✅ File ready for attachment with ID: {upload_id}")
        return file_info
        
    except Exception as e:
        print(f"❌ Error in quickUpload: {e}")
        return None

# Load environment variables
load_dotenv()


class SimpleMessageListener:
    """
    Bot to read and upload all Discord messages from July 1st to current date
    
    Features:
    - Uploads files to Notion using official quickUpload function (3-step API process)
    - Supports Google Drive integration for file backup
    - Handles images and files with direct Notion upload
    - Rate limiting and retry logic for robust operation
    """
    
    def __init__(self):
        # Basic configuration
        self.token = os.getenv('DISCORD_TOKEN')
        self.target_server_id = os.getenv('MONITORING_SERVER_ID')
        self.target_channel_ids = self._parse_channel_ids(os.getenv('MONITORING_CHANNEL_IDS', ''))
        self.log_file = os.getenv('LOG_FILE', './logs/messages.json')
        
        # Date range configuration
        self.start_date = datetime.datetime(2025, 7, 18, 0, 42, tzinfo=datetime.timezone.utc)
        self.end_date = datetime.datetime.now(datetime.timezone.utc)
        
        # Processing control
        self.processed_messages = 0
        self.failed_messages = 0
        self.is_processing = False
        
        # Notion configuration
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.notion_client = None
        
        # Heartbeat configuration
        self.heartbeat_url = os.getenv('HEALTHCHECKS_PING_URL', 'https://hc-ping.com/f679a27c-8a41-4ae2-9504-78f1b260e71d')
        self.heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', '300'))  # Default: 5 minutes
        self.heartbeat_system = None
        
        # Google Drive configuration
        self.google_drive_enabled = os.getenv('GOOGLE_DRIVE_ENABLED', 'false').lower() == 'true'
        self.google_drive_credentials = os.getenv('GOOGLE_DRIVE_CREDENTIALS', 'credentials.json')
        self.google_drive_token = os.getenv('GOOGLE_DRIVE_TOKEN', 'token.json')
        self.google_drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', None)  # Specific folder ID
        self.google_drive_manager = None
        
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
        
        # Initialize Google Drive manager if enabled
        if self.google_drive_enabled:
            try:
                self.google_drive_manager = GoogleDriveManager(
                    credentials_path=self.google_drive_credentials,
                    token_path=self.google_drive_token,
                    target_folder_id=self.google_drive_folder_id  # Pass specific folder ID
                )
                print("✅ Google Drive manager created")
            except Exception as e:
                print(f"❌ Error creating Google Drive manager: {e}")
                self.google_drive_manager = None
        
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
                print("📋 Processing ALL channels in the server")
            
            print(f"📁 Saving messages to: {self.log_file}")
            print(f"📅 Date range: {self.start_date.date()} to {self.end_date.date()}")
            
            # Start heartbeat system
            if self.heartbeat_system:
                print("💓 Starting heartbeat system...")
                asyncio.create_task(self.heartbeat_system.start_heartbeat())
            
            # Initialize Google Drive if enabled
            if self.google_drive_manager:
                print("☁️ Initializing Google Drive...")
                drive_success = await self.google_drive_manager.initialize()
                if drive_success:
                    print("✅ Google Drive initialized successfully")
                else:
                    print("❌ Google Drive initialization failed")
                    self.google_drive_manager = None
            
            print("-" * 60)
            
            # Check if target server exists
            target_server = self._get_target_server()
            if target_server:
                print(f"✅ Server found: {target_server.name}")
                if hasattr(target_server, 'member_count'):
                    print(f"👥 Members: {target_server.member_count}")
                print("-" * 60)
                
                # Start message processing
                await self._process_all_messages()
            else:
                print(f"❌ Server not found! Check the server ID.")
                print("-" * 60)
                await self.client.close()
        
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
    
    async def _handle_rate_limit_error(self, error: Exception, attempt: int = 1):
        """
        Handle rate limiting errors with exponential backoff
        """
        if "429" in str(error) or "Too Many Requests" in str(error):
            # Exponential backoff: 2^attempt seconds
            backoff_delay = min(2 ** attempt, 60)  # Max 60 seconds
            print(f"⚠️ Rate limit hit! Backing off for {backoff_delay} seconds (attempt {attempt})")
            
            # Send rate limit warning to heartbeat
            if self.heartbeat_system:
                await self.heartbeat_system.send_ping("fail", f"Rate limit hit, backing off {backoff_delay}s")
            
            await asyncio.sleep(backoff_delay)
            return True
        return False

    async def _smart_delay(self, message_count: int):
        """
        Intelligent delay system to prevent rate limiting
        Adapts delay based on processing volume and adds randomization
        """
        base_delay = 0.5  # 2 requests/second base (much safer than 0.1s)
        
        if message_count % 100 == 0:
            # Longer pause every 100 messages for cooling down
            delay = base_delay * 2
            print(f"🛑 Extended cooling period (100 messages): {delay}s")
            await asyncio.sleep(delay)
        elif message_count % 50 == 0:
            # Medium pause every 50 messages
            delay = base_delay * 1.5
            print(f"⏸️ Medium pause (50 messages): {delay}s")
            await asyncio.sleep(delay)
        else:
            # Regular delay with randomization to avoid patterns
            random_offset = random.uniform(0, 0.3)
            delay = base_delay + random_offset
            await asyncio.sleep(delay)

    async def _upload_file_to_notion_official(self, temp_path: str, filename: str, message_id: str) -> Optional[dict]:
        """
        Upload file directly to Notion using the official quickUpload function
        Returns file object that can be used in Notion properties
        """
        try:
            print(f"📁 Uploading {filename} directly to Notion via official API...")
            
            if not self.notion_token:
                print("❌ No Notion token available")
                return None
            
            # Use the official 3-step API process
            return await self._upload_file_direct_to_notion(temp_path, filename, message_id)
                        
        except Exception as e:
            print(f"❌ Error uploading {filename} to Notion: {e}")
            return None

    async def _upload_file_to_existing_page(self, temp_path: str, filename: str, page_id: str) -> Optional[dict]:
        """
        Upload file to an existing Notion page using the quickUpload function
        """
        try:
            if not self.notion_token:
                print("❌ No Notion token available")
                return None
            
            print(f"📁 Uploading {filename} to existing Notion page via quickUpload...")
            
            # Use quickUpload function in a thread to avoid blocking
            def _upload_sync():
                # Type assertion since we've already checked that notion_token is not None
                notion_token: str = self.notion_token  # type: ignore
                return quickUpload(temp_path, page_id, notion_token)
            
            result = await asyncio.to_thread(_upload_sync)
            
            if result:
                print(f"✅ File uploaded to existing page successfully: {filename}")
            else:
                print(f"❌ Failed to upload {filename} to existing page")
            
            return result
                        
        except Exception as e:
            print(f"❌ Error uploading {filename} to existing page: {e}")
            return None

    async def _upload_file_direct_to_notion(self, temp_path: str, filename: str, message_id: str) -> Optional[dict]:
        """
        Upload file directly to Notion using the official Direct Upload API (3-step process)
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.notion_token}',
                'Notion-Version': '2022-06-28'
            }
            
            async with aiohttp.ClientSession() as session:
                # Step 1: Create file upload object (empty body)
                print(f"📁 Step 1: Creating file upload object for {filename}...")
                async with session.post(
                    'https://api.notion.com/v1/file_uploads',
                    headers={**headers, 'Content-Type': 'application/json'},
                    json={}  # Empty body as per official docs
                ) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        print(f"❌ Failed to create file upload: {response.status} - {response_text}")
                        return None
                    
                    upload_data = await response.json()
                    upload_id = upload_data.get('id')
                    upload_url = upload_data.get('upload_url')
                    
                    if not upload_id or not upload_url:
                        print("❌ No upload ID or upload URL in response")
                        return None
                    
                    print(f"✅ File upload object created with ID: {upload_id}")
                    
                    # Step 2: Upload file content using multipart/form-data
                    print(f"📁 Step 2: Uploading file content...")
                    
                    # Read file content
                    def _read_file_content():
                        with open(temp_path, 'rb') as f:
                            return f.read()
                    
                    file_content = await asyncio.to_thread(_read_file_content)
                    
                    # Create multipart form data
                    form_data = aiohttp.FormData()
                    mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                    form_data.add_field('file', file_content, filename=filename, content_type=mime_type)
                    
                    # Upload the file (don't set Content-Type header, let aiohttp handle multipart boundary)
                    upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
                    async with session.post(
                        upload_url,  # This should be something like /v1/file_uploads/{id}/send
                        headers=upload_headers,
                        data=form_data
                    ) as upload_response:
                        if upload_response.status not in [200, 201]:
                            upload_text = await upload_response.text()
                            print(f"❌ File upload failed: {upload_response.status} - {upload_text}")
                            return None
                        
                        upload_result = await upload_response.json()
                        print(f"✅ File uploaded successfully: {filename}")
                        
                        # Step 3: Return file upload object for Notion properties
                        # The file can now be attached using the upload_id
                        file_info = {
                            "type": "file_upload",
                            "file_upload": {
                                "id": upload_id
                            },
                            "name": filename
                        }
                        
                        print(f"✅ File ready for attachment with ID: {upload_id}")
                        return file_info
                        
        except Exception as e:
            print(f"❌ Error in direct Notion upload: {e}")
            return None

    async def _process_all_messages(self):
        """Process all messages from the specified date range"""
        if self.is_processing:
            print("⚠️ Processing already in progress")
            return
        
        self.is_processing = True
        self.processed_messages = 0
        self.failed_messages = 0
        
        try:
            target_server = self._get_target_server()
            if not target_server:
                print("❌ Target server not found")
                return
            
            print(f"🔍 Starting to process messages from {self.start_date.date()} to {self.end_date.date()}")
            
            # Get channels to process
            channels_to_process = []
            
            if self.target_channel_ids:
                # Process specific channels
                for channel_id in self.target_channel_ids:
                    try:
                        channel = target_server.get_channel(int(channel_id))
                        if channel and isinstance(channel, discord.TextChannel):
                            channels_to_process.append(channel)
                        else:
                            print(f"⚠️ Channel not found or not a text channel: {channel_id}")
                    except ValueError:
                        print(f"⚠️ Invalid channel ID: {channel_id}")
            else:
                # Process all text channels
                channels_to_process = [ch for ch in target_server.channels if isinstance(ch, discord.TextChannel)]
            
            print(f"📋 Found {len(channels_to_process)} channels to process")
            
            for channel in channels_to_process:
                await self._process_channel_messages(channel)
                
                # Send progress heartbeat
                if self.heartbeat_system:
                    progress_msg = f"Processed {self.processed_messages} messages, failed: {self.failed_messages}"
                    await self.heartbeat_system.send_ping("success", progress_msg)
            
            # Final summary
            print("-" * 60)
            print(f"✅ Processing completed!")
            print(f"📊 Total messages processed: {self.processed_messages}")
            print(f"❌ Failed messages: {self.failed_messages}")
            print(f"💾 Messages saved to: {self.log_file}")
            
            # Send completion heartbeat
            if self.heartbeat_system:
                completion_msg = f"Processing completed. Total: {self.processed_messages}, Failed: {self.failed_messages}"
                await self.heartbeat_system.send_ping("success", completion_msg)
            
            print("-" * 60)
            print("🏁 Bot will close in 5 seconds...")
            await asyncio.sleep(5)
            await self.client.close()
            
        except Exception as e:
            print(f"❌ Error during message processing: {e}")
            
            # Send error heartbeat
            if self.heartbeat_system:
                await self.heartbeat_system.send_ping("fail", f"Processing error: {str(e)[:100]}")
            
        finally:
            self.is_processing = False
    
    async def _process_channel_messages(self, channel: discord.TextChannel):
        """Process all messages in a specific channel within the date range"""
        try:
            print(f"📝 Processing channel: #{channel.name}")
            
            channel_message_count = 0
            
            # Get messages in the date range using Discord's history
            async for message in channel.history(
                limit=None,
                after=self.start_date,
                before=self.end_date,
                oldest_first=True
            ):
                try:
                    # Process the message with retry logic for rate limits
                    max_retries = 3
                    for attempt in range(1, max_retries + 1):
                        try:
                            await self._log_message(message)
                            break  # Success, exit retry loop
                        except Exception as msg_error:
                            # Check if it's a rate limit error
                            if await self._handle_rate_limit_error(msg_error, attempt):
                                if attempt < max_retries:
                                    print(f"🔄 Retrying message processing (attempt {attempt + 1}/{max_retries})")
                                    continue
                                else:
                                    print(f"❌ Max retries reached for message {message.id}")
                                    raise msg_error
                            else:
                                # Not a rate limit error, re-raise immediately
                                raise msg_error
                    
                    self.processed_messages += 1
                    channel_message_count += 1
                    
                    # Show progress every 50 messages
                    if self.processed_messages % 50 == 0:
                        print(f"📊 Progress: {self.processed_messages} messages processed...")
                    
                    # Smart delay to prevent rate limiting
                    await self._smart_delay(self.processed_messages)
                    
                except Exception as e:
                    print(f"❌ Error processing message {message.id}: {e}")
                    self.failed_messages += 1
            
            print(f"✅ Channel #{channel.name} completed: {channel_message_count} messages")
            
        except discord.Forbidden:
            print(f"❌ No access to channel #{channel.name}")
        except Exception as e:
            print(f"❌ Error processing channel #{channel.name}: {e}")
    
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
    
    async def _process_attachment_with_tempfile(self, attachment: discord.Attachment, message_id: str) -> Optional[dict]:
        """
        Process Discord attachment: download, upload to Google Drive, and return file info
        Returns file info with Google Drive URL or Discord URL as fallback
        Also determines if the file is an image for direct Notion upload
        """
        try:
            print(f"📥 Processing attachment: {attachment.filename}")
            
            # Create safe filename for extension detection
            safe_filename = "".join(c for c in attachment.filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
            
            # Get file extension
            _, ext = os.path.splitext(attachment.filename)
            if not ext:
                ext = '.tmp'
            
            # Check if it's an image file
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.tif'}
            is_image = ext.lower() in image_extensions
            
            # Download file from Discord using temporary file
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as response:
                    if response.status == 200:
                        # Use temporary file that will be automatically deleted
                        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                            temp_path = temp_file.name
                            
                            # Download to temporary file
                            async for chunk in response.content.iter_chunked(8192):
                                temp_file.write(chunk)
                        
                        print(f"✅ Attachment downloaded to temporary file: {attachment.filename}")
                        
                        # Get file info using async file operations
                        def _get_file_size():
                            return os.path.getsize(temp_path)
                        
                        file_size = await asyncio.to_thread(_get_file_size)
                        mime_type, _ = mimetypes.guess_type(attachment.filename)
                        
                        # Try to upload to Google Drive if enabled
                        google_drive_info = None
                        final_url = attachment.url  # Fallback to Discord URL
                        upload_method = "discord"
                        
                        if self.google_drive_manager and self.google_drive_manager.is_initialized():
                            print(f"☁️ Uploading {attachment.filename} to Google Drive...")
                            google_drive_info = await self.google_drive_manager.upload_file(
                                temp_path, 
                                attachment.filename, 
                                message_id
                            )
                            
                            if google_drive_info:
                                final_url = google_drive_info['shareable_link']
                                upload_method = "google_drive"
                                print(f"✅ File uploaded to Google Drive: {attachment.filename}")
                            else:
                                print(f"⚠️ Google Drive upload failed, using Discord URL: {attachment.filename}")
                        else:
                            print(f"⚠️ Google Drive not available, using Discord URL: {attachment.filename}")
                        
                        file_info = {
                            "filename": attachment.filename,
                            "safe_filename": safe_filename,
                            "original_url": attachment.url,
                            "final_url": final_url,
                            "upload_method": upload_method,
                            "temp_path": temp_path,
                            "size": file_size,
                            "discord_size": attachment.size,
                            "mime_type": mime_type or 'application/octet-stream',
                            "width": getattr(attachment, 'width', None),
                            "height": getattr(attachment, 'height', None),
                            "google_drive_info": google_drive_info,
                            "is_image": is_image,
                            "extension": ext.lower(),
                            "cleanup_needed": True  # Mark for cleanup after Notion upload
                        }
                        
                        # Note: Don't clean up temp file yet - we might need it for direct Notion upload
                        return file_info
                    else:
                        print(f"❌ Failed to download attachment: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error processing attachment {attachment.filename}: {e}")
            return None
    
    async def _upload_image_to_notion(self, temp_path: str, filename: str) -> Optional[dict]:
        """
        Upload image file directly to Notion using internal API (experimental)
        This uses Notion's internal file upload endpoint that the web client uses
        """
        try:
            print(f"🖼️ Attempting direct upload to Notion: {filename}")
            
            # Read file content
            def _read_file_content():
                with open(temp_path, 'rb') as f:
                    return f.read()
            
            file_content = await asyncio.to_thread(_read_file_content)
            
            # Get file info
            file_size = len(file_content)
            mime_type, _ = mimetypes.guess_type(filename)
            
            # Try to use Notion's internal file upload API
            # This is experimental and uses undocumented endpoints
            notion_headers = {
                'Authorization': f'Bearer {self.notion_token}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            
            try:
                # Step 1: Request upload URL from Notion
                async with aiohttp.ClientSession() as session:
                    # First, get signed upload URL
                    upload_request = {
                        "name": filename,
                        "contentType": mime_type or 'image/png'
                    }
                    
                    async with session.post(
                        'https://api.notion.com/v1/files',
                        headers=notion_headers,
                        json=upload_request
                    ) as response:
                        if response.status == 200:
                            upload_data = await response.json()
                            
                            # Extract upload URL and file info
                            if 'url' in upload_data:
                                file_url = upload_data['url']
                                
                                print(f"✅ Got Notion upload URL for: {filename}")
                                
                                # Return file object for Notion
                                return {
                                    "name": filename,
                                    "file": {
                                        "url": file_url
                                    }
                                }
                            else:
                                print(f"⚠️ Notion didn't return upload URL for: {filename}")
                                return None
                        else:
                            print(f"⚠️ Notion file upload request failed: {response.status}")
                            return None
                            
            except Exception as upload_error:
                print(f"⚠️ Notion direct upload failed: {upload_error}")
                return None
            
        except Exception as e:
            print(f"❌ Error in direct Notion upload: {e}")
            return None

    async def _cleanup_temp_files(self, temp_file_paths: List[str]):
        """Clean up temporary files asynchronously"""
        for temp_path in temp_file_paths:
            try:
                def _cleanup_single_file():
                    try:
                        os.unlink(temp_path)
                        return True
                    except OSError as e:
                        print(f"⚠️ Could not delete temporary file: {temp_path} - {e}")
                        return False
                
                cleanup_success = await asyncio.to_thread(_cleanup_single_file)
                if cleanup_success:
                    print(f"🧹 Temporary file cleaned up: {os.path.basename(temp_path)}")
                    
            except Exception as e:
                print(f"❌ Error cleaning up temp file {temp_path}: {e}")

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
            
            # Check for attachments and process them
            has_attachment = len(message.attachments) > 0
            
            # Process attachments - using temporary files
            attachment_files = []
            preview_images = []  # New list for Preview Images property
            temp_files_to_cleanup = []  # Track temp files for cleanup
            
            if has_attachment:
                for attachment in message.attachments:
                    # Try to process the attachment with Google Drive integration
                    file_info = await self._process_attachment_with_tempfile(attachment, message_id)
                    
                    # Small additional delay between attachment processing to prevent rate limiting
                    await asyncio.sleep(0.2)  # 200ms between attachments
                    
                    if file_info:
                        # Successfully processed (either Google Drive or Discord URL)
                        upload_method = file_info.get('upload_method', 'discord')
                        final_url = file_info.get('final_url', file_info['original_url'])
                        is_image = file_info.get('is_image', False)
                        
                        print(f"✅ Attachment processed ({upload_method}): {file_info['filename']}")
                        
                        # Create Notion file object with the final URL (Google Drive or Discord)
                        file_entry = {
                            "name": file_info['filename'],
                            "external": {
                                "url": final_url
                            }
                        }
                        
                        # If it's an image, add to both attachment_files and preview_images
                        if is_image:
                            # Try direct upload to Notion using official API
                            direct_notion_file = await self._upload_file_to_notion_official(
                                file_info['temp_path'], 
                                file_info['filename'],
                                message_id
                            )
                            
                            if direct_notion_file:
                                # Successfully uploaded directly to Notion
                                preview_images.append(direct_notion_file)
                                print(f"🖼️ Image uploaded directly to Notion: {file_info['filename']}")
                            else:
                                # Fallback to external URL
                                preview_image_entry = {
                                    "name": f"🖼️ {file_info['filename']}",
                                    "external": {
                                        "url": file_info['original_url']  # Use original Discord URL for images
                                    }
                                }
                                preview_images.append(preview_image_entry)
                                print(f"🖼️ Image added to Preview Images (external URL): {file_info['filename']}")
                        
                        # For non-images, try to upload to Notion as well for the regular Attached File property
                        else:
                            # Try direct upload to Notion for non-images too
                            direct_notion_file = await self._upload_file_to_notion_official(
                                file_info['temp_path'], 
                                file_info['filename'],
                                message_id
                            )
                            
                            if direct_notion_file:
                                # Use Notion-hosted file
                                file_entry = direct_notion_file
                                print(f"📁 File uploaded directly to Notion: {file_info['filename']}")
                            # Otherwise keep the existing file_entry with external URL
                        
                        attachment_files.append(file_entry)
                        
                        # Add upload method info to filename if it's Google Drive
                        if upload_method == "google_drive":
                            file_entry["name"] = f"📁 {file_info['filename']}"  # Add Drive icon
                        
                        # Track temp file for cleanup
                        if file_info.get('cleanup_needed') and file_info.get('temp_path'):
                            temp_files_to_cleanup.append(file_info['temp_path'])
                    else:
                        # Fall back to just external URL if processing fails
                        print(f"⚠️ Could not process attachment, using Discord URL only: {attachment.filename}")
                        attachment_files.append({
                            "name": attachment.filename,
                            "external": {
                                "url": attachment.url
                            }
                        })
            
            # Don't clean up temporary files yet - we need them for quickUpload later
            # They will be cleaned up after the quickUpload attempts
            
            # Check for URLs in content
            import re
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, content)
            has_url = len(urls) > 0
            attached_url = urls[0] if urls else ""
            
            # Original message URL
            message_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else ""
            
            # ISO formatted date
            message_date = message.created_at.isoformat()
            
            # Check if message is a reply
            replied_message_notion_url = None
            if message.reference and message.reference.message_id:
                replied_message_id = str(message.reference.message_id)
                replied_message_notion_url = await self._find_message_in_notion(replied_message_id)
                
                if replied_message_notion_url:
                    print(f"🔗 Message is a reply to: {replied_message_id}")
                else:
                    print(f"⚠️  Original message not found in Notion: {replied_message_id}")
            
            # Create children blocks for page content
            page_children = [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"📧 Discord Message"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"👤 Author: {author_name}\n🖥️ Server: {server_name}\n📺 Channel: #{channel_name}\n📅 Date: {message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "💬 Message content:"
                                },
                                "annotations": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "quote",
                    "quote": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content if len(content) <= 2000 else content[:1997] + "..."
                                }
                            }
                        ]
                    }
                }
            ]
            
            # Add attachment information if present
            if has_attachment:
                page_children.extend([
                    {
                        "object": "block",
                        "type": "divider",
                        "divider": {}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"📎 Attached files ({len(message.attachments)}):"
                                    },
                                    "annotations": {
                                        "bold": True
                                    }
                                }
                            ]
                        }
                    }
                ])
                
                # Add each attachment as a bullet point
                for attachment in message.attachments:
                    is_image = any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.tif'])
                    file_icon = "🖼️" if is_image else "📄"
                    page_children.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"{file_icon} {attachment.filename} ({attachment.size} bytes)"
                                    }
                                }
                            ]
                        }
                    })
            
            # Add URL information if present
            if has_url:
                page_children.extend([
                    {
                        "object": "block",
                        "type": "divider",
                        "divider": {}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "� URL found in the message:"
                                    },
                                    "annotations": {
                                        "bold": True
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": attached_url
                                    },
                                    "href": attached_url
                                }
                            ]
                        }
                    }
                ])
            
            # Add reply information if present
            if replied_message_notion_url:
                page_children.extend([
                    {
                        "object": "block",
                        "type": "divider",
                        "divider": {}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "💬 This message is a reply to:"
                                    },
                                    "annotations": {
                                        "bold": True
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "View original message"
                                    },
                                    "href": replied_message_notion_url
                                }
                            ]
                        }
                    }
                ])

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
                            "start": message_date
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
                        "url": attached_url if has_url else None
                    },
                    "Message URL": {
                        "url": message_url if message_url else None
                    }
                },
                "children": page_children
            }
            
            # Add attachments if present
            if attachment_files:
                notion_page["properties"]["Attached File"] = {
                    "files": attachment_files
                }
            
            # Add preview images if present
            if preview_images:
                notion_page["properties"]["Preview Images"] = {
                    "files": preview_images
                }
                print(f"🖼️ Added {len(preview_images)} images to Preview Images property")
            
            # Add original message URL if reply
            if replied_message_notion_url:
                notion_page["properties"]["Original Message"] = {
                    "url": replied_message_notion_url
                }
            
            # Create Notion page in a thread to avoid blocking with retry logic
            max_notion_retries = 3
            response = None
            for attempt in range(1, max_notion_retries + 1):
                try:
                    response = await asyncio.to_thread(
                        self.notion_client.pages.create,
                        **notion_page
                    )
                    break  # Success
                except Exception as notion_error:
                    if await self._handle_rate_limit_error(notion_error, attempt):
                        if attempt < max_notion_retries:
                            print(f"🔄 Retrying Notion save (attempt {attempt + 1}/{max_notion_retries})")
                            continue
                        else:
                            print(f"❌ Max Notion retries reached for message {message_id}")
                            return None
                    else:
                        # Not a rate limit error, re-raise
                        raise notion_error
            
            # If we successfully created the page and have temp files, upload them using quickUpload
            if response and temp_files_to_cleanup:
                page_id = response['id']  # type: ignore
                print(f"📄 Page created successfully, now uploading files using quickUpload...")
                
                # Upload files to the created page using quickUpload
                uploaded_files_via_quick = []
                for temp_path in temp_files_to_cleanup:
                    # Find the corresponding filename
                    filename = os.path.basename(temp_path)
                    
                    # Try to upload using quickUpload
                    quick_upload_result = await self._upload_file_to_existing_page(temp_path, filename, page_id)
                    
                    if quick_upload_result:
                        uploaded_files_via_quick.append(quick_upload_result)
                        print(f"✅ File {filename} uploaded via quickUpload")
                    else:
                        print(f"⚠️ quickUpload failed for {filename}, file was already included via external URL")
                
                # If we have successfully uploaded files via quickUpload, update the page
                if uploaded_files_via_quick:
                    try:
                        # Get existing properties
                        existing_attached_files = notion_page["properties"].get("Attached File", {}).get("files", [])
                        existing_preview_images = notion_page["properties"].get("Preview Images", {}).get("files", [])
                        
                        # Add quickUpload files to existing ones
                        all_attached_files = existing_attached_files + uploaded_files_via_quick
                        
                        # Update the page with quickUpload files
                        update_properties = {
                            "Attached File": {
                                "files": all_attached_files
                            }
                        }
                        
                        # Note: No need to add to Preview Images again as they were already added during initial processing
                        
                        # Update the page with new file properties
                        await asyncio.to_thread(
                            self.notion_client.pages.update,
                            page_id=page_id,
                            properties=update_properties
                        )
                        
                        print(f"✅ Page updated with {len(uploaded_files_via_quick)} files via quickUpload")
                        
                    except Exception as update_error:
                        print(f"⚠️ Failed to update page with quickUpload files: {update_error}")
                
                # Clean up temporary files after quickUpload attempts
                if temp_files_to_cleanup:
                    await self._cleanup_temp_files(temp_files_to_cleanup)
            else:
                # Clean up temp files even if page creation failed or no temp files for quickUpload
                if temp_files_to_cleanup:
                    await self._cleanup_temp_files(temp_files_to_cleanup)
            
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
                await self._log_message_to_file(message)
                
        except Exception as e:
            print(f"❌ Error logging message: {e}")
            # As last resort, try saving to file
            try:
                await self._log_message_to_file(message)
            except:
                print(f"❌ Critical error: Could not save message by any method")
    
    async def _log_message_to_file(self, message: discord.Message):
        """Log message to JSON file (backup method) - Asynchronous version"""
        try:
            import json
            
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
            
            # Check for URLs in content
            import re
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, content)
            has_url = len(urls) > 0
            attached_url = urls[0] if urls else None
            
            # Original message URL
            message_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else None
            
            # ISO formatted date
            message_date = message.created_at.isoformat()
            
            # Process attachments
            attached_files = []
            preview_images_info = []  # For backup logging
            if message.attachments:
                for attachment in message.attachments:
                    # Check if it's an image
                    _, ext = os.path.splitext(attachment.filename)
                    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.tif'}
                    is_image = ext.lower() in image_extensions
                    
                    attachment_info = {
                        "name": attachment.filename,
                        "url": attachment.url,
                        "size": attachment.size,
                        "width": getattr(attachment, 'width', None),
                        "height": getattr(attachment, 'height', None),
                        "is_image": is_image,
                        "extension": ext.lower()
                    }
                    
                    attached_files.append(attachment_info)
                    
                    # If it's an image, also add to preview images
                    if is_image:
                        preview_images_info.append({
                            "filename": attachment.filename,
                            "url": attachment.url,
                            "width": getattr(attachment, 'width', None),
                            "height": getattr(attachment, 'height', None)
                        })
            
            # Check if message is a reply
            original_message_id = None
            if message.reference and message.reference.message_id:
                original_message_id = str(message.reference.message_id)
            
            # Create JSON structure matching Notion fields
            message_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "message_id": message_id,
                "author": author_name,
                "date": message_date,
                "server": server_name,
                "channel": channel_name,
                "content": content,
                "attached_url": attached_url,
                "message_url": message_url,
                "attached_files": attached_files if attached_files else None,
                "preview_images": preview_images_info if preview_images_info else None,
                "original_message_id": original_message_id,
                "has_embeds": len(message.embeds) > 0,
                "embed_count": len(message.embeds) if message.embeds else 0,
                "image_count": len(preview_images_info) if preview_images_info else 0
            }
            
            # Change log file extension to .json
            json_log_file = self.log_file.replace('.txt', '.json')
            
            # Define async function for file operations
            def _read_write_json_file():
                # Read existing data or create new list
                try:
                    with open(json_log_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = []
                except (FileNotFoundError, json.JSONDecodeError):
                    existing_data = []
                
                # Append new message
                existing_data.append(message_data)
                
                # Write back to file
                with open(json_log_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
                return True
            
            # Execute file operations in a separate thread
            await asyncio.to_thread(_read_write_json_file)
            
            # Show in console with image info
            image_info = f" [🖼️{len(preview_images_info)} images]" if preview_images_info else ""
            print(f"📝 [BACKUP JSON] [{server_name}] #{channel_name} | {author_name}: {content[:50]}{'...' if len(content) > 50 else ''}{image_info}")
            
        except Exception as e:
            print(f"❌ Error logging message to JSON file: {e}")
            # Fallback to old text format if JSON fails
            try:
                timestamp = datetime.datetime.now().isoformat()
                log_entry = f"[{timestamp}] ERROR LOGGING JSON - {server_name} > #{channel_name} | {author_name}: {content}\n"
                
                # Async fallback write operation
                def _write_fallback():
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        f.write(log_entry)
                
                await asyncio.to_thread(_write_fallback)
            except:
                print(f"❌ Critical error: Could not save message by any method")
    
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
            print("   🖼️ Files will be uploaded directly to Notion via official 3-step upload API")
            print("   📁 All files appear in both 'Attached File' and 'Preview Images' (for images) properties")
            print("   🔄 Uses official endpoints: /files/upload, signed URL, /files/upload/{id}/complete")
        
        # Heartbeat configuration validation
        if not self.heartbeat_url:
            print("⚠️  Heartbeat URL not configured. Set HEALTHCHECKS_PING_URL in the .env file")
        else:
            print(f"✅ Heartbeat system configured: {self.heartbeat_url[:50]}...")
        
        # Google Drive configuration validation
        if self.google_drive_enabled:
            if not os.path.exists(self.google_drive_credentials):
                print(f"❌ Google Drive credentials not found: {self.google_drive_credentials}")
                print("   Download credentials.json from Google Cloud Console")
                print("   Set GOOGLE_DRIVE_ENABLED=false to disable Google Drive")
            else:
                print("✅ Google Drive enabled and credentials found")
                if self.google_drive_folder_id:
                    print(f"📁 Target folder ID: {self.google_drive_folder_id}")
                else:
                    print("📁 Will create 'Discord Attachments' folder in personal drive")
        else:
            print("⚠️  Google Drive disabled. Files will use Discord URLs only.")
            print("   Set GOOGLE_DRIVE_ENABLED=true to enable Google Drive uploads")
        
        return True
    
    def run(self):
        """Start the bot"""
        if not self.validate_config():
            return
        
        print("🚀 Starting Discord Message Listener...")
        print("📋 Configuration:")
        print(f"   - Server: {self.target_server_id}")
        print(f"   - Channels: {'Specific' if self.target_channel_ids else 'All'}")
        print(f"   - Notion: {'✅ Configured (Official 3-Step Upload API + Smart Rate Limiting)' if self.notion_client else '❌ Not configured'}")
        print(f"   - Google Drive: {'✅ Enabled' if self.google_drive_enabled else '❌ Disabled'}")
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

