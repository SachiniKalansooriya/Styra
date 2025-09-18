import React, { useState, useEffect } from 'react';
import { Alert } from 'react-native';
import { ThemeProvider } from './src/themes/ThemeProvider';
import { LandingScreen } from './src/screens/LandingScreen';
import { LoginScreen } from './src/screens/LoginScreen';
import { SignUpScreen } from './src/screens/SignUpScreen';
import HomeScreen from './src/screens/HomeScreen';
import MyWardrobeScreen from './src/screens/MyWardrobeScreen';
import GetOutfitScreen from './src/screens/GetOutfitScreen';
import TripPlannerScreen from './src/screens/TripPlannerScreen';
import AddClothesScreen from './src/screens/AddClothesScreen';
import FavoriteOutfitsScreen from './src/screens/FavoriteOutfitsScreen';
import WornOutfitsScreen from './src/screens/WornOutfitsScreen';
import connectionService from './src/services/connectionService';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('Landing');
  const [screenParams, setScreenParams] = useState({});
  const [backendConnected, setBackendConnected] = useState(false);

  const navigate = (screenName, params = {}) => {
    setCurrentScreen(screenName);
    setScreenParams(params);
  };

  const goBack = () => {
    setCurrentScreen('Home');
    setScreenParams({});
  };

  useEffect(() => {
    const testConnection = async () => {
      try {
        const connectionResult = await connectionService.initializeApp();
        setBackendConnected(connectionResult.backend.success);
        
        if (!connectionResult.backend.success) {
          console.warn('Backend not available, using offline mode');
        } else {
          console.log('Backend connected successfully!');
        }
      } catch (error) {
        console.error('Connection test failed:', error);
        setBackendConnected(false);
      }
    };

    testConnection();
  }, []);

  const renderScreen = () => {
    const navigationProps = { 
      navigation: { 
        navigate, 
        goBack,
        params: screenParams 
      },
      backendConnected,
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
      case 'TripPlanner':
        return <TripPlannerScreen {...navigationProps} />;
      case 'FavoriteOutfits':
        return <FavoriteOutfitsScreen {...navigationProps} />;
      case 'WornOutfits':
        return <WornOutfitsScreen {...navigationProps} />;
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