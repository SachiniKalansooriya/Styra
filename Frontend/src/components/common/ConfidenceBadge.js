import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../../themes/ThemeProvider';

export const ConfidenceBadge = ({ confidence, style }) => {
  const { theme } = useTheme();
  
  const getConfidenceColor = () => {
    if (confidence >= 90) return '#4CAF50'; // Green
    if (confidence >= 70) return '#FF9800'; // Orange  
    return '#F44336'; // Red
  };

  const getConfidenceEmoji = () => {
    if (confidence >= 90) return '🔥';
    if (confidence >= 70) return '💡';
    return '🤔';
  };

  return (
    <View style={[
      styles.badge,
      { backgroundColor: getConfidenceColor() },
      style
    ]}>
      <Text style={styles.emoji}>{getConfidenceEmoji()}</Text>
      <Text style={styles.text}>{confidence}% match</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  emoji: {
    fontSize: 14,
    marginRight: 4,
  },
  text: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
});