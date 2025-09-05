from datetime import datetime
import logging
from database.connection import db
import uuid
import json

logger = logging.getLogger(__name__)

class AnalysisHistoryService:
    """Service for managing analysis history in the database"""
    
    def __init__(self):
        # Create analysis_history table if it doesn't exist
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """Create analysis_history table if it doesn't exist"""
        try:
            # First, enable uuid-ossp extension if not already enabled
            extension_query = "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""
            try:
                db.execute_query(extension_query, fetch=False)
            except Exception as e:
                logger.warning(f"Could not create uuid-ossp extension: {e}")
                
            query = """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                analysis_method VARCHAR(50) NOT NULL,
                suggested_category VARCHAR(50) NOT NULL,
                suggested_color VARCHAR(30) NOT NULL,
                suggested_occasion VARCHAR(30) NOT NULL,
                confidence DECIMAL(5,2) NOT NULL,
                ai_description TEXT,
                features JSONB,
                image_stored BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
            db.execute_query(query, fetch=False)
            logger.info("Analysis history table created or confirmed to exist")
        except Exception as e:
            logger.error(f"Error creating analysis_history table: {e}")
    
    def save_analysis_result(self, analysis_result):
        """Save analysis result to the database"""
        try:
            # Generate UUID for the analysis
            analysis_id = str(uuid.uuid4())
            
            # Extract data from analysis result
            analysis_method = analysis_result.get('analysis_method', 'unknown')
            suggested_category = analysis_result.get('suggestedCategory', 'unknown')
            suggested_color = analysis_result.get('suggestedColor', 'unknown')
            suggested_occasion = analysis_result.get('suggestedOccasion', 'casual')
            confidence = float(analysis_result.get('confidence', 0.0))
            ai_description = analysis_result.get('ai_description', '')
            
            # Store features as JSON for JSONB
            features = analysis_result.get('features', {})
            
            # Insert into the database with explicit ID
            query = """
            INSERT INTO analysis_history 
            (id, analysis_method, suggested_category, suggested_color, suggested_occasion, 
             confidence, ai_description, features, image_stored)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
            """
            
            params = (
                analysis_id,
                analysis_method, 
                suggested_category,
                suggested_color,
                suggested_occasion,
                confidence,
                ai_description,
                json.dumps(features),  # Convert to JSON string for JSONB
                False  # image_stored default is False for now
            )
            
            result = db.execute_query(query, params)
            
            if result and len(result) > 0:
                returned_id = result[0]['id']
                created_at = result[0]['created_at']
                logger.info(f"Analysis result saved to database with ID: {returned_id}")
                return {
                    "analysis_id": str(returned_id),
                    "created_at": created_at
                }
            else:
                logger.warning("Analysis result was not saved properly")
                return None
                
        except Exception as e:
            logger.error(f"Error saving analysis result: {e}")
            return None
    
    def get_analysis_history(self, limit=50, offset=0):
        """Get analysis history from the database"""
        try:
            query = """
            SELECT id, analysis_method, suggested_category, suggested_color, 
                   suggested_occasion, confidence, ai_description, features, 
                   image_stored, created_at
            FROM analysis_history
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            params = (limit, offset)
            results = db.execute_query(query, params)
            
            if results:
                # Convert UUID to string and ensure features is proper dict
                for result in results:
                    if 'id' in result:
                        result['id'] = str(result['id'])
                    if 'features' in result and result['features']:
                        # JSONB should already be parsed by psycopg2
                        if isinstance(result['features'], str):
                            try:
                                result['features'] = json.loads(result['features'])
                            except:
                                result['features'] = {}
                    else:
                        result['features'] = {}
                
                logger.info(f"Retrieved {len(results)} analysis history records")
                return results
            else:
                logger.info("No analysis history records found")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving analysis history: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id):
        """Get a specific analysis by ID"""
        try:
            query = """
            SELECT id, analysis_method, suggested_category, suggested_color, 
                   suggested_occasion, confidence, ai_description, features, 
                   image_stored, created_at
            FROM analysis_history
            WHERE id = %s
            """
            params = (analysis_id,)
            results = db.execute_query(query, params)
            
            if results and len(results) > 0:
                result = results[0]
                # Convert UUID to string and parse features JSON
                if 'id' in result:
                    result['id'] = str(result['id'])
                if 'features' in result and result['features']:
                    try:
                        result['features'] = json.loads(result['features'])
                    except:
                        result['features'] = {}
                
                logger.info(f"Retrieved analysis with ID: {analysis_id}")
                return result
            else:
                logger.info(f"No analysis found with ID: {analysis_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving analysis by ID: {e}")
            return None

# Create global instance
analysis_history_service = AnalysisHistoryService()
