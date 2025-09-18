// services/tripService.js
import apiService from './apiService';

class TripService {
  async saveTrip(tripData, packingResult) {
    try {
      console.log('Saving trip to database...');
      
      const tripToSave = {
        user_id: 1, // Default user for now
        destination: tripData.destination,
        start_date: tripData.startDate,
        end_date: tripData.endDate,
        activities: tripData.activities || [],
        weather_expected: tripData.weatherExpected,
        packing_style: tripData.packingStyle || 'minimal',
        packing_list: packingResult.categories || [],
        wardrobe_matches: packingResult.wardrobeMatches || {},
        coverage_analysis: packingResult.coverage || {},
        notes: ''
      };
      
      console.log('Trip data to save:', tripToSave);
      
      const response = await apiService.post('/api/trips', tripToSave);
      
      console.log('Trip saved successfully:', response);
      return response;
      
    } catch (error) {
      console.error('Error saving trip:', error);
      throw error;
    }
  }
  
  async getUserTrips(userId = 1) {
    try {
      console.log('Getting user trips...');
      
      const response = await apiService.get(`/api/trips?user_id=${userId}`);
      
      console.log('Retrieved trips response:', response);
      
      // Backend returns { status: "success", trips: [...], count: n }
      // We need to extract the trips array
      const trips = response.trips || [];
      console.log('Extracted trips array:', trips);
      
      return trips;
      
    } catch (error) {
      console.error('Error getting trips:', error);
      throw error;
    }
  }
  
  async getTripById(tripId) {
    try {
      const response = await apiService.get(`/api/trips/${tripId}`);
      return response;
    } catch (error) {
      console.error('Error getting trip by ID:', error);
      throw error;
    }
  }
  
  async updateTrip(tripId, updates) {
    try {
      const response = await apiService.put(`/api/trips/${tripId}`, updates);
      return response;
    } catch (error) {
      console.error('Error updating trip:', error);
      throw error;
    }
  }
  
  async deleteTrip(tripId) {
    try {
      const response = await apiService.delete(`/api/trips/${tripId}`);
      return response;
    } catch (error) {
      console.error('Error deleting trip:', error);
      throw error;
    }
  }
}

export default new TripService();
