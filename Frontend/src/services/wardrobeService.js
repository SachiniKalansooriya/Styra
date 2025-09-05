import apiService from './apiService';
import { storage } from '../utils/storage';
import connectionService from './connectionService';

class WardrobeService {
  async addWardrobeItem(itemData) {
    try {
      const isOnline = await connectionService.isBackendAvailable();
      
      if (isOnline) {
        try {
          const response = await apiService.post('/api/wardrobe/items', itemData);
          // Don't save locally when backend is available to prevent duplicates
          
          return {
            success: true,
            data: response.item || response, // Handle both response formats
            source: 'backend',
            message: 'Item saved to backend'
          };
        } catch (backendError) {
          console.log('Backend save failed, using local storage:', backendError.message);
          const localItem = await storage.addWardrobeItem(itemData);
          
          return {
            success: true,
            data: localItem,
            source: 'local',
            message: 'Item saved locally - will sync when backend available',
            pendingSync: true
          };
        }
      } else {
        const localItem = await storage.addWardrobeItem(itemData);
        
        return {
          success: true,
          data: localItem,
          source: 'local',
          message: 'Item saved locally - offline mode',
          pendingSync: true
        };
      }
    } catch (error) {
      throw new Error(`Failed to save wardrobe item: ${error.message}`);
    }
  }

  async getWardrobeItems(filters = {}) {
    try {
      const isOnline = await connectionService.isBackendAvailable();
      
      if (isOnline) {
        try {
          const response = await apiService.get('/api/wardrobe/items', filters);
          // Extract the items array from the backend response
          return response.items || [];
        } catch (error) {
          console.log('Backend fetch failed, using local storage');
          return await storage.getWardrobeItems();
        }
      } else {
        return await storage.getWardrobeItems();
      }
    } catch (error) {
      console.error('Error fetching wardrobe items:', error);
      return [];
    }
  }
}

export default new WardrobeService();