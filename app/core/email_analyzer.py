import openai
from typing import Dict, Any, List, Tuple
import re
import logging
from email.utils import parsedate_to_datetime
import dns.resolver
import spf
import dmarc
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailAnalyzer:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def analyze_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an email for potential phishing attempts and security risks.
        Returns a dictionary containing risk score and analysis details.
        """
        try:
            # Initialize risk score and findings
            risk_score = 0
            findings = []
            
            # 1. Check email authentication (SPF, DKIM, DMARC)
            auth_checks = self._check_email_authentication(email_data)
            risk_score += auth_checks['risk_score']
            findings.extend(auth_checks['findings'])
            
            # 2. Analyze email content using GenAI
            content_analysis = self._analyze_content(email_data)
            risk_score += content_analysis['risk_score']
            findings.extend(content_analysis['findings'])
            
            # 3. Check for suspicious URLs
            url_analysis = self._analyze_urls(email_data)
            risk_score += url_analysis['risk_score']
            findings.extend(url_analysis['findings'])
            
            # 4. Analyze sender behavior
            sender_analysis = self._analyze_sender(email_data)
            risk_score += sender_analysis['risk_score']
            findings.extend(sender_analysis['findings'])
            
            # Normalize risk score to 0-100
            final_risk_score = min(100, max(0, risk_score))
            
            return {
                'risk_score': final_risk_score,
                'risk_level': self._get_risk_level(final_risk_score),
                'findings': findings,
                'recommendation': self._get_recommendation(final_risk_score)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing email: {str(e)}")
            return {
                'risk_score': 100,
                'risk_level': 'ERROR',
                'findings': [f"Error during analysis: {str(e)}"],
                'recommendation': "Unable to analyze email due to an error."
            }
    
    def _check_email_authentication(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check SPF, DKIM, and DMARC records."""
        findings = []
        risk_score = 0
        
        try:
            # Extract domain from sender email
            sender_domain = email_data['sender'].split('@')[-1].strip('>')
            
            # Check SPF
            spf_result = spf.check2(sender_domain, email_data['sender'], '127.0.0.1')
            if spf_result[0] != 'pass':
                risk_score += 20
                findings.append(f"SPF check failed: {spf_result[0]}")
            
            # Check DMARC
            dmarc_result = dmarc.check(sender_domain)
            if dmarc_result['status'] != 'pass':
                risk_score += 20
                findings.append(f"DMARC check failed: {dmarc_result['status']}")
            
        except Exception as e:
            risk_score += 30
            findings.append(f"Error checking email authentication: {str(e)}")
        
        return {'risk_score': risk_score, 'findings': findings}
    
    def _analyze_content(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email content using GenAI."""
        findings = []
        risk_score = 0
        
        try:
            # Prepare prompt for GPT
            prompt = f"""
            Analyze this email for potential phishing or social engineering attempts:
            
            Subject: {email_data['subject']}
            From: {email_data['sender']}
            Body: {email_data['body']}
            
            Check for:
            1. Urgency or pressure tactics
            2. Requests for sensitive information
            3. Unusual grammar or formatting
            4. Suspicious requests or instructions
            5. Mismatched sender and content
            6. Social engineering patterns
            
            Provide a detailed analysis and risk assessment.
            """
            
            # Get GPT analysis
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a security expert analyzing emails for phishing attempts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            # Extract risk indicators from GPT response
            if "high risk" in analysis.lower():
                risk_score += 40
            elif "medium risk" in analysis.lower():
                risk_score += 20
            elif "low risk" in analysis.lower():
                risk_score += 10
            
            findings.append(f"Content Analysis: {analysis}")
            
        except Exception as e:
            risk_score += 30
            findings.append(f"Error analyzing content: {str(e)}")
        
        return {'risk_score': risk_score, 'findings': findings}
    
    def _analyze_urls(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze URLs in the email content."""
        findings = []
        risk_score = 0
        
        try:
            # Extract URLs from email body
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                            email_data['body'])
            
            for url in urls:
                parsed_url = urlparse(url)
                
                # Check for suspicious TLDs
                suspicious_tlds = ['.xyz', '.tk', '.pw', '.info', '.biz']
                if any(parsed_url.netloc.endswith(tld) for tld in suspicious_tlds):
                    risk_score += 15
                    findings.append(f"Suspicious TLD detected in URL: {url}")
                
                # Check for IP addresses in URLs
                if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', parsed_url.netloc):
                    risk_score += 20
                    findings.append(f"IP address used in URL: {url}")
                
                # Check for URL shorteners
                url_shorteners = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co']
                if any(shortener in parsed_url.netloc for shortener in url_shorteners):
                    risk_score += 10
                    findings.append(f"URL shortener detected: {url}")
        
        except Exception as e:
            risk_score += 10
            findings.append(f"Error analyzing URLs: {str(e)}")
        
        return {'risk_score': risk_score, 'findings': findings}
    
    def _analyze_sender(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sender information and behavior."""
        findings = []
        risk_score = 0
        
        try:
            # Check for display name spoofing
            if '<' in email_data['sender']:
                display_name, email = email_data['sender'].split('<')
                if display_name.strip() and '@' in display_name:
                    risk_score += 15
                    findings.append("Potential display name spoofing detected")
            
            # Check for unusual sender domains
            sender_domain = email_data['sender'].split('@')[-1].strip('>')
            common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            if sender_domain not in common_domains:
                try:
                    dns.resolver.resolve(sender_domain, 'MX')
                except:
                    risk_score += 20
                    findings.append(f"Sender domain {sender_domain} has no MX records")
        
        except Exception as e:
            risk_score += 10
            findings.append(f"Error analyzing sender: {str(e)}")
        
        return {'risk_score': risk_score, 'findings': findings}
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Convert risk score to risk level."""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "SAFE"
    
    def _get_recommendation(self, risk_score: int) -> str:
        """Generate recommendation based on risk score."""
        if risk_score >= 80:
            return "DO NOT OPEN - This email shows strong signs of being malicious."
        elif risk_score >= 60:
            return "HIGHLY SUSPICIOUS - Exercise extreme caution and verify sender."
        elif risk_score >= 40:
            return "SUSPICIOUS - Review carefully before taking any action."
        elif risk_score >= 20:
            return "LOW RISK - Proceed with normal caution."
        else:
            return "SAFE - No significant risks detected." 