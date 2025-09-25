import React, { useState, useEffect } from 'react';
import { Alert } from 'react-native';
import { ThemeProvider } from './src/themes/ThemeProvider';
import { LandingScreen } from './src/screens/LandingScreen';
import { LoginScreen } from './src/screens/LoginScreen';
import { SignUpScreen } from './src/screens/SignUpScreen';
import HomeScreen from './src/screens/HomeScreen';
import MyWardrobeScreen from './src/screens/MyWardrobeScreen';
import GetOutfitScreen from './src/screens/GetOutfitScreen';
import AddClothesScreen from './src/screens/AddClothesScreen';
import FavoriteOutfitsScreen from './src/screens/FavoriteOutfitsScreen';
import WornOutfitsScreen from './src/screens/WornOutfitsScreen';
import BuyRecommendationsScreen from './src/screens/BuyRecommendationsScreen';
import connectionService from './src/services/connectionService';
import authService from './src/services/authService';
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiService from './src/services/apiService';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('Landing');
  const [screenParams, setScreenParams] = useState({});
  const [backendConnected, setBackendConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const navigate = (screenName, params = {}) => {
    console.log('=== NAVIGATION CALLED ===');
    console.log('Navigating to:', screenName);
    console.log('With params:', params);
    console.log('From screen:', currentScreen);
    console.log('Is authenticated:', isAuthenticated);
    console.log('========================');
    
    // Check if trying to navigate to protected screens without authentication
    const protectedScreens = ['Home', 'MyWardrobe', 'GetOutfit', 'TripPlanner', 'FavoriteOutfits', 'WornOutfits', 'AddClothes', 'BuyRecommendations', 'SavedTrips', 'PackingListResults'];
    
    if (protectedScreens.includes(screenName) && !isAuthenticated) {
      console.log('Access denied - redirecting to Landing');
      Alert.alert('Access Denied', 'Please log in to access this feature');
      setCurrentScreen('Landing');
      setScreenParams({});
      return;
    }
    
    setCurrentScreen(screenName);
    setScreenParams(params);
  };

  const goBack = () => {
    if (isAuthenticated) {
      setCurrentScreen('Home');
    } else {
      setCurrentScreen('Landing');
    }
    setScreenParams({});
  };

const handleSuccessfulAuth = (user) => {
  console.log('Authentication successful for user:', user);
  setIsAuthenticated(true);
  navigate('Home'); // This will take user directly to Home after login/signup
};
  const handleLogout = async () => {
    try {
      await authService.signOut();
      setIsAuthenticated(false);
      navigate('Landing');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  useEffect(() => {
const initializeApp = async () => {
  console.log('=== APP INITIALIZATION START ===');
  try {
    // Check backend connection first
    const connectionResult = await connectionService.initializeApp();
    setBackendConnected(connectionResult.backend.success);
    
    if (!connectionResult.backend.success) {
      console.warn('Backend not available, using offline mode');
    }

    // Check for stored authentication
    const authResult = await authService.loadUserFromStorage();

    if (authResult.success && authResult.user) {
      // Verify the stored token with backend before trusting it
      try {
        const token = authService.getToken ? authService.getToken() : null;
        console.log('Found stored token, verifying with backend...');
        const verifyResponse = await apiService.request('/auth/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          }
        });

        if (verifyResponse && verifyResponse.status === 'success') {
          console.log('Token verified by backend. User authenticated.');
          setIsAuthenticated(true);
        } else {
          console.log('Stored token invalid according to backend. Clearing local auth.');
          await authService.signOut();
          setIsAuthenticated(false);
        }
      } catch (err) {
        console.warn('Token verification failed:', err.message || err);
        await authService.signOut();
        setIsAuthenticated(false);
      }
      // Don't automatically navigate - let user see landing page first
    } else {
      console.log('No valid authentication found');
      setIsAuthenticated(false);
    }
    
    // Always start with Landing screen
    setCurrentScreen('Landing');
    
  } catch (error) {
    console.error('App initialization error:', error);
    setIsAuthenticated(false);
    setCurrentScreen('Landing');
    setBackendConnected(false);
  } finally {
    setIsLoading(false);
    console.log('=== APP INITIALIZATION COMPLETE ===');
  }
};

    initializeApp();
  }, []);

  // Show loading state while checking authentication
  if (isLoading) {
    return null; // You can add a loading screen component here
  }

  const renderScreen = () => {
    console.log('=== RENDER SCREEN DEBUG ===');
    console.log('Current screen:', currentScreen);
    console.log('Screen params:', screenParams);
    console.log('Is authenticated:', isAuthenticated);
    console.log('=========================');
    
    const navigationProps = { 
      navigation: { 
        navigate, 
        goBack,
        params: screenParams 
      },
      backendConnected,
      isAuthenticated,
      onAuthSuccess: handleSuccessfulAuth,
      onLogout: handleLogout,
      route: { params: screenParams } // Add route prop for compatibility
    };
    
    switch (currentScreen) {
      case 'Landing':
        return <LandingScreen {...navigationProps} />;
      case 'Login':
        return <LoginScreen {...navigationProps} />;
      case 'SignUp':
        return <SignUpScreen {...navigationProps} />;
      case 'Home':
        return <HomeScreen {...navigationProps} />;
      case 'AddClothes':
        return <AddClothesScreen {...navigationProps} />;
      case 'MyWardrobe':
        return <MyWardrobeScreen {...navigationProps} />;
      case 'GetOutfit':
        return <GetOutfitScreen {...navigationProps} />;
      case 'FavoriteOutfits':
        return <FavoriteOutfitsScreen {...navigationProps} />;
      case 'WornOutfits':
        return <WornOutfitsScreen {...navigationProps} />;
      case 'BuyRecommendations':
        return <BuyRecommendationsScreen {...navigationProps} />;
      default:
        return <LandingScreen {...navigationProps} />;
    }
  };

  return (
    <ThemeProvider>
      {renderScreen()}
    </ThemeProvider>
  );
}