// screens/GetOutfitScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  Image,
  Alert,
  ScrollView,
  ActivityIndicator,
  TextInput,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Location from 'expo-location';
import apiService from '../services/apiService';
import outfitHistoryService from '../services/outfitHistoryService';
import favoriteOutfitService from '../services/favoriteOutfitService';
import weatherService from '../services/weatherService';

const GetOutfitScreen = ({ navigation }) => {
  const [currentOutfit, setCurrentOutfit] = useState(null);
  const [multiOutfits, setMultiOutfits] = useState(null); // New state for multiple recommendations
  const [showMultiView, setShowMultiView] = useState(false); // Toggle between single and multi view
  const [loading, setLoading] = useState(false);
  const [regeneratingItem, setRegeneratingItem] = useState(null); // Track which item is being regenerated
  const [weatherInfo, setWeatherInfo] = useState(null);
  const [occasion, setOccasion] = useState('casual');
  const [location, setLocation] = useState(null);
  const [locationPermission, setLocationPermission] = useState(null);
  
  // Demo weather feature
  const [demoMode, setDemoMode] = useState(false);
  const [demoTemperature, setDemoTemperature] = useState('25');
  const [demoCondition, setDemoCondition] = useState('sunny');

  const occasions = [
    { id: 'casual', name: 'Casual', icon: 'shirt' },
    { id: 'work', name: 'Work', icon: 'briefcase' },
    { id: 'formal', name: 'Formal', icon: 'business' },
    { id: 'workout', name: 'Workout', icon: 'fitness' },
    { id: 'date', name: 'Date Night', icon: 'heart' },
  ];

  // Loading weather data
  const defaultWeatherData = {
    temperature: null,
    condition: 'loading',
    description: 'Loading weather...',
    humidity: null,
    windSpeed: null,
    location: 'Getting location...'
  };

 

  useEffect(() => {
    requestLocationPermission();
    // Set immediate fallback outfit for testing
    setCurrentOutfit(mockOutfits.casual);
    // Weather will be loaded when location is obtained
    // Then try to get real outfit
    generateOutfit();
  }, []);

  useEffect(() => {
    generateOutfit();
  }, [occasion]);

  useEffect(() => {
    if (location) {
      fetchWeatherInfo();
    }
  }, [location]);

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
          'Location permission is required for accurate weather-based outfit recommendations. Using Galle as default location.',
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
        'Unable to get your GPS location. Using Galle as default for outfit recommendations.',
        [{ text: 'OK' }]
      );
    }
  };

  const fetchWeatherInfo = async () => {
    if (location && location.latitude && location.longitude) {
      try {
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
          
          setWeatherInfo({
            temperature: weatherData.current.temperature,
            condition: weatherData.current.condition,
            humidity: weatherData.current.humidity,
            windSpeed: weatherData.current.windSpeed,
            precipitation: weatherData.current.precipitation,
            location: cityName || weatherData.current.location?.name || 'Current Location',
            icon: weatherData.current.icon,
          });
        } else {
          // Fallback to loading state if API fails
          setWeatherInfo(defaultWeatherData);
        }
      } catch (error) {
        console.error('Error fetching weather:', error);
        // Fallback to loading state if API fails
        setWeatherInfo(defaultWeatherData);
      }
    } else {
      // Use loading state if no location available
      setWeatherInfo(defaultWeatherData);
    }
  };

// Update the generateOutfit function in your GetOutfitScreen.js

const generateOutfit = async () => {
  setLoading(true);
  
  try {
    let requestData;
    
    if (demoMode) {
      // Demo mode: use manual temperature input
      console.log('Demo mode: Using manual weather input', { 
        temperature: demoTemperature, 
        condition: demoCondition,
        occasion 
      });
      
      requestData = {
        user_id: 1,
        demo_weather: {
          temperature: parseInt(demoTemperature),
          condition: demoCondition,
          humidity: 60, // Default demo values
          windSpeed: 10,
          precipitation: 0,
          location: 'Demo Location'
        },
        occasion: occasion
      };
      
      // Update weather info immediately for demo
      setWeatherInfo({
        temperature: parseInt(demoTemperature),
        condition: demoCondition,
        humidity: 60,
        windSpeed: 10,
        precipitation: 0,
        location: 'Demo Mode',
        icon: getWeatherIcon(demoCondition)
      });
      
    } else {
      // Real weather mode: use GPS location
      const locationData = location || {
        latitude: 37.7749,
        longitude: -122.4194,
      };
      
      console.log('Real weather mode: Using GPS location', { locationData, occasion });
      
      requestData = {
        user_id: 1,
        location: {
          latitude: locationData.latitude,
          longitude: locationData.longitude
        },
        occasion: occasion
      };
    }
    
    // Call your AI recommendation endpoint using apiService
    const data = await apiService.post('/api/outfit/ai-recommendation', requestData);
    
    console.log('API Response:', data); // For debugging
    
    if (data.status === 'success' && data.outfit && !data.outfit.error) {
      console.log('Setting outfit from API:', data.outfit);
      setCurrentOutfit(data.outfit);
      
      // Fix weather data location to be a string instead of object
      const weatherData = {
        ...data.weather,
        location: data.weather?.location?.name || data.weather?.location || 'Current Location'
      };
      setWeatherInfo(weatherData);
    } else {
      // Handle case where user has no wardrobe items
      if (data.outfit?.error) {
        console.log('API returned error:', data.outfit);
        Alert.alert(
          'Wardrobe Empty', 
          data.outfit.message || 'Please add some clothes to your wardrobe first!',
          [
            { text: 'Add Clothes', onPress: () => navigation.navigate('AddClothes') },
            { text: 'Use Demo Outfit', onPress: () => {
              setCurrentOutfit(mockOutfits[occasion] || mockOutfits.casual);
              // Keep current weather info (don't override with mock data)
            }},
            { text: 'OK', style: 'cancel' }
          ]
        );
      } else {
        console.log('No outfit data available, using fallback');
        setCurrentOutfit(mockOutfits[occasion] || mockOutfits.casual);
        // Keep current weather info (don't override with mock data)
      }
    }
  } catch (error) {
    console.error('Outfit generation error:', error);
    console.log('Using fallback outfit due to error');
    
    // Always show fallback instead of alert for now
    setCurrentOutfit(mockOutfits[occasion] || mockOutfits.casual);
    // Keep current weather info (don't override with mock data)
    
    // Optional: show alert only if you want to notify user
    // Alert.alert(
    //   'Connection Error', 
    //   'Could not connect to AI service. Showing demo outfit.',
    //   [{ text: 'OK' }]
    // );
  } finally {
    setLoading(false);
  }
};

// New function to generate multi-occasion recommendations
const generateMultiOutfits = async () => {
  setLoading(true);
  
  try {
    let requestData;
    
    if (demoMode) {
      requestData = {
        user_id: 1,
        demo_weather: {
          temperature: parseInt(demoTemperature),
          condition: demoCondition,
          humidity: 60,
          windSpeed: 10,
          precipitation: 0,
          location: 'Demo Location'
        },
        occasions: ['casual', 'work', 'formal', 'workout', 'datenight']
      };
    } else {
      requestData = {
        user_id: 1,
        location: location ? {
          latitude: location.latitude,
          longitude: location.longitude
        } : {
          latitude: 40.7128,
          longitude: -74.0060
        },
        occasions: ['casual', 'work', 'formal', 'workout', 'datenight']
      };
    }
    
    console.log('Generating multi-occasion outfits:', requestData);
    
    const data = await apiService.post('/api/outfit/enhanced-recommendations', requestData);
    
    console.log('Multi-outfit API Response:', data);
    
    if (data.status === 'success' && data.recommendations) {
      console.log('Setting multi outfits from API:', data.recommendations);
      setMultiOutfits(data);
      setShowMultiView(true);
      
      // Set weather info
      if (data.weather) {
        const weatherData = {
          ...data.weather,
          location: data.weather?.location || 'Current Location'
        };
        setWeatherInfo(weatherData);
      }
    } else {
      // Fallback to mock data
      console.log('Using fallback multi outfits');
      const fallbackMultiOutfits = {
        status: 'success',
        recommendations: {
          casual: mockOutfits.casual,
          work: mockOutfits.work,
          formal: { ...mockOutfits.work, confidence: 85, reason: 'Perfect for formal events' },
          workout: { ...mockOutfits.casual, confidence: 90, reason: 'Great for gym and exercise' },
          datenight: { ...mockOutfits.work, confidence: 88, reason: 'Stylish choice for romantic dinner' }
        },
        wardrobe_analysis: {
          total_items: 15,
          occasion_readiness: {
            casual: { confidence: 92, status: 'excellent' },
            work: { confidence: 88, status: 'good' },
            formal: { confidence: 85, status: 'good' },
            workout: { confidence: 90, status: 'excellent' },
            datenight: { confidence: 88, status: 'good' }
          }
        }
      };
      setMultiOutfits(fallbackMultiOutfits);
      setShowMultiView(true);
    }
  } catch (error) {
    console.error('Multi-outfit generation error:', error);
    
    // Show fallback multi outfits
    const fallbackMultiOutfits = {
      status: 'success',
      recommendations: {
        casual: mockOutfits.casual,
        work: mockOutfits.work,
        formal: { ...mockOutfits.work, confidence: 85, reason: 'Perfect for formal events' },
        workout: { ...mockOutfits.casual, confidence: 90, reason: 'Great for gym and exercise' },
        datenight: { ...mockOutfits.work, confidence: 88, reason: 'Stylish choice for romantic dinner' }
      },
      wardrobe_analysis: {
        total_items: 15,
        occasion_readiness: {
          casual: { confidence: 92, status: 'excellent' },
          work: { confidence: 88, status: 'good' },
          formal: { confidence: 85, status: 'good' },
          workout: { confidence: 90, status: 'excellent' },
          datenight: { confidence: 88, status: 'good' }
        }
      }
    };
    setMultiOutfits(fallbackMultiOutfits);
    setShowMultiView(true);
  } finally {
    setLoading(false);
  }
};

const getWeatherIcon = (condition) => {
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
    return 'cloud';
  } else if (conditionLower.includes('loading')) {
    return 'hourglass-outline';
  } else {
    return 'partly-sunny';
  }
};

const getCityNameFromCoordinates = (lat, lon) => {
  // Define Sri Lankan cities with their approximate coordinates
  const cities = [
    { name: 'Galle', lat: 6.0535, lon: 80.2210, radius: 0.1 },
    { name: 'Colombo', lat: 6.9271, lon: 79.8612, radius: 0.15 },
    { name: 'Kandy', lat: 7.2966, lon: 80.6350, radius: 0.1 },
    { name: 'Jaffna', lat: 9.6615, lon: 80.0255, radius: 0.1 },
    { name: 'Negombo', lat: 7.2084, lon: 79.8380, radius: 0.08 },
    { name: 'Matara', lat: 5.9549, lon: 80.5550, radius: 0.08 },
    { name: 'Batticaloa', lat: 7.7102, lon: 81.6924, radius: 0.1 },
    { name: 'Trincomalee', lat: 8.5874, lon: 81.2152, radius: 0.1 },
    { name: 'Anuradhapura', lat: 8.3114, lon: 80.4037, radius: 0.1 },
    { name: 'Polonnaruwa', lat: 7.9403, lon: 81.0188, radius: 0.1 },
    { name: 'Ratnapura', lat: 6.6828, lon: 80.4034, radius: 0.1 },
    { name: 'Badulla', lat: 6.9934, lon: 81.0550, radius: 0.1 },
    { name: 'Kurunegala', lat: 7.4818, lon: 80.3609, radius: 0.1 },
  ];

  // Find the closest city within radius
  for (const city of cities) {
    const distance = Math.sqrt(
      Math.pow(lat - city.lat, 2) + Math.pow(lon - city.lon, 2)
    );
    if (distance <= city.radius) {
      return city.name;
    }
  }

  // If no exact match found, return null to use API location
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

const regenerateItem = async (itemCategory) => {
  if (!currentOutfit) return;
  
  try {
    setRegeneratingItem(itemCategory);
    
    // Find the current item in this category to exclude it
    const currentItem = currentOutfit.items ? 
      currentOutfit.items.find(item => 
        item.category && item.category.toLowerCase() === itemCategory.toLowerCase()
      ) : null;
    
    const requestData = {
      current_outfit: currentOutfit,
      item_category: itemCategory,
      current_item_id: currentItem ? currentItem.id : null, // Add current item ID
      occasion: occasion,
      user_id: 1,
      user_preferences: {
        occasion: occasion,
        weather: weatherInfo?.condition || 'mild',
        style: 'casual'
      }
    };
    
    console.log('Regenerating item:', itemCategory, 'Current item ID:', currentItem?.id, requestData);
    
    const response = await apiService.post('/api/outfit/regenerate-item', requestData);
    
    if (response && response.status === 'success') {
      setCurrentOutfit(response.outfit);
      
      // Show more detailed success message
      const newItemName = response.replaced_item?.new_item || 'new item';
      const alternativesCount = response.replaced_item?.alternatives_available || 0;
      
      Alert.alert(
        'Item Updated!', 
        `New ${itemCategory}: ${newItemName}${alternativesCount > 0 ? ` (${alternativesCount} more alternatives available)` : ''}`,
        [{ text: 'OK' }]
      );
    } else {
      Alert.alert('Error', response.message || 'Failed to regenerate item');
    }
  } catch (error) {
    console.error('Error regenerating item:', error);
    Alert.alert('Error', 'Failed to regenerate item. Please try again.');
  } finally {
    setRegeneratingItem(null);
  }
};

const handleLikeOutfit = async () => {
  if (!currentOutfit) return;
  
  try {
    await apiService.post('/api/outfit/feedback', {
      user_id: 1,
      outfit_id: currentOutfit.id,
      feedback_type: 'like',
      weather_data: weatherInfo,
      occasion: occasion
    });
    
    Alert.alert('Outfit Liked!', 'Thanks for the feedback! Our AI will learn from your preferences.');
  } catch (error) {
    console.error('Feedback error:', error);
  }
};
  const handleDislikeOutfit = () => {
    generateOutfit(); // Generate a new outfit
  };

  const handleWearOutfit = async () => {
    if (!currentOutfit || !currentOutfit.items) {
      Alert.alert('Error', 'No outfit to record');
      return;
    }

    try {
      setLoading(true);
      
      // Get current location for context (optional)
      let location = null;
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const locationData = await Location.getCurrentPositionAsync({});
          const reverseGeocode = await Location.reverseGeocodeAsync({
            latitude: locationData.coords.latitude,
            longitude: locationData.coords.longitude,
          });
          
          if (reverseGeocode.length > 0) {
            const address = reverseGeocode[0];
            location = `${address.city || ''}, ${address.region || ''}`.trim().replace(/^,|,$/, '');
          }
        }
      } catch (locationError) {
        console.log('Could not get location:', locationError);
      }

      // Format outfit data for storage
      const outfitData = outfitHistoryService.formatOutfitForStorage(
        currentOutfit.items,
        occasion,
        currentOutfit.confidence
      );

      // Record the worn outfit using the outfit history service
      const result = await outfitHistoryService.recordWornOutfit(
        outfitData,
        occasion,
        weatherInfo?.condition || defaultWeatherData.condition,
        location,
        new Date().toISOString().split('T')[0] // Today's date in YYYY-MM-DD format
      );

      if (result && result.status === 'success') {
        Alert.alert(
          'Outfit Recorded!',
          `This outfit has been saved to your history for today.`,
          [
            { text: 'View History', onPress: () => navigation.navigate('WornOutfits') },
            { text: 'Generate New Outfit', onPress: generateOutfit },
            { text: 'OK', style: 'default' }
          ]
        );
      } else {
        throw new Error(result?.message || 'Failed to record outfit');
      }
    } catch (error) {
      console.error('Error recording outfit:', error);
      Alert.alert(
        'Error',
        'Failed to record outfit. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSaveFavorite = async () => {
    if (!currentOutfit || !currentOutfit.items) {
      Alert.alert('Error', 'No outfit to save as favorite');
      return;
    }

    Alert.prompt(
      'Save as Favorite',
      'Give this outfit a name:',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Save',
          onPress: async (outfitName) => {
            if (!outfitName || outfitName.trim() === '') {
              outfitName = `Outfit ${new Date().toLocaleDateString()}`;
            }

            try {
              setLoading(true);

              const outfitData = {
                items: currentOutfit.items,
                occasion: occasion,
                confidence: currentOutfit.confidence,
                reason: currentOutfit.reason,
                weather_context: weatherInfo || defaultWeatherData
              };

              const result = await favoriteOutfitService.saveFavorite(
                1, // user_id
                outfitData,
                outfitName.trim()
              );

              if (result && result.success) {
                Alert.alert(
                  'Saved!',
                  `"${outfitName}" has been saved to your favorites.`,
                  [
                    { text: 'View Favorites', onPress: () => navigation.navigate('FavoriteOutfits') },
                    { text: 'OK', style: 'default' }
                  ]
                );
              } else {
                throw new Error(result?.message || 'Failed to save favorite');
              }
            } catch (error) {
              console.error('Error saving favorite:', error);
              Alert.alert(
                'Error',
                'Failed to save outfit as favorite. Please try again.', 
                [{ text: 'OK' }]
              );
            } finally {
              setLoading(false);
            }
          },
        },
      ],
      'plain-text',
      `Outfit ${new Date().toLocaleDateString()}`
    );
  };

  const renderOccasionSelector = () => (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false}
      style={styles.occasionSelector}
      contentContainerStyle={styles.occasionSelectorContent}
    >
      {occasions.map((occ) => (
        <TouchableOpacity
          key={occ.id}
          style={[
            styles.occasionButton,
            occasion === occ.id && styles.selectedOccasionButton
          ]}
          onPress={() => setOccasion(occ.id)}
        >
          <Ionicons 
            name={occ.icon} 
            size={20} 
            color={occasion === occ.id ? '#fff' : '#666'} 
          />
          <Text style={[
            styles.occasionButtonText,
            occasion === occ.id && styles.selectedOccasionButtonText
          ]}>
            {occ.name}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  const renderWeatherCard = () => (
    <View style={styles.weatherCard}>
      <View style={styles.weatherInfo}>
        <Ionicons 
          name={getWeatherIcon(weatherInfo?.condition)} 
          size={24} 
          color="#FFD700" 
        />
        <Text style={styles.temperature}>
          {weatherInfo?.temperature ? `${weatherInfo.temperature}°C` : 'Loading...'}
        </Text>
        <Text style={styles.weatherDescription}>
          {weatherInfo?.description || 'Loading weather...'}
        </Text>
        <TouchableOpacity 
          style={styles.weatherRefreshButton} 
          onPress={() => {
            console.log('Refreshing GPS location and weather...');
            requestLocationPermission();
          }}
        >
          <Ionicons name="refresh" size={16} color="#666" />
        </TouchableOpacity>
      </View>
      <Text style={styles.weatherDetails}>
        {weatherInfo?.location && (
          <>📍 {weatherInfo.location} • </>
        )}
        {weatherInfo?.humidity ? `Humidity: ${weatherInfo.humidity}%` : 'Loading humidity...'} • {weatherInfo?.windSpeed ? `Wind: ${weatherInfo.windSpeed} km/h` : 'Loading wind...'}
      </Text>
    </View>
  );

  const renderDemoControls = () => (
    <View style={styles.demoCard}>
      <View style={styles.demoHeader}>
        <Text style={styles.demoTitle}>Weather Mode</Text>
        <View style={styles.demoToggle}>
          <Text style={[styles.demoModeText, !demoMode && styles.activeModeText]}>
            Real Weather
          </Text>
          <Switch
            value={demoMode}
            onValueChange={setDemoMode}
            trackColor={{ false: '#81b0ff', true: '#8A724C' }}
            thumbColor={demoMode ? '#fff' : '#B99668'}
          />
          <Text style={[styles.demoModeText, demoMode && styles.activeModeText]}>
            Demo Mode
          </Text>
        </View>
      </View>
      
      {demoMode && (
        <View style={styles.demoInputs}>
          <View style={styles.demoRow}>
            <Text style={styles.demoLabel}>Temperature (°C):</Text>
            <TextInput
              style={styles.demoInput}
              value={demoTemperature}
              onChangeText={setDemoTemperature}
              keyboardType="numeric"
              placeholder="25"
            />
          </View>
          
          <View style={styles.demoRow}>
            <Text style={styles.demoLabel}>Weather Condition:</Text>
            <View style={styles.conditionButtons}>
              {['sunny', 'cloudy', 'rainy', 'cold'].map((condition) => (
                <TouchableOpacity
                  key={condition}
                  style={[
                    styles.conditionButton,
                    demoCondition === condition && styles.selectedConditionButton
                  ]}
                  onPress={() => setDemoCondition(condition)}
                >
                  <Text style={[
                    styles.conditionText,
                    demoCondition === condition && styles.selectedConditionText
                  ]}>
                    {condition.charAt(0).toUpperCase() + condition.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
          
          <TouchableOpacity 
            style={styles.demoGenerateButton} 
            onPress={generateOutfit}
          >
            <Text style={styles.demoGenerateButtonText}>
              Generate with Demo Weather
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );

  const renderOutfitItems = () => (
    <View style={styles.outfitContainer}>
      <Text style={styles.outfitTitle}>Today's Recommendation</Text>
      
      {currentOutfit && (
        <>
          <View style={styles.confidenceContainer}>
            <Text style={styles.confidenceText}>
              {currentOutfit.confidence}% match confidence
            </Text>
            <View style={styles.confidenceBar}>
              <View 
                style={[
                  styles.confidenceFill, 
                  { width: `${currentOutfit.confidence}%` }
                ]} 
              />
            </View>
          </View>

          <View style={styles.itemsContainer}>
            {currentOutfit.items && currentOutfit.items.map((item, index) => (
              <View key={item.id || index} style={styles.outfitItemRow}>
                <View style={styles.itemDisplayContainer}>
                  <Image 
                    source={{ uri: item.image_path ? `http://172.20.10.7:8000${item.image_path}` : 'https://via.placeholder.com/150' }} 
                    style={styles.itemImage} 
                  />
                  <View style={styles.itemDetails}>
                    <Text style={styles.itemName}>{item.name}</Text>
                    <Text style={styles.itemCategory}>{item.category}</Text>
                    {item.color && (
                      <Text style={styles.itemColor}>Color: {item.color}</Text>
                    )}
                    {item.brand && (
                      <Text style={styles.itemBrand}>{item.brand}</Text>
                    )}
                  </View>
                </View>
                
                <TouchableOpacity 
                  style={[
                    styles.retryItemButton,
                    regeneratingItem === item.category && styles.buttonDisabled
                  ]}
                  onPress={() => regenerateItem(item.category)}
                  disabled={regeneratingItem === item.category || loading}
                >
                  {regeneratingItem === item.category ? (
                    <ActivityIndicator size="small" color="#fff" />
                  ) : (
                    <Ionicons name="refresh" size={16} color="#fff" />
                  )}
                  <Text style={styles.retryItemText}>
                    {regeneratingItem === item.category ? 'Finding...' : `Try Another`}
                  </Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>

          <View style={styles.reasonContainer}>
            <Text style={styles.reasonTitle}>Why this outfit?</Text>
            <Text style={styles.reasonText}>{currentOutfit.reason}</Text>
          </View>
        </>
      )}
    </View>
  );


  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Get Outfit</Text>
        <View style={styles.headerActions}>

          <TouchableOpacity onPress={showMultiView ? generateMultiOutfits : generateOutfit}>
            <Ionicons name="refresh" size={24} color="#DCC9A7" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.content}>
        {weatherInfo && renderWeatherCard()}
        
        {!showMultiView && renderDemoControls()}
        
        {!showMultiView && renderOccasionSelector()}

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FF8C42" />
            <Text style={styles.loadingText}>
              {showMultiView ? 'Generating outfits for all occasions...' : 'Generating your perfect outfit...'}
            </Text>
          </View>
        ) : showMultiView ? (
          renderMultiOutfitView()
        ) : currentOutfit ? (
          renderOutfitItems()
        ) : (
          <View style={styles.emptyContainer}>
            <Ionicons name="shirt-outline" size={64} color="#ccc" />
            <Text style={styles.emptyTitle}>No Outfit Generated</Text>
            <Text style={styles.emptyText}>Tap the refresh button to get outfit suggestions</Text>
            <TouchableOpacity style={styles.generateButton} onPress={generateOutfit}>
              <Text style={styles.generateButtonText}>Generate Outfit</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>

      {!loading && currentOutfit && (
  <View style={styles.actionButtons}>
    <View style={styles.buttonRow}>
      <TouchableOpacity 
        style={styles.dislikeButton} 
        onPress={handleDislikeOutfit}
      >
        <Ionicons name="thumbs-down" size={20} color="#fff" />
        <Text style={styles.buttonText}>Try Again</Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.favoriteButton} 
        onPress={handleSaveFavorite}
      >
        <Ionicons name="heart-outline" size={20} color="#fff" />
        <Text style={styles.buttonText}>Favorite</Text>
      </TouchableOpacity>
    </View>
    
    <View style={styles.buttonRow}>
      <TouchableOpacity 
        style={styles.likeButton} 
        onPress={handleLikeOutfit}
      >
        <Ionicons name="heart" size={20} color="#fff" />
        <Text style={styles.buttonText}>Save</Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.wearButton} 
        onPress={handleWearOutfit}
      >
        <Ionicons name="checkmark" size={20} color="#fff" />
        <Text style={styles.buttonText}>Wear This</Text>
      </TouchableOpacity>
    </View>
  </View>
)}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  content: {
    flex: 1,
  },
  weatherCard: {
    backgroundColor: '#F7F3E8',
    margin: 20,
    padding: 15,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#8A724C',
  },
  weatherInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    position: 'relative',
  },
  weatherRefreshButton: {
    position: 'absolute',
    right: 0,
    padding: 5,
    backgroundColor: 'rgba(0,0,0,0.05)',
    borderRadius: 15,
  },
  temperature: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 10,
  },
  weatherDescription: {
    fontSize: 16,
    color: '#666',
    marginLeft: 10,
    flex: 1,
  },
  weatherDetails: {
    fontSize: 14,
    color: '#666',
  },
  occasionSelector: {
    maxHeight: 60,
  },
  occasionSelectorContent: {
    paddingHorizontal: 20,
  },
  occasionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F7F3E8',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 10,
  },
  selectedOccasionButton: {
    backgroundColor: '#DCC9A7',
  },
  occasionButtonText: {
    color: '#666',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 5,
  },
  selectedOccasionButtonText: {
    color: 'black',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  outfitContainer: {
    margin: 20,
  },
  outfitTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  confidenceContainer: {
    marginBottom: 20,
  },
  confidenceText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  confidenceBar: {
    height: 6,
    backgroundColor: '#f0f0f0',
    borderRadius: 3,
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#B99668',
    borderRadius: 3,
  },
  itemsContainer: {
    flexDirection: 'column',
    marginBottom: 20,
  },
  outfitItemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    paddingVertical: 10,
    marginBottom: 10,
    backgroundColor: 'white',
    borderRadius: 10,
  },
  itemDisplayContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  outfitItem: {
    alignItems: 'center',
    flex: 1,
  },
  itemImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    marginRight: 12,
  },
  itemDetails: {
    flex: 1,
  },
  itemName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  itemCategory: {
    fontSize: 12,
    color: '#666',
    marginBottom: 1,
  },
  itemColor: {
    fontSize: 11,
    color: '#888',
    marginBottom: 1,
  },
  itemBrand: {
    fontSize: 11,
    color: '#888',
    fontStyle: 'italic',
  },
  reasonContainer: {
    backgroundColor: '#f8f8f8',
    padding: 15,
    borderRadius: 10,
  },
  reasonTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  reasonText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  actionButtons: {
  paddingHorizontal: 20,
  paddingVertical: 15,
  borderTopWidth: 1,
  borderTopColor: '#f0f0f0',
},
buttonRow: {
  flexDirection: 'row',
  marginBottom: 10,
},
dislikeButton: {
  flex: 1,
  backgroundColor: '#B99668',
  flexDirection: 'row',
  justifyContent: 'center',
  alignItems: 'center',
  paddingVertical: 12,
  borderRadius: 8,
  marginRight: 5,
},
favoriteButton: {
  flex: 1,
  backgroundColor: '#B99668',
  flexDirection: 'row',
  justifyContent: 'center',
  alignItems: 'center',
  paddingVertical: 12,
  borderRadius: 8,
  marginLeft: 5,
},
likeButton: {
  flex: 1,
  backgroundColor: '#B99668',
  flexDirection: 'row',
  justifyContent: 'center',
  alignItems: 'center',
  paddingVertical: 12,
  borderRadius: 8,
  marginRight: 5,
},
wearButton: {
  flex: 1,
  backgroundColor: '#B99668',
  flexDirection: 'row',
  justifyContent: 'center',
  alignItems: 'center',
  paddingVertical: 12,
  borderRadius: 8,
  marginLeft: 5,
},
  buttonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 5,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 24,
  },
  generateButton: {
    backgroundColor: '#8A724C',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 25,
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  retryItemButton: {
    backgroundColor: '#8A724C',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 100,
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  retryItemText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
    marginLeft: 4,
  },
  // Demo controls styles
  demoCard: {
    backgroundColor: '#f8f9fa',
    margin: 15,
    padding: 15,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  demoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  demoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#B99668',
  },
  demoToggle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  demoModeText: {
    fontSize: 12,
    color: '#666',
    marginHorizontal: 8,
  },
  activeModeText: {
    color: '#8A724C',
    fontWeight: '600',
  },
  demoInputs: {
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
    paddingTop: 15,
  },
  demoRow: {
    marginBottom: 15,
  },
  demoLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  demoInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  conditionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  conditionButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: '#fff',
  },
  selectedConditionButton: {
    backgroundColor: '#DCC9A7',
    borderColor: '#B99668',
  },
  conditionText: {
    fontSize: 14,
    color: 'black',
  },
  selectedConditionText: {
    color: 'black',
    fontWeight: '600',
  },
  demoGenerateButton: {
    backgroundColor: '#DCC9A7',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  demoGenerateButtonText: {
    color: 'black',
    fontSize: 16,
    fontWeight: '600',
  },
  // Header actions styles
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  viewToggle: {
    padding: 8,
    marginRight: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#FF8C42',
  },
  activeViewToggle: {
    backgroundColor: '#FF8C42',
  },
  // Multi-outfit view styles
  multiOutfitContainer: {
    padding: 15,
  },
  multiOutfitTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  analysisCard: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },
  analysisTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  analysisText: {
    fontSize: 12,
    color: '#666',
  },
  occasionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  occasionCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 2,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  occasionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  occasionName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
  occasionContent: {
    padding: 12,
  },
  confidenceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  confidenceLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  statusBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  statusText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  outfitPreview: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 8,
  },
  previewItem: {
    alignItems: 'center',
    flex: 1,
  },
  previewImage: {
    width: 30,
    height: 30,
    borderRadius: 6,
    backgroundColor: '#f0f0f0',
    marginBottom: 4,
  },
  previewItemText: {
    fontSize: 10,
    color: '#666',
    textAlign: 'center',
  },
  outfitReason: {
    fontSize: 11,
    color: '#888',
    lineHeight: 14,
  },
  errorContent: {
    alignItems: 'center',
    paddingVertical: 10,
  },
  errorText: {
    fontSize: 11,
    color: '#E74C3C',
    textAlign: 'center',
    marginTop: 5,
  },
});

export default GetOutfitScreen;