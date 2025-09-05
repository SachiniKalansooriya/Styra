from datetime import datetime
import logging
from database.connection import db

logger = logging.getLogger(__name__)

class WardrobeService:
    """Service for managing wardrobe items in the database"""
    
    def save_wardrobe_item(self, item_data):
        """Save a wardrobe item to the database"""
        try:
            # Extract data from item
            name = item_data.get('name', 'Untitled Item')
            category = item_data.get('category', 'unknown')
            color = item_data.get('color', 'unknown')
            season = item_data.get('season', 'all')
            image_path = item_data.get('image_path')
            
            logger.info(f"Saving wardrobe item: name={name}, category={category}, color={color}, image_path={image_path}")
            
            # Analysis-related fields
            confidence = float(item_data.get('confidence', 0.0)) if item_data.get('confidence') else None
            analysis_method = item_data.get('analysis_method', None)
            
            # User ID (default to 1 for now)
            user_id = item_data.get('user_id', 1)
            
            # Insert into the database
            query = """
            INSERT INTO wardrobe_items 
            (user_id, name, category, color, season, image_path, confidence, analysis_method)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
            """
            
            params = (
                user_id, name, category, color, season, image_path, confidence, analysis_method
            )
            
            logger.info(f"Executing query with params: {params}")
            result = db.execute_query(query, params)
            
            if result and len(result) > 0:
                returned_id = result[0]['id']
                created_at = result[0]['created_at']
                logger.info(f"Wardrobe item saved successfully with ID: {returned_id}, image_path: {image_path}")
                return {
                    "item_id": str(returned_id),
                    "created_at": created_at
                }
            else:
                logger.warning("Wardrobe item was not saved properly")
                return None
                
        except Exception as e:
            logger.error(f"Error saving wardrobe item: {e}")
            return None
    
    def get_wardrobe_items(self, limit=100, offset=0):
        """Get wardrobe items from the database"""
        try:
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
            logger.error(f"Error retrieving wardrobe items: {e}")
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
            logger.error(f"Error retrieving wardrobe item by ID: {e}")
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
            
            if result and len(result) > 0:
                logger.info(f"Wardrobe item deleted from database: {item_id}")
                return True
            else:
                logger.warning(f"No wardrobe item found to delete: {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting wardrobe item: {e}")
            return False

# Create global instance
wardrobe_service = WardrobeService()