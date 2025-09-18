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
import * as Location from 'expo-location';
import { useTheme } from '../themes/ThemeProvider';
import wardrobeService from '../services/wardrobeService';
import connectionService from '../services/connectionService';
import weatherService from '../services/weatherService';

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
    temperature: null,
    condition: null,
    description: 'Loading weather...',
    humidity: null,
    location: 'Getting location...'
  });
  const [backendConnected, setBackendConnected] = useState(false);
  const [location, setLocation] = useState(null);
  const [locationPermission, setLocationPermission] = useState(null);

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
    requestLocationPermission();
  }, []);

  useEffect(() => {
    if (location) {
      loadTodayWeather();
    }
  }, [location]);

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

  const getCityNameFromCoordinates = (lat, lon) => {
    // Define Sri Lankan cities with their approximate coordinates and smaller radius for accuracy
    const cities = [
      { name: 'Galle', lat: 6.0535, lon: 80.2210, radius: 0.05 }, // ~5.5km radius
      { name: 'Colombo', lat: 6.9271, lon: 79.8612, radius: 0.08 }, // Larger radius for metro area
      { name: 'Kandy', lat: 7.2966, lon: 80.6350, radius: 0.05 },
      { name: 'Jaffna', lat: 9.6615, lon: 80.0255, radius: 0.05 },
      { name: 'Negombo', lat: 7.2084, lon: 79.8380, radius: 0.04 },
      { name: 'Matara', lat: 5.9549, lon: 80.5550, radius: 0.04 },
      { name: 'Batticaloa', lat: 7.7102, lon: 81.6924, radius: 0.05 },
      { name: 'Trincomalee', lat: 8.5874, lon: 81.2152, radius: 0.05 },
      { name: 'Anuradhapura', lat: 8.3114, lon: 80.4037, radius: 0.05 },
      { name: 'Polonnaruwa', lat: 7.9403, lon: 81.0188, radius: 0.05 },
      { name: 'Ratnapura', lat: 6.6828, lon: 80.4034, radius: 0.05 },
      { name: 'Badulla', lat: 6.9934, lon: 81.0550, radius: 0.05 },
      { name: 'Kurunegala', lat: 7.4818, lon: 80.3609, radius: 0.05 },
      // Add more suburbs/towns around Galle for better detection
      { name: 'Unawatuna', lat: 6.0100, lon: 80.2500, radius: 0.02 },
      { name: 'Hikkaduwa', lat: 6.1410, lon: 80.1019, radius: 0.02 },
      { name: 'Bentota', lat: 6.4200, lon: 79.9956, radius: 0.02 },
      { name: 'Mirissa', lat: 5.9486, lon: 80.4572, radius: 0.02 },
      { name: 'Weligama', lat: 5.9748, lon: 80.4295, radius: 0.02 },
    ];

    // Sort by distance and return the closest city within radius
    const cityDistances = cities.map(city => ({
      ...city,
      distance: Math.sqrt(
        Math.pow(lat - city.lat, 2) + Math.pow(lon - city.lon, 2)
      )
    }));

    // Sort by distance (closest first)
    cityDistances.sort((a, b) => a.distance - b.distance);

    // Return the closest city if it's within its radius
    const closestCity = cityDistances[0];
    if (closestCity && closestCity.distance <= closestCity.radius) {
      console.log(`Detected city: ${closestCity.name} (distance: ${(closestCity.distance * 111).toFixed(1)}km)`);
      return closestCity.name;
    }

    console.log('No city detected within radius, closest was:', closestCity?.name, 'at', (closestCity?.distance * 111).toFixed(1), 'km');
    return null;
  };

  const getAccurateCityName = async (latitude, longitude) => {
    try {
      console.log('Getting accurate city name for coordinates:', latitude, longitude);
      
      // Try OpenStreetMap Nominatim API (free reverse geocoding)
      try {
        const nominatimUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=14&addressdetails=1`;
        
        const response = await fetch(nominatimUrl, {
          headers: {
            'User-Agent': 'StyraApp/1.0', // Required by Nominatim
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('Nominatim reverse geocoding result:', data);
          
          if (data.address) {
            // Try to get the most appropriate city/town name
            const cityName = data.address.city || 
                            data.address.town || 
                            data.address.village || 
                            data.address.suburb ||
                            data.address.municipality ||
                            data.address.county ||
                            data.address.state_district;
            
            if (cityName) {
              console.log('Found city via Nominatim:', cityName);
              return cityName;
            }
          }
        }
      } catch (error) {
        console.log('Nominatim API failed:', error.message);
      }
      
      // Fallback to Expo Location reverse geocoding
      try {
        const reverseGeocode = await Location.reverseGeocodeAsync({
          latitude,
          longitude,
        });

        if (reverseGeocode && reverseGeocode.length > 0) {
          const location = reverseGeocode[0];
          console.log('Expo reverse geocoding result:', location);
          
          const cityName = location.city || 
                          location.subregion || 
                          location.district || 
                          location.region || 
                          location.name;
          
          if (cityName) {
            console.log('Found city via Expo reverse geocoding:', cityName);
            return cityName;
          }
        }
      } catch (error) {
        console.log('Expo reverse geocoding failed:', error.message);
      }
      
      // Final fallback to coordinate-based detection
      return getCityNameFromCoordinates(latitude, longitude);
      
    } catch (error) {
      console.error('All reverse geocoding methods failed:', error);
      return getCityNameFromCoordinates(latitude, longitude);
    }
  };

  const loadTodayWeather = async () => {
    if (location && location.latitude && location.longitude) {
      try {
        console.log('Loading real weather data for location:', location);
        const weatherData = await weatherService.getCurrentWeather(
          location.latitude, 
          location.longitude
        );
        
        if (weatherData.status === 'success' && weatherData.current) {
          // Try to get accurate city name using reverse geocoding
          let cityName = null;
          try {
            cityName = await getAccurateCityName(location.latitude, location.longitude);
          } catch (error) {
            console.log('Reverse geocoding failed, using coordinate-based detection');
            cityName = getCityNameFromCoordinates(location.latitude, location.longitude);
          }
          
          setTodayWeather({
            temperature: weatherData.current.temperature,
            condition: weatherData.current.condition ? weatherData.current.condition.toLowerCase() : 'unknown',
            description: weatherData.current.condition || 'Weather data unavailable',
            humidity: weatherData.current.humidity,
            windSpeed: weatherData.current.windSpeed,
            location: cityName || weatherData.current.location?.name || 'Current Location'
          });
          console.log('Real weather data loaded for', cityName || 'unknown location');
        } else {
          // Keep loading state if API fails
          console.log('Weather API returned no data, keeping loading state');
        }
      } catch (error) {
        console.error('Error loading real weather:', error);
        // Keep loading state if API fails
        console.log('Weather API failed, keeping loading state');
      }
    } else {
      // Keep loading state if no location available
      console.log('No location available, keeping loading state');
    }
  };

  const requestLocationPermission = async () => {
    try {
      console.log('Requesting location permission and GPS coordinates...');
      
      // Request location permission
      let { status } = await Location.requestForegroundPermissionsAsync();
      setLocationPermission(status);
      
      if (status === 'granted') {
        console.log('Location permission granted, getting GPS coordinates...');
        
        // Use high accuracy location settings with extended timeout
        let locationData = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.BestForNavigation, // Highest accuracy
          timeout: 25000, // 25 seconds timeout for better GPS lock
          maximumAge: 5000, // Don't use cached data older than 5 seconds
        });

        console.log('GPS coordinates obtained:', {
          latitude: locationData.coords.latitude,
          longitude: locationData.coords.longitude,
          accuracy: locationData.coords.accuracy + 'm',
          timestamp: new Date(locationData.timestamp).toLocaleString()
        });

        // Try multiple readings for better accuracy if the first one is poor
        if (locationData.coords.accuracy > 100) { // If accuracy is poor (>100m)
          console.log('GPS accuracy is poor, attempting second reading...');
          await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds
          
          try {
            let betterLocation = await Location.getCurrentPositionAsync({
              accuracy: Location.Accuracy.BestForNavigation,
              timeout: 20000,
              maximumAge: 1000,
            });
            
            if (betterLocation.coords.accuracy < locationData.coords.accuracy) {
              locationData = betterLocation;
              console.log('Used improved GPS reading with accuracy:', betterLocation.coords.accuracy + 'm');
            }
          } catch (error) {
            console.log('Second GPS reading failed, using first reading');
          }
        }

        setLocation({
          latitude: locationData.coords.latitude,
          longitude: locationData.coords.longitude,
        });

      } else {
        console.log('Location permission denied, using fallback location for Galle');
        // Use Galle coordinates as fallback
        setLocation({
          latitude: 6.0535, // Galle, Sri Lanka
          longitude: 80.2210,
        });
        
        Alert.alert(
          'Location Access Denied',
          'Location permission is required for accurate weather. Using Galle as default location.',
          [
            { text: 'OK' },
            { 
              text: 'Enable Location', 
              onPress: () => {
                // Try to request permission again
                requestLocationPermission();
              }
            }
          ]
        );
      }
    } catch (error) {
      console.error('Error with GPS location:', error);
      // Fallback to Galle coordinates
      setLocation({
        latitude: 6.0535, // Galle, Sri Lanka
        longitude: 80.2210,
      });
      
      Alert.alert(
        'GPS Error',
        'Unable to get your GPS location. Using Galle as default.',
        [{ text: 'OK' }]
      );
    }
  };  const getWeatherIcon = (condition) => {
    if (!condition) return 'help-circle-outline';
    
    const conditionLower = String(condition).toLowerCase();
    if (conditionLower.includes('sun') || conditionLower.includes('clear')) {
      return 'sunny';
    } else if (conditionLower.includes('cloud') || conditionLower.includes('overcast')) {
      return 'cloudy';
    } else if (conditionLower.includes('rain') || conditionLower.includes('shower') || conditionLower.includes('drizzle')) {
      return 'rainy';
    } else if (conditionLower.includes('snow')) {
      return 'snow';
    } else if (conditionLower.includes('thunder') || conditionLower.includes('storm')) {
      return 'thunderstorm';
    } else if (conditionLower.includes('fog') || conditionLower.includes('mist')) {
      return 'cloudy';
    } else if (conditionLower.includes('partly')) {
      return 'partly-sunny';
    } else if (conditionLower.includes('loading')) {
      return 'hourglass-outline';
    } else {
      return 'partly-sunny';
    }
  };

  const getWeatherOutfitSuggestion = () => {
    if (!todayWeather.temperature) {
      return 'Loading weather-based suggestions...';
    }
    
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
    },
    {
      id: 'saved-trips',
      title: 'Saved Trips',
      subtitle: 'Your trip history',
      icon: 'airplane',
      color: '#3498db',
      onPress: () => navigation.navigate('SavedTrips')
    },
    {
      id: 'favorites',
      title: 'Favorites',
      subtitle: 'Saved outfits',
      icon: 'heart',
      color: '#9b59b6',
      onPress: () => {
        console.log('Navigating to FavoriteOutfits screen');
        navigation.navigate('FavoriteOutfits');
      }
    },
    {
      id: 'worn-outfits',
      title: 'Worn Outfits',
      subtitle: 'Outfit history',
      icon: 'checkmark-circle',
      color: '#2ecc71',
      onPress: () => {
        console.log('Navigating to WornOutfits screen');
        navigation.navigate('WornOutfits');
      }
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
                  <Text style={styles.weatherTemp}>
                    {todayWeather.temperature ? `${todayWeather.temperature}°C` : 'Loading...'}
                  </Text>
                  <Text style={styles.weatherDesc}>{todayWeather.description}</Text>
                  {todayWeather.location && (
                    <Text style={styles.weatherLocation}>{todayWeather.location}</Text>
                  )}
                  <Text style={styles.weatherSuggestion}>{getWeatherOutfitSuggestion()}</Text>
                </View>
                <View style={styles.weatherRight}>
                  <View style={styles.weatherIconContainer}>
                    <Ionicons 
                      name={getWeatherIcon(todayWeather.condition)} 
                      size={60} 
                      color="#fff" 
                    />
                    <TouchableOpacity 
                      style={styles.refreshButton} 
                      onPress={() => {
                        console.log('Refreshing GPS location and weather...');
                        requestLocationPermission();
                      }}
                    >
                      <Ionicons name="refresh" size={20} color="#fff" />
                    </TouchableOpacity>
                  </View>
                  {todayWeather.humidity && (
                    <Text style={styles.weatherHumidity}>{todayWeather.humidity}% humidity</Text>
                  )}
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

            {/* Worn Outfits Feature Card */}
            <TouchableOpacity 
              style={styles.featureCard}
              onPress={() => navigation.navigate('WornOutfits')}
            >
              <LinearGradient
                colors={['#a8edea', '#fed6e3']}
                style={styles.featureGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                <View style={styles.featureContent}>
                  <View style={styles.featureLeft}>
                    <Text style={[styles.featureTitle, { color: '#2D3436' }]}>Worn Outfits</Text>
                    <Text style={[styles.featureSubtitle, { color: '#636E72' }]}>
                      View your outfit history with dates
                    </Text>
                    <View style={[styles.featureButton, { backgroundColor: '#2D3436' }]}>
                      <Text style={styles.featureButtonText}>View History</Text>
                      <Ionicons name="checkmark-circle" size={16} color="#fff" />
                    </View>
                  </View>
                  <View style={styles.featureRight}>
                    <Ionicons name="calendar" size={50} color="#2D3436" />
                  </View>
                </View>
              </LinearGradient>
            </TouchableOpacity>
          </View>
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
  weatherLocation: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.8,
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
  weatherIconContainer: {
    alignItems: 'center',
    position: 'relative',
  },
  refreshButton: {
    position: 'absolute',
    top: -5,
    right: -10,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 15,
    padding: 5,
    marginTop: 5,
  },
  weatherHumidity: {
    fontSize: 10,
    color: '#fff',
    opacity: 0.8,
    marginTop: 5,
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
    width: '100%', // Make the card full width
    alignSelf: 'center',
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