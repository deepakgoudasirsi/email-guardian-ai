import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask Configuration
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Gmail API Configuration
GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DB', 'email_guardian')

# Email Analysis Configuration
RISK_THRESHOLD = float(os.getenv('RISK_THRESHOLD', '0.7'))
MAX_EMAILS_TO_ANALYZE = int(os.getenv('MAX_EMAILS_TO_ANALYZE', '100'))

# Application Configuration
APP_NAME = "Email Guardian"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered email security analysis tool"