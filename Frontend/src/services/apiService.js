import API_CONFIG from '../config/api';

class ApiService {
  constructor() {
    // Try multiple URLs for better connectivity
    this.urls = [
      API_CONFIG.primary,
      API_CONFIG.fallback,
      API_CONFIG.localhost,
    ].filter(Boolean); // Remove undefined URLs
    
    this.timeout = API_CONFIG.TIMEOUT;
    this.headers = API_CONFIG.HEADERS;
  }

  // Generic request method with multiple URL fallback
  async request(endpoint, options = {}) {
    let lastError;

    for (const baseUrl of this.urls) {
      try {
        const url = `${baseUrl}${endpoint}`;
        const config = {
          headers: {
            ...this.headers,
            ...options.headers,
          },
          ...options,
        };

        console.log(`Trying API request to: ${url}`);
        
        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
          controller.abort();
        }, this.timeout);
        
        const response = await fetch(url, {
          ...config,
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`✅ API success with ${baseUrl}:`, data);
        return data;
      } catch (error) {
        console.log(`❌ Failed ${baseUrl}:`, error.message);
        lastError = error;
        continue; // Try next URL
      }
    }
    
    // If all URLs failed, throw the last error
    console.error('🚫 All API endpoints failed');
    throw new Error(`All backend connections failed. Last error: ${lastError?.message || 'Unknown'}`);
  }

  // GET request
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
    });
  }

  // POST request
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // PUT request
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck() {
    return this.get('/health');
  }

  // Test connection
  async testConnection() {
    try {
      const response = await this.get('/');
      return {
        success: true,
        message: 'Backend connection successful',
        data: response,
      };
    } catch (error) {
      return {
        success: false,
        message: 'Backend connection failed',
        error: error.message,
      };
    }
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService;
