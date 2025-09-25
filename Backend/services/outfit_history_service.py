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
                    -- Optional image columns for thumbnails
                    image_url VARCHAR(500),
                    image_path VARCHAR(500),
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
                       image_url, image_path, confidence_score, rating, notes, outfit_data, created_at
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
                
                # Parse outfit_data safely
                if item.get('outfit_data'):
                    try:
                        item['outfit_data'] = json.loads(item['outfit_data']) if isinstance(item['outfit_data'], str) else item['outfit_data']
                    except:
                        item['outfit_data'] = {}

                # Enhanced image handling and normalization
                try:
                    outfit_blob = item.get('outfit_data') or {}
                    items = outfit_blob.get('items') if isinstance(outfit_blob, dict) else None
                    if not isinstance(items, list):
                        items = []

                    # Row-level image fields
                    row_image_url = item.get('image_url')
                    row_image_path = item.get('image_path')

                    # Process each clothing item
                    for ci in items:
                        if not isinstance(ci, dict):
                            continue
                        
                        # Extract image from multiple possible field names
                        ci_image = None
                        image_candidates = [
                            ci.get('image_url'),
                            ci.get('image_path'), 
                            ci.get('image'),
                            ci.get('path'),
                            ci.get('uri'),
                            ci.get('src'),
                            ci.get('imageUri'),
                            ci.get('imageUrl')
                        ]
                        
                        for candidate in image_candidates:
                            if candidate and isinstance(candidate, str) and candidate.strip():
                                ci_image = candidate
                                break
                        
                        # If item lacks image, use row fallbacks
                        if not ci_image:
                            ci_image = row_image_url or row_image_path
                        
                        # Set both image fields
                        if ci_image:
                            ci['image_url'] = ci_image
                            ci['image_path'] = ci_image
                        else:
                            ci['image_url'] = None
                            ci['image_path'] = None

                    # Update the items back
                    if isinstance(outfit_blob, dict):
                        outfit_blob['items'] = items
                        item['outfit_data'] = outfit_blob

                    # If row-level images are missing, try to get from first item
                    if (not row_image_url and not row_image_path) and items:
                        first_item = items[0]
                        if isinstance(first_item, dict):
                            first_image = first_item.get('image_url') or first_item.get('image_path')
                            if first_image:
                                item['image_url'] = first_image
                                item['image_path'] = first_image
                                
                except Exception as e:
                    logger.error(f"Error processing outfit images: {e}")
                    pass
                    
                history.append(item)
            
            cursor.close()
            return {'history': history}
            
        except Exception as e:
            logger.error(f"Error getting outfit history: {e}")
            return {'history': []}
    
    def record_worn_outfit(self, user_id: int, outfit_data: dict, occasion: str = 'casual',
                          weather: str = '', location: str = '', worn_date=None):
        """Record when an outfit is worn with enhanced image extraction"""
        try:
            if not self.conn:
                return None
            
            if worn_date is None:
                worn_date = datetime.now()
            
            cursor = self.conn.cursor()
            
            # Enhanced image extraction logic
            image_url = None
            image_path = None
            
            logger.info(f"Recording outfit for user {user_id}")
            logger.info(f"Outfit data structure: {json.dumps(outfit_data, indent=2, default=str)}")
            
            try:
                items = outfit_data.get('items', [])
                logger.info(f"Found {len(items)} items in outfit_data")
                
                if items:
                    first_item = items[0]
                    logger.info(f"First item type: {type(first_item)}")
                    logger.info(f"First item data: {json.dumps(first_item, indent=2, default=str)}")
                    
                    if isinstance(first_item, dict):
                        # Try multiple possible image field names in order of preference
                        image_candidates = [
                            first_item.get('image_path'),
                            first_item.get('image_url'),
                            first_item.get('imageUrl'),
                            first_item.get('imageUri'),
                            first_item.get('image'),
                            first_item.get('path'),
                            first_item.get('uri'),
                            first_item.get('src'),
                            first_item.get('photo'),
                            first_item.get('picture')
                        ]
                        
                        logger.info(f"Image candidates: {image_candidates}")
                        
                        # Use the first non-None, non-empty value
                        for candidate in image_candidates:
                            if candidate and isinstance(candidate, str) and candidate.strip():
                                image_path = candidate
                                image_url = candidate
                                logger.info(f"Selected image: {image_path}")
                                break
                        
                        if not image_path:
                            logger.warning(f"No valid image found in first item. Available keys: {list(first_item.keys())}")
                    else:
                        logger.warning(f"First item is not a dict: {type(first_item)} - {first_item}")
                else:
                    logger.warning("No items found in outfit_data")
                    
            except Exception as e:
                logger.error(f"Error extracting image from outfit_data: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
            
            try:
                check_sql = """
                    SELECT id FROM outfit_history
                    WHERE user_id = %s
                      AND DATE(worn_date) = DATE(%s)
                      AND outfit_data = %s::jsonb
                    LIMIT 1
                """
                cursor.execute(check_sql, (user_id, worn_date, json.dumps(outfit_data)))
                existing = cursor.fetchone()
                if existing:
                    logger.info(f"Duplicate worn outfit detected for user {user_id}, returning existing id {existing[0]}")
                    cursor.close()
                    return {'outfit_id': existing[0], 'duplicate': True}
            except Exception as e:
                logger.warning(f"Duplicate check failed: {e}")

            query = """
                INSERT INTO outfit_history (user_id, worn_date, occasion, weather, location, image_url, image_path, outfit_data, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            cursor.execute(query, (
                user_id, worn_date, occasion, weather, location,
                image_url, image_path, json.dumps(outfit_data), datetime.now()
            ))
            
            result = cursor.fetchone()
            self.conn.commit()
            cursor.close()
            
            if result:
                logger.info(f"Outfit recorded with ID: {result[0]}, image_path: {image_path}, image_url: {image_url}")
                return {'outfit_id': result[0]}
            return None
            
        except Exception as e:
            logger.error(f"Error recording worn outfit: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None