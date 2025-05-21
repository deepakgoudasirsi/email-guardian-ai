from flask import Flask, render_template, jsonify, request, redirect, url_for
from src.config.config import FLASK_SECRET_KEY, FLASK_DEBUG
from src.api.gmail_service import GmailService
from src.api.analysis_service import AnalysisService
from src.models.email_model import EmailModel
from src.utils.logger import setup_logger

# Initialize Flask app
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Setup logger
logger = setup_logger()

# Initialize services
gmail_service = GmailService()
analysis_service = AnalysisService()

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/auth/gmail')
def gmail_auth():
    """Handle Gmail OAuth authentication."""
    try:
        auth_url = gmail_service.get_auth_url()
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Gmail authentication error: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth callback and token storage."""
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({'error': 'No authorization code provided'}), 400
        
        gmail_service.handle_auth_callback(code)
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Auth callback error: {str(e)}")
        return jsonify({'error': 'Authentication callback failed'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_emails():
    """Analyze emails for phishing attempts."""
    try:
        data = request.get_json()
        email_ids = data.get('email_ids', [])
        
        if not email_ids:
            return jsonify({'error': 'No email IDs provided'}), 400
        
        results = []
        for email_id in email_ids:
            email_data = gmail_service.get_email(email_id)
            analysis_result = analysis_service.analyze_email(email_data)
            results.append(analysis_result)
        
        return jsonify({'results': results})
    except Exception as e:
        logger.error(f"Email analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/emails')
def get_emails():
    """Retrieve recent emails from Gmail."""
    try:
        emails = gmail_service.get_recent_emails()
        return jsonify({'emails': emails})
    except Exception as e:
        logger.error(f"Email retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve emails'}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        raise 