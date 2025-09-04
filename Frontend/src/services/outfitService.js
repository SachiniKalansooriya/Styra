import apiService from './apiService';

class OutfitService {
  // Get outfit recommendations
  async getOutfitRecommendations(preferences = {}) {
    try {
      return await apiService.post('/outfits/recommendations', preferences);
    } catch (error) {
      throw new Error(`Failed to get outfit recommendations: ${error.message}`);
    }
  }

  // Get outfit for specific occasion
  async getOutfitForOccasion(occasion, weatherData = {}) {
    try {
      return await apiService.post('/outfits/occasion', {
        occasion,
        weather: weatherData,
      });
    } catch (error) {
      throw new Error(`Failed to get outfit for occasion: ${error.message}`);
    }
  }

  // Save favorite outfit
  async saveFavoriteOutfit(outfitData) {
    try {
      return await apiService.post('/outfits/favorites', outfitData);
    } catch (error) {
      throw new Error(`Failed to save favorite outfit: ${error.message}`);
    }
  }

  // Get favorite outfits
  async getFavoriteOutfits() {
    try {
      return await apiService.get('/outfits/favorites');
    } catch (error) {
      throw new Error(`Failed to get favorite outfits: ${error.message}`);
    }
  }

  // Get outfit history
  async getOutfitHistory() {
    try {
      return await apiService.get('/outfits/history');
    } catch (error) {
      throw new Error(`Failed to get outfit history: ${error.message}`);
    }
  }
}

export default new OutfitService();
