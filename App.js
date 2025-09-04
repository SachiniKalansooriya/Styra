import React, { useState } from 'react';
import { ThemeProvider } from './src/themes/ThemeProvider';
import { LandingScreen } from './src/screens/LandingScreen';
import { LoginScreen } from './src/screens/LoginScreen';
import { SignUpScreen } from './src/screens/SignUpScreen';
import HomeScreen from './src/screens/HomeScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('Landing');

  const navigate = (screenName) => {
    setCurrentScreen(screenName);
  };

  const renderScreen = () => {
    const navigationProps = { navigation: { navigate } };
    
    switch (currentScreen) {
      case 'Landing':
        return <LandingScreen {...navigationProps} />;
      case 'Login':
        return <LoginScreen {...navigationProps} />;
      case 'SignUp':
        return <SignUpScreen {...navigationProps} />;
      case 'Home':
        return <HomeScreen {...navigationProps} />;
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