from flask import Flask, redirect, request, session, url_for
from src.api.gmail_service import GmailService

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

gmail_service = GmailService()

@app.route('/')
def index():
    return 'Email Guardian is running!'

@app.route('/privacy')
def privacy():
    return 'Privacy Policy'

@app.route('/terms')
def terms():
    return 'Terms of Service'

@app.route('/gmail/auth')
def gmail_auth():
    auth_url = gmail_service.get_auth_url()
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    if code:
        gmail_service.handle_auth_callback(code)
        return redirect(url_for('index'))
    return 'Authorization failed', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True) 