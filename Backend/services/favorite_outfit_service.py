# services/favorite_outfit_service.py
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from database.connection import db

logger = logging.getLogger(__name__)

class FavoriteOutfitService:
    def __init__(self):
        # Table already exists from your schema, no need to create it
        pass
    
    def save_favorite_outfit(self, user_id: int, outfit_data: Dict, outfit_name: str = None) -> Dict:
        """Save an outfit as favorite with name"""
        try:
            if not outfit_name:
                outfit_name = f"Outfit {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Prepare outfit data
            outfit_json = json.dumps(outfit_data.get('items', []))
            weather_json = json.dumps(outfit_data.get('weather_context', {}))
            occasion = outfit_data.get('occasion', 'casual')
            confidence = float(outfit_data.get('confidence', 0))
            
            # Insert into database
            insert_query = """
                INSERT INTO favorite_outfits 
                (user_id, name, occasion, confidence_score, weather_context, outfit_data)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            result = db.execute_query(insert_query, (
                user_id, outfit_name, occasion, confidence, weather_json, outfit_json
            ))
            
            if result:
                favorite_id = result[0]['id']
                logger.info(f"Outfit '{outfit_name}' saved as favorite with ID: {favorite_id}")
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
    
    def save_favorite(self, user_id: int, outfit_data: dict, name: str) -> Dict:
        """Save an outfit as favorite - main entry point"""
        try:
            return self.save_favorite_outfit(user_id, outfit_data, name)
            
        except Exception as e:
            logger.error(f"Error in save_favorite: {e}")
            return {
                'success': False,
                'message': f'Error saving favorite: {str(e)}'
            }
    
    def get_user_favorites(self, user_id: int) -> Dict:
        """Get all favorite outfits for a user"""
        try:
            query = """
                SELECT id, name, occasion, confidence_score, weather_context, 
                       outfit_data, notes, times_worn, created_at, updated_at
                FROM favorite_outfits
                WHERE user_id = %s
                ORDER BY created_at DESC
            """
            
            favorites = db.execute_query(query, (user_id,))
            
            # Format the response
            formatted_favorites = []
            for fav in favorites:
                try:
                    # Parse outfit data
                    outfit_items = json.loads(fav['outfit_data']) if fav['outfit_data'] else []
                    weather_context = json.loads(fav['weather_context']) if fav['weather_context'] else {}
                    
                    formatted_fav = {
                        'id': fav['id'],
                        'name': fav['name'],  # Use the stored name
                        'items': outfit_items,
                        'occasion': fav['occasion'],
                        'weather_context': weather_context,
                        'confidence': fav['confidence_score'],
                        'notes': fav['notes'],
                        'times_worn': fav['times_worn'] or 0,
                        'created_at': fav['created_at'].isoformat() if fav['created_at'] else None,
                        'updated_at': fav['updated_at'].isoformat() if fav['updated_at'] else None
                    }
                    formatted_favorites.append(formatted_fav)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing outfit data for favorite {fav['id']}: {e}")
                    continue
            
            return {
                'status': 'success',
                'favorites': formatted_favorites
            }
            
        except Exception as e:
            logger.error(f"Error getting user favorites: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'favorites': []
            }
    
    def delete_favorite(self, user_id: int, favorite_id: int) -> Dict:
        """Delete a favorite outfit by ID"""
        try:
            query = """
                DELETE FROM favorite_outfits 
                WHERE id = %s AND user_id = %s
            """
            
            db.execute_query(query, (favorite_id, user_id))
            return {
                'status': 'success',
                'message': 'Favorite deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting favorite: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_favorite_by_id(self, favorite_id: int) -> Optional[Dict]:
        """Get a favorite outfit by ID"""
        try:
            query = """
                SELECT id, user_id, name, occasion, confidence_score, weather_context,
                       outfit_data, notes, times_worn, created_at, updated_at
                FROM favorite_outfits
                WHERE id = %s
            """
            
            result = db.execute_query(query, (favorite_id,))
            
            if result:
                fav = result[0]
                outfit_items = json.loads(fav['outfit_data']) if fav['outfit_data'] else []
                weather_context = json.loads(fav['weather_context']) if fav['weather_context'] else {}
                
                return {
                    'id': fav['id'],
                    'user_id': fav['user_id'],
                    'name': fav['name'],
                    'items': outfit_items,
                    'occasion': fav['occasion'],
                    'weather_context': weather_context,
                    'confidence': fav['confidence_score'],
                    'notes': fav['notes'],
                    'times_worn': fav['times_worn'] or 0,
                    'created_at': fav['created_at'].isoformat() if fav['created_at'] else None,
                    'updated_at': fav['updated_at'].isoformat() if fav['updated_at'] else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting favorite by ID: {e}")
            return None
    
    def update_favorite(self, user_id: int, favorite_id: int, updates: Dict) -> Dict:
        """Update a favorite outfit including name"""
        try:
            update_fields = []
            values = []
            
            if 'name' in updates:
                update_fields.append('name = %s')
                values.append(updates['name'])
            
            if 'notes' in updates:
                update_fields.append('notes = %s')
                values.append(updates['notes'])
            
            if 'occasion' in updates:
                update_fields.append('occasion = %s')
                values.append(updates['occasion'])
            
            if not update_fields:
                return {
                    'status': 'error',
                    'message': 'No valid fields to update'
                }
            
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            values.extend([favorite_id, user_id])
            
            query = f"""
                UPDATE favorite_outfits 
                SET {', '.join(update_fields)}
                WHERE id = %s AND user_id = %s
            """
            
            db.execute_query(query, values)
            
            return {
                'status': 'success',
                'message': 'Favorite outfit updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating favorite outfit: {e}")
            return {
                'status': 'error',
                'message': f'Error updating favorite: {str(e)}'
            }
    
    def wear_favorite_outfit(self, favorite_id: int) -> Dict:
        """Mark a favorite outfit as worn"""
        try:
            query = """
                UPDATE favorite_outfits 
                SET times_worn = times_worn + 1,
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