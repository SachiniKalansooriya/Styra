import React, { useState } from 'react';
import { ThemeProvider } from './src/themes/ThemeProvider';
import { LandingScreen } from './src/screens/LandingScreen';
import { LoginScreen } from './src/screens/LoginScreen';
import { SignUpScreen } from './src/screens/SignUpScreen';
import HomeScreen from './src/screens/HomeScreen';
import MyWardrobeScreen from './src/screens/MyWardrobeScreen';
import GetOutfitScreen from './src/screens/GetOutfitScreen';
import TripPlannerScreen from './src/screens/TripPlannerScreen';
import AddClothesScreen from './src/screens/AddClothesScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('Landing');
  const [screenParams, setScreenParams] = useState({});

  const navigate = (screenName, params = {}) => {
    setCurrentScreen(screenName);
    setScreenParams(params);
  };

  const goBack = () => {
    // Simple back navigation - you can make this more sophisticated with a navigation stack
    setCurrentScreen('Home');
    setScreenParams({});
  };

  const renderScreen = () => {
    const navigationProps = { 
      navigation: { 
        navigate, 
        goBack,
        params: screenParams 
      } 
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