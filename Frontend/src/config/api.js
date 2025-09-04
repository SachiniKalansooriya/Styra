// API Configuration
const getApiUrl = () => {
  // In development, you have multiple options:
  // 1. Use your computer's IP (if firewall allows)
  // 2. Use localhost when testing on web
  // 3. Use Expo tunnel URL when using physical device
  
  const isDevelopment = __DEV__ || true;
  
  if (isDevelopment) {
    // Try multiple URLs for development
    return {
      primary: 'http://172.20.10.7:8000',     // Your computer's IP
      fallback: 'http://127.0.0.1:8000',      // Localhost
      localhost: 'http://10.0.2.2:8000',      // Android emulator
    };
  }
  
  // Production URL (when you deploy)
  return {
    primary: 'https://your-production-api.com',
    fallback: 'http://127.0.0.1:8000',
  };
};

const API_CONFIG = {
  ...getApiUrl(),
  TIMEOUT: 10000, // 10 seconds
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
};

export default API_CONFIG;
