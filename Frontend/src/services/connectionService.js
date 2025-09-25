
const BASE_URL = 'http://172.20.10.7:8000';

class ConnectionService {
  async initializeApp() {
    try {
      console.log('Testing backend connection...');
      
      const backendTest = await this.isBackendAvailable();
      
      return {
        backend: {
          success: backendTest,
          url: BASE_URL
        }
      };
    } catch (error) {
      console.error('Connection initialization failed:', error);
      return {
        backend: {
          success: false,
          url: BASE_URL,
          error: error.message
        }
      };
    }
  }

  async isBackendAvailable() {
    try {
      const response = await fetch(`${BASE_URL}/health`, {
        method: 'GET',
        timeout: 5000,
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.status === 'healthy';
      }
      return false;
    } catch (error) {
      console.log('Backend connection failed:', error);
      return false;
    }
  }

  async testConnection() {
    try {
      const response = await fetch(`${BASE_URL}/`, {
        method: 'GET',
        timeout: 5000,
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Backend response:', data);
        return true;
      }
      return false;
    } catch (error) {
      console.log('Backend test failed:', error);
      return false;
    }
  }
}

export default new ConnectionService();