import apiService from './apiService';

class ConnectionService {
  constructor() {
    this.isOnline = false;
    this.lastConnectionCheck = null;
  }

  async testBackendConnection() {
    try {
      console.log('Testing backend connection...');
      const result = await apiService.testConnection();
      this.isOnline = true;
      this.lastConnectionCheck = new Date();
      return result;
    } catch (error) {
      this.isOnline = false;
      console.log('Backend offline, switching to offline mode');
      return {
        success: false,
        message: 'Backend not available - using offline mode',
        error: error.message,
        offline: true,
      };
    }
  }

  async testAllServices() {
    const results = {
      backend: await this.testBackendConnection(),
      health: null,
    };

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

  async initializeApp() {
    console.log('Initializing app connections...');
    const connectionTest = await this.testAllServices();
    
    if (!connectionTest.backend.success) {
      console.log('Running in offline mode - some features will use mock data');
    } else {
      console.log('Backend connected - full functionality available!');
    }

    return connectionTest;
  }

  async isBackendAvailable() {
    if (this.lastConnectionCheck && 
        Date.now() - this.lastConnectionCheck.getTime() < 30000) {
      return this.isOnline;
    }
    
    const result = await this.testBackendConnection();
    return result.success;
  }
}

export default new ConnectionService();