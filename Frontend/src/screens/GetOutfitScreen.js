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
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Location from 'expo-location';
import apiService from '../services/apiService';
import outfitHistoryService from '../services/outfitHistoryService';
import favoriteOutfitService from '../services/favoriteOutfitService';

const GetOutfitScreen = ({ navigation }) => {
  const [currentOutfit, setCurrentOutfit] = useState(null);
  const [loading, setLoading] = useState(false);
  const [regeneratingItem, setRegeneratingItem] = useState(null); // Track which item is being regenerated
  const [weatherInfo, setWeatherInfo] = useState(null);
  const [occasion, setOccasion] = useState('casual');
  const [location, setLocation] = useState(null);
  const [locationPermission, setLocationPermission] = useState(null);

  const occasions = [
    { id: 'casual', name: 'Casual', icon: 'shirt' },
    { id: 'work', name: 'Work', icon: 'briefcase' },
    { id: 'formal', name: 'Formal', icon: 'business' },
    { id: 'workout', name: 'Workout', icon: 'fitness' },
    { id: 'date', name: 'Date Night', icon: 'heart' },
  ];

  // Mock weather data - replace with actual weather API
  const mockWeatherData = {
    temperature: 22,
    condition: 'sunny',
    description: 'Sunny',
    humidity: 45,
    windSpeed: 15,
  };

  // Mock outfit data
  const mockOutfits = {
    casual: {
      id: '1',
      items: [
        {
          id: 'top1',
          name: 'White Cotton T-Shirt',
          category: 'Top',
          image: 'https://via.placeholder.com/150',
        },
        {
          id: 'bottom1',
          name: 'Blue Denim Jeans',
          category: 'Bottom',
          image: 'https://via.placeholder.com/150',
        },
        {
          id: 'shoes1',
          name: 'White Sneakers',
          category: 'Shoes',
          image: 'https://via.placeholder.com/150',
        },
      ],
      confidence: 92,
      reason: 'Perfect for comfortable daily activities with sunny weather',
    },
    work: {
      id: '2',
      items: [
        {
          id: 'top2',
          name: 'Blue Button Shirt',
          category: 'Top',
          image: 'https://via.placeholder.com/150',
        },
        {
          id: 'bottom2',
          name: 'Black Formal Pants',
          category: 'Bottom',
          image: 'https://via.placeholder.com/150',
        },
        {
          id: 'shoes2',
          name: 'Black Formal Shoes',
          category: 'Shoes',
          image: 'https://via.placeholder.com/150',
        },
      ],
      confidence: 88,
      reason: 'Professional look suitable for office meetings',
    },
  };

  useEffect(() => {
    requestLocationPermission();
    // Set immediate fallback outfit for testing
    setCurrentOutfit(mockOutfits.casual);
    setWeatherInfo(mockWeatherData);
    // Then try to get real outfit
    generateOutfit();
  }, []);

  useEffect(() => {
    generateOutfit();
  }, [occasion]);

  const requestLocationPermission = async () => {
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      setLocationPermission(status);
      
      if (status === 'granted') {
        let locationData = await Location.getCurrentPositionAsync({});
        setLocation({
          latitude: locationData.coords.latitude,
          longitude: locationData.coords.longitude,
        });
      } else {
        // Use default location if permission denied
        setLocation({
          latitude: 37.7749, // San Francisco default
          longitude: -122.4194,
        });
      }
    } catch (error) {
      console.error('Error requesting location permission:', error);
      // Fallback to default location
      setLocation({
        latitude: 37.7749,
        longitude: -122.4194,
      });
    }
  };

  const fetchWeatherInfo = () => {
    // In a real app, you'd fetch from a weather API
    setWeatherInfo(mockWeatherData);
  };

// Update the generateOutfit function in your GetOutfitScreen.js

const generateOutfit = async () => {
  setLoading(true);
  
  try {
    // Use default location if not available
    const locationData = location || {
      latitude: 37.7749,
      longitude: -122.4194,
    };
    
    console.log('Starting outfit generation...', { locationData, occasion });
    
    // Call your AI recommendation endpoint using apiService
    const data = await apiService.post('/api/outfit/ai-recommendation', {
      user_id: 1, // Replace with actual user ID from your auth system
      location: {
        latitude: locationData.latitude,
        longitude: locationData.longitude
      },
      occasion: occasion
    });
    
    console.log('API Response:', data); // For debugging
    
    if (data.status === 'success' && data.outfit && !data.outfit.error) {
      console.log('Setting outfit from API:', data.outfit);
      setCurrentOutfit(data.outfit);
      setWeatherInfo(data.weather);
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
              setWeatherInfo(mockWeatherData);
            }},
            { text: 'OK', style: 'cancel' }
          ]
        );
      } else {
        console.log('No outfit data available, using fallback');
        setCurrentOutfit(mockOutfits[occasion] || mockOutfits.casual);
        setWeatherInfo(mockWeatherData);
      }
    }
  } catch (error) {
    console.error('Outfit generation error:', error);
    console.log('Using fallback outfit due to error');
    
    // Always show fallback instead of alert for now
    setCurrentOutfit(mockOutfits[occasion] || mockOutfits.casual);
    setWeatherInfo(mockWeatherData);
    
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
        weatherInfo?.condition || mockWeatherData.condition,
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
                weather_context: weatherInfo || mockWeatherData
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
        <Ionicons name="sunny" size={24} color="#FFD700" />
        <Text style={styles.temperature}>{weatherInfo?.temperature}°C</Text>
        <Text style={styles.weatherDescription}>{weatherInfo?.description}</Text>
      </View>
      <Text style={styles.weatherDetails}>
        Humidity: {weatherInfo?.humidity}% • Wind: {weatherInfo?.windSpeed} km/h
      </Text>
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
        <TouchableOpacity onPress={generateOutfit}>
          <Ionicons name="refresh" size={24} color="#FF8C42" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {weatherInfo && renderWeatherCard()}
        
        {renderOccasionSelector()}

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FF8C42" />
            <Text style={styles.loadingText}>Generating your perfect outfit...</Text>
          </View>
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
    backgroundColor: '#f8f9ff',
    margin: 20,
    padding: 15,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#FF8C42',
  },
  weatherInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
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
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 10,
  },
  selectedOccasionButton: {
    backgroundColor: '#FF8C42',
  },
  occasionButtonText: {
    color: '#666',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 5,
  },
  selectedOccasionButtonText: {
    color: '#fff',
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
    backgroundColor: '#FF8C42',
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
    backgroundColor: '#f9f9f9',
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
  backgroundColor: '#666',
  flexDirection: 'row',
  justifyContent: 'center',
  alignItems: 'center',
  paddingVertical: 12,
  borderRadius: 8,
  marginRight: 5,
},
favoriteButton: {
  flex: 1,
  backgroundColor: '#9b59b6',
  flexDirection: 'row',
  justifyContent: 'center',
  alignItems: 'center',
  paddingVertical: 12,
  borderRadius: 8,
  marginLeft: 5,
},
likeButton: {
  flex: 1,
  backgroundColor: '#e74c3c',
  flexDirection: 'row',
  justifyContent: 'center',
  alignItems: 'center',
  paddingVertical: 12,
  borderRadius: 8,
  marginRight: 5,
},
wearButton: {
  flex: 1,
  backgroundColor: '#27ae60',
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
    backgroundColor: '#FF8C42',
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
    backgroundColor: '#FF8C42',
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
});

export default GetOutfitScreen;