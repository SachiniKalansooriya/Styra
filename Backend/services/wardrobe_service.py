from datetime import datetime
import logging
from database.connection import db

logger = logging.getLogger(__name__)

class WardrobeService:
    """Service for managing wardrobe items in the database"""
    
    def save_wardrobe_item(self, item_data):
        """Save a wardrobe item to the database"""
        try:
            # Extract and validate data
            name = str(item_data.get('name', 'Untitled Item')).strip()
            category = str(item_data.get('category', 'unknown')).strip()
            color = str(item_data.get('color', 'unknown')).strip()
            season = str(item_data.get('season', 'all')).strip()
            image_path = item_data.get('image_path')
            
            logger.info(f"Saving wardrobe item: name={name}, category={category}, color={color}")
            
            # Handle confidence field
            confidence = None
            if item_data.get('confidence') is not None:
                try:
                    confidence = float(item_data.get('confidence'))
                    confidence = max(0.0, min(1.0, confidence))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid confidence value: {item_data.get('confidence')}, error: {e}")
                    confidence = None
            
            analysis_method = item_data.get('analysis_method')
            user_id = int(item_data.get('user_id', 1))
            
            # Prepare the INSERT query
            query = """
            INSERT INTO wardrobe_items 
            (user_id, name, category, color, season, image_path, confidence, analysis_method, created_at)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, created_at
            """
            
            params = (
                user_id, name, category, color, season, image_path, confidence, analysis_method
            )
            
            logger.info(f"Executing query with params: {params}")
            result = db.execute_query(query, params)
            logger.info(f"Database result: {result}")
            
            if result:
                returned_id = result['id']
                created_at = result['created_at']
                logger.info(f"Wardrobe item saved successfully with ID: {returned_id}")
                return {
                    "item_id": str(returned_id),
                    "created_at": created_at
                }
            else:
                logger.error("No result returned from INSERT query")
                return None
                
        except Exception as e:
            logger.exception(f"Error saving wardrobe item: {e}")
            return None
    
    def get_wardrobe_items(self, limit=100, offset=0, user_id=None):
        """Get wardrobe items from the database"""
        try:
            if user_id:
                query = """
                SELECT id, user_id, name, category, color, season, image_path, 
                       confidence, analysis_method, times_worn, last_worn, 
                       created_at, updated_at
                FROM wardrobe_items
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """
                params = (user_id, limit, offset)
            else:
                query = """
                SELECT id, user_id, name, category, color, season, image_path, 
                       confidence, analysis_method, times_worn, last_worn, 
                       created_at, updated_at
                FROM wardrobe_items
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """
                params = (limit, offset)
                
            results = db.execute_query(query, params)
            
            if results:
                items = []
                for result in results:
                    item = dict(result)
                    # Convert integer ID to string for consistency
                    if 'id' in item:
                        item['id'] = str(item['id'])
                    # Map image_path to image_url for frontend compatibility
                    if 'image_path' in item:
                        item['image_url'] = item['image_path']
                    items.append(item)
                
                logger.info(f"Retrieved {len(items)} wardrobe items from database")
                return items
            else:
                logger.info("No wardrobe items found in database")
                return []
                
        except Exception as e:
            logger.exception(f"Error retrieving wardrobe items: {e}")
            return []
    
    def get_wardrobe_item_by_id(self, item_id):
        """Get a specific wardrobe item by ID"""
        try:
            query = """
            SELECT id, user_id, name, category, color, season, image_path, 
                   confidence, analysis_method, times_worn, last_worn, 
                   created_at, updated_at
            FROM wardrobe_items
            WHERE id = %s
            """
            params = (item_id,)
            results = db.execute_query(query, params)
            
            if results and len(results) > 0:
                item = dict(results[0])
                # Convert integer ID to string
                if 'id' in item:
                    item['id'] = str(item['id'])
                # Map image_path to image_url for frontend compatibility
                if 'image_path' in item:
                    item['image_url'] = item['image_path']
                
                return item
            else:
                return None
                
        except Exception as e:
            logger.exception(f"Error retrieving wardrobe item by ID: {e}")
            return None
    
    def delete_wardrobe_item(self, item_id):
        """Delete a wardrobe item from the database"""
        try:
            query = """
            DELETE FROM wardrobe_items 
            WHERE id = %s
            RETURNING id
            """
            params = (item_id,)
            result = db.execute_query(query, params)
            
            if result:
                logger.info(f"Wardrobe item deleted from database: {item_id}")
                return True
            else:
                logger.warning(f"No wardrobe item found to delete: {item_id}")
                return False
                
        except Exception as e:
            logger.exception(f"Error deleting wardrobe item: {e}")
            return False

# Create global instance
wardrobe_service = WardrobeService()