# services/favorite_outfit_service.py
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from database.connection import db

logger = logging.getLogger(__name__)

class FavoriteOutfitService:
    def __init__(self):
        pass

    def _normalize_occasion(self, raw_occasion) -> str:
        """Normalize incoming occasion values to DB enum values."""
        try:
            occ_candidate = str(raw_occasion).lower() if raw_occasion is not None else 'casual'
        except Exception:
            occ_candidate = 'casual'

        allowed_occasions = {
            'casual', 'formal', 'business', 'athletic',
            'beachwear', 'party', 'datenight', 'seasonal'
        }

        occasion_map = {
            'work': 'business',
            'workplace': 'business',
            'workout': 'athletic',
            'gym': 'athletic',
            'sports': 'athletic',
            'beach': 'beachwear',
            'date': 'datenight',
            'date-night': 'datenight',
            'nightout': 'party',
            'party-night': 'party'
        }

        if occ_candidate in allowed_occasions:
            return occ_candidate
        if occ_candidate in occasion_map:
            return occasion_map[occ_candidate]

        # Fuzzy fallback
        if 'work' in occ_candidate:
            return 'business'
        if 'date' in occ_candidate:
            return 'datenight'
        if 'beach' in occ_candidate:
            return 'beachwear'
        if 'sport' in occ_candidate or 'gym' in occ_candidate:
            return 'athletic'
        if 'party' in occ_candidate or 'night' in occ_candidate:
            return 'party'

        return 'casual'
    
    def save_favorite_outfit(self, user_id: int, outfit_data: Dict, outfit_name: str = None) -> Dict:
        """Save an outfit as favorite with name"""
        try:
            if not outfit_name:
                outfit_name = f"Outfit {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Prepare outfit data
            outfit_items = outfit_data.get('items', []) or []
            outfit_json = json.dumps(outfit_items)
            weather_json = json.dumps(outfit_data.get('weather_context', {}))
            # Normalize occasion to DB enum value
            occasion = self._normalize_occasion(outfit_data.get('occasion', 'casual'))
            confidence = float(outfit_data.get('confidence', 0))
            # Try to extract a representative image from the first item
            image_url = None
            image_path = None
            try:
                if isinstance(outfit_items, (list, tuple)) and len(outfit_items) > 0:
                    first_item = outfit_items[0]
                    if isinstance(first_item, dict):
                        image_url = first_item.get('image_url') or first_item.get('image') or None
                        image_path = first_item.get('image_path') or first_item.get('path') or None
            except Exception:
                image_url = None
                image_path = None
            
            # Insert into database
            insert_query = """
                INSERT INTO favorite_outfits 
                (user_id, name, occasion, confidence_score, weather_context, outfit_data, image_url, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            result = db.execute_query(insert_query, (
                user_id, outfit_name, occasion, confidence, weather_json, outfit_json, image_url, image_path
            ))

            favorite_id = None
            try:
                if isinstance(result, dict):
                    # cursor.fetchone() with RealDictCursor -> dict
                    favorite_id = result.get('id')
                elif isinstance(result, (list, tuple)) and len(result) > 0:
                    first = result[0]
                    if isinstance(first, dict):
                        favorite_id = first.get('id')
                elif isinstance(result, bool):
                    # No RETURNING but affected rows indicated success
                    favorite_id = None
            except Exception as e:
                logger.error(f"Error parsing DB result for favorite insert: {e}")

            if favorite_id:
                logger.info(f"Outfit '{outfit_name}' saved as favorite with ID: {favorite_id}")
                return {
                    'success': True,
                    'message': 'Outfit saved to favorites!',
                    'id': favorite_id
                }

            # If we didn't get an ID back, provide the raw result for debugging
            return {
                'success': False,
                'message': f'Failed to save outfit to favorites: {result}',
                'raw_result': result
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
                       outfit_data, notes, times_worn, image_url, image_path, created_at, updated_at
                FROM favorite_outfits
                WHERE user_id = %s
                ORDER BY created_at DESC
            """
            
            favorites = db.execute_query(query, (user_id,))
            
            # Format the response
            formatted_favorites = []
            for fav in favorites:
                try:
                    # Parse outfit_data which may be stored as a JSON string or
                    # may already be returned by psycopg2 as a Python list/dict
                    raw_outfit = fav.get('outfit_data')
                    if raw_outfit is None:
                        outfit_items = []
                    elif isinstance(raw_outfit, (list, dict)):
                        outfit_items = raw_outfit
                    elif isinstance(raw_outfit, str):
                        try:
                            outfit_items = json.loads(raw_outfit)
                        except Exception:
                            outfit_items = []
                    else:
                        outfit_items = []

                    # Same for weather_context
                    raw_weather = fav.get('weather_context')
                    if raw_weather is None:
                        weather_context = {}
                    elif isinstance(raw_weather, (dict, list)):
                        weather_context = raw_weather
                    elif isinstance(raw_weather, str):
                        try:
                            weather_context = json.loads(raw_weather)
                        except Exception:
                            weather_context = {}
                    else:
                        weather_context = {}

                    formatted_fav = {
                        'id': fav['id'],
                        'name': fav['name'],  # Use the stored name
                        'items': outfit_items,
                        'occasion': fav['occasion'],
                        'weather_context': weather_context,
                        'confidence': fav['confidence_score'],
                        'notes': fav['notes'],
                        'times_worn': fav['times_worn'] or 0,
                        'image_url': fav.get('image_url'),
                        'image_path': fav.get('image_path'),
                        'created_at': fav['created_at'].isoformat() if fav['created_at'] else None,
                        'updated_at': fav['updated_at'].isoformat() if fav['updated_at'] else None
                    }
                    formatted_favorites.append(formatted_fav)
                except Exception as e:
                    logger.error(f"Error parsing outfit data for favorite {fav.get('id')}: {e}")
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
                       outfit_data, notes, times_worn, image_url, image_path, created_at, updated_at
                FROM favorite_outfits
                WHERE id = %s
            """
            
            result = db.execute_query(query, (favorite_id,))
            
            if result:
                fav = result[0]

                # Parse outfit_data robustly (accept already-parsed lists/dicts)
                raw_outfit = fav.get('outfit_data')
                if raw_outfit is None:
                    outfit_items = []
                elif isinstance(raw_outfit, (list, dict)):
                    outfit_items = raw_outfit
                elif isinstance(raw_outfit, str):
                    try:
                        outfit_items = json.loads(raw_outfit)
                    except Exception:
                        outfit_items = []
                else:
                    outfit_items = []

                raw_weather = fav.get('weather_context')
                if raw_weather is None:
                    weather_context = {}
                elif isinstance(raw_weather, (dict, list)):
                    weather_context = raw_weather
                elif isinstance(raw_weather, str):
                    try:
                        weather_context = json.loads(raw_weather)
                    except Exception:
                        weather_context = {}
                else:
                    weather_context = {}

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
                    'image_url': fav.get('image_url'),
                    'image_path': fav.get('image_path'),
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
                # Normalize occasion before saving to DB
                normalized = self._normalize_occasion(updates['occasion'])
                update_fields.append('occasion = %s')
                values.append(normalized)
            
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