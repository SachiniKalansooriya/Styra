import apiService from './apiService';

class OutfitHistoryService {
async recordWornOutfit(outfitData, occasion = null, weather = null, location = null, wornDate = null) {
  try {
    const requestData = {
      outfit_data: outfitData,
      occasion,
      weather,
      location,
      worn_date: wornDate
    };

    console.log('Recording worn outfit:', requestData);
    const response = await apiService.post('/api/outfit/wear', requestData);
    
    if (response.status === 'success') {
      console.log('Outfit recorded successfully:', response);
      return response;
    } else {
      throw new Error(response.message || 'Failed to record outfit');
    }
  } catch (error) {
    console.error('Error recording worn outfit:', error);
    throw error;
  }
}

  async getOutfitHistory(limit = 50, startDate = null, endDate = null) {
  try {
    const params = new URLSearchParams({
      limit: limit.toString()
      // Remove the hardcoded user_id: '1' line
    });

    if (startDate) {
      params.append('start_date', startDate);
    }
    if (endDate) {
      params.append('end_date', endDate);
    }

    console.log('Getting outfit history with params:', params.toString());

    const response = await apiService.get(`/api/outfit/history?${params.toString()}`);
    console.log('Raw outfit history response:', response);

    if (response && (response.status === 'success' || response.history)) {
      // If status present and success, return as-is; otherwise wrap history into expected shape
      if (response.status === 'success') {
        console.log('Outfit history retrieved:', response);
        return response;
      }

      // No explicit status but history exists
      console.log('Outfit history retrieved (no status):', response.history);
      return { status: 'success', history: response.history };
    } else {
      throw new Error(response.message || 'Failed to get outfit history');
    }
  } catch (error) {
    console.error('Error getting outfit history:', error);
    throw error;
  }
}


  async getOutfitByDate(wornDate) {
  try {
    console.log('Getting outfit for date:', wornDate);
    // Remove ?user_id=1 from the URL
    const response = await apiService.get(`/api/outfit/history/${wornDate}`);
    
    console.log('Outfit by date response:', response);
    return response;
  } catch (error) {
    console.error('Error getting outfit by date:', error);
    throw error;
  }
}

  async rateOutfit(outfitId, rating, notes = null) {
    try {
      const requestData = {
        outfit_id: outfitId,
        rating,
        notes
      };

      console.log('Rating outfit:', requestData);

      const response = await apiService.post('/api/outfit/rate', requestData);
      
      if (response.status === 'success') {
        console.log('Outfit rated successfully:', response);
        return response;
      } else {
        throw new Error(response.message || 'Failed to rate outfit');
      }
    } catch (error) {
      console.error('Error rating outfit:', error);
      throw error;
    }
  }

  // Helper function to format outfit data for storage
  formatOutfitForStorage(outfitItems, occasion = null, confidence = null) {
    return {
      items: outfitItems.map(item => ({
        id: item.id,
        name: item.name || item.item,
        category: item.category,
        color: item.color,
        image_url: item.image_url,
        confidence: item.confidence
      })),
      occasion,
      confidence,
      generated_at: new Date().toISOString(),
      total_items: outfitItems.length
    };
  }

  // Helper function to get today's date in YYYY-MM-DD format
  getTodayDate() {
    return new Date().toISOString().split('T')[0];
  }

  // Helper function to get date range for the last week
  getLastWeekRange() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);
    
    return {
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0]
    };
  }

  // Helper function to get date range for the last month
  getLastMonthRange() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 1);
    
    return {
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0]
    };
  }
}

export default new OutfitHistoryService();
