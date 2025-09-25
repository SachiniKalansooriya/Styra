// src/config/api.js
const getApiUrl = () => {
  const isDevelopment = __DEV__ || true;
  
  if (isDevelopment) {
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
  TIMEOUT: 30000, // Increased to 30 seconds for image uploads
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    // Prevent intermediate caches from returning stale responses
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    Pragma: 'no-cache',
    Expires: '0',
  },
};

export default API_CONFIG;