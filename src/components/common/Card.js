import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useTheme } from '../../themes/ThemeProvider';

export const Card = ({ children, style, elevated = true }) => {
  const { theme } = useTheme();
  
  return (
    <View style={[
      styles.card,
      {
        backgroundColor: theme.surface,
        shadowColor: theme.shadow,
      },
      elevated && styles.elevated,
      style
    ]}>
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    padding: 16,
    margin: 8,
  },
  elevated: {
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
  },
});