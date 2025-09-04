// src/utils/storage.js
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';

const WARDROBE_KEY = 'wardrobe_items';
const IMAGES_DIRECTORY = FileSystem.documentDirectory + 'styra_images/';

// Ensure images directory exists
const ensureImageDirectoryExists = async () => {
  const dirInfo = await FileSystem.getInfoAsync(IMAGES_DIRECTORY);
  if (!dirInfo.exists) {
    await FileSystem.makeDirectoryAsync(IMAGES_DIRECTORY, { intermediates: true });
  }
};

// Process and save image locally
const processAndSaveImage = async (imageUri) => {
  try {
    await ensureImageDirectoryExists();
    
    // Generate unique filename
    const timestamp = Date.now();
    const filename = `item_${timestamp}.jpg`;
    const localUri = IMAGES_DIRECTORY + filename;
    
    // Copy image to local directory (without manipulation for now)
    await FileSystem.copyAsync({
      from: imageUri,
      to: localUri,
    });
    
    return {
      localUri,
      filename,
      size: (await FileSystem.getInfoAsync(localUri)).size,
    };
  } catch (error) {
    console.error('Error processing image:', error);
    throw new Error('Failed to process image');
  }
};

// Delete image file
const deleteImageFile = async (filename) => {
  try {
    const localUri = IMAGES_DIRECTORY + filename;
    const fileInfo = await FileSystem.getInfoAsync(localUri);
    if (fileInfo.exists) {
      await FileSystem.deleteAsync(localUri);
    }
  } catch (error) {
    console.error('Error deleting image file:', error);
  }
};

// Extract color information from image (simplified)
const extractColorInfo = async (imageUri) => {
  // This is a simplified color extraction
  // In a real app, you might use ML services or color analysis libraries
  const colors = ['Red', 'Blue', 'Green', 'Black', 'White', 'Gray', 'Brown', 'Pink', 'Purple', 'Yellow', 'Orange'];
  return colors[Math.floor(Math.random() * colors.length)];
};

// AI-powered category suggestion (mock implementation)
const suggestCategory = async (imageUri) => {
  // This would typically call an ML service or AI API
  // For now, return a mock suggestion
  const categories = ['Tops', 'Bottoms', 'Dresses', 'Shoes', 'Accessories', 'Outerwear'];
  return categories[Math.floor(Math.random() * categories.length)];
};

export const cameraBackend = {
  // Process captured image and extract metadata
  processNewClothingItem: async (imageUri, captureMetadata = {}) => {
    try {
      // Process and save image
      const imageData = await processAndSaveImage(imageUri);
      
      // Extract color information
      const suggestedColor = await extractColorInfo(imageUri);
      
      // Suggest category using AI (mock)
      const suggestedCategory = await suggestCategory(imageUri);
      
      // Create item metadata
      const itemMetadata = {
        id: Date.now().toString(),
        imageData,
        suggestedColor,
        suggestedCategory,
        captureDate: new Date().toISOString(),
        captureMetadata,
        processed: true,
      };
      
      return itemMetadata;
    } catch (error) {
      console.error('Error processing clothing item:', error);
      throw error;
    }
  },
  
  // Save processed item to wardrobe
  saveClothingItem: async (itemData) => {
    try {
      const existingItems = await storage.getWardrobeItems();
      
      const newItem = {
        ...itemData,
        id: itemData.id || Date.now().toString(),
        addedDate: new Date().toISOString(),
        timesWorn: 0,
        lastWorn: null,
        isFavorite: false,
        tags: [],
        notes: '',
      };
      
      const updatedItems = [...existingItems, newItem];
      await storage.saveWardrobeItems(updatedItems);
      
      return newItem;
    } catch (error) {
      console.error('Error saving clothing item:', error);
      throw error;
    }
  },
  
  // Delete clothing item and its image
  deleteClothingItem: async (itemId) => {
    try {
      const items = await storage.getWardrobeItems();
      const itemToDelete = items.find(item => item.id === itemId);
      
      if (itemToDelete && itemToDelete.imageData && itemToDelete.imageData.filename) {
        await deleteImageFile(itemToDelete.imageData.filename);
      }
      
      const updatedItems = items.filter(item => item.id !== itemId);
      await storage.saveWardrobeItems(updatedItems);
      
      return true;
    } catch (error) {
      console.error('Error deleting clothing item:', error);
      throw error;
    }
  },
  
  // Get image URI for display
  getImageUri: (filename) => {
    return IMAGES_DIRECTORY + filename;
  },
  
  // Batch import images
  batchProcessImages: async (imageUris) => {
    try {
      const processedItems = [];
      
      for (const imageUri of imageUris) {
        const processed = await cameraBackend.processNewClothingItem(imageUri);
        processedItems.push(processed);
      }
      
      return processedItems;
    } catch (error) {
      console.error('Error in batch processing:', error);
      throw error;
    }
  },
  
  // Get storage statistics
  getStorageStats: async () => {
    try {
      const items = await storage.getWardrobeItems();
      const dirInfo = await FileSystem.getInfoAsync(IMAGES_DIRECTORY);
      
      let totalImageSize = 0;
      if (dirInfo.exists) {
        const files = await FileSystem.readDirectoryAsync(IMAGES_DIRECTORY);
        for (const file of files) {
          const fileInfo = await FileSystem.getInfoAsync(IMAGES_DIRECTORY + file);
          totalImageSize += fileInfo.size || 0;
        }
      }
      
      return {
        totalItems: items.length,
        totalImageSize: Math.round(totalImageSize / 1024 / 1024 * 100) / 100, // MB
        storageLocation: IMAGES_DIRECTORY,
      };
    } catch (error) {
      console.error('Error getting storage stats:', error);
      return { totalItems: 0, totalImageSize: 0, storageLocation: IMAGES_DIRECTORY };
    }
  },
  
  // Clean up orphaned images
  cleanupOrphanedImages: async () => {
    try {
      const items = await storage.getWardrobeItems();
      const usedFilenames = items
        .filter(item => item.imageData && item.imageData.filename)
        .map(item => item.imageData.filename);
      
      const dirInfo = await FileSystem.getInfoAsync(IMAGES_DIRECTORY);
      if (!dirInfo.exists) return;
      
      const allFiles = await FileSystem.readDirectoryAsync(IMAGES_DIRECTORY);
      const orphanedFiles = allFiles.filter(filename => !usedFilenames.includes(filename));
      
      for (const filename of orphanedFiles) {
        await deleteImageFile(filename);
      }
      
      return orphanedFiles.length;
    } catch (error) {
      console.error('Error cleaning up orphaned images:', error);
      return 0;
    }
  },
};

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
