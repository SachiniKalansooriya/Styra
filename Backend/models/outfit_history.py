# models/outfit_history.py
from datetime import datetime
from typing import List, Dict, Any

class OutfitHistory:
    """Model for tracking user's outfit history"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.create_table()
    
    def create_table(self):
        """Create outfit history table if it doesn't exist"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS outfit_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL DEFAULT 1,
            worn_date DATE NOT NULL,
            outfit_data JSONB NOT NULL,
            occasion VARCHAR(100),
            weather VARCHAR(50),
            location VARCHAR(200),
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_outfit_history_user_date 
        ON outfit_history(user_id, worn_date);
        
        CREATE INDEX IF NOT EXISTS idx_outfit_history_occasion 
        ON outfit_history(occasion);
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(create_table_query)
            self.db.commit()
            cursor.close()
            
            # Check if table was created
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'outfit_history'
                );
            """)
            table_exists = cursor.fetchone()[0]
            cursor.close()
            
            if table_exists:
                print("Outfit history table created or confirmed to exist")
            else:
                print("Failed to create outfit history table")
                
        except Exception as e:
            print(f"Error creating outfit history table: {e}")
            self.db.rollback()
    
    def save_worn_outfit(self, user_id: int, outfit_data: Dict[str, Any], 
                        occasion: str = None, weather: str = None, 
                        location: str = None, worn_date: datetime = None) -> int:
        """Save a worn outfit to history"""
        if not worn_date:
            worn_date = datetime.now().date()
        
        insert_query = """
        INSERT INTO outfit_history 
        (user_id, worn_date, outfit_data, occasion, weather, location)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(insert_query, (
                user_id, worn_date, outfit_data, occasion, weather, location
            ))
            outfit_id = cursor.fetchone()[0]
            self.db.commit()
            cursor.close()
            return outfit_id
        except Exception as e:
            print(f"Error saving worn outfit: {e}")
            self.db.rollback()
            raise e
    
    def get_outfit_history(self, user_id: int, limit: int = 50, 
                          start_date: datetime = None, 
                          end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get user's outfit history"""
        query = """
        SELECT id, worn_date, outfit_data, occasion, weather, location, 
               rating, notes, created_at
        FROM outfit_history 
        WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND worn_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND worn_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY worn_date DESC, created_at DESC LIMIT %s"
        params.append(limit)
        
        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            history = []
            for row in results:
                history.append({
                    'id': row[0],
                    'worn_date': row[1].isoformat() if row[1] else None,
                    'outfit_data': row[2],
                    'occasion': row[3],
                    'weather': row[4],
                    'location': row[5],
                    'rating': row[6],
                    'notes': row[7],
                    'created_at': row[8].isoformat() if row[8] else None
                })
            
            return history
        except Exception as e:
            print(f"Error fetching outfit history: {e}")
            return []
    
    def get_outfit_by_date(self, user_id: int, date: datetime) -> Dict[str, Any]:
        """Get outfit worn on a specific date"""
        query = """
        SELECT id, outfit_data, occasion, weather, location, rating, notes
        FROM outfit_history 
        WHERE user_id = %s AND worn_date = %s
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(query, (user_id, date))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'id': result[0],
                    'outfit_data': result[1],
                    'occasion': result[2],
                    'weather': result[3],
                    'location': result[4],
                    'rating': result[5],
                    'notes': result[6]
                }
            return None
        except Exception as e:
            print(f"Error fetching outfit by date: {e}")
            return None
    
    def update_outfit_rating(self, outfit_id: int, rating: int, notes: str = None) -> bool:
        """Update outfit rating and notes"""
        query = """
        UPDATE outfit_history 
        SET rating = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(query, (rating, notes, outfit_id))
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error updating outfit rating: {e}")
            self.db.rollback()
            return False
    
    def get_outfit_stats(self, user_id: int) -> Dict[str, Any]:
        """Get outfit statistics for user"""
        query = """
        SELECT 
            COUNT(*) as total_outfits,
            COUNT(DISTINCT worn_date) as days_tracked,
            AVG(rating) as avg_rating,
            COUNT(CASE WHEN rating >= 4 THEN 1 END) as liked_outfits,
            MAX(worn_date) as last_worn_date
        FROM outfit_history 
        WHERE user_id = %s
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'total_outfits': result[0] or 0,
                    'days_tracked': result[1] or 0,
                    'avg_rating': float(result[2]) if result[2] else 0,
                    'liked_outfits': result[3] or 0,
                    'last_worn_date': result[4].isoformat() if result[4] else None
                }
            return {}
        except Exception as e:
            print(f"Error fetching outfit stats: {e}")
            return {}
