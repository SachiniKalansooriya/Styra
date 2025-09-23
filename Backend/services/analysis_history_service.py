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
            try:
                db.execute_query("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            except Exception as e:
                logger.warning(f"Could not create uuid-ossp extension: {e}")
            
            # verify table
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
            import json
            
            query = """
                INSERT INTO analysis_history (analysis_type, result_data, confidence_score, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id, created_at
            """
            
            # Convert analysis_result to proper JSON string
            result_json = json.dumps(analysis_result) if analysis_result else '{}'
            
            result = db.execute_query(query, (
                analysis_result.get('analysis_method', 'clothing_analysis'),
                result_json,  # Use proper JSON string
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