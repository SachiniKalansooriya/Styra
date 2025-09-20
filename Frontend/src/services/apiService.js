// src/services/apiService.js
import API_CONFIG from '../config/api';

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.primary;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    // Get auth token for protected endpoints
    let authHeaders = {};
    try {
      // Dynamically import to avoid circular dependency
      const authService = require('./authService').default;
      const token = authService.getToken();
      if (token && !endpoint.includes('/auth/')) {
        authHeaders.Authorization = `Bearer ${token}`;
      }
    } catch (e) {
      console.log('Could not get auth token:', e);
    }
    
    const config = {
      headers: {
        ...API_CONFIG.HEADERS,
        ...authHeaders,
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
        // Don't clear auth for login endpoint 401s - those are expected for wrong credentials
        if (response.status === 401 && !endpoint.includes('/auth/login')) {
          console.log('Unauthorized response - clearing auth');
          // Only import authService when needed to avoid circular dependencies
          try {
            const authService = require('./authService').default;
            if (authService && authService.signOut) {
              await authService.signOut();
            }
          } catch (e) {
            console.log('Could not clear auth:', e);
          }
          throw new Error('Authentication expired. Please log in again.');
        }
        
        // Log more details for 500 errors
        if (response.status === 500) {
          console.error('Server error 500 for endpoint:', endpoint);
          try {
            const errorData = await response.json();
            console.error('Server error details:', errorData);
          } catch (e) {
            console.error('Could not parse server error response');
          }
        }
        
        // For other errors, let the calling code handle the response
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