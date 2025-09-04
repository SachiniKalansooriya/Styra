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
    // Simple back navigation - you can make this more sophisticated with a navigation stack
    setCurrentScreen('Home');
    setScreenParams({});
  };

  // Test backend connection on app start
  useEffect(() => {
    const testConnection = async () => {
      try {
        const connectionResult = await connectionService.initializeApp();
        setBackendConnected(connectionResult.backend.success);
        
        if (!connectionResult.backend.success) {
          // Show connection warning but don't block the app
          console.warn('Backend not available, using offline mode');
          // Optionally show a toast or alert to inform the user
          // Alert.alert(
          //   'Offline Mode', 
          //   'Backend server is not available. Some features may be limited.',
          //   [{ text: 'OK' }]
          // );
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
      backendConnected // Pass connection status to all screens
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