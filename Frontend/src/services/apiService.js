// apiService.js
import API_CONFIG from '../config/api';

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.primary;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        ...API_CONFIG.HEADERS,
        ...options.headers,
      },
      ...options,
    };

    console.log('=== API REQUEST DEBUG ===');
    console.log('URL:', url);
    console.log('Config:', config);
    console.log('Base URL:', this.baseURL);
    console.log('========================');

    try {
      const response = await fetch(url, config);
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        url: url
      });
      throw error;
    }
  }

  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      ...options,
    });
  }

  async postFormData(endpoint, formData, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData, let browser set it
        'Accept': 'application/json',
        ...options.headers,
      },
      ...options,
    });
  }

  async get(endpoint, params = {}) {
    const queryString = Object.keys(params).length > 0 
      ? '?' + new URLSearchParams(params).toString() 
      : '';
    
    return this.request(`${endpoint}${queryString}`, {
      method: 'GET',
    });
  }

  async testConnection() {
    try {
      const response = await this.get('/');
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async healthCheck() {
    return this.get('/health');
  }

  // New method for image analysis
  async analyzeClothingImage(imageUri) {
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'clothing_item.jpg',
      });

      return await this.postFormData('/api/analyze-clothing', formData);
    } catch (error) {
      console.error('Image analysis failed:', error);
      throw error;
    }
  }
}

export default new ApiService();