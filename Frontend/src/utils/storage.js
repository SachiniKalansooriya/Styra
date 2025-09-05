import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import apiService from '../services/apiService';
const WARDROBE_KEY = 'wardrobe_items';
const IMAGES_DIRECTORY = FileSystem.documentDirectory + 'styra_images/';

const ensureImageDirectoryExists = async () => {
  const dirInfo = await FileSystem.getInfoAsync(IMAGES_DIRECTORY);
  if (!dirInfo.exists) {
    await FileSystem.makeDirectoryAsync(IMAGES_DIRECTORY, { intermediates: true });
  }
};

const processAndSaveImage = async (imageUri) => {
  try {
    await ensureImageDirectoryExists();
    
    const timestamp = Date.now();
    const filename = `item_${timestamp}.jpg`;
    const localUri = IMAGES_DIRECTORY + filename;
    
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

const extractColorInfo = async (imageUri) => {
  const colors = ['Red', 'Blue', 'Green', 'Black', 'White', 'Gray', 'Brown', 'Pink', 'Purple', 'Yellow', 'Orange'];
  return colors[Math.floor(Math.random() * colors.length)];
};

const suggestCategory = async (imageUri) => {
  const categories = ['tops', 'bottoms', 'dresses', 'shoes', 'accessories', 'outerwear'];
  return categories[Math.floor(Math.random() * categories.length)];
};

export const cameraBackend = {
  processNewClothingItem: async (imageUri, captureMetadata = {}) => {
    try {
      const imageData = await processAndSaveImage(imageUri);
      
      // Try to get AI analysis from backend
      let suggestedColor = 'Unknown';
      let suggestedCategory = 'tops';
      let suggestedOccasion = 'casual';  // Initialize with default value
      let analysisSource = 'fallback';
      
      try {
        console.log('Requesting AI analysis from backend...');
        const analysisResult = await apiService.analyzeClothingImage(imageUri);
        
        if (analysisResult.status === 'success') {
          suggestedColor = analysisResult.analysis.suggestedColor || suggestedColor;
          suggestedCategory = analysisResult.analysis.suggestedCategory || suggestedCategory;
          suggestedOccasion = analysisResult.analysis.suggestedOccasion || 'casual';
          analysisSource = 'backend_ai';
          console.log('Backend AI analysis successful:', analysisResult.analysis);
        }
      } catch (error) {
        console.log('Backend analysis failed, using fallback:', error.message);
        // Fallback to simple local analysis
        suggestedColor = await extractColorInfo(imageUri);
        suggestedCategory = await suggestCategory(imageUri);
        suggestedOccasion = 'casual'; // Set default occasion for fallback
        analysisSource = 'local_fallback';
      }
      
      const itemMetadata = {
        id: Date.now().toString(),
        imageData,
        suggestedColor,
        suggestedCategory,
        suggestedOccasion,
        captureDate: new Date().toISOString(),
        captureMetadata,
        analysisSource,
        processed: true,
      };
      
      return itemMetadata;
    } catch (error) {
      console.error('Error processing clothing item:', error);
      throw error;
    }
  },
};

export const storage = {
  saveWardrobeItems: async (items) => {
    try {
      await AsyncStorage.setItem(WARDROBE_KEY, JSON.stringify(items));
      return true;
    } catch (error) {
      console.error('Error saving wardrobe items:', error);
      return false;
    }
  },

  getWardrobeItems: async () => {
    try {
      const items = await AsyncStorage.getItem(WARDROBE_KEY);
      return items ? JSON.parse(items) : [];
    } catch (error) {
      console.error('Error getting wardrobe items:', error);
      return [];
    }
  },

  addWardrobeItem: async (item) => {
    try {
      const existingItems = await storage.getWardrobeItems();
      const newItem = {
        ...item,
        id: item.id || Date.now().toString(),
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
};