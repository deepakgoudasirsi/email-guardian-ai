from datetime import datetime
from pymongo import MongoClient
from src.config.config import MONGODB_URI, MONGODB_DB
from src.utils.logger import setup_logger

logger = setup_logger()

class EmailModel:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB]
        self.collection = self.db.emails

    def save_analysis(self, analysis_result):
        """Save email analysis results to the database."""
        try:
            document = {
                'email_id': analysis_result['email_id'],
                'subject': analysis_result['subject'],
                'sender': analysis_result['sender'],
                'risk_score': analysis_result['risk_score'],
                'is_phishing': analysis_result['is_phishing'],
                'analysis': analysis_result['analysis'],
                'recommendations': analysis_result['recommendations'],
                'analyzed_at': datetime.utcnow()
            }
            
            # Update if exists, insert if not
            self.collection.update_one(
                {'email_id': analysis_result['email_id']},
                {'$set': document},
                upsert=True
            )
            
            return True
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
            raise

    def get_analysis(self, email_id):
        """Retrieve analysis results for a specific email."""
        try:
            return self.collection.find_one({'email_id': email_id})
        except Exception as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            raise

    def get_recent_analyses(self, limit=10):
        """Retrieve recent email analyses."""
        try:
            return list(self.collection.find().sort('analyzed_at', -1).limit(limit))
        except Exception as e:
            logger.error(f"Error retrieving recent analyses: {str(e)}")
            raise

    def get_phishing_emails(self):
        """Retrieve all emails marked as phishing."""
        try:
            return list(self.collection.find({'is_phishing': True}))
        except Exception as e:
            logger.error(f"Error retrieving phishing emails: {str(e)}")
            raise

    def get_high_risk_emails(self, threshold=0.7):
        """Retrieve emails with risk scores above the threshold."""
        try:
            return list(self.collection.find({'risk_score': {'$gte': threshold}}))
        except Exception as e:
            logger.error(f"Error retrieving high-risk emails: {str(e)}")
            raise 