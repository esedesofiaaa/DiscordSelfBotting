"""
Google Drive Manager for Discord Bot
Handles uploading files to Google Drive and returning shareable links
Supports both OAuth 2.0 (Desktop App) and Service Account
"""

import os
import json
import asyncio
import pickle
from typing import Optional, Dict, Any, Union
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


class GoogleDriveManager:
    """Manages Google Drive file uploads for Discord attachments"""
    
    # Google Drive API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: Optional[str] = 'token.pickle', target_folder_id: Optional[str] = None, service_account_path: Optional[str] = None):
        """
        Initialize Google Drive manager
        
        Args:
            credentials_path: Path to OAuth2 Client Secrets JSON (credentials.json)
            token_path: Path to User Access Token pickle (token.pickle)
            target_folder_id: Specific folder ID to upload files
            service_account_path: Path to Service Account JSON (fallback)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service_account_path = service_account_path
        self.target_folder_id = target_folder_id
        
        self.service: Optional[Any] = None
        self.credentials: Optional[Any] = None
        self.folder_id: Optional[str] = None
        self._initialized = False
        self.auth_method = "unknown"
    
    async def initialize(self) -> bool:
        """
        Initialize Google Drive service
        Prioritizes OAuth 2.0 (token.pickle) -> Service Account
        """
        try:
            # 1. Try OAuth 2.0 (Preferred)
            if self.token_path and os.path.exists(self.token_path):
                print("🔑 Found token.pickle, attempting OAuth 2.0 authentication...")
                if await self._authenticate_oauth():
                    self.auth_method = "oauth2"
            
            # 2. If OAuth failed or not available, try Service Account
            if not self.credentials and self.service_account_path and os.path.exists(self.service_account_path):
                print("🤖 Found service_account.json, attempting Service Account authentication...")
                if await self._authenticate_service_account():
                    self.auth_method = "service_account"
            
            # 3. If still no credentials, try interactive OAuth flow (only if credentials.json exists)
            if not self.credentials and os.path.exists(self.credentials_path):
                print("⚠️ No token or service account. Attempting interactive OAuth flow...")
                if await self._authenticate_oauth():
                    self.auth_method = "oauth2"

            if not self.credentials:
                print("❌ No valid credentials found for Google Drive.")
                return False
            
            # Build Google Drive service
            self.service = build('drive', 'v3', credentials=self.credentials)
            
            # Test connection
            about = await self._test_connection()
            if not about:
                return False
            
            # Setup folder
            if self.target_folder_id:
                self.folder_id = await self._verify_target_folder()
            else:
                self.folder_id = await self._get_or_create_discord_folder()
            
            if self.folder_id:
                print(f"✅ Google Drive initialized successfully ({self.auth_method})")
                print(f"📁 Target folder ID: {self.folder_id}")
                self._initialized = True
                return True
            else:
                print("❌ Failed to access target folder")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing Google Drive: {e}")
            return False

    async def _authenticate_oauth(self) -> bool:
        """Authenticate using OAuth 2.0 (credentials.json + token.pickle)"""
        try:
            creds = None
            # 1. Load existing token
            if self.token_path and os.path.exists(self.token_path):
                try:
                    with open(self.token_path, 'rb') as token:
                        creds = pickle.load(token)
                except Exception as e:
                    print(f"⚠️ Error loading token.pickle: {e}")
            
            # 2. Validate or Refresh
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("🔄 Refreshing expired OAuth token...")
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"❌ Failed to refresh token: {e}")
                        creds = None
                
                if not creds:
                    # No valid token, need full flow
                    if not os.path.exists(self.credentials_path):
                        print(f"⚠️ Credentials file not found for OAuth: {self.credentials_path}")
                        return False
                        
                    print("🌐 Starting local OAuth server (check browser)...")
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        print(f"❌ OAuth flow failed: {e}")
                        return False
                
                # 3. Save updated token
                if self.token_path:
                    try:
                        with open(self.token_path, 'wb') as token:
                            pickle.dump(creds, token)
                        print(f"💾 Token saved to {self.token_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to save token.pickle: {e}")
            
            self.credentials = creds
            return True
            
        except Exception as e:
            print(f"❌ Error in OAuth authentication: {e}")
            return False

    async def _authenticate_service_account(self) -> bool:
        """Authenticate with Google Drive API using Service Account"""
        try:
            if not self.service_account_path or not os.path.exists(self.service_account_path):
                return False
            
            # Load and validate service account credentials
            try:
                with open(self.service_account_path, 'r') as f:
                    creds_info = json.load(f)
                
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_info, scopes=self.SCOPES
                )
                
                print(f"📧 Service Account: {creds_info.get('client_email', 'Unknown')}")
                return True
                
            except Exception as e:
                print(f"❌ Error loading service account: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Error authenticating Service Account: {e}")
            return False
    
    async def _test_connection(self) -> Optional[Dict[str, Any]]:
        """Test connection to Google Drive API"""
        try:
            def _test_operations():
                if self.service is None:
                    return None
                about = self.service.about().get(fields="user,storageQuota").execute()
                return about
            
            about = await asyncio.to_thread(_test_operations)
            
            if about:
                user_info = about.get('user', {})
                email = user_info.get('emailAddress', 'Unknown')
                print(f"✅ Connected to Google Drive as: {email}")
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
                    folder = self.service.files().get(
                        fileId=self.target_folder_id,
                        fields='id,name,mimeType,parents,driveId,capabilities',
                        supportsAllDrives=True
                    ).execute()
                    
                    if folder.get('mimeType') == 'application/vnd.google-apps.folder':
                        folder_name = folder.get('name', 'Unknown')
                        capabilities = folder.get('capabilities', {})
                        
                        if not capabilities.get('canAddChildren', False):
                            print(f"❌ No permission to add files to folder '{folder_name}'")
                            return None
                        
                        print(f"📁 Using folder '{folder_name}' ({self.target_folder_id})")
                        return self.target_folder_id
                    else:
                        print(f"❌ Target ID is not a folder: {self.target_folder_id}")
                        return None
                        
                except HttpError as e:
                    print(f"❌ Error accessing folder {self.target_folder_id}: {e}")
                    return None
            
            return await asyncio.to_thread(_verify_operations)
            
        except Exception as e:
            print(f"❌ Error verifying target folder: {e}")
            return None
    
    async def _get_or_create_discord_folder(self) -> Optional[str]:
        """Get or create Discord Attachments folder"""
        if not self.service:
            return None
        
        try:
            def _folder_operations():
                query = "name='Discord Attachments' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.service.files().list(
                    q=query, 
                    fields="files(id, name)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                folders = results.get('files', [])
                
                if folders:
                    return folders[0]['id']
                else:
                    folder_metadata = {
                        'name': 'Discord Attachments',
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                    folder = self.service.files().create(
                        body=folder_metadata, 
                        fields='id,name',
                        supportsAllDrives=True
                    ).execute()
                    return folder.get('id')
            
            return await asyncio.to_thread(_folder_operations)
            
        except Exception as e:
            print(f"❌ Error managing Discord folder: {e}")
            return None
    
    async def upload_file(self, file_path: str, original_filename: str, message_id: str) -> Optional[Dict[str, Any]]:
        """Upload file to Google Drive"""
        if not self._initialized or not self.service or not self.folder_id:
            return None
        
        try:
            def _upload_operations():
                safe_filename = f"msg_{message_id}_{original_filename}"
                
                file_metadata = {
                    'name': safe_filename,
                    'parents': [self.folder_id],
                    'description': f'Discord attachment from message {message_id}'
                }
                
                media = MediaFileUpload(
                    file_path, 
                    resumable=True,
                    chunksize=1024*1024
                )
                
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,size,mimeType,webViewLink,webContentLink',
                    supportsAllDrives=True
                ).execute()
                
                # Make public for Notion
                permission = {'type': 'anyone', 'role': 'reader'}
                self.service.permissions().create(
                    fileId=file['id'],
                    body=permission,
                    supportsAllDrives=True
                ).execute()
                
                return {
                    'id': file['id'],
                    'name': file['name'],
                    'shareable_link': file.get('webViewLink'),
                    'direct_download_link': f"https://drive.google.com/uc?id={file['id']}&export=download"
                }
            
            result = await asyncio.to_thread(_upload_operations)
            if result:
                print(f"✅ Uploaded to Drive: {original_filename}")
                return result
            return None
            
        except Exception as e:
            print(f"❌ Error uploading to Drive: {e}")
            return None

    def is_initialized(self) -> bool:
        return self._initialized