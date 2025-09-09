# services/outfit_history_service.py
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from models.outfit_history import OutfitHistory

logger = logging.getLogger(__name__)

class OutfitHistoryService:
    """Service for managing user's outfit history"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.outfit_history = OutfitHistory(db_connection)
        logger.info("Outfit history service initialized")
    
    def record_worn_outfit(self, outfit_data: Dict[str, Any], 
                          user_id: int = 1, 
                          occasion: str = None,
                          weather: str = None,
                          location: str = None,
                          worn_date: date = None) -> Dict[str, Any]:
        """Record that user wore a specific outfit"""
        try:
            if not worn_date:
                worn_date = datetime.now().date()
            
            # Check if outfit already recorded for this date
            existing = self.outfit_history.get_outfit_by_date(user_id, worn_date)
            if existing:
                logger.warning(f"Outfit already recorded for {worn_date}, updating...")
                # Could implement update logic here
            
            # Save the outfit
            outfit_id = self.outfit_history.save_worn_outfit(
                user_id=user_id,
                outfit_data=outfit_data,
                occasion=occasion,
                weather=weather,
                location=location,
                worn_date=worn_date
            )
            
            logger.info(f"Recorded worn outfit {outfit_id} for user {user_id} on {worn_date}")
            
            return {
                'status': 'success',
                'outfit_id': outfit_id,
                'worn_date': worn_date.isoformat(),
                'message': 'Outfit recorded successfully'
            }
            
        except Exception as e:
            logger.error(f"Error recording worn outfit: {e}")
            return {
                'status': 'error',
                'message': f'Failed to record outfit: {str(e)}'
            }
    
    def get_user_outfit_history(self, user_id: int = 1, 
                               limit: int = 50,
                               start_date: str = None,
                               end_date: str = None) -> Dict[str, Any]:
        """Get user's complete outfit history"""
        try:
            # Parse dates if provided
            parsed_start = None
            parsed_end = None
            
            if start_date:
                parsed_start = datetime.fromisoformat(start_date).date()
            if end_date:
                parsed_end = datetime.fromisoformat(end_date).date()
            
            history = self.outfit_history.get_outfit_history(
                user_id=user_id,
                limit=limit,
                start_date=parsed_start,
                end_date=parsed_end
            )
            
            # Get statistics
            stats = self.outfit_history.get_outfit_stats(user_id)
            
            logger.info(f"Retrieved {len(history)} outfit history entries for user {user_id}")
            
            return {
                'status': 'success',
                'history': history,
                'stats': stats,
                'total_count': len(history)
            }
            
        except Exception as e:
            logger.error(f"Error getting outfit history: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get outfit history: {str(e)}',
                'history': [],
                'stats': {}
            }
    
    def get_outfit_by_date(self, worn_date: str, user_id: int = 1) -> Dict[str, Any]:
        """Get specific outfit worn on a date"""
        try:
            target_date = datetime.fromisoformat(worn_date).date()
            outfit = self.outfit_history.get_outfit_by_date(user_id, target_date)
            
            if outfit:
                logger.info(f"Found outfit for user {user_id} on {worn_date}")
                return {
                    'status': 'success',
                    'outfit': outfit,
                    'worn_date': worn_date
                }
            else:
                return {
                    'status': 'not_found',
                    'message': f'No outfit found for {worn_date}',
                    'outfit': None
                }
                
        except Exception as e:
            logger.error(f"Error getting outfit by date: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get outfit: {str(e)}',
                'outfit': None
            }
    
    def rate_outfit(self, outfit_id: int, rating: int, notes: str = None) -> Dict[str, Any]:
        """Rate a worn outfit"""
        try:
            if not 1 <= rating <= 5:
                return {
                    'status': 'error',
                    'message': 'Rating must be between 1 and 5'
                }
            
            success = self.outfit_history.update_outfit_rating(outfit_id, rating, notes)
            
            if success:
                logger.info(f"Updated outfit {outfit_id} rating to {rating}")
                return {
                    'status': 'success',
                    'message': 'Outfit rated successfully'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to update rating'
                }
                
        except Exception as e:
            logger.error(f"Error rating outfit: {e}")
            return {
                'status': 'error',
                'message': f'Failed to rate outfit: {str(e)}'
            }
    
    def get_popular_items(self, user_id: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get most frequently worn wardrobe items"""
        try:
            # This would require more complex analysis of outfit_data
            # For now, return basic stats
            stats = self.outfit_history.get_outfit_stats(user_id)
            
            return {
                'status': 'success',
                'stats': stats,
                'message': 'Popular items analysis (basic implementation)'
            }
            
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            return {
                'status': 'error',
                'message': f'Failed to analyze popular items: {str(e)}'
            }
