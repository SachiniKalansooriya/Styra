// src/services/authService.js
import AsyncStorage from '@react-native-async-storage/async-storage';
import connectionService from './connectionService';

class AuthService {
  constructor() {
    this.baseURL = connectionService.baseURL;
    this.token = null;
    this.user = null;
  }

  // Add validation methods
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  validateSignupForm(formData) {
    const errors = [];
    const { name, email, password, confirmPassword } = formData;

    if (!name || name.trim().length < 2) {
      errors.push('Name must be at least 2 characters long');
    }

    if (!email || !this.validateEmail(email)) {
      errors.push('Please enter a valid email address');
    }

    if (!password || password.length < 6) {
      errors.push('Password must be at least 6 characters long');
    }

    if (password !== confirmPassword) {
      errors.push('Passwords do not match');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  async signIn(email, password) {
    try {
      console.log('Attempting signin with:', email);
      
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      console.log('Login response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.log('Login error response:', errorData);
        return {
          success: false,
          error: errorData.detail || errorData.message || `Login failed with status ${response.status}`
        };
      }

      const data = await response.json();
      console.log('Signin response:', data);

      if (data.status === 'success' && data.access_token) {
        // Store token and user data safely
        try {
          await AsyncStorage.setItem('access_token', data.access_token);
          await AsyncStorage.setItem('user_data', JSON.stringify(data.user));
          if (data.expires_in) {
            await AsyncStorage.setItem('token_expires', data.expires_in.toString());
          }
        } catch (storageError) {
          console.error('Storage error:', storageError);
          // Continue anyway - the login was successful
        }
        
        this.token = data.access_token;
        this.user = data.user;
        
        console.log('JWT token stored successfully');
        
        return {
          success: true,
          user: data.user,
          token: data.access_token,
          message: data.message
        };
      } else {
        return {
          success: false,
          error: data.detail || data.message || 'Login failed'
        };
      }
    } catch (error) {
      console.error('Signin error:', error);
      return {
        success: false,
        error: 'Network error - please check your connection'
      };
    }
  }

  async signUp(userData) {
    try {
      console.log('Attempting signup with:', userData);
      
      const response = await fetch(`${this.baseURL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      console.log('Signup response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.log('Signup error response:', errorData);
        return {
          success: false,
          error: errorData.detail || errorData.message || `Signup failed with status ${response.status}`
        };
      }

      const data = await response.json();
      console.log('Signup response:', data);

      if (data.status === 'success') {
        // Don't auto-login after signup - just return success
        return {
          success: true,
          user: data.user,
          message: data.message || 'Account created successfully! Please log in.'
        };
      } else {
        return {
          success: false,
          error: data.detail || data.message || 'Signup failed'
        };
      }
    } catch (error) {
      console.error('Signup error:', error);
      return {
        success: false,
        error: 'Network error - please check your connection'
      };
    }
  }

  async loadUserFromStorage() {
    try {
      const token = await AsyncStorage.getItem('access_token');
      const userData = await AsyncStorage.getItem('user_data');
      
      if (token && userData) {
        // Verify token with backend
        const isValid = await this.verifyToken(token);
        if (isValid) {
          this.token = token;
          this.user = JSON.parse(userData);
          console.log('JWT token loaded and verified from storage');
          return {
            success: true,
            user: this.user,
            token: this.token
          };
        } else {
          // Token invalid, clear storage
          console.log('Stored JWT token is invalid, clearing storage');
          await this.signOut();
          return { success: false, error: 'Token expired' };
        }
      }
      
      console.log('No stored JWT token found');
      return { success: false };
    } catch (error) {
      console.error('Load user from storage error:', error);
      return { success: false };
    }
  }

  async verifyToken(token) {
    try {
      const response = await fetch(`${this.baseURL}/auth/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return response.ok && data.status === 'success';
    } catch (error) {
      console.error('Token verification error:', error);
      return false;
    }
  }

  async signOut() {
    try {
      // Notify backend (optional, since JWT is stateless)
      if (this.token) {
        try {
          await fetch(`${this.baseURL}/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${this.token}`,
              'Content-Type': 'application/json',
            },
          });
        } catch (error) {
          console.log('Logout API call failed, but continuing with local cleanup');
        }
      }
      
      // Clear local storage
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('user_data');
      await AsyncStorage.removeItem('token_expires');
      
      this.token = null;
      this.user = null;
      
      console.log('JWT tokens cleared, user signed out');
      return { success: true };
    } catch (error) {
      console.error('Signout error:', error);
      return { success: false };
    }
  }

  getAuthHeaders() {
    if (this.token) {
      return {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      };
    }
    return {
      'Content-Type': 'application/json',
    };
  }

  isAuthenticated() {
    return !!this.token;
  }

  getCurrentUser() {
    return this.user;
  }

  getToken() {
    return this.token;
  }
}

export default new AuthService();