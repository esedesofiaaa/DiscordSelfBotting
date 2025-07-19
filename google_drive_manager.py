"""
Google Drive Manager for Discord Bot
Handles uploading files to Google Drive and returning shareable links
"""

import os
import asyncio
from typing import Optional, Dict, Any, Union
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import json


class GoogleDriveManager:
    """Manages Google Drive file uploads for Discord attachments"""
    
    # Google Drive API scopes - includes shared drives access
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json', target_folder_id: Optional[str] = None):
        """
        Initialize Google Drive manager
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load access token
            target_folder_id: Specific folder ID to upload files (can be in shared drives)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service: Optional[Any] = None
        self.target_folder_id = target_folder_id  # User-specified folder ID
        self.folder_id: Optional[str] = None  # Final folder ID to use
        
    async def initialize(self) -> bool:
        """
        Initialize Google Drive service
        Returns True if successful, False otherwise
        """
        try:
            # Run authentication in thread to avoid blocking
            def _authenticate():
                return self._authenticate_google_drive()
            
            self.service = await asyncio.to_thread(_authenticate)
            
            if self.service:
                # Use specific folder ID or create/get Discord attachments folder
                if self.target_folder_id:
                    # Verify the target folder exists and is accessible
                    self.folder_id = await self._verify_target_folder()
                else:
                    # Create or get Discord attachments folder in personal drive
                    self.folder_id = await self._get_or_create_discord_folder()
                
                if self.folder_id:
                    print(f"✅ Google Drive initialized successfully")
                    print(f"📁 Target folder ID: {self.folder_id}")
                    return True
                else:
                    print("❌ Failed to access target folder")
                    return False
            else:
                print("❌ Failed to initialize Google Drive service")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing Google Drive: {e}")
            return False
    
    def _authenticate_google_drive(self) -> Optional[Any]:
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                print(f"⚠️ Error loading existing token: {e}")
        
        # If no valid credentials, perform OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("🔄 Refreshed Google Drive credentials")
                except Exception as e:
                    print(f"⚠️ Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    print(f"❌ Credentials file not found: {self.credentials_path}")
                    print("📋 To set up Google Drive integration:")
                    print("   1. Go to https://console.cloud.google.com/")
                    print("   2. Create a new project or select existing")
                    print("   3. Enable Google Drive API")
                    print("   4. Create OAuth2 credentials (Desktop application)")
                    print("   5. Download credentials.json to project root")
                    return None
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    print("✅ New Google Drive credentials obtained")
                except Exception as e:
                    print(f"❌ Error during OAuth flow: {e}")
                    return None
            
            # Save credentials for next time
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                print(f"💾 Credentials saved to {self.token_path}")
            except Exception as e:
                print(f"⚠️ Could not save credentials: {e}")
        
        # Build the service
        try:
            service = build('drive', 'v3', credentials=creds)
            return service
        except Exception as e:
            print(f"❌ Error building Google Drive service: {e}")
            return None
    
    async def _verify_target_folder(self) -> Optional[str]:
        """Verify that the target folder ID exists and is accessible"""
        if not self.service or not self.target_folder_id:
            return None
        
        try:
            def _verify_operations():
                try:
                    # Try to get folder metadata - works for both personal and shared drives
                    if self.service is None:
                        return None
                        
                    folder = self.service.files().get(
                        fileId=self.target_folder_id,
                        fields='id,name,mimeType,parents,driveId',
                        supportsAllDrives=True
                    ).execute()
                    
                    if folder.get('mimeType') == 'application/vnd.google-apps.folder':
                        folder_name = folder.get('name', 'Unknown')
                        drive_id = folder.get('driveId')
                        
                        if drive_id:
                            print(f"📁 Using folder '{folder_name}' in shared drive: {self.target_folder_id}")
                        else:
                            print(f"📁 Using folder '{folder_name}' in personal drive: {self.target_folder_id}")
                        
                        return self.target_folder_id
                    else:
                        print(f"❌ Target ID is not a folder: {self.target_folder_id}")
                        return None
                        
                except Exception as e:
                    print(f"❌ Cannot access folder {self.target_folder_id}: {e}")
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
                # Search for existing Discord Attachments folder
                if self.service is None:
                    return None
                    
                query = "name='Discord Attachments' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.service.files().list(q=query, fields="files(id, name)").execute()
                folders = results.get('files', [])
                
                if folders:
                    # Use existing folder
                    folder_id = folders[0]['id']
                    print(f"📁 Using existing Discord Attachments folder: {folder_id}")
                    return folder_id
                else:
                    # Create new folder
                    folder_metadata = {
                        'name': 'Discord Attachments',
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                    folder = self.service.files().create(body=folder_metadata, fields='id').execute()
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
        if not self.service or not self.folder_id:
            print("❌ Google Drive not initialized")
            return None
        
        try:
            def _upload_operations():
                # Create unique filename with message ID prefix
                if self.service is None:
                    return None
                    
                safe_filename = f"msg_{message_id}_{original_filename}"
                
                # File metadata
                file_metadata = {
                    'name': safe_filename,
                    'parents': [self.folder_id],
                    'description': f'Discord attachment from message {message_id}'
                }
                
                # Upload file with support for shared drives
                media = MediaFileUpload(file_path, resumable=True)
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,size,mimeType,webViewLink,webContentLink,driveId',
                    supportsAllDrives=True
                ).execute()
                
                # Make file publicly viewable
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                self.service.permissions().create(
                    fileId=file['id'],
                    body=permission,
                    supportsAllDrives=True
                ).execute()
                
                # Generate direct download link
                file_id = file['id']
                direct_link = f"https://drive.google.com/uc?id={file_id}&export=download"
                
                return {
                    'id': file_id,
                    'name': file['name'],
                    'original_name': original_filename,
                    'size': int(file.get('size', 0)),
                    'mime_type': file.get('mimeType', 'application/octet-stream'),
                    'web_view_link': file.get('webViewLink'),
                    'web_content_link': file.get('webContentLink'),
                    'direct_download_link': direct_link,
                    'shareable_link': file.get('webViewLink')  # Use this for Notion
                }
            
            result = await asyncio.to_thread(_upload_operations)
            print(f"✅ File uploaded to Google Drive: {original_filename}")
            return result
            
        except HttpError as e:
            print(f"❌ Google Drive HTTP error uploading {original_filename}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error uploading {original_filename} to Google Drive: {e}")
            return None
    
    async def get_upload_stats(self) -> Dict[str, Any]:
        """Get statistics about uploaded files"""
        if not self.service or not self.folder_id:
            return {"status": "not_initialized"}
        
        try:
            def _get_stats():
                # Query files in Discord folder with shared drives support
                if self.service is None:
                    return {"status": "not_initialized"}
                    
                query = f"'{self.folder_id}' in parents and trashed=false"
                results = self.service.files().list(
                    q=query,
                    fields="files(id,name,size,createdTime)",
                    pageSize=1000,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                
                files = results.get('files', [])
                total_files = len(files)
                total_size = sum(int(f.get('size', 0)) for f in files if f.get('size'))
                
                return {
                    "status": "initialized",
                    "total_files": total_files,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "folder_id": self.folder_id
                }
            
            return await asyncio.to_thread(_get_stats)
            
        except Exception as e:
            print(f"❌ Error getting upload stats: {e}")
            return {"status": "error", "error": str(e)}
    
    def is_initialized(self) -> bool:
        """Check if Google Drive is properly initialized"""
        return self.service is not None and self.folder_id is not None
