# services/wardrobe_service.py
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
            
            # Handle season properly - only allow valid enum values
            season = str(item_data.get('season', 'all')).strip().lower()
            valid_seasons = ['spring', 'summer', 'fall', 'winter', 'all']
            if season not in valid_seasons:
                logger.warning(f"Invalid season value '{season}', defaulting to 'all'")
                season = 'all'  # Default to 'all' for invalid values
            
            image_path = item_data.get('image_path')
            
            logger.info(f"Saving wardrobe item: name={name}, category={category}, color={color}, season={season}")
            
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
            
            # Remove any fields that might cause issues
            # Don't pass occasion to database if it doesn't have an occasion column
            
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
                # Handle both single dict and list responses
                if isinstance(result, list) and len(result) > 0:
                    result_data = result[0]
                else:
                    result_data = result
                
                returned_id = result_data['id']
                created_at = result_data['created_at']
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
                # Handle both single item and list results
                results_list = results if isinstance(results, list) else [results]
                
                for result in results_list:
                    item = dict(result)
                    # Convert integer ID to string for consistency
                    if 'id' in item:
                        item['id'] = str(item['id'])
                    # Map image_path to image_url for frontend compatibility
                    if 'image_path' in item:
                        item['image_url'] = item['image_path']
                    # Add default values for missing fields
                    item['timesWorn'] = item.get('times_worn', 0)
                    item['pendingSync'] = False  # Items from DB are synced
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
            
            if results:
                # Handle both single dict and list responses
                if isinstance(results, list) and len(results) > 0:
                    item = dict(results[0])
                else:
                    item = dict(results)
                
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
    
    def get_user_wardrobe_items(self, user_id, limit=100):
        """Get wardrobe items for a specific user"""
        return self.get_wardrobe_items(limit=limit, user_id=user_id)
    
    def update_item_wear_count(self, item_id):
        """Update the times worn count for an item"""
        try:
            query = """
            UPDATE wardrobe_items 
            SET times_worn = COALESCE(times_worn, 0) + 1, 
                last_worn = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, times_worn
            """
            result = db.execute_query(query, (item_id,))
            
            if result:
                logger.info(f"Updated wear count for item {item_id}")
                return True
            return False
            
        except Exception as e:
            logger.exception(f"Error updating wear count: {e}")
            return False

# Create global instance
wardrobe_service = WardrobeService()