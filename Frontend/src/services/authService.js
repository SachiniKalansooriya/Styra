// authService.js
import apiService from './apiService';
import AsyncStorage from '@react-native-async-storage/async-storage';

class AuthService {
  constructor() {
    this.currentUser = null;
    this.token = null;
  }

  // Sign up new user
  async signUp(userData) {
    try {
      console.log('Attempting signup with:', userData);
      
      const response = await apiService.post('/auth/signup', {
        name: userData.name,
        email: userData.email,
        password: userData.password
      });

      console.log('Signup response:', response);

      if (response.status === 'success') {
        // Store user data and token
        this.currentUser = response.user;
        this.token = response.token || 'mock_token';
        
        // Save to AsyncStorage for persistence
        await AsyncStorage.setItem('user', JSON.stringify(response.user));
        await AsyncStorage.setItem('token', this.token);
        
        return {
          success: true,
          user: response.user,
          message: response.message
        };
      } else {
        return {
          success: false,
          error: response.message || 'Signup failed'
        };
      }
    } catch (error) {
      console.error('Signup error:', error);
      return {
        success: false,
        error: error.message || 'Network error occurred'
      };
    }
  }

  // Sign in existing user
  async signIn(email, password) {
    try {
      console.log('Attempting signin with:', email);
      
      const response = await apiService.post('/auth/login', {
        email,
        password
      });

      console.log('Signin response:', response);

      if (response.status === 'success') {
        this.currentUser = response.user;
        this.token = response.token;
        
        // Save to AsyncStorage
        await AsyncStorage.setItem('user', JSON.stringify(response.user));
        await AsyncStorage.setItem('token', response.token);
        
        return {
          success: true,
          user: response.user,
          message: response.message
        };
      } else {
        return {
          success: false,
          error: response.message || 'Login failed'
        };
      }
    } catch (error) {
      console.error('Signin error:', error);
      return {
        success: false,
        error: error.message || 'Network error occurred'
      };
    }
  }

  // Sign out user
  async signOut() {
    try {
      this.currentUser = null;
      this.token = null;
      
      // Clear AsyncStorage
      await AsyncStorage.removeItem('user');
      await AsyncStorage.removeItem('token');
      
      return { success: true };
    } catch (error) {
      console.error('Signout error:', error);
      return { success: false, error: error.message };
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return this.currentUser !== null && this.token !== null;
  }

  // Get current user
  getCurrentUser() {
    return this.currentUser;
  }

  // Get auth token
  getToken() {
    return this.token;
  }

  // Load user from storage (for app initialization)
  async loadUserFromStorage() {
    try {
      const userData = await AsyncStorage.getItem('user');
      const token = await AsyncStorage.getItem('token');
      
      if (userData && token) {
        this.currentUser = JSON.parse(userData);
        this.token = token;
        return { success: true, user: this.currentUser };
      }
      
      return { success: false };
    } catch (error) {
      console.error('Error loading user from storage:', error);
      return { success: false, error: error.message };
    }
  }

  // Validate email format
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Validate password strength
  validatePassword(password) {
    const errors = [];
    
    if (password.length < 6) {
      errors.push('Password must be at least 6 characters long');
    }
    
    if (!/(?=.*[a-z])/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    
    if (!/(?=.*[A-Z])/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    
    if (!/(?=.*\d)/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Basic validation for signup form
  validateSignupForm(formData) {
    const errors = [];
    
    // Name validation
    if (!formData.name || formData.name.trim().length < 2) {
      errors.push('Name must be at least 2 characters long');
    }
    
    // Email validation
    if (!formData.email) {
      errors.push('Email is required');
    } else if (!this.validateEmail(formData.email)) {
      errors.push('Please enter a valid email address');
    }
    
    // Password validation
    if (!formData.password) {
      errors.push('Password is required');
    } else {
      const passwordValidation = this.validatePassword(formData.password);
      if (!passwordValidation.isValid) {
        errors.push(...passwordValidation.errors);
      }
    }
    
    // Confirm password validation
    if (!formData.confirmPassword) {
      errors.push('Please confirm your password');
    } else if (formData.password !== formData.confirmPassword) {
      errors.push('Passwords do not match');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

export default new AuthService();
