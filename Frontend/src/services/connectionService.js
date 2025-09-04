import apiService from './apiService';

class ConnectionService {
  constructor() {
    this.isOnline = false;
    this.lastConnectionCheck = null;
  }

  // Test backend connection with better error handling
  async testBackendConnection() {
    try {
      console.log('🔍 Testing backend connection...');
      const result = await apiService.testConnection();
      this.isOnline = true;
      this.lastConnectionCheck = new Date();
      return result;
    } catch (error) {
      this.isOnline = false;
      console.log('🔌 Backend offline, switching to offline mode');
      return {
        success: false,
        message: 'Backend not available - using offline mode',
        error: error.message,
        offline: true,
      };
    }
  }

  // Test all services with graceful degradation
  async testAllServices() {
    const results = {
      backend: await this.testBackendConnection(),
      health: null,
    };

    // Only test health if backend is reachable
    if (results.backend.success) {
      try {
        const healthData = await apiService.healthCheck();
        results.health = {
          success: true,
          data: healthData,
        };
      } catch (error) {
        results.health = {
          success: false,
          error: error.message,
        };
      }
    }

    return results;
  }

  // Initialize app with graceful offline handling
  async initializeApp() {
    console.log('🚀 Initializing app connections...');
    const connectionTest = await this.testAllServices();
    
    if (!connectionTest.backend.success) {
      console.log('📱 Running in offline mode - some features will use mock data');
      // App can still function with local storage and mock data
    } else {
      console.log('🌐 Backend connected - full functionality available!');
    }

    return connectionTest;
  }

  // Check if backend is available
  async isBackendAvailable() {
    // Use cached result if recent
    if (this.lastConnectionCheck && 
        Date.now() - this.lastConnectionCheck.getTime() < 30000) { // 30 seconds
      return this.isOnline;
    }
    
    const result = await this.testBackendConnection();
    return result.success;
  }

  // Get mock data when offline
  getMockData(type) {
    const mockData = {
      wardrobeItems: [
        {
          id: 1,
          name: "Blue Denim Jeans",
          category: "Bottoms",
          color: "Blue",
          season: "All",
          lastWorn: null,
          timesWorn: 5
        },
        {
          id: 2,
          name: "White Cotton T-Shirt",
          category: "Tops",
          color: "White",
          season: "Summer",
          lastWorn: "2025-09-01",
          timesWorn: 8
        }
      ],
      outfits: [
        {
          id: 1,
          name: "Casual Day Out",
          items: ["White T-Shirt", "Blue Jeans", "Sneakers"],
          confidence: 92,
          reason: "Perfect for comfortable daily activities"
        }
      ],
      weather: {
        temperature: 28,
        condition: "sunny",
        description: "Sunny",
        location: "Your Location"
      }
    };

    return mockData[type] || [];
  }
}

export default new ConnectionService();
