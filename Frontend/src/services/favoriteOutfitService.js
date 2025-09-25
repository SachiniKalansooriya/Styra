import apiService from './apiService';

class FavoriteOutfitService {
  
  // Save an outfit as favorite
  async saveFavorite(userId, outfitData, outfitName) {
    try {
      const response = await apiService.post('/api/favorites', {
        // Remove userId - backend gets it from JWT token
        outfit_data: outfitData,
        name: outfitName
      });
      console.log('favoriteOutfitService.saveFavorite raw response:', response);

      if (response === null || response === undefined) {
        return { success: false, message: 'Empty response from server', id: null, raw: response };
      }

      if (typeof response === 'boolean' || typeof response === 'number') {
        return { success: !!response, message: !!response ? 'Saved' : 'Failed to save', id: null, raw: response };
      }

      if (response.status) {
        return {
          success: response.status === 'success',
          message: response.message || '',
          id: response.favorite_id || response.id || null,
          raw: response
        };
      }

      if (typeof response.success !== 'undefined') {
        return {
          success: !!response.success,
          message: response.message || '',
          id: response.id || response.favorite_id || null,
          raw: response
        };
      }

      return { success: false, message: 'Unexpected server response', id: null, raw: response };
    } catch (error) {
      console.error('Error saving favorite outfit:', error);
      throw error;
    }
  }

  // Get all favorite outfits for a user
  async getUserFavorites(userId) {
    try {
      console.log(`Getting favorites for user ${userId}`);
      // Remove userId from URL - backend gets it from JWT token
      const response = await apiService.get('/api/favorites');
      return response;
    } catch (error) {
      console.error('Error getting user favorites:', error);
      throw error;
    }
  }

  // Get a specific favorite outfit
  async getFavoriteById(userId, favoriteId) {
    try {
      // Remove userId from URL - backend gets it from JWT token
      const response = await apiService.get(`/api/favorites/${favoriteId}`);
      return response;
    } catch (error) {
      console.error('Error getting favorite by ID:', error);
      throw error;
    }
  }

  // Update a favorite outfit
  async updateFavorite(userId, favoriteId, updates) {
    try {
      // Remove userId from URL - backend gets it from JWT token
      const response = await apiService.put(`/api/favorites/${favoriteId}`, updates);
      return response;
    } catch (error) {
      console.error('Error updating favorite outfit:', error);
      throw error;
    }
  }

  // Delete a favorite outfit
  async deleteFavorite(userId, favoriteId) {
    try {
      const response = await apiService.delete(`/api/favorites/${favoriteId}`);
      return response;
    } catch (error) {
      console.error('Error deleting favorite outfit:', error);
      throw error;
    }
  }

  // Mark a favorite outfit as worn
  async wearFavorite(userId, favoriteId) {
    try {
      const response = await apiService.post(`/api/favorites/${favoriteId}/wear`);
      return response;
    } catch (error) {
      console.error('Error marking favorite as worn:', error);
      throw error;
    }
  }
}

export default new FavoriteOutfitService();