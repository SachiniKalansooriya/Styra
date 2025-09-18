// Simple test to check if the backend is reachable
// Run this in the React Native app to test connectivity

const testBackendConnection = async () => {
  console.log('Testing backend connection...');
  
  try {
    // Test simple GET request first
    const response = await fetch('http://172.20.10.7:8000/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Success! Response data:', data);
    } else {
      console.log('HTTP error:', response.status);
    }
  } catch (error) {
    console.error('Connection test failed:', error);
    console.error('Error type:', typeof error);
    console.error('Error message:', error.message);
  }
};

// Call this function to test
testBackendConnection();
