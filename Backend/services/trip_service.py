#!/usr/bin/env python3
"""
Trip Service - Handles CRUD operations for trips
"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from database.connection import db
from models.trip import Trip

logger = logging.getLogger(__name__)

class TripService:
    def __init__(self):
        """Initialize the trip service"""
        self.logger = logging.getLogger(__name__)

    def save_trip(self, trip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a new trip to the database
        
        Args:
            trip_data: Dictionary containing trip information
            
        Returns:
            Dictionary containing saved trip data with ID
        """
        try:
            self.logger.info(f"Saving trip to database: {trip_data.get('destination', 'Unknown')}")
            
            # Prepare trip data with JSON serialization for JSONB fields
            prepared_data = trip_data.copy()
            
            # Convert lists and dicts to JSON strings for PostgreSQL JSONB columns
            if 'packing_list' in prepared_data and isinstance(prepared_data['packing_list'], (list, dict)):
                prepared_data['packing_list'] = json.dumps(prepared_data['packing_list'])
            
            if 'wardrobe_matches' in prepared_data and isinstance(prepared_data['wardrobe_matches'], (list, dict)):
                prepared_data['wardrobe_matches'] = json.dumps(prepared_data['wardrobe_matches'])
            
            if 'coverage_analysis' in prepared_data and isinstance(prepared_data['coverage_analysis'], (list, dict)):
                prepared_data['coverage_analysis'] = json.dumps(prepared_data['coverage_analysis'])
            
            # Insert trip into database
            query = """
                INSERT INTO trips (
                    user_id, destination, start_date, end_date, 
                    activities, weather_expected, packing_style,
                    packing_list, wardrobe_matches, coverage_analysis, notes
                ) VALUES (
                    %(user_id)s, %(destination)s, %(start_date)s, %(end_date)s,
                    %(activities)s, %(weather_expected)s, %(packing_style)s,
                    %(packing_list)s, %(wardrobe_matches)s, %(coverage_analysis)s, %(notes)s
                ) RETURNING id, created_at, updated_at;
            """
            
            result = db.execute_query(query, prepared_data, fetch=True)
            
            if result and len(result) > 0:
                saved_trip = result[0]
                trip_data.update({
                    'id': saved_trip['id'],
                    'created_at': saved_trip['created_at'].isoformat() if saved_trip['created_at'] else None,
                    'updated_at': saved_trip['updated_at'].isoformat() if saved_trip['updated_at'] else None
                })
                
                self.logger.info(f"Trip saved successfully with ID: {saved_trip['id']}")
                return trip_data
            else:
                raise Exception("Failed to save trip - no result returned")
                
        except Exception as e:
            self.logger.error(f"Error saving trip: {e}")
            raise e

    def get_user_trips(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all trips for a user
        
        Args:
            user_id: User ID to get trips for
            
        Returns:
            List of trip dictionaries
        """
        try:
            self.logger.info(f"Getting trips for user: {user_id}")
            
            query = """
                SELECT * FROM trips 
                WHERE user_id = %(user_id)s 
                ORDER BY created_at DESC;
            """
            
            results = db.execute_query(query, {'user_id': user_id}, fetch=True)
            
            if results:
                trips = []
                for result in results:
                    trip_dict = dict(result)
                    
                    # Parse JSON fields back to Python objects
                    if trip_dict.get('packing_list') and isinstance(trip_dict['packing_list'], str):
                        try:
                            trip_dict['packing_list'] = json.loads(trip_dict['packing_list'])
                        except (json.JSONDecodeError, TypeError):
                            trip_dict['packing_list'] = []
                    
                    if trip_dict.get('wardrobe_matches') and isinstance(trip_dict['wardrobe_matches'], str):
                        try:
                            trip_dict['wardrobe_matches'] = json.loads(trip_dict['wardrobe_matches'])
                        except (json.JSONDecodeError, TypeError):
                            trip_dict['wardrobe_matches'] = {}
                    
                    if trip_dict.get('coverage_analysis') and isinstance(trip_dict['coverage_analysis'], str):
                        try:
                            trip_dict['coverage_analysis'] = json.loads(trip_dict['coverage_analysis'])
                        except (json.JSONDecodeError, TypeError):
                            trip_dict['coverage_analysis'] = {}
                    
                    # Convert dates to ISO format for JSON serialization
                    if trip_dict.get('start_date'):
                        trip_dict['start_date'] = trip_dict['start_date'].isoformat()
                    if trip_dict.get('end_date'):
                        trip_dict['end_date'] = trip_dict['end_date'].isoformat()
                    if trip_dict.get('created_at'):
                        trip_dict['created_at'] = trip_dict['created_at'].isoformat()
                    if trip_dict.get('updated_at'):
                        trip_dict['updated_at'] = trip_dict['updated_at'].isoformat()
                    trips.append(trip_dict)
                
                self.logger.info(f"Found {len(trips)} trips for user {user_id}")
                return trips
            else:
                self.logger.info(f"No trips found for user {user_id}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting user trips: {e}")
            raise e

    def get_trip_by_id(self, trip_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific trip by ID
        
        Args:
            trip_id: Trip ID to retrieve
            
        Returns:
            Trip dictionary or None if not found
        """
        try:
            query = """
                SELECT * FROM trips 
                WHERE id = %(trip_id)s;
            """
            
            results = db.execute_query(query, {'trip_id': trip_id}, fetch=True)
            
            if results and len(results) > 0:
                trip_dict = dict(results[0])
                
                # Parse JSON fields back to Python objects
                if trip_dict.get('packing_list') and isinstance(trip_dict['packing_list'], str):
                    try:
                        trip_dict['packing_list'] = json.loads(trip_dict['packing_list'])
                    except (json.JSONDecodeError, TypeError):
                        trip_dict['packing_list'] = []
                
                if trip_dict.get('wardrobe_matches') and isinstance(trip_dict['wardrobe_matches'], str):
                    try:
                        trip_dict['wardrobe_matches'] = json.loads(trip_dict['wardrobe_matches'])
                    except (json.JSONDecodeError, TypeError):
                        trip_dict['wardrobe_matches'] = {}
                
                if trip_dict.get('coverage_analysis') and isinstance(trip_dict['coverage_analysis'], str):
                    try:
                        trip_dict['coverage_analysis'] = json.loads(trip_dict['coverage_analysis'])
                    except (json.JSONDecodeError, TypeError):
                        trip_dict['coverage_analysis'] = {}
                
                # Convert dates to ISO format
                if trip_dict.get('start_date'):
                    trip_dict['start_date'] = trip_dict['start_date'].isoformat()
                if trip_dict.get('end_date'):
                    trip_dict['end_date'] = trip_dict['end_date'].isoformat()
                if trip_dict.get('created_at'):
                    trip_dict['created_at'] = trip_dict['created_at'].isoformat()
                if trip_dict.get('updated_at'):
                    trip_dict['updated_at'] = trip_dict['updated_at'].isoformat()
                
                return trip_dict
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting trip by ID {trip_id}: {e}")
            raise e

    def update_trip(self, trip_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing trip
        
        Args:
            trip_id: Trip ID to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated trip dictionary
        """
        try:
            # Build dynamic update query
            set_clauses = []
            params = {'trip_id': trip_id, 'updated_at': datetime.utcnow()}
            
            for key, value in updates.items():
                if key not in ['id', 'created_at', 'updated_at']:
                    set_clauses.append(f"{key} = %({key})s")
                    params[key] = value
            
            if not set_clauses:
                raise ValueError("No valid fields to update")
            
            query = f"""
                UPDATE trips 
                SET {', '.join(set_clauses)}, updated_at = %(updated_at)s
                WHERE id = %(trip_id)s
                RETURNING *;
            """
            
            results = db.execute_query(query, params, fetch=True)
            
            if results and len(results) > 0:
                trip_dict = dict(results[0])
                # Convert dates to ISO format
                if trip_dict.get('start_date'):
                    trip_dict['start_date'] = trip_dict['start_date'].isoformat()
                if trip_dict.get('end_date'):
                    trip_dict['end_date'] = trip_dict['end_date'].isoformat()
                if trip_dict.get('created_at'):
                    trip_dict['created_at'] = trip_dict['created_at'].isoformat()
                if trip_dict.get('updated_at'):
                    trip_dict['updated_at'] = trip_dict['updated_at'].isoformat()
                
                self.logger.info(f"Trip {trip_id} updated successfully")
                return trip_dict
            else:
                raise Exception(f"Trip {trip_id} not found")
                
        except Exception as e:
            self.logger.error(f"Error updating trip {trip_id}: {e}")
            raise e

    def delete_trip(self, trip_id: int) -> bool:
        """
        Delete a trip
        
        Args:
            trip_id: Trip ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            query = """
                DELETE FROM trips 
                WHERE id = %(trip_id)s;
            """
            
            rows_affected = db.execute_query(query, {'trip_id': trip_id}, fetch=False)
            
            if rows_affected > 0:
                self.logger.info(f"Trip {trip_id} deleted successfully")
                return True
            else:
                self.logger.warning(f"Trip {trip_id} not found for deletion")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting trip {trip_id}: {e}")
            raise e

# Global instance
trip_service = TripService()
