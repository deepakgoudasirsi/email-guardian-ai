import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from src.utils.logger import setup_logger
from src.config.config import GMAIL_TOKEN_FILE

logger = setup_logger()

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._load_credentials()

    def _load_credentials(self):
        """Load or refresh Gmail API credentials."""
        try:
            # Desktop application credentials
            client_config = {
                "installed": {
                    "client_id": "1016950334030-374tt3hljg3c6f1pd6omsrc19f7lprgu.apps.googleusercontent.com",
                    "project_id": "email-guardian",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "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",
                    "redirect_uris": ["http://localhost"]
                }
            }

            # Use only the essential scope
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

            if os.path.exists(GMAIL_TOKEN_FILE):
                self.creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, SCOPES)
            
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_config(
                        client_config, 
                        SCOPES
                    )
                    self.creds = flow.run_local_server(
                        port=5003,
                        success_message='Authentication successful! You can close this window.',
                        open_browser=True
                    )
                
                with open(GMAIL_TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=self.creds)
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            raise

    def get_auth_url(self):
        """Get the Gmail OAuth authorization URL."""
        try:
            client_config = {
                "installed": {
                    "client_id": "1072167891733-t0nj0ot96np6upgghjbp95b01jb8cgp7.apps.googleusercontent.com",
                    "project_id": "email-guardian",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "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",
                    "redirect_uris": ["http://localhost"]
                }
            }
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            flow = InstalledAppFlow.from_client_config(
                client_config, 
                SCOPES,
                redirect_uri="http://localhost"
            )
            return flow.authorization_url()[0]
        except Exception as e:
            logger.error(f"Error getting auth URL: {str(e)}")
            raise

    def handle_auth_callback(self, code):
        """Handle the OAuth callback and store credentials."""
        try:
            client_config = {
                "installed": {
                    "client_id": "1072167891733-t0nj0ot96np6upgghjbp95b01jb8cgp7.apps.googleusercontent.com",
                    "project_id": "email-guardian",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "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",
                    "redirect_uris": ["http://localhost"]
                }
            }
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            flow = InstalledAppFlow.from_client_config(
                client_config, 
                SCOPES,
                redirect_uri="http://localhost"
            )
            self.creds = flow.fetch_token(code=code)
            
            with open(GMAIL_TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=self.creds)
        except Exception as e:
            logger.error(f"Error handling auth callback: {str(e)}")
            raise

    def get_recent_emails(self, max_results=10):
        """Retrieve recent emails from Gmail."""
        try:
            results = self.service.users().messages().list(
                userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            emails = []
            for message in messages:
                email_data = self.get_email(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            logger.error(f"Error retrieving emails: {str(e)}")
            raise

    def get_email(self, email_id):
        """Retrieve a specific email by ID."""
        try:
            message = self.service.users().messages().get(
                userId='me', id=email_id, format='full').execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Get email body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                        break
            elif 'body' in message['payload']:
                body = base64.urlsafe_b64decode(
                    message['payload']['body']['data']).decode('utf-8')
            
            return {
                'id': email_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            }
        except Exception as e:
            logger.error(f"Error retrieving email {email_id}: {str(e)}")
            raise 