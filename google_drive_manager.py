"""
Google Drive Manager for Discord Bot
Handles uploading files to Google Drive and returning shareable links
Updated to use Service Account instead of OAuth2 for server environments
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, Union
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


class GoogleDriveManager:
    """Manages Google Drive file uploads for Discord attachments using Service Account"""
    
    # Google Drive API scopes - includes shared drives access
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_path: str = 'service_account.json', token_path: Optional[str] = None, target_folder_id: Optional[str] = None):
        """
        Initialize Google Drive manager with Service Account
        
        Args:
            credentials_path: Path to Service Account JSON file (replaces OAuth2 credentials)
            token_path: Legacy parameter, ignored for Service Account compatibility
            target_folder_id: Specific folder ID to upload files (can be in shared drives)
        """
        self.credentials_path = credentials_path
        self.service: Optional[Any] = None
        self.credentials: Optional[service_account.Credentials] = None
        self.target_folder_id = target_folder_id  # User-specified folder ID
        self.folder_id: Optional[str] = None  # Final folder ID to use
        self._initialized = False
        
        # Legacy compatibility - ignore token_path for Service Account
        if token_path:
            print("ℹ️ Note: token_path parameter is ignored when using Service Account")
    
    async def initialize(self) -> bool:
        """
        Initialize Google Drive service with Service Account
        Returns True if successful, False otherwise
        """
        try:
            # Authenticate with Service Account
            if not await self._authenticate_service_account():
                return False
            
            # Build Google Drive service
            self.service = build('drive', 'v3', credentials=self.credentials)
            
            # Test connection and get service account info
            about = await self._test_connection()
            if not about:
                return False
            
            # Use specific folder ID or create/get Discord attachments folder
            if self.target_folder_id:
                # Verify the target folder exists and is accessible
                self.folder_id = await self._verify_target_folder()
            else:
                # Create or get Discord attachments folder in accessible drive
                self.folder_id = await self._get_or_create_discord_folder()
            
            if self.folder_id:
                print(f"✅ Google Drive initialized successfully with Service Account")
                print(f"📁 Target folder ID: {self.folder_id}")
                self._initialized = True
                return True
            else:
                print("❌ Failed to access target folder")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing Google Drive: {e}")
            return False
    
    async def _authenticate_service_account(self) -> bool:
        """Authenticate with Google Drive API using Service Account"""
        try:
            # Check if service account file exists
            if not os.path.exists(self.credentials_path):
                print(f"❌ Service account file not found: {self.credentials_path}")
                print("📋 To set up Service Account:")
                print("   1. Go to https://console.cloud.google.com/")
                print("   2. Navigate to IAM & Admin > Service Accounts")
                print("   3. Create a new Service Account")
                print("   4. Download the JSON key file")
                print("   5. Save it as 'service_account.json' in project root")
                return False
            
            # Load and validate service account credentials
            try:
                with open(self.credentials_path, 'r') as f:
                    creds_info = json.load(f)
                
                # Validate required fields
                required_fields = ['type', 'project_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if field not in creds_info]
                
                if missing_fields:
                    print(f"❌ Invalid service account file. Missing fields: {missing_fields}")
                    return False
                
                if creds_info['type'] != 'service_account':
                    print("❌ Invalid credentials type. Expected 'service_account'")
                    return False
                
                print(f"📧 Service Account Email: {creds_info['client_email']}")
                print(f"📁 Project ID: {creds_info['project_id']}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in service account file: {e}")
                return False
            
            # Create credentials from service account info
            self.credentials = service_account.Credentials.from_service_account_info(
                creds_info, scopes=self.SCOPES
            )
            
            print("✅ Service Account credentials loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error authenticating Service Account: {e}")
            return False
    
    async def _test_connection(self) -> Optional[Dict[str, Any]]:
        """Test connection to Google Drive API"""
        try:
            def _test_operations():
                if self.service is None:
                    return None
                    
                # Get information about the service account
                about = self.service.about().get(fields="user,storageQuota").execute()
                return about
            
            about = await asyncio.to_thread(_test_operations)
            
            if about:
                user_info = about.get('user', {})
                service_email = user_info.get('emailAddress', 'Unknown')
                print(f"✅ Connected to Google Drive as: {service_email}")
                return about
            else:
                print("❌ Failed to connect to Google Drive")
                return None
                
        except Exception as e:
            print(f"❌ Error testing Google Drive connection: {e}")
            return None
    
    async def _verify_target_folder(self) -> Optional[str]:
        """Verify that the target folder ID exists and is accessible"""
        if not self.service or not self.target_folder_id:
            return None
        
        try:
            def _verify_operations():
                try:
                    if self.service is None:
                        return None
                        
                    # Try to get folder metadata - works for both personal and shared drives
                    folder = self.service.files().get(
                        fileId=self.target_folder_id,
                        fields='id,name,mimeType,parents,driveId,capabilities',
                        supportsAllDrives=True
                    ).execute()
                    
                    if folder.get('mimeType') == 'application/vnd.google-apps.folder':
                        folder_name = folder.get('name', 'Unknown')
                        drive_id = folder.get('driveId')
                        capabilities = folder.get('capabilities', {})
                        
                        # Check if we can add files to this folder
                        can_add_children = capabilities.get('canAddChildren', False)
                        if not can_add_children:
                            print(f"❌ No permission to add files to folder '{folder_name}'")
                            print(f"   Share the folder with the service account email as Editor")
                            return None
                        
                        if drive_id:
                            print(f"📁 Using folder '{folder_name}' in shared drive: {self.target_folder_id}")
                        else:
                            print(f"📁 Using folder '{folder_name}' in personal drive: {self.target_folder_id}")
                        
                        return self.target_folder_id
                    else:
                        print(f"❌ Target ID is not a folder: {self.target_folder_id}")
                        return None
                        
                except HttpError as e:
                    if e.resp.status == 404:
                        print(f"❌ Folder not found or not accessible: {self.target_folder_id}")
                        print(f"   Make sure to share the folder with the service account")
                    elif e.resp.status == 403:
                        print(f"❌ Permission denied accessing folder: {self.target_folder_id}")
                        print(f"   Share the folder with the service account as Editor")
                    else:
                        print(f"❌ Error accessing folder {self.target_folder_id}: {e}")
                    return None
                except Exception as e:
                    print(f"❌ Unexpected error accessing folder {self.target_folder_id}: {e}")
                    return None
            
            return await asyncio.to_thread(_verify_operations)
            
        except Exception as e:
            print(f"❌ Error verifying target folder: {e}")
            return None
    
    async def _get_or_create_discord_folder(self) -> Optional[str]:
        """Get or create Discord Attachments folder in Google Drive"""
        if not self.service:
            return None
        
        try:
            def _folder_operations():
                if self.service is None:
                    return None
                    
                # Search for existing Discord Attachments folder
                query = "name='Discord Attachments' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.service.files().list(
                    q=query, 
                    fields="files(id, name)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                folders = results.get('files', [])
                
                if folders:
                    # Use existing folder
                    folder_id = folders[0]['id']
                    print(f"📁 Using existing Discord Attachments folder: {folder_id}")
                    return folder_id
                else:
                    # Create new folder in root of the service account's drive
                    folder_metadata = {
                        'name': 'Discord Attachments',
                        'mimeType': 'application/vnd.google-apps.folder',
                        'description': 'Folder for Discord bot file attachments'
                    }
                    folder = self.service.files().create(
                        body=folder_metadata, 
                        fields='id,name',
                        supportsAllDrives=True
                    ).execute()
                    folder_id = folder.get('id')
                    print(f"📁 Created new Discord Attachments folder: {folder_id}")
                    return folder_id
            
            return await asyncio.to_thread(_folder_operations)
            
        except Exception as e:
            print(f"❌ Error managing Discord folder: {e}")
            return None
    
    async def upload_file(self, file_path: str, original_filename: str, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Upload file to Google Drive and return file info with shareable link
        
        Args:
            file_path: Local path to file to upload
            original_filename: Original filename from Discord
            message_id: Discord message ID for organizing
            
        Returns:
            Dict with file info including shareable URL, or None if failed
        """
        if not self._initialized or not self.service or not self.folder_id:
            print("❌ Google Drive not initialized")
            return None
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        try:
            def _upload_operations():
                if self.service is None:
                    return None
                    
                # Create unique filename with message ID prefix
                safe_filename = f"msg_{message_id}_{original_filename}"
                
                # File metadata
                file_metadata = {
                    'name': safe_filename,
                    'parents': [self.folder_id],
                    'description': f'Discord attachment from message {message_id}'
                }
                
                # Upload file with support for shared drives
                media = MediaFileUpload(
                    file_path, 
                    resumable=True,
                    chunksize=1024*1024  # 1MB chunks for better reliability
                )
                
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,size,mimeType,webViewLink,webContentLink,driveId',
                    supportsAllDrives=True
                ).execute()
                
                # Make file publicly viewable (required for Notion embedding)
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                self.service.permissions().create(
                    fileId=file['id'],
                    body=permission,
                    supportsAllDrives=True,
                    fields='id'
                ).execute()
                
                # Generate different link formats
                file_id = file['id']
                direct_link = f"https://drive.google.com/uc?id={file_id}"
                
                return {
                    'id': file_id,
                    'name': file['name'],
                    'original_name': original_filename,
                    'size': int(file.get('size', 0)),
                    'mime_type': file.get('mimeType', 'application/octet-stream'),
                    'web_view_link': file.get('webViewLink'),
                    'web_content_link': file.get('webContentLink'),
                    'direct_download_link': f"{direct_link}&export=download",
                    'shareable_link': file.get('webViewLink'),  # Use this for Notion
                    'direct_link': direct_link  # Clean direct link for embedding
                }
            
            result = await asyncio.to_thread(_upload_operations)
            
            if result:
                print(f"✅ File uploaded to Google Drive: {original_filename}")
                print(f"🔗 Shareable link: {result['shareable_link']}")
                return result
            else:
                print(f"❌ Failed to upload {original_filename}")
                return None
            
        except HttpError as e:
            if e.resp.status == 403:
                print(f"❌ Permission denied uploading to Google Drive: {e}")
                print("   Check that the service account has Editor access to the folder")
            elif e.resp.status == 429:
                print(f"❌ Google Drive API quota exceeded: {e}")
                print("   Try again later or reduce upload frequency")
            elif e.resp.status == 413:
                print(f"❌ File too large for Google Drive: {original_filename}")
            else:
                print(f"❌ Google Drive HTTP error uploading {original_filename}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error uploading {original_filename} to Google Drive: {e}")
            print(f"   Error type: {type(e).__name__}")
            return None
    
    async def get_upload_stats(self) -> Dict[str, Any]:
        """Get statistics about uploaded files"""
        if not self._initialized or not self.service or not self.folder_id:
            return {"status": "not_initialized"}
        
        try:
            def _get_stats():
                if self.service is None:
                    return {"status": "not_initialized"}
                    
                # Query files in Discord folder with shared drives support
                query = f"'{self.folder_id}' in parents and trashed=false"
                results = self.service.files().list(
                    q=query,
                    fields="files(id,name,size,createdTime,mimeType)",
                    pageSize=1000,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                
                files = results.get('files', [])
                total_files = len(files)
                total_size = sum(int(f.get('size', 0)) for f in files if f.get('size'))
                
                # Count by type
                file_types = {}
                for f in files:
                    mime_type = f.get('mimeType', 'unknown')
                    file_types[mime_type] = file_types.get(mime_type, 0) + 1
                
                return {
                    "status": "initialized",
                    "total_files": total_files,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "folder_id": self.folder_id,
                    "file_types": file_types,
                    "auth_method": "service_account"
                }
            
            return await asyncio.to_thread(_get_stats)
            
        except Exception as e:
            print(f"❌ Error getting upload stats: {e}")
            return {"status": "error", "error": str(e)}
    
    def is_initialized(self) -> bool:
        """Check if Google Drive is properly initialized"""
        return self._initialized and self.service is not None and self.folder_id is not None
    
    async def get_folder_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current upload folder
        
        Returns:
            dict: Folder information if available, None otherwise
        """
        if not self._initialized or not self.folder_id or not self.service:
            return None
        
        try:
            def _get_folder_info():
                if self.service is None:
                    return None
                    
                folder = self.service.files().get(
                    fileId=self.folder_id,
                    fields='id,name,webViewLink,createdTime,description,driveId',
                    supportsAllDrives=True
                ).execute()
                
                return {
                    'id': folder.get('id'),
                    'name': folder.get('name'),
                    'web_view_link': folder.get('webViewLink'),
                    'created_time': folder.get('createdTime'),
                    'description': folder.get('description'),
                    'drive_id': folder.get('driveId'),
                    'is_shared_drive': bool(folder.get('driveId'))
                }
            
            return await asyncio.to_thread(_get_folder_info)
            
        except Exception as e:
            print(f"❌ Error getting folder info: {e}")
            return None
    
    async def cleanup(self):
        """Clean up resources"""
        # Service accounts don't need explicit cleanup like OAuth2 tokens
        # But this method is here for compatibility and future use
        self._initialized = False
        self.service = None
        self.credentials = None
        self.folder_id = None
        print("🧹 Google Drive manager cleaned up")
    
    def get_auth_method(self) -> str:
        """Return the authentication method being used"""
        return "service_account"
    
    async def test_permissions(self) -> Dict[str, Any]:
        """Test permissions for the current setup"""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        try:
            def _test_permissions():
                if self.service is None or self.folder_id is None:
                    return {"status": "not_initialized"}
                
                # Test folder access
                try:
                    folder = self.service.files().get(
                        fileId=self.folder_id,
                        fields='capabilities',
                        supportsAllDrives=True
                    ).execute()
                    
                    capabilities = folder.get('capabilities', {})
                    
                    return {
                        "status": "success",
                        "can_add_children": capabilities.get('canAddChildren', False),
                        "can_list_children": capabilities.get('canListChildren', False),
                        "can_read_metadata": True,  # If we got here, we can read
                        "auth_method": "service_account"
                    }
                    
                except Exception as e:
                    return {
                        "status": "error",
                        "error": str(e),
                        "auth_method": "service_account"
                    }
            
            return await asyncio.to_thread(_test_permissions)
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "auth_method": "service_account"
            }