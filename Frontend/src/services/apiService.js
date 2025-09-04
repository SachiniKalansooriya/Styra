import API_CONFIG from '../config/api';

class ApiService {
  constructor() {
    this.urls = [
      API_CONFIG.primary,
      API_CONFIG.fallback,
      API_CONFIG.localhost,
    ].filter(Boolean);
    
    this.timeout = API_CONFIG.TIMEOUT;
    this.headers = API_CONFIG.HEADERS;
  }

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
        console.log(`API success with ${baseUrl}:`, data);
        return data;
      } catch (error) {
        console.log(`Failed ${baseUrl}:`, error.message);
        lastError = error;
        continue;
      }
    }
    
    console.error('All API endpoints failed');
    throw new Error(`All backend connections failed. Last error: ${lastError?.message || 'Unknown'}`);
  }

  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
    });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  async healthCheck() {
    return this.get('/health');
  }

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

const apiService = new ApiService();
export default apiService;