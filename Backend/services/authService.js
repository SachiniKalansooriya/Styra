import AsyncStorage from '@react-native-async-storage/async-storage';
import connectionService from './connectionService';

class AuthService {
  constructor() {
    this.baseURL = connectionService.baseURL;
    this.token = null;
    this.user = null;
  }

  async signIn(email, password) {
    try {
      console.log('Attempting JWT login with:', email);
      
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      console.log('Login response status:', response.status);
      console.log('Login response data:', data);

      if (response.ok && data.status === 'success' && data.access_token) {
        // Store token and user data
        await AsyncStorage.setItem('access_token', data.access_token);
        await AsyncStorage.setItem('user_data', JSON.stringify(data.user));
        await AsyncStorage.setItem('token_expires', data.expires_in.toString());
        
        this.token = data.access_token;
        this.user = data.user;
        
        console.log('JWT token stored successfully');
        
        return {
          success: true,
          user: data.user,
          token: data.access_token
        };
      } else {
        return {
          success: false,
          error: data.detail || data.message || 'Login failed'
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: 'Network error - please check your connection'
      };
    }
  }

  async signUp(userData) {
    try {
      console.log('Attempting JWT signup with:', userData);
      
      const response = await fetch(`${this.baseURL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();
      console.log('Signup response:', data);

      if (response.ok && data.status === 'success' && data.access_token) {
        // Store token and user data
        await AsyncStorage.setItem('access_token', data.access_token);
        await AsyncStorage.setItem('user_data', JSON.stringify(data.user));
        await AsyncStorage.setItem('token_expires', data.expires_in.toString());
        
        this.token = data.access_token;
        this.user = data.user;
        
        return {
          success: true,
          user: data.user,
          token: data.access_token
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