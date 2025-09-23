import logging
from database.connection import db
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class TripService:
    def save_trip(self, trip_data):
        """Save trip to database"""
        try:
            # Extract trip details
            destination = trip_data.get('destination')
            start_date = trip_data.get('start_date')
            end_date = trip_data.get('end_date')
            activities = json.dumps(trip_data.get('activities', []))
            weather_expected = trip_data.get('weather_expected')
            packing_style = trip_data.get('packing_style', 'minimal')
            packing_list = json.dumps(trip_data.get('packing_list', []))
            user_id = trip_data.get('user_id', 1)
            
            query = """
                INSERT INTO trips (user_id, destination, start_date, end_date, activities, 
                                 weather_expected, packing_style, packing_list, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """
            
            result = db.execute_query(query, (
                user_id, destination, start_date, end_date, activities,
                weather_expected, packing_style, packing_list, datetime.now()
            ))
            
            if result:
                logger.info(f"Trip saved successfully with ID: {result['id']}")
                return {
                    'id': result['id'],
                    'created_at': result['created_at'],
                    'message': 'Trip saved successfully'
                }
            
            raise Exception("Failed to save trip")
            
        except Exception as e:
            logger.error(f"Error saving trip: {e}")
            raise e
    
    def get_user_trips(self, user_id=1):
        """Get all trips for a user"""
        try:
            query = """
                SELECT * FROM trips
                WHERE user_id = %s
                ORDER BY created_at DESC
            """
            
            trips = db.execute_query(query, (user_id,))
            
            # Convert to list of dicts and parse JSON fields
            result = []
            for trip in trips:
                trip_dict = dict(trip)
                # Parse JSON fields back to Python objects
                if trip_dict.get('activities'):
                    try:
                        trip_dict['activities'] = json.loads(trip_dict['activities'])
                    except:
                        trip_dict['activities'] = []
                
                if trip_dict.get('packing_list'):
                    try:
                        trip_dict['packing_list'] = json.loads(trip_dict['packing_list'])
                    except:
                        trip_dict['packing_list'] = []
                
                result.append(trip_dict)
            
            logger.info(f"Retrieved {len(result)} trips for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting user trips: {e}")
            raise e
    
    def delete_trip(self, trip_id):
        """Delete a trip"""
        try:
            query = "DELETE FROM trips WHERE id = %s"
            db.execute_query(query, (trip_id,))
            logger.info(f"Trip {trip_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting trip: {e}")
            raise e

# Global instance
trip_service = TripService()