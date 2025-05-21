from flask import Flask, render_template, jsonify, request
from api.gmail_service import GmailService
from core.email_analyzer import EmailAnalyzer
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
gmail_service = GmailService()
email_analyzer = EmailAnalyzer()

@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Fetch and analyze recent emails."""
    try:
        # Get recent emails
        emails = gmail_service.get_emails(max_results=10)
        
        # Analyze each email
        analyzed_emails = []
        for email in emails:
            analysis = email_analyzer.analyze_email(email)
            analyzed_emails.append({
                'id': email['id'],
                'subject': email['subject'],
                'sender': email['sender'],
                'date': email['date'],
                'risk_score': analysis['risk_score'],
                'risk_level': analysis['risk_level'],
                'findings': analysis['findings'],
                'recommendation': analysis['recommendation']
            })
        
        return jsonify({
            'status': 'success',
            'emails': analyzed_emails
        })
        
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/email/<email_id>', methods=['GET'])
def get_email_details(email_id):
    """Get detailed analysis of a specific email."""
    try:
        # Get email details
        email_data = gmail_service.get_email_details(email_id)
        
        if not email_data:
            return jsonify({
                'status': 'error',
                'message': 'Email not found'
            }), 404
        
        # Analyze email
        analysis = email_analyzer.analyze_email(email_data)
        
        return jsonify({
            'status': 'success',
            'email': {
                'id': email_id,
                'subject': email_data['subject'],
                'sender': email_data['sender'],
                'date': email_data['date'],
                'body': email_data['body'],
                'attachments': email_data['attachments'],
                'analysis': analysis
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching email details: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_email():
    """Analyze a specific email content."""
    try:
        data = request.json
        if not data or 'email' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No email data provided'
            }), 400
        
        # Analyze email
        analysis = email_analyzer.analyze_email(data['email'])
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing email: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Start the Flask application
    app.run(debug=True, port=5000) 