import React, { createContext, useContext, useState, useEffect } from 'react';
import { weatherThemes, getThemeForWeather } from './weatherThemes';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState(weatherThemes.sunny);
  const [weatherCondition, setWeatherCondition] = useState('sunny');

  const changeThemeByWeather = (weather) => {
    const newTheme = getThemeForWeather(weather);
    setCurrentTheme(newTheme);
    setWeatherCondition(weather);
  };

  const changeThemeByMood = (mood) => {
    if (mood === 'party') {
      setCurrentTheme(weatherThemes.party);
    } else if (mood === 'calm') {
      setCurrentTheme(weatherThemes.rainy);
    }
    // Add more mood mappings
  };

  return (
    <ThemeContext.Provider 
      value={{
        theme: currentTheme,
        weatherCondition,
        changeThemeByWeather,
        changeThemeByMood,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};