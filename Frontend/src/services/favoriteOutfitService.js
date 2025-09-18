// src/services/favoriteOutfitService.js
import apiService from './apiService';

class FavoriteOutfitService {
  
  // Save an outfit as favorite
  async saveFavorite(userId, outfitData, outfitName) {
    try {
      const response = await apiService.post('/api/outfit/favorites/save', {
        user_id: userId,
        outfit_data: outfitData,
        outfit_name: outfitName
      });
      return response;
    } catch (error) {
      console.error('Error saving favorite outfit:', error);
      throw error;
    }
  }

  // Get all favorite outfits for a user
  async getUserFavorites(userId) {
    try {
      console.log(`Getting favorites for user ${userId}`);
      const response = await apiService.get(`/api/outfit/favorites/${userId}`);
      return response;
    } catch (error) {
      console.error('Error getting user favorites:', error);
      throw error;
    }
  }

  // Get a specific favorite outfit
  async getFavoriteById(userId, favoriteId) {
    try {
      const response = await apiService.get(`/api/outfit/favorites/${userId}/${favoriteId}`);
      return response;
    } catch (error) {
      console.error('Error getting favorite by ID:', error);
      throw error;
    }
  }

  // Update a favorite outfit
  async updateFavorite(userId, favoriteId, updates) {
    try {
      const response = await apiService.put(`/api/outfit/favorites/${userId}/${favoriteId}`, updates);
      return response;
    } catch (error) {
      console.error('Error updating favorite outfit:', error);
      throw error;
    }
  }

  // Delete a favorite outfit
  async deleteFavorite(userId, favoriteId) {
    try {
      const response = await apiService.delete(`/api/outfit/favorites/${userId}/${favoriteId}`);
      return response;
    } catch (error) {
      console.error('Error deleting favorite outfit:', error);
      throw error;
    }
  }

  // Mark a favorite outfit as worn
  async wearFavorite(userId, favoriteId) {
    try {
      const response = await apiService.post(`/api/outfit/favorites/${userId}/${favoriteId}/wear`);
      return response;
    } catch (error) {
      console.error('Error marking favorite as worn:', error);
      throw error;
    }
  }

}

export default new FavoriteOutfitService();
