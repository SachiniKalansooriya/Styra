import React from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

import { useTheme } from '../themes/ThemeProvider';
import { Card } from '../components/common/Card';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';

export default function HomeScreen({ navigation }) {
  const { theme, changeThemeByWeather, weatherCondition } = useTheme();

  const mockOutfits = [
    { 
      id: 1, 
      name: "Sunny Day Casual", 
      confidence: 92, 
      weather: "sunny",
      description: "Perfect for a bright day out"
    },
    { 
      id: 2, 
      name: "Rainy Day Cozy", 
      confidence: 88, 
      weather: "rainy",
      description: "Stay warm and stylish"
    },
    { 
      id: 3, 
      name: "Party Night Glam", 
      confidence: 95, 
      weather: "party",
      description: "Turn heads at any event"
    },
    { 
      id: 4, 
      name: "Professional Look", 
      confidence: 90, 
      weather: "cloudy",
      description: "Confident and business-ready"
    },
  ];

  const quickActions = [
    {
      id: 1,
      title: "Add Clothes",
      icon: "camera-outline",
      color: theme.primary,
      description: "Photograph new items",
    },
    {
      id: 2,
      title: "My Wardrobe",
      icon: "shirt-outline",
      color: theme.secondary,
      description: "Browse your collection",
    },
    {
      id: 3,
      title: "Get Outfit",
      icon: "sparkles-outline",
      color: theme.accent,
      description: "AI recommendations",
    },
    {
      id: 4,
      title: "Trip Planner",
      icon: "airplane-outline",
      color: "#9C27B0",
      description: "Pack smart for travel",
    },
  ];

  return (
    <LinearGradient 
      colors={theme.background} 
      style={styles.container}
    >
      <StatusBar style="auto" />
      
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={[styles.greeting, { color: theme.text }]}>Good Morning! ☀️</Text>
          <Text style={[styles.title, { color: theme.text }]}>✨ Styra</Text>
        </View>
        <TouchableOpacity style={styles.profileButton}>
          <Ionicons name="person-circle-outline" size={32} color={theme.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView 
        style={styles.content} 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        
        {/* Weather Theme Switcher */}
        <Card style={styles.themeCard}>
          <View style={styles.cardHeader}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>🌤️ Theme Mood</Text>
            <Text style={[styles.sectionSubtitle, { color: theme.text }]}>
              Current: {weatherCondition}
            </Text>
          </View>
          <View style={styles.themeButtons}>
            {[
              { key: 'sunny', emoji: '☀️', label: 'Sunny' },
              { key: 'rainy', emoji: '🌧️', label: 'Rainy' },
              { key: 'cloudy', emoji: '☁️', label: 'Cloudy' },
              { key: 'party', emoji: '🎉', label: 'Party' },
            ].map((weather) => (
              <TouchableOpacity
                key={weather.key}
                style={[
                  styles.themeButton,
                  { 
                    backgroundColor: weatherCondition === weather.key 
                      ? theme.primary 
                      : 'rgba(255,255,255,0.3)',
                    borderColor: weatherCondition === weather.key 
                      ? theme.primary 
                      : 'transparent',
                    borderWidth: 2,
                  }
                ]}
                onPress={() => changeThemeByWeather(weather.key)}
              >
                <Text style={styles.themeEmoji}>{weather.emoji}</Text>
                <Text style={[
                  styles.themeButtonText,
                  { 
                    color: weatherCondition === weather.key 
                      ? 'white' 
                      : theme.text,
                    fontWeight: weatherCondition === weather.key ? 'bold' : '500'
                  }
                ]}>
                  {weather.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Card>

        {/* Quick Actions Grid */}
        <Card style={styles.actionsCard}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>⚡ Quick Actions</Text>
          <View style={styles.actionsGrid}>
            {quickActions.map((action) => (
              <TouchableOpacity
                key={action.id}
                style={[styles.actionItem, { borderColor: action.color }]}
              >
                <View style={[styles.actionIcon, { backgroundColor: action.color }]}>
                  <Ionicons name={action.icon} size={24} color="white" />
                </View>
                <Text style={[styles.actionTitle, { color: theme.text }]}>
                  {action.title}
                </Text>
                <Text style={[styles.actionDescription, { color: theme.text }]}>
                  {action.description}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Card>

        {/* Today's Outfit Suggestions */}
        <Card style={styles.outfitsCard}>
          <View style={styles.cardHeader}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>✨ Today's Picks</Text>
            <TouchableOpacity>
              <Text style={[styles.seeAll, { color: theme.primary }]}>See All</Text>
            </TouchableOpacity>
          </View>
          
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.outfitsList}
            contentContainerStyle={styles.outfitsListContent}
          >
            {mockOutfits.map((outfit) => (
              <View key={outfit.id} style={styles.outfitCard}>
                <View style={styles.outfitImagePlaceholder}>
                  <Ionicons name="shirt-outline" size={40} color={theme.primary} />
                </View>
                
                <View style={styles.outfitInfo}>
                  <View style={styles.outfitHeader}>
                    <Text style={[styles.outfitName, { color: theme.text }]} numberOfLines={1}>
                      {outfit.name}
                    </Text>
                  </View>
                  
                  <Text style={[styles.outfitDescription, { color: theme.text }]} numberOfLines={2}>
                    {outfit.description}
                  </Text>
                  
                  <View style={styles.outfitFooter}>
                    <ConfidenceBadge confidence={outfit.confidence} />
                    <TouchableOpacity style={styles.heartButton}>
                      <Ionicons name="heart-outline" size={20} color={theme.primary} />
                    </TouchableOpacity>
                  </View>
                </View>
              </View>
            ))}
          </ScrollView>
        </Card>

        {/* Weather Info Card */}
        <Card style={styles.weatherCard}>
          <View style={styles.weatherHeader}>
            <View>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>🌡️ Today's Weather</Text>
              <Text style={[styles.weatherLocation, { color: theme.text }]}>
                Negombo, Western Province
              </Text>
            </View>
            <View style={styles.weatherInfo}>
              <Text style={[styles.weatherTemp, { color: theme.primary }]}>28°C</Text>
              <Text style={[styles.weatherCondition, { color: theme.text }]}>Sunny</Text>
            </View>
          </View>
          <Text style={[styles.weatherSuggestion, { color: theme.text }]}>
            Perfect weather for light, breathable fabrics! ✨
          </Text>
        </Card>

        {/* Statistics Card */}
        <Card style={styles.statsCard}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>📊 Your Style Stats</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: theme.primary }]}>47</Text>
              <Text style={[styles.statLabel, { color: theme.text }]}>Items</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: theme.primary }]}>23</Text>
              <Text style={[styles.statLabel, { color: theme.text }]}>Outfits</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: theme.primary }]}>12</Text>
              <Text style={[styles.statLabel, { color: theme.text }]}>Favorites</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: theme.primary }]}>89%</Text>
              <Text style={[styles.statLabel, { color: theme.text }]}>Match Rate</Text>
            </View>
          </View>
        </Card>

      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  greeting: {
    fontSize: 16,
    opacity: 0.8,
    marginBottom: 4,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  profileButton: {
    padding: 8,
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 30,
  },
  
  // Card Styles
  themeCard: {
    marginBottom: 16,
  },
  actionsCard: {
    marginBottom: 16,
  },
  outfitsCard: {
    marginBottom: 16,
  },
  weatherCard: {
    marginBottom: 16,
  },
  statsCard: {
    marginBottom: 16,
  },
  
  // Header Styles
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  sectionSubtitle: {
    fontSize: 14,
    opacity: 0.7,
    marginTop: 2,
  },
  seeAll: {
    fontSize: 14,
    fontWeight: '600',
  },

  // Theme Buttons
  themeButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  themeButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 16,
    marginHorizontal: 4,
  },
  themeEmoji: {
    fontSize: 20,
    marginBottom: 4,
  },
  themeButtonText: {
    fontSize: 12,
    textAlign: 'center',
  },

  // Quick Actions
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  actionItem: {
    width: '48%',
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 16,
    borderRadius: 16,
    borderWidth: 2,
    marginBottom: 12,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  actionIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
    textAlign: 'center',
  },
  actionDescription: {
    fontSize: 12,
    opacity: 0.7,
    textAlign: 'center',
  },

  // Outfits List
  outfitsList: {
    marginTop: 8,
  },
  outfitsListContent: {
    paddingRight: 16,
  },
  outfitCard: {
    width: 180,
    marginRight: 16,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 16,
    overflow: 'hidden',
  },
  outfitImagePlaceholder: {
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  outfitInfo: {
    padding: 12,
  },
  outfitHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  outfitName: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  outfitDescription: {
    fontSize: 12,
    opacity: 0.8,
    marginBottom: 12,
    lineHeight: 16,
  },
  outfitFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  heartButton: {
    padding: 4,
  },

  // Weather Card
  weatherHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  weatherLocation: {
    fontSize: 14,
    opacity: 0.7,
    marginTop: 2,
  },
  weatherInfo: {
    alignItems: 'flex-end',
  },
  weatherTemp: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  weatherCondition: {
    fontSize: 14,
    opacity: 0.8,
  },
  weatherSuggestion: {
    fontSize: 14,
    fontStyle: 'italic',
    opacity: 0.8,
    textAlign: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.2)',
  },

  // Stats Grid
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    opacity: 0.8,
  },
});