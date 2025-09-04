import apiService from './apiService';

class WardrobeService {
  // Get all wardrobe items
  async getWardrobeItems(filters = {}) {
    try {
      return await apiService.get('/wardrobe/items', filters);
    } catch (error) {
      throw new Error(`Failed to fetch wardrobe items: ${error.message}`);
    }
  }

  // Add new wardrobe item
  async addWardrobeItem(itemData) {
    try {
      return await apiService.post('/wardrobe/items', itemData);
    } catch (error) {
      throw new Error(`Failed to add wardrobe item: ${error.message}`);
    }
  }

  // Update wardrobe item
  async updateWardrobeItem(itemId, updateData) {
    try {
      return await apiService.put(`/wardrobe/items/${itemId}`, updateData);
    } catch (error) {
      throw new Error(`Failed to update wardrobe item: ${error.message}`);
    }
  }

  // Delete wardrobe item
  async deleteWardrobeItem(itemId) {
    try {
      return await apiService.delete(`/wardrobe/items/${itemId}`);
    } catch (error) {
      throw new Error(`Failed to delete wardrobe item: ${error.message}`);
    }
  }

  // Upload image for wardrobe item
  async uploadItemImage(imageData) {
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: imageData.uri,
        type: 'image/jpeg',
        name: 'wardrobe_item.jpg',
      });

      return await apiService.request('/wardrobe/upload-image', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    } catch (error) {
      throw new Error(`Failed to upload image: ${error.message}`);
    }
  }

  // Get wardrobe statistics
  async getWardrobeStats() {
    try {
      return await apiService.get('/wardrobe/stats');
    } catch (error) {
      throw new Error(`Failed to fetch wardrobe stats: ${error.message}`);
    }
  }

  // Search wardrobe items
  async searchWardrobeItems(query) {
    try {
      return await apiService.get('/wardrobe/search', { q: query });
    } catch (error) {
      throw new Error(`Failed to search wardrobe items: ${error.message}`);
    }
  }
}

export default new WardrobeService();
