import openai
from src.config.config import OPENAI_API_KEY, OPENAI_MODEL, RISK_THRESHOLD
from src.utils.logger import setup_logger

logger = setup_logger()

class AnalysisService:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL

    def analyze_email(self, email_data):
        """Analyze an email for phishing attempts using OpenAI."""
        try:
            # Prepare the prompt for analysis
            prompt = self._create_analysis_prompt(email_data)
            
            # Get analysis from OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert email security analyst. Analyze the following email for potential phishing attempts, spoofing, and security risks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            
            # Extract risk score and recommendations
            risk_score = self._extract_risk_score(analysis)
            recommendations = self._extract_recommendations(analysis)
            
            return {
                'email_id': email_data['id'],
                'subject': email_data['subject'],
                'sender': email_data['sender'],
                'risk_score': risk_score,
                'is_phishing': risk_score >= RISK_THRESHOLD,
                'analysis': analysis,
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Error analyzing email: {str(e)}")
            raise

    def _create_analysis_prompt(self, email_data):
        """Create a detailed prompt for email analysis."""
        return f"""
        Analyze the following email for potential security risks:

        From: {email_data['sender']}
        Subject: {email_data['subject']}
        Date: {email_data['date']}
        
        Content:
        {email_data['body']}

        Please provide:
        1. A risk score between 0 and 1 (where 1 is highest risk)
        2. Detailed analysis of potential threats
        3. Specific recommendations for handling this email
        4. Any suspicious patterns or indicators found
        """

    def _extract_risk_score(self, analysis):
        """Extract the risk score from the analysis text."""
        try:
            # Look for risk score in the format "risk score: X" or "risk: X"
            import re
            score_match = re.search(r'risk\s*score:?\s*(\d*\.?\d+)', analysis.lower())
            if score_match:
                return float(score_match.group(1))
            return 0.5  # Default to medium risk if score not found
        except Exception as e:
            logger.error(f"Error extracting risk score: {str(e)}")
            return 0.5

    def _extract_recommendations(self, analysis):
        """Extract recommendations from the analysis text."""
        try:
            # Split the analysis into sections and look for recommendations
            sections = analysis.split('\n\n')
            for section in sections:
                if 'recommend' in section.lower() or 'suggest' in section.lower():
                    return section.strip()
            return "No specific recommendations provided."
        except Exception as e:
            logger.error(f"Error extracting recommendations: {str(e)}")
            return "Error extracting recommendations." 