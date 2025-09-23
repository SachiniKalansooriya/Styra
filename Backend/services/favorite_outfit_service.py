import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from database.connection import db

logger = logging.getLogger(__name__)

class FavoriteOutfitService:
    def __init__(self):
        self.create_table_if_not_exists()
    
    def create_table_if_not_exists(self):
        """Create favorite_outfits table if it doesn't exist"""
        try:
            create_table_query = """
                CREATE TABLE IF NOT EXISTS favorite_outfits (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    outfit_name VARCHAR(255) NOT NULL,
                    outfit_data TEXT NOT NULL,
                    occasion VARCHAR(100),
                    season VARCHAR(50),
                    weather_context TEXT,
                    confidence_score INTEGER DEFAULT 0,
                    notes TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    times_worn INTEGER DEFAULT 0,
                    last_worn TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            db.execute_query(create_table_query)
            logger.info("Favorite outfits table created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating favorite_outfits table: {e}")
    
    def save_favorite_outfit(self, user_id: int, outfit_data: Dict, outfit_name: str = None) -> Dict:
        """Save an outfit as favorite"""
        try:
            # Generate outfit name if not provided
            if not outfit_name:
                outfit_name = f"Outfit {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Prepare outfit data
            outfit_json = json.dumps(outfit_data.get('items', []))
            weather_json = json.dumps(outfit_data.get('weather_context', {}))
            occasion = outfit_data.get('occasion', 'casual')
            confidence = outfit_data.get('confidence', 0)
            
            # Determine season based on current date or weather
            current_month = datetime.now().month
            season_map = {
                (12, 1, 2): 'winter',
                (3, 4, 5): 'spring', 
                (6, 7, 8): 'summer',
                (9, 10, 11): 'fall'
            }
            season = next((season for months, season in season_map.items() if current_month in months), 'all')
            
            # Insert into database
            insert_query = """
                INSERT INTO favorite_outfits 
                (user_id, outfit_name, outfit_data, occasion, season, weather_context, confidence_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            result = db.execute_query(insert_query, (
                user_id, outfit_name, outfit_json, occasion, season, weather_json, confidence
            ))
            
            if result:
                favorite_id = result[0]['id']
                logger.info(f"Outfit saved as favorite with ID: {favorite_id}")
                return {
                    'success': True,
                    'message': 'Outfit saved to favorites!',
                    'id': favorite_id
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to save outfit to favorites'
                }
                
        except Exception as e:
            logger.error(f"Error saving favorite outfit: {e}")
            return {
                'success': False,
                'message': f'Error saving favorite: {str(e)}'
            }
    
    def save_favorite(self, favorite_data: dict) -> Dict:
        """Save an outfit as favorite - updated to match endpoint"""
        try:
            user_id = favorite_data['user_id']
            outfit_name = favorite_data.get('name', f"Outfit {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            outfit_data = favorite_data.get('outfit_data', {})
            
            # Use the existing save_favorite_outfit method
            return self.save_favorite_outfit(user_id, outfit_data, outfit_name)
            
        except Exception as e:
            logger.error(f"Error in save_favorite: {e}")
            return {
                'success': False,
                'message': f'Error saving favorite: {str(e)}'
            }
    
    def get_user_favorites(self, user_id: int) -> List[Dict]:
        """Get all favorite outfits for a user"""
        try:
            query = """
                SELECT id, outfit_name, outfit_data, occasion, season, 
                       weather_context, confidence_score, notes, times_worn,
                       last_worn, created_at, updated_at
                FROM favorite_outfits
                WHERE user_id = %s AND is_active = TRUE
                ORDER BY created_at DESC
            """
            
            favorites = db.execute_query(query, (user_id,))
            
            # Format the response
            formatted_favorites = []
            for fav in favorites:
                try:
                    outfit_items = json.loads(fav['outfit_data']) if fav['outfit_data'] else []
                    weather_context = json.loads(fav['weather_context']) if fav['weather_context'] else {}
                    
                    formatted_fav = {
                        'id': fav['id'],
                        'name': fav['outfit_name'],
                        'items': outfit_items,
                        'occasion': fav['occasion'],
                        'season': fav['season'],
                        'weather_context': weather_context,
                        'confidence': fav['confidence_score'],
                        'notes': fav['notes'],
                        'times_worn': fav['times_worn'] or 0,
                        'last_worn': fav['last_worn'].isoformat() if fav['last_worn'] else None,
                        'created_at': fav['created_at'].isoformat() if fav['created_at'] else None,
                        'updated_at': fav['updated_at'].isoformat() if fav['updated_at'] else None
                    }
                    formatted_favorites.append(formatted_fav)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing outfit data for favorite {fav['id']}: {e}")
                    continue
            
            return formatted_favorites
            
        except Exception as e:
            logger.error(f"Error getting user favorites: {e}")
            return []
    
    def delete_favorite(self, favorite_id: int) -> bool:
        """Delete a favorite outfit by ID"""
        try:
            query = """
                UPDATE favorite_outfits 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            db.execute_query(query, (favorite_id,))
            return True
            
        except Exception as e:
            logger.error(f"Error deleting favorite: {e}")
            return False
    
    def get_favorite_by_id(self, favorite_id: int) -> Optional[Dict]:
        """Get a favorite outfit by ID"""
        try:
            query = """
                SELECT id, user_id, outfit_name, outfit_data, occasion, season, 
                       weather_context, confidence_score, notes, times_worn,
                       last_worn, created_at, updated_at
                FROM favorite_outfits
                WHERE id = %s AND is_active = TRUE
            """
            
            result = db.execute_query(query, (favorite_id,))
            
            if result:
                fav = result[0]
                outfit_items = json.loads(fav['outfit_data']) if fav['outfit_data'] else []
                weather_context = json.loads(fav['weather_context']) if fav['weather_context'] else {}
                
                return {
                    'id': fav['id'],
                    'user_id': fav['user_id'],
                    'name': fav['outfit_name'],
                    'items': outfit_items,
                    'occasion': fav['occasion'],
                    'season': fav['season'],
                    'weather_context': weather_context,
                    'confidence': fav['confidence_score'],
                    'notes': fav['notes'],
                    'times_worn': fav['times_worn'] or 0,
                    'last_worn': fav['last_worn'].isoformat() if fav['last_worn'] else None,
                    'created_at': fav['created_at'].isoformat() if fav['created_at'] else None,
                    'updated_at': fav['updated_at'].isoformat() if fav['updated_at'] else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting favorite by ID: {e}")
            return None
    
    def update_favorite(self, favorite_id: int, updates: Dict) -> Dict:
        """Update a favorite outfit"""
        try:
            # Build dynamic update query
            update_fields = []
            values = []
            
            if 'outfit_name' in updates:
                update_fields.append('outfit_name = %s')
                values.append(updates['outfit_name'])
            
            if 'notes' in updates:
                update_fields.append('notes = %s')
                values.append(updates['notes'])
            
            if 'occasion' in updates:
                update_fields.append('occasion = %s')
                values.append(updates['occasion'])
            
            if not update_fields:
                return {
                    'success': False,
                    'message': 'No valid fields to update'
                }
            
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            values.append(favorite_id)
            
            query = f"""
                UPDATE favorite_outfits 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            
            db.execute_query(query, values)
            
            return {
                'success': True,
                'message': 'Favorite outfit updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating favorite outfit: {e}")
            return {
                'success': False,
                'message': f'Error updating favorite: {str(e)}'
            }
    
    def wear_favorite_outfit(self, favorite_id: int) -> Dict:
        """Mark a favorite outfit as worn"""
        try:
            query = """
                UPDATE favorite_outfits 
                SET times_worn = times_worn + 1, 
                    last_worn = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            db.execute_query(query, (favorite_id,))
            
            return {
                'success': True,
                'message': 'Outfit marked as worn!'
            }
            
        except Exception as e:
            logger.error(f"Error updating worn status: {e}")
            return {
                'success': False,
                'message': f'Error updating worn status: {str(e)}'
            }

# Global instance
favorite_outfit_service = FavoriteOutfitService()