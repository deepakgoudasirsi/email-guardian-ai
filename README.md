# Email Guardian AI 🛡️

A powerful AI-driven email security tool that protects your Gmail inbox from phishing, spam, and malicious content using GPT-4.


## Overview

Email Guardian is an intelligent email security solution that analyzes your Gmail messages in real-time to identify potential security threats. Using advanced AI (GPT-4) and comprehensive security checks, it provides detailed risk analysis and actionable recommendations to keep your inbox safe.

## Tech Stack

- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB
- **Authentication**: Google OAuth2
- **AI/ML**: OpenAI GPT-4
- **APIs**: Gmail API, OpenAI API
- **Security**: SPF, DMARC, DKIM validation

## Features

- 🔍 **AI-Powered Analysis**: Uses GPT-4 to analyze email content for phishing attempts and malicious content
- 🎯 **Risk Scoring**: Categorizes emails into five risk levels (SAFE, LOW, MEDIUM, HIGH, CRITICAL)
- 🔐 **Security Checks**:
  - SPF, DMARC, and DKIM validation
  - Suspicious URL detection
  - Sender authentication
  - Display name spoofing detection
- 📊 **Detailed Analysis**: Provides comprehensive security reports with actionable recommendations
- 🔄 **Real-time Monitoring**: Continuously monitors your inbox for new threats
- 📱 **User-friendly Interface**: Clean and intuitive web interface for viewing analysis results

## How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/email-guardian-ai.git
   cd email-guardian-ai
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with:
   ```
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_uri
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5003`

## Screenshots

### Dashboard View
![Dashboard](screenshots/dashboard.png)

### Email Analysis
![Analysis](screenshots/analysis.png)

### Risk Level Display
![Risk Levels](screenshots/risk-levels.png)

## Security Features

- **Email Authentication**: Validates SPF, DMARC, and DKIM records
- **URL Analysis**: Detects suspicious links and domains
- **Content Analysis**: Uses GPT-4 to identify phishing attempts and social engineering
- **Sender Verification**: Checks for display name spoofing and suspicious sender domains

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT-4 API
- Google for Gmail API
- Flask framework
- MongoDB 
