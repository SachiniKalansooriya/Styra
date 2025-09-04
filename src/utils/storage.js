// src/utils/storage.js
import AsyncStorage from '@react-native-async-storage/async-storage';

const WARDROBE_KEY = 'wardrobe_items';

export const storage = {
  // Save wardrobe items
  saveWardrobeItems: async (items) => {
    try {
      await AsyncStorage.setItem(WARDROBE_KEY, JSON.stringify(items));
      return true;
    } catch (error) {
      console.error('Error saving wardrobe items:', error);
      return false;
    }
  },

  // Get wardrobe items
  getWardrobeItems: async () => {
    try {
      const items = await AsyncStorage.getItem(WARDROBE_KEY);
      return items ? JSON.parse(items) : [];
    } catch (error) {
      console.error('Error getting wardrobe items:', error);
      return [];
    }
  },

  // Add a new item to wardrobe
  addWardrobeItem: async (item) => {
    try {
      const existingItems = await storage.getWardrobeItems();
      const newItem = {
        ...item,
        id: Date.now().toString(), // Simple ID generation
        addedDate: new Date().toISOString(),
        timesWorn: 0,
        lastWorn: null,
      };
      const updatedItems = [...existingItems, newItem];
      await storage.saveWardrobeItems(updatedItems);
      return newItem;
    } catch (error) {
      console.error('Error adding wardrobe item:', error);
      return null;
    }
  },

  // Update an item in wardrobe
  updateWardrobeItem: async (itemId, updates) => {
    try {
      const items = await storage.getWardrobeItems();
      const updatedItems = items.map(item => 
        item.id === itemId ? { ...item, ...updates } : item
      );
      await storage.saveWardrobeItems(updatedItems);
      return true;
    } catch (error) {
      console.error('Error updating wardrobe item:', error);
      return false;
    }
  },

  // Delete an item from wardrobe
  deleteWardrobeItem: async (itemId) => {
    try {
      const items = await storage.getWardrobeItems();
      const filteredItems = items.filter(item => item.id !== itemId);
      await storage.saveWardrobeItems(filteredItems);
      return true;
    } catch (error) {
      console.error('Error deleting wardrobe item:', error);
      return false;
    }
  },

  // Mark item as worn
  markItemAsWorn: async (itemId) => {
    try {
      const items = await storage.getWardrobeItems();
      const updatedItems = items.map(item => {
        if (item.id === itemId) {
          return {
            ...item,
            timesWorn: (item.timesWorn || 0) + 1,
            lastWorn: new Date().toISOString().split('T')[0], // YYYY-MM-DD format
          };
        }
        return item;
      });
      await storage.saveWardrobeItems(updatedItems);
      return true;
    } catch (error) {
      console.error('Error marking item as worn:', error);
      return false;
    }
  },
};
