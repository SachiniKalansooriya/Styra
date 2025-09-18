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
      
      if (response && response.status === 'success') {
        console.log('Worn outfits loaded successfully:', response.history?.length);
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

  const renderWornOutfitItem = ({ item }) => {
    console.log('Rendering outfit item:', JSON.stringify(item, null, 2));
    console.log('Outfit data items:', item.outfit_data?.items);
    console.log('Outfit data structure:', typeof item.outfit_data, item.outfit_data);
    
    return (
      <View style={styles.outfitCard}>
        <View style={styles.outfitHeader}>
          <Text style={styles.outfitDate}>{formatDate(item.worn_date)}</Text>
          <Text style={styles.outfitOccasion}>{item.occasion || 'Casual'}</Text>
        </View>
        
        <View style={styles.outfitItemsContainer}>
          {item.outfit_data && item.outfit_data.items && item.outfit_data.items.length > 0 ? (
            item.outfit_data.items.map((clothingItem, index) => (
              <View key={index} style={styles.clothingItem}>
                <View style={styles.circularImageContainer}>
                  <Image 
                    source={{ 
                      uri: (() => {
                        const imageUrl = clothingItem.image_path || clothingItem.image_url;
                        if (!imageUrl) return 'https://via.placeholder.com/100';
                        if (imageUrl.startsWith('http')) return imageUrl;
                        return `http://172.20.10.7:8000${imageUrl}`;
                      })()
                    }} 
                    style={styles.circularImage} 
                    onError={() => console.log('Image failed to load:', clothingItem.image_path || clothingItem.image_url)}
                  />
                </View>
                <Text style={styles.clothingName} numberOfLines={2}>
                  {clothingItem.name || clothingItem.item || 'Unknown Item'}
                </Text>
              </View>
            ))
          ) : (
            <Text style={styles.noItemsText}>No items found for this outfit</Text>
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
    backgroundColor: '#fff',
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
    backgroundColor: '#fff',
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
    color: '#FF8C42',
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
  noItemsText: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: 20,
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
    color: '#FF8C42',
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
