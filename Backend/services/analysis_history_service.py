# Backend/services/analysis_history_service.py
import logging
from database.connection import db
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalysisHistoryService:
    def __init__(self):
        self.create_table()
    
    def create_table(self):
        """Create analysis_history table if it doesn't exist"""
        try:
            # Try to create uuid extension (ignore if it fails)
            try:
                db.execute_query("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            except Exception as e:
                logger.warning(f"Could not create uuid-ossp extension: {e}")
            
            # Table should already exist from setup script, but let's verify
            query = """
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id SERIAL PRIMARY KEY,
                    analysis_type VARCHAR(100),
                    input_data JSONB,
                    result_data JSONB,
                    confidence_score DECIMAL(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            db.execute_query(query)
            logger.info("Analysis history table created or confirmed to exist")
            
        except Exception as e:
            logger.error(f"Error creating analysis_history table: {e}")
    
    def save_analysis_result(self, analysis_result):
        """Save analysis result to database"""
        try:
            query = """
                INSERT INTO analysis_history (analysis_type, result_data, confidence_score, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id, created_at
            """
            
            result = db.execute_query(query, (
                analysis_result.get('analysis_method', 'clothing_analysis'),
                str(analysis_result),  # Convert to string for now
                analysis_result.get('confidence', 0),
                datetime.now()
            ))
            
            if result:
                return {
                    'analysis_id': result['id'],
                    'created_at': result['created_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error saving analysis result: {e}")
            return None

# Global instance
analysis_history_service = AnalysisHistoryService()