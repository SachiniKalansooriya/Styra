# services/outfit_history_service.py
import psycopg2
import psycopg2.extras
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class OutfitHistoryService:
    def __init__(self, db_connection=None):
        self.conn = db_connection
        self._create_table_if_not_exists()
        logger.info("Outfit history service initialized")
    
    def _create_table_if_not_exists(self):
        """Create outfit history table if it doesn't exist"""
        try:
            if self.conn:
                cursor = self.conn.cursor()
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS outfit_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    worn_date TIMESTAMP NOT NULL,
                    occasion VARCHAR(100),
                    weather VARCHAR(100),
                    location VARCHAR(255),
                    confidence_score DECIMAL(5,3),
                    rating INTEGER,
                    notes TEXT,
                    outfit_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                cursor.execute(create_table_sql)
                self.conn.commit()
                cursor.close()
                print("Outfit history table created or confirmed to exist")
        except Exception as e:
            logger.error(f"Error creating outfit history table: {e}")
    
    def get_user_outfit_history(self, user_id: int, limit: int = 50, 
                               start_date: str = None, end_date: str = None):
        """Get user's outfit history"""
        try:
            if not self.conn:
                return {'history': []}
            
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            query = """
                SELECT id, user_id, worn_date, occasion, weather, location,
                       confidence_score, rating, notes, outfit_data, created_at
                FROM outfit_history
                WHERE user_id = %s
                ORDER BY worn_date DESC, created_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (user_id, limit))
            results = cursor.fetchall()
            
            history = []
            for row in results:
                item = dict(row)
                if item.get('outfit_data'):
                    try:
                        item['outfit_data'] = json.loads(item['outfit_data']) if isinstance(item['outfit_data'], str) else item['outfit_data']
                    except:
                        item['outfit_data'] = {}
                history.append(item)
            
            cursor.close()
            return {'history': history}
            
        except Exception as e:
            logger.error(f"Error getting outfit history: {e}")
            return {'history': []}
    
    def record_worn_outfit(self, user_id: int, outfit_data: dict, occasion: str = 'casual',
                          weather: str = '', location: str = '', worn_date=None):
        """Record when an outfit is worn"""
        try:
            if not self.conn:
                return None
            
            if worn_date is None:
                worn_date = datetime.now()
            
            cursor = self.conn.cursor()
            
            query = """
                INSERT INTO outfit_history (user_id, worn_date, occasion, weather, location, outfit_data, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            cursor.execute(query, (
                user_id, worn_date, occasion, weather, location, 
                json.dumps(outfit_data), datetime.now()
            ))
            
            result = cursor.fetchone()
            self.conn.commit()
            cursor.close()
            
            if result:
                return {'outfit_id': result[0]}
            return None
            
        except Exception as e:
            logger.error(f"Error recording worn outfit: {e}")
            return None