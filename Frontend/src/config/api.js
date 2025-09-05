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
      primary: 'http://172.20.10.7:8000',     // Your ASUS laptop's IP
      fallback: 'http://localhost:8000',       // Won't work on phone, but useful for web
      androidEmulator: 'http://10.0.2.2:8000', // For Android emulator only
    };
  }
  
  // Production URL (when you deploy)
  return {
    primary: 'https://your-production-api.com',
    fallback: 'http://172.20.10.7:8000',
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
