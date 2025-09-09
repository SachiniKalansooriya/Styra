// screens/HomeScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
  Image,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../themes/ThemeProvider';
import wardrobeService from '../services/wardrobeService';
import connectionService from '../services/connectionService';

const { width } = Dimensions.get('window');

const HomeScreen = ({ navigation }) => {
  const { theme } = useTheme();
  const [user, setUser] = useState({ name: 'Fashion Lover' });
  const [wardrobeStats, setWardrobeStats] = useState({
    totalItems: 0,
    recentlyAdded: 0,
    mostWornCategory: 'tops'
  });
  const [todayWeather, setTodayWeather] = useState({
    temperature: 24,
    condition: 'sunny',
    description: 'Sunny'
  });
  const [backendConnected, setBackendConnected] = useState(false);

  const handleGetOutfit = async () => {
    try {
      console.log('Calling AI outfit recommendation...');
      console.log('Using URL: http://172.20.10.7:8000/api/outfit/ai-recommendation');
      
      const response = await fetch('http://172.20.10.7:8000/api/outfit/ai-recommendation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 1,
          occasion: 'casual',
          location: {
            latitude: 40.7128,
            longitude: -74.0060
          }
        })
      });
      
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Full AI Response:', JSON.stringify(data, null, 2));
      
      if (data.outfit && data.outfit.error) {
        console.log('Outfit Error:', data.outfit.error);
        console.log('Error Message:', data.outfit.message);
        
        Alert.alert(
          'Wardrobe Setup Needed',
          data.outfit.message || 'Please add clothes with proper categories (tops, bottoms, shoes)',
          [
            { text: 'Add Sample Items', onPress: () => addSampleWardrobe() },
            { text: 'Add Manually', onPress: () => navigation.navigate('AddClothes') },
            { text: 'Try Anyway', onPress: () => navigation.navigate('GetOutfit') }
          ]
        );
        return;
      }
      
      if (data.status === 'success' && data.outfit && data.outfit.items && data.outfit.items.length > 0) {
        console.log('Found items:', data.outfit.items.length);
        console.log('Items:', data.outfit.items);
        
        navigation.navigate('GetOutfit', { 
          outfit: data.outfit,
          weather: data.weather 
        });
      } else {
        Alert.alert(
          'Wardrobe Ready!',
          'Add a few more items for better AI recommendations, or try our sample wardrobe.',
          [
            { text: 'Add Sample Items', onPress: () => addSampleWardrobe() },
            { text: 'Add Items', onPress: () => navigation.navigate('AddClothes') },
            { text: 'Try Manual', onPress: () => navigation.navigate('GetOutfit') }
          ]
        );
      }
    } catch (error) {
      console.error('Detailed error:', error);
      Alert.alert(
        'Connection Error',
        'Could not connect to AI styling service. Make sure your backend is running on http://172.20.10.7:8000',
        [
          { text: 'Check Backend', onPress: () => checkBackendStatus() },
          { text: 'Try Manual', onPress: () => navigation.navigate('GetOutfit') },
          { text: 'OK' }
        ]
      );
    }
  };

  const addSampleWardrobe = async () => {
    try {
      console.log('Adding sample wardrobe items...');
      const response = await fetch('http://172.20.10.7:8000/api/test/add-sample-wardrobe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const result = await response.json();
      console.log('Sample wardrobe result:', result);
      
      if (result.status === 'success') {
        Alert.alert(
          'Sample Items Added!',
          'Sample wardrobe items have been added. Try getting an outfit now!',
          [
            { text: 'Get Outfit', onPress: () => handleGetOutfit() },
            { text: 'View Wardrobe', onPress: () => navigation.navigate('MyWardrobe') }
          ]
        );
        loadWardrobeStats(); // Refresh stats
      } else {
        Alert.alert('Error', 'Failed to add sample items: ' + result.message);
      }
    } catch (error) {
      console.error('Error adding sample wardrobe:', error);
      Alert.alert('Error', 'Failed to add sample wardrobe items');
    }
  };

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://172.20.10.7:8000/health');
      const status = await response.json();
      console.log('Backend status:', status);
      
      Alert.alert(
        'Backend Status',
        `Status: ${status.status}\nDatabase: ${status.services?.database?.status || 'unknown'}`,
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert(
        'Backend Offline',
        'Backend server is not running. Please start it with: python main.py',
        [{ text: 'OK' }]
      );
    }
  };

  useEffect(() => {
    checkConnection();
    loadWardrobeStats();
    loadTodayWeather();
  }, []);

  const checkConnection = async () => {
    try {
      const connected = await connectionService.isBackendAvailable();
      setBackendConnected(connected);
    } catch (error) {
      setBackendConnected(false);
    }
  };

  const loadWardrobeStats = async () => {
    try {
      const items = await wardrobeService.getWardrobeItems();
      
      if (Array.isArray(items)) {
        const categories = {};
        items.forEach(item => {
          const category = item.category || 'unknown';
          categories[category] = (categories[category] || 0) + 1;
        });

        const mostWorn = Object.keys(categories).reduce((a, b) => 
          categories[a] > categories[b] ? a : b, 'tops'
        );

        setWardrobeStats({
          totalItems: items.length,
          recentlyAdded: items.filter(item => {
            const addedDate = new Date(item.created_at || item.addedDate);
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            return addedDate > weekAgo;
          }).length,
          mostWornCategory: mostWorn
        });
      }
    } catch (error) {
      console.error('Error loading wardrobe stats:', error);
    }
  };

  const loadTodayWeather = () => {
    const conditions = [
      { temp: 24, condition: 'sunny', desc: 'Sunny' },
      { temp: 18, condition: 'cloudy', desc: 'Cloudy' },
      { temp: 15, condition: 'rainy', desc: 'Light Rain' }
    ];
    
    const today = conditions[0];
    setTodayWeather({
      temperature: today.temp,
      condition: today.condition,
      description: today.desc
    });
  };

  const getWeatherIcon = (condition) => {
    switch (condition) {
      case 'sunny': return 'sunny';
      case 'cloudy': return 'cloudy';
      case 'rainy': return 'rainy';
      default: return 'partly-sunny';
    }
  };

  const getWeatherOutfitSuggestion = () => {
    if (todayWeather.temperature > 25) {
      return 'Light, breathable fabrics recommended';
    } else if (todayWeather.temperature < 15) {
      return 'Layer up with warm pieces';
    } else {
      return 'Perfect weather for versatile styling';
    }
  };

  const quickActions = [
    {
      id: 'camera',
      title: 'Add Clothes',
      subtitle: 'Photo & AI analysis',
      icon: 'camera',
      color: '#FF6B6B',
      onPress: () => navigation.navigate('AddClothes')
    },
    {
      id: 'outfit',
      title: 'Get Outfit',
      subtitle: 'AI styling assistant',
      icon: 'shirt',
      color: '#4ECDC4',
      onPress: () => handleGetOutfit()
    },
    {
      id: 'wardrobe',
      title: 'My Wardrobe',
      subtitle: `${wardrobeStats.totalItems} items`,
      icon: 'library',
      color: '#45B7D1',
      onPress: () => navigation.navigate('MyWardrobe')
    },
    {
      id: 'trip',
      title: 'Trip Planner',
      subtitle: 'Smart packing lists',
      icon: 'bag',
      color: '#FF8C42',
      onPress: () => navigation.navigate('TripPlanner')
    }
  ];

  const renderQuickAction = (action) => (
    <TouchableOpacity
      key={action.id}
      style={[styles.quickActionCard, { backgroundColor: action.color + '15' }]}
      onPress={action.onPress}
    >
      <View style={[styles.quickActionIcon, { backgroundColor: action.color }]}>
        <Ionicons name={action.icon} size={24} color="#fff" />
      </View>
      <Text style={styles.quickActionTitle}>{action.title}</Text>
      <Text style={styles.quickActionSubtitle}>{action.subtitle}</Text>
    </TouchableOpacity>
  );

  return (
    <LinearGradient colors={theme.background} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={[styles.greeting, { color: theme.text }]}>
              Good {new Date().getHours() < 12 ? 'Morning' : new Date().getHours() < 17 ? 'Afternoon' : 'Evening'}
            </Text>
            <Text style={[styles.userName, { color: theme.text }]}>{user.name}</Text>
          </View>
          
          <View style={styles.headerActions}>
            <TouchableOpacity 
              style={styles.connectionStatus}
              onPress={checkConnection}
            >
              <View style={[
                styles.connectionDot, 
                { backgroundColor: backendConnected ? '#4CAF50' : '#FF5722' }
              ]} />
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.notificationButton}
              onPress={() => Alert.alert('Notifications', 'No new notifications')}
            >
              <Ionicons name="notifications-outline" size={24} color={theme.text} />
            </TouchableOpacity>
          </View>
        </View>

        <ScrollView 
          style={styles.content}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >
          {/* Weather Card */}
          <View style={styles.weatherCard}>
            <LinearGradient
              colors={['#FF8C42', '#FF6B6B']}
              style={styles.weatherGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            >
              <View style={styles.weatherContent}>
                <View style={styles.weatherLeft}>
                  <Text style={styles.weatherTemp}>{todayWeather.temperature}°C</Text>
                  <Text style={styles.weatherDesc}>{todayWeather.description}</Text>
                  <Text style={styles.weatherSuggestion}>{getWeatherOutfitSuggestion()}</Text>
                </View>
                <View style={styles.weatherRight}>
                  <Ionicons 
                    name={getWeatherIcon(todayWeather.condition)} 
                    size={60} 
                    color="#fff" 
                  />
                </View>
              </View>
            </LinearGradient>
          </View>

          {/* Quick Actions Grid */}
          <View style={styles.quickActionsContainer}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>Quick Actions</Text>
            <View style={styles.quickActionsGrid}>
              {quickActions.map(renderQuickAction)}
            </View>
          </View>

          {/* Wardrobe Insights */}
          <View style={styles.insightsContainer}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>Wardrobe Insights</Text>
            
            <View style={styles.insightsGrid}>
              <View style={[styles.insightCard, styles.insightCardLarge]}>
                <View style={styles.insightHeader}>
                  <Ionicons name="analytics" size={24} color="#FF8C42" />
                  <Text style={styles.insightTitle}>Total Items</Text>
                </View>
                <Text style={styles.insightValue}>{wardrobeStats.totalItems}</Text>
                <Text style={styles.insightSubtext}>
                  {wardrobeStats.recentlyAdded} added this week
                </Text>
              </View>

              <View style={styles.insightCard}>
                <View style={styles.insightHeader}>
                  <Ionicons name="trending-up" size={20} color="#4ECDC4" />
                  <Text style={styles.insightTitleSmall}>Most Worn</Text>
                </View>
                <Text style={styles.insightValueSmall}>{wardrobeStats.mostWornCategory}</Text>
              </View>

              <View style={styles.insightCard}>
                <View style={styles.insightHeader}>
                  <Ionicons name="time" size={20} color="#45B7D1" />
                  <Text style={styles.insightTitleSmall}>Last Added</Text>
                </View>
                <Text style={styles.insightValueSmall}>
                  {wardrobeStats.recentlyAdded > 0 ? 'This week' : 'None recent'}
                </Text>
              </View>
            </View>
          </View>

          {/* Featured Cards */}
          <View style={styles.featuredContainer}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>Discover</Text>
            
            {/* Trip Planner Feature Card */}
            <TouchableOpacity 
              style={styles.featureCard}
              onPress={() => navigation.navigate('TripPlanner')}
            >
              <LinearGradient
                colors={['#667eea', '#764ba2']}
                style={styles.featureGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                <View style={styles.featureContent}>
                  <View style={styles.featureLeft}>
                    <Text style={styles.featureTitle}>Plan Your Trip</Text>
                    <Text style={styles.featureSubtitle}>
                      Smart packing lists based on your wardrobe
                    </Text>
                    <View style={styles.featureButton}>
                      <Text style={styles.featureButtonText}>Start Planning</Text>
                      <Ionicons name="arrow-forward" size={16} color="#fff" />
                    </View>
                  </View>
                  <View style={styles.featureRight}>
                    <Ionicons name="airplane" size={50} color="#fff" />
                  </View>
                </View>
              </LinearGradient>
            </TouchableOpacity>

            {/* AI Styling Feature Card */}
            <TouchableOpacity 
              style={styles.featureCard}
              onPress={() => handleGetOutfit()}
            >
              <LinearGradient
                colors={['#ffecd2', '#fcb69f']}
                style={styles.featureGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                <View style={styles.featureContent}>
                  <View style={styles.featureLeft}>
                    <Text style={[styles.featureTitle, { color: '#8B4513' }]}>AI Stylist</Text>
                    <Text style={[styles.featureSubtitle, { color: '#8B4513' }]}>
                      Get personalized outfit recommendations
                    </Text>
                    <View style={[styles.featureButton, { backgroundColor: '#8B4513' }]}>
                      <Text style={styles.featureButtonText}>Try Now</Text>
                      <Ionicons name="sparkles" size={16} color="#fff" />
                    </View>
                  </View>
                  <View style={styles.featureRight}>
                    <Ionicons name="color-wand" size={50} color="#8B4513" />
                  </View>
                </View>
              </LinearGradient>
            </TouchableOpacity>

            {/* Outfit History Feature Card */}
            <TouchableOpacity 
              style={styles.featureCard}
              onPress={() => navigation.navigate('OutfitHistory')}
            >
              <LinearGradient
                colors={['#a8edea', '#fed6e3']}
                style={styles.featureGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                <View style={styles.featureContent}>
                  <View style={styles.featureLeft}>
                    <Text style={[styles.featureTitle, { color: '#2D3436' }]}>Style History</Text>
                    <Text style={[styles.featureSubtitle, { color: '#636E72' }]}>
                      Track your outfits and style journey
                    </Text>
                    <View style={[styles.featureButton, { backgroundColor: '#2D3436' }]}>
                      <Text style={styles.featureButtonText}>View History</Text>
                      <Ionicons name="time" size={16} color="#fff" />
                    </View>
                  </View>
                  <View style={styles.featureRight}>
                    <Ionicons name="calendar" size={50} color="#2D3436" />
                  </View>
                </View>
              </LinearGradient>
            </TouchableOpacity>
          </View>

          {/* Debug Panel */}
          {__DEV__ && (
            <View style={styles.debugContainer}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>Debug Panel</Text>
              <View style={styles.debugButtons}>
                <TouchableOpacity 
                  style={styles.debugButton}
                  onPress={() => checkBackendStatus()}
                >
                  <Text style={styles.debugButtonText}>Check Backend</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={styles.debugButton}
                  onPress={() => addSampleWardrobe()}
                >
                  <Text style={styles.debugButtonText}>Add Sample Items</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          <View style={styles.bottomSpacing} />
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 20,
  },
  greeting: {
    fontSize: 16,
    opacity: 0.8,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 2,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectionStatus: {
    marginRight: 15,
  },
  connectionDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  notificationButton: {
    padding: 5,
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
  },
  weatherCard: {
    marginBottom: 25,
  },
  weatherGradient: {
    borderRadius: 16,
    padding: 20,
  },
  weatherContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  weatherLeft: {
    flex: 1,
  },
  weatherTemp: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  weatherDesc: {
    fontSize: 18,
    color: '#fff',
    marginBottom: 5,
  },
  weatherSuggestion: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
  },
  weatherRight: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  quickActionsContainer: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionCard: {
    width: (width - 60) / 2,
    padding: 20,
    borderRadius: 16,
    marginBottom: 15,
    alignItems: 'center',
  },
  quickActionIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  quickActionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
    textAlign: 'center',
  },
  quickActionSubtitle: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  insightsContainer: {
    marginBottom: 25,
  },
  insightsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  insightCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  insightCardLarge: {
    width: '100%',
    marginBottom: 15,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginLeft: 8,
  },
  insightTitleSmall: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginLeft: 6,
  },
  insightValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FF8C42',
    marginBottom: 5,
  },
  insightValueSmall: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    textTransform: 'capitalize',
  },
  insightSubtext: {
    fontSize: 14,
    color: '#666',
  },
  featuredContainer: {
    marginBottom: 25,
  },
  featureCard: {
    marginBottom: 15,
    borderRadius: 16,
    overflow: 'hidden',
  },
  featureGradient: {
    padding: 20,
  },
  featureContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  featureLeft: {
    flex: 1,
    paddingRight: 20,
  },
  featureTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  featureSubtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
    marginBottom: 15,
    lineHeight: 20,
  },
  featureButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  featureButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginRight: 6,
  },
  featureRight: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  debugContainer: {
    marginBottom: 25,
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
    padding: 15,
  },
  debugButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  debugButton: {
    backgroundColor: '#FF8C42',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 8,
    flex: 0.48,
  },
  debugButtonText: {
    color: '#fff',
    textAlign: 'center',
    fontWeight: '600',
  },
  bottomSpacing: {
    height: 20,
  },
});

export default HomeScreen;