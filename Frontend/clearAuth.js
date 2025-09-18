// Clear authentication storage - run this once to reset authentication state
import AsyncStorage from '@react-native-async-storage/async-storage';

const clearAuthStorage = async () => {
  try {
    await AsyncStorage.removeItem('user');
    await AsyncStorage.removeItem('token');
    console.log('Authentication storage cleared');
  } catch (error) {
    console.error('Error clearing auth storage:', error);
  }
};

// Call this function to clear storage
clearAuthStorage();
