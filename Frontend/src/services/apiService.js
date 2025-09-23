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
      timeout: this.timeout,
      ...options,
    };

    console.log('=== API REQUEST DEBUG ===');
    console.log('URL:', url);
    console.log('Method:', config.method || 'GET');
    console.log('Has Auth:', !!authHeaders.Authorization);
    console.log('========================');

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);
      
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (!response.ok) {
        if (response.status === 401 && !endpoint.includes('/auth/login')) {
          console.log('Unauthorized response - clearing auth');
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
        
        if (response.status === 500) {
          console.error('Server error 500 for endpoint:', endpoint);
          try {
            const errorData = await response.json();
            console.error('Server error details:', errorData);
            throw new Error(`Server error: ${errorData.detail || 'Internal server error'}`);
          } catch (e) {
            throw new Error('Server error occurred');
          }
        }
        
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response data received successfully');
      return data;
      
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      
      // Handle different types of errors
      if (error.name === 'AbortError') {
        throw new Error('Request timeout - please check your connection');
      }
      if (error.message.includes('Network request failed')) {
        throw new Error('Network error - check your internet connection');
      }
      if (error.message.includes('fetch')) {
        throw new Error('Connection error - make sure the backend is running');
      }
      
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

  async delete(endpoint, options = {}) {
  return this.request(endpoint, {
    method: 'DELETE',
    ...options,
  });
}

  async postFormData(endpoint, formData, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
        // Don't set Content-Type for FormData
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
      const response = await this.get('/health');
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async healthCheck() {
    return this.get('/health');
  }

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