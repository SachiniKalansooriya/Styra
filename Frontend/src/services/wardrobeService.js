// services/wardrobeService.js
import apiService from './apiService';
import { storage } from '../utils/storage';
import connectionService from './connectionService';

class WardrobeService {
  async getWardrobeItems(filters = {}) {
    try {
      const isOnline = await connectionService.isBackendAvailable();
      
      if (isOnline) {
        try {
          const response = await apiService.get('/api/wardrobe/items', filters);
          
          console.log('Backend response:', response);
          
          return response.items || [];
          
        } catch (error) {
          console.log('Backend fetch failed, using local storage:', error.message);
          
       
          if (error.message.includes('Authentication expired')) {
            throw error;
          }
          
          return await storage.getWardrobeItems();
        }
      } else {
        return await storage.getWardrobeItems();
      }
    } catch (error) {
      console.error('Error fetching wardrobe items:', error);
      if (error.message.includes('Authentication expired')) {
        throw error;
      }
      
      return [];
    }
  }

  async addWardrobeItem(itemData) {
    try {
      const isOnline = await connectionService.isBackendAvailable();
      
      if (isOnline) {
        try {
          // Your apiService handles auth automatically
          const response = await apiService.post('/api/wardrobe/items', itemData);
          
          return {
            success: true,
            data: response.item || response,
            source: 'backend',
            message: 'Item saved to backend'
          };
        } catch (backendError) {
          console.log('Backend save failed, using local storage:', backendError.message);
          
          // If auth expired, throw the error
          if (backendError.message.includes('Authentication expired')) {
            throw backendError;
          }
          
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

  async deleteWardrobeItem(itemId) {
    try {
      const isOnline = await connectionService.isBackendAvailable();
      
      if (isOnline) {
        try {
          // Add delete method to your apiService
          await apiService.delete(`/api/wardrobe/items/${itemId}`);
          return { success: true, source: 'backend' };
        } catch (error) {
          console.log('Backend delete failed, using local storage');
          
          if (error.message.includes('Authentication expired')) {
            throw error;
          }
        }
      }
      
      // Fallback to local storage
      await storage.deleteWardrobeItem(itemId);
      return { success: true, source: 'local' };
      
    } catch (error) {
      throw new Error(`Failed to delete item: ${error.message}`);
    }
  }
}

export default new WardrobeService();