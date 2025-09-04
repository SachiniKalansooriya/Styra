import apiService from './apiService';

class UserService {
  // User authentication
  async login(credentials) {
    try {
      return await apiService.post('/auth/login', credentials);
    } catch (error) {
      throw new Error(`Login failed: ${error.message}`);
    }
  }

  async signup(userData) {
    try {
      return await apiService.post('/auth/signup', userData);
    } catch (error) {
      throw new Error(`Signup failed: ${error.message}`);
    }
  }

  async logout() {
    try {
      return await apiService.post('/auth/logout');
    } catch (error) {
      throw new Error(`Logout failed: ${error.message}`);
    }
  }

  // User profile
  async getUserProfile() {
    try {
      return await apiService.get('/user/profile');
    } catch (error) {
      throw new Error(`Failed to get user profile: ${error.message}`);
    }
  }

  async updateUserProfile(profileData) {
    try {
      return await apiService.put('/user/profile', profileData);
    } catch (error) {
      throw new Error(`Failed to update profile: ${error.message}`);
    }
  }
}

export default new UserService();
