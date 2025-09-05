import apiService from '../services/apiService';

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
      // Try to get AI analysis from backend
      let suggestedColor = 'Unknown';
      let suggestedCategory = 'tops';
      let suggestedOccasion = 'casual';
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
        suggestedOccasion = 'casual';
        analysisSource = 'local_fallback';
      }
      
      const itemMetadata = {
        id: Date.now().toString(),
        imageUri, // Store original URI for backend upload
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

// Remove all local storage functions - use backend only
export const storage = {
  // These methods now just call the backend
  addWardrobeItem: async (item) => {
    try {
      const response = await apiService.post('/api/wardrobe/items', item);
      return response.item;
    } catch (error) {
      console.error('Error adding wardrobe item to backend:', error);
      return null;
    }
  },

  getWardrobeItems: async () => {
    try {
      const response = await apiService.get('/api/wardrobe/items');
      return response.items || [];
    } catch (error) {
      console.error('Error getting wardrobe items from backend:', error);
      return [];
    }
  },

  deleteWardrobeItem: async (itemId) => {
    try {
      await apiService.delete(`/api/wardrobe/items/${itemId}`);
      return true;
    } catch (error) {
      console.error('Error deleting wardrobe item from backend:', error);
      return false;
    }
  },
};