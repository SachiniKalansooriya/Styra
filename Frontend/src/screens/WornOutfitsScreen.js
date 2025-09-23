// screens/WornOutfitsScreen.js
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
  ActivityIndicator,
  FlatList,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import outfitHistoryService from '../services/outfitHistoryService';
import API_CONFIG from '../config/api';

const WornOutfitsScreen = ({ navigation }) => {
  const [wornOutfits, setWornOutfits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadWornOutfits();
    
    // Add a focus listener to reload data when the screen is focused
    if (navigation.addListener) {
      const unsubscribe = navigation.addListener('focus', () => {
        console.log('WornOutfits screen focused - reloading data');
        loadWornOutfits();
      });
      
      // Cleanup on unmount
      return unsubscribe;
    }
  }, [navigation]);

  const loadWornOutfits = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Loading worn outfits history...');
      
      const response = await outfitHistoryService.getOutfitHistory(50);
      console.log('Raw outfit history service response:', response);

      if (response && response.status === 'success') {
        console.log('Worn outfits loaded successfully:', response.history?.length);
        
        // Enhanced logging for debugging
        response.history?.forEach((outfit, index) => {
          console.log(`Outfit ${index}:`, {
            id: outfit.id,
            worn_date: outfit.worn_date,
            image_url: outfit.image_url,
            image_path: outfit.image_path,
            outfit_data_structure: outfit.outfit_data ? Object.keys(outfit.outfit_data) : 'null',
            items_count: outfit.outfit_data?.items?.length || 0,
            first_item: outfit.outfit_data?.items?.[0] || 'no items'
          });
        });
        
        setWornOutfits(response.history || []);
      } else {
        throw new Error(response?.message || 'Failed to load outfit history');
      }
    } catch (error) {
      console.error('Error loading worn outfits:', error);
      setError('Failed to load outfit history. Please try again.');
      Alert.alert('Error', 'Failed to load worn outfits history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadWornOutfits();
    setRefreshing(false);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      month: 'short', 
      day: 'numeric',
      year: 'numeric' 
    });
  };

  const getImageUri = (clothingItem, fallbackItem = null) => {
    const base = API_CONFIG.primary || 'http://localhost:8000';
    
    // Try multiple sources in order of preference
    const imageSources = [
      clothingItem?.image_url,
      clothingItem?.image_path, 
      clothingItem?.imageUrl,
      clothingItem?.imageUri,
      clothingItem?.image,
      clothingItem?.path,
      clothingItem?.uri,
      clothingItem?.src,
      clothingItem?.photo,
      clothingItem?.picture,
      fallbackItem?.image_url,
      fallbackItem?.image_path
    ];
    
    console.log('Image sources for item:', imageSources.filter(Boolean));
    
    for (const source of imageSources) {
      if (source && typeof source === 'string' && source.trim()) {
        console.log('Processing image source:', source);
        
        if (source.match(/^https?:\/\//i)) {
          console.log('Using absolute URL:', source);
          return source;
        } else if (source.startsWith('/')) {
          const fullUrl = `${base}${source}`;
          console.log('Using relative URL:', fullUrl);
          return fullUrl;
        } else {
          const fullUrl = `${base}/${source}`.replace(/([^:\/])\/\//g, '$1/');
          console.log('Using constructed URL:', fullUrl);
          return fullUrl;
        }
      }
    }
    
    const placeholder = 'https://via.placeholder.com/100?text=No+Image';
    console.log('Using placeholder:', placeholder);
    return placeholder;
  };

  const renderWornOutfitItem = ({ item }) => {
    console.log('Rendering outfit item:', {
      id: item.id,
      worn_date: item.worn_date,
      image_url: item.image_url,
      image_path: item.image_path,
      items_count: item.outfit_data?.items?.length || 0
    });
    
    return (
      <View style={styles.outfitCard}>
        <View style={styles.outfitHeader}>
          <Text style={styles.outfitDate}>{formatDate(item.worn_date)}</Text>
          <Text style={styles.outfitOccasion}>{item.occasion || 'Casual'}</Text>
        </View>
        
        <View style={styles.outfitItemsContainer}>
          {item.outfit_data && item.outfit_data.items && item.outfit_data.items.length > 0 ? (
            item.outfit_data.items.map((clothingItem, index) => {
              const resolvedUri = getImageUri(clothingItem, item);
              
              console.log(`Item ${index} resolved URI:`, resolvedUri);
              console.log(`Item ${index} data:`, clothingItem);

              return (
                <View key={index} style={styles.clothingItem}>
                  <View style={styles.circularImageContainer}>
                    <Image
                      source={{ uri: resolvedUri }}
                      style={styles.circularImage}
                      onError={(e) => {
                        console.log('Image failed to load:', resolvedUri);
                        console.log('Error details:', e.nativeEvent);
                      }}
                      onLoad={() => {
                        console.log('Image loaded successfully:', resolvedUri);
                      }}
                      onLoadStart={() => {
                        console.log('Image load started:', resolvedUri);
                      }}
                    />
                  </View>
                  <Text style={styles.clothingName} numberOfLines={2}>
                    {clothingItem.name || clothingItem.item || clothingItem.title || 'Unknown Item'}
                  </Text>
                </View>
              );
            })
          ) : (
            <View style={styles.noItemsContainer}>
              <Text style={styles.noItemsText}>No items found for this outfit</Text>
              <Text style={styles.debugText}>
                Debug: outfit_data = {item.outfit_data ? 'exists' : 'null'}, 
                items = {item.outfit_data?.items ? `array[${item.outfit_data.items.length}]` : 'null'}
              </Text>
            </View>
          )}
        </View>
        
        {item.weather && (
          <View style={styles.weatherContainer}>
            <Ionicons 
              name={getWeatherIcon(item.weather)} 
              size={16} 
              color="#666" 
            />
            <Text style={styles.weatherText}>{item.weather}</Text>
          </View>
        )}
        
        {item.location && (
          <View style={styles.locationContainer}>
            <Ionicons name="location" size={16} color="#666" />
            <Text style={styles.locationText}>{item.location}</Text>
          </View>
        )}
        
        {item.outfit_data && item.outfit_data.confidence && (
          <View style={styles.confidenceContainer}>
            <Text style={styles.confidenceText}>
              {item.outfit_data.confidence}% match
            </Text>
          </View>
        )}
        
        {/* Debug information - remove in production */}
        <View style={styles.debugContainer}>
          <Text style={styles.debugText}>
            Debug: ID={item.id}, Items={item.outfit_data?.items?.length || 0}, 
            Image={item.image_path ? 'has path' : 'no path'}
          </Text>
        </View>
      </View>
    );
  };

  const getWeatherIcon = (weather) => {
    const weatherLower = String(weather).toLowerCase();
    if (weatherLower.includes('sun') || weatherLower.includes('clear')) {
      return 'sunny';
    } else if (weatherLower.includes('cloud') || weatherLower.includes('overcast')) {
      return 'cloudy';
    } else if (weatherLower.includes('rain') || weatherLower.includes('shower')) {
      return 'rainy';
    } else if (weatherLower.includes('snow')) {
      return 'snow';
    } else if (weatherLower.includes('thunder') || weatherLower.includes('storm')) {
      return 'thunderstorm';
    } else {
      return 'partly-sunny';
    }
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="calendar-outline" size={80} color="#ccc" />
      <Text style={styles.emptyTitle}>No Worn Outfits</Text>
      <Text style={styles.emptyText}>
        When you wear an outfit, it will appear here with the date and occasion.
      </Text>
      <TouchableOpacity 
        style={styles.getOutfitButton}
        onPress={() => navigation.navigate('GetOutfit')}
      >
        <Text style={styles.getOutfitButtonText}>Generate an Outfit</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Worn Outfits</Text>
        <View style={styles.placeholder} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FF8C42" />
          <Text style={styles.loadingText}>Loading outfit history...</Text>
        </View>
      ) : (
        <FlatList
          data={wornOutfits}
          renderItem={renderWornOutfitItem}
          keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
          contentContainerStyle={wornOutfits.length === 0 ? styles.emptyList : styles.listContainer}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={renderEmptyState}
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    paddingTop: 25, // Extra padding for status bar
    backgroundColor: '#F7F3E8',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  placeholder: {
    width: 24,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  listContainer: {
    padding: 15,
  },
  emptyList: {
    flex: 1,
  },
  outfitCard: {
    backgroundColor: '#F7F3E8',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  outfitHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  outfitDate: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  outfitOccasion: {
    fontSize: 16,
    color: '#8A724C',
    fontWeight: '500',
  },
  outfitItemsContainer: {
    flexDirection: 'row',
    marginBottom: 15,
    flexWrap: 'wrap',
    paddingHorizontal: 5,
  },
  clothingItem: {
    alignItems: 'center',
    marginRight: 15,
    marginBottom: 10,
    width: 80,
  },
  circularImageContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    overflow: 'hidden',
    backgroundColor: '#f0f0f0',
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  circularImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  clothingName: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    fontWeight: '500',
  },
  noItemsContainer: {
    flex: 1,
    paddingVertical: 20,
  },
  noItemsText: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  debugContainer: {
    marginTop: 10,
    padding: 8,
    backgroundColor: '#e9ecef',
    borderRadius: 4,
  },
  debugText: {
    fontSize: 10,
    color: '#6c757d',
    fontFamily: 'monospace',
  },
  weatherContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  weatherText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 5,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  locationText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 5,
  },
  confidenceContainer: {
    alignSelf: 'flex-end',
  },
  confidenceText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8A724C',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333',
    marginTop: 20,
    marginBottom: 10,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
  },
  getOutfitButton: {
    backgroundColor: '#FF8C42',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  getOutfitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default WornOutfitsScreen;