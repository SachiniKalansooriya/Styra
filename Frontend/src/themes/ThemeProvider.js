import React, { createContext, useContext } from 'react';
import { lightTheme } from './weatherThemes';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  return (
    <ThemeContext.Provider 
      value={{
        theme: lightTheme,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};