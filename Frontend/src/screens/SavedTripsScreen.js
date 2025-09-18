import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  RefreshControl,
  ScrollView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import tripService from '../services/tripService';

const SavedTripsScreen = ({ navigation }) => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      setLoading(true);
      console.log('Loading saved trips...');
      
      const userTrips = await tripService.getUserTrips();
      setTrips(userTrips);
      
      console.log('Loaded trips:', userTrips);
    } catch (error) {
      console.error('Error loading trips:', error);
      Alert.alert('Error', 'Failed to load saved trips');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTrips();
    setRefreshing(false);
  };

  const deleteTrip = async (tripId) => {
    Alert.alert(
      'Delete Trip',
      'Are you sure you want to delete this trip?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await tripService.deleteTrip(tripId);
              setTrips(trips.filter(trip => trip.id !== tripId));
              Alert.alert('Success', 'Trip deleted successfully');
            } catch (error) {
              console.error('Error deleting trip:', error);
              Alert.alert('Error', 'Failed to delete trip');
            }
          }
        }
      ]
    );
  };

  const viewTripDetails = (trip) => {
    const duration = getTripDuration(trip.start_date, trip.end_date);
    const packingStats = getPackingStats(trip.packing_list);
    
    let packingDetails = '';
    if (trip.packing_list && trip.packing_list.length > 0) {
      packingDetails = '\n\nPacking List:\n';
      trip.packing_list.forEach(category => {
        const categoryName = category.name || category.category || 'Category';
        const itemCount = category.items ? category.items.length : 0;
        packingDetails += `\n${categoryName}:\n`;
        
        if (category.items && category.items.length > 0) {
          category.items.forEach(item => {
            // Extract item name and quantity
            let itemName = item;
            let quantity = '';
            
            // Ensure item is a string before using match
            if (typeof item === 'string') {
              // Check if item has quantity in format "Item (quantity)" or "Item: quantity"
              const quantityMatch = item.match(/^(.+?)\s*[\(\:]?\s*(\d+)\s*[\)\s]*$/);
              if (quantityMatch) {
                itemName = quantityMatch[1].trim();
                quantity = ` (${quantityMatch[2]})`;
              } else {
                // If no quantity found, assume 1
                quantity = ' (1)';
              }
            } else if (typeof item === 'object' && item !== null) {
              // Handle if item is an object with name/quantity properties
              itemName = item.name || item.item || String(item);
              quantity = item.quantity ? ` (${item.quantity})` : ' (1)';
            } else {
              // Handle other types
              itemName = String(item);
              quantity = ' (1)';
            }
            
            packingDetails += `• ${itemName}${quantity}\n`;
          });
        } else {
          packingDetails += `• No items listed\n`;
        }
      });
    }
    
    Alert.alert(
      `${trip.destination} Trip`,
      `Duration: ${duration} days\nDates: ${formatDate(trip.start_date)} - ${formatDate(trip.end_date)}\nActivities: ${trip.activities?.join(', ') || 'None'}\nWeather: ${trip.weather_expected || 'Unknown'}\nPacking Style: ${trip.packing_style || 'Not specified'}\n\nPacking Summary:\n• ${packingStats.totalItems} total items\n• ${packingStats.categories} categories${packingDetails}`,
      [
        { text: 'Close', style: 'cancel' },
        { text: 'Edit Trip', onPress: () => {
          // Future enhancement: navigate to edit screen
          Alert.alert('Coming Soon', 'Trip editing will be available in a future update');
        }}
      ]
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const getTripDuration = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getPackingStats = (packingList) => {
    if (!packingList || !Array.isArray(packingList)) {
      return { totalItems: 0, categories: 0 };
    }

    let totalItems = 0;
    const categories = packingList.length;

    packingList.forEach(category => {
      if (category.items && Array.isArray(category.items)) {
        totalItems += category.items.length;
      }
    });

    return { totalItems, categories };
  };

  const renderTripItem = ({ item }) => {
    const duration = getTripDuration(item.start_date, item.end_date);
    const packingStats = getPackingStats(item.packing_list);
    
    return (
      <TouchableOpacity
        style={styles.tripCard}
        onPress={() => viewTripDetails(item)}
      >
        <View style={styles.tripHeader}>
          <View style={styles.tripInfo}>
            <Text style={styles.destination}>{item.destination}</Text>
            <Text style={styles.dates}>
              {formatDate(item.start_date)} - {formatDate(item.end_date)} ({duration} days)
            </Text>
            {item.activities && item.activities.length > 0 && (
              <Text style={styles.activities}>
                Activities: {item.activities.join(', ')}
              </Text>
            )}
            {item.weather_expected && (
              <Text style={styles.weather}>
                Weather: {item.weather_expected}
              </Text>
            )}
          </View>
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={() => deleteTrip(item.id)}
          >
            <Ionicons name="trash-outline" size={20} color="#ff4444" />
          </TouchableOpacity>
        </View>
        
        {/* Packing Statistics */}
        <View style={styles.packingStats}>
          <View style={styles.statItem}>
            <Ionicons name="bag-outline" size={16} color="#007AFF" />
            <Text style={styles.statText}>
              {packingStats.totalItems} items
            </Text>
          </View>
          <View style={styles.statItem}>
            <Ionicons name="grid-outline" size={16} color="#007AFF" />
            <Text style={styles.statText}>
              {packingStats.categories} categories
            </Text>
          </View>
          {item.packing_style && (
            <View style={styles.statItem}>
              <Ionicons name="star-outline" size={16} color="#007AFF" />
              <Text style={styles.statText}>
                {item.packing_style}
              </Text>
            </View>
          )}
        </View>
        
        {/* Detailed Packing Preview */}
        {item.packing_list && item.packing_list.length > 0 && (
          <View style={styles.packingPreview}>
            <Text style={styles.packingTitle}>Packing Items:</Text>
            {item.packing_list.map((category, categoryIndex) => (
              <View key={categoryIndex} style={styles.categorySection}>
                {category.name && (
                  <Text style={styles.categoryHeader}>{category.name}:</Text>
                )}
                {category.items && Array.isArray(category.items) ? (
                  <View style={styles.itemsContainer}>
                    {category.items.slice(0, 6).map((item, itemIndex) => {
                      // Extract item name and quantity
                      let itemName = item;
                      let quantity = '';
                      
                      // Ensure item is a string before using match
                      if (typeof item === 'string') {
                        // Check if item has quantity in format "Item (quantity)" or "Item: quantity"
                        const quantityMatch = item.match(/^(.+?)\s*[\(\:]?\s*(\d+)\s*[\)\s]*$/);
                        if (quantityMatch) {
                          itemName = quantityMatch[1].trim();
                          quantity = ` (${quantityMatch[2]})`;
                        } else {
                          // If no quantity found, assume 1
                          quantity = ' (1)';
                        }
                      } else if (typeof item === 'object' && item !== null) {
                        // Handle if item is an object with name/quantity properties
                        itemName = item.name || item.item || String(item);
                        quantity = item.quantity ? ` (${item.quantity})` : ' (1)';
                      } else {
                        // Handle other types
                        itemName = String(item);
                        quantity = ' (1)';
                      }
                      
                      return (
                        <Text key={itemIndex} style={styles.packingItem}>
                          {itemName}{quantity}
                        </Text>
                      );
                    })}
                    {category.items.length > 6 && (
                      <Text style={styles.moreItems}>
                        +{category.items.length - 6} more items
                      </Text>
                    )}
                  </View>
                ) : (
                  <Text style={styles.noItems}>No items listed</Text>
                )}
              </View>
            ))}
          </View>
        )}
        
        <View style={styles.tripFooter}>
          <Text style={styles.createdDate}>
            Saved: {formatDate(item.created_at)}
          </Text>
          <Ionicons name="chevron-forward" size={16} color="#888" />
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.navigate('Home')}
          >
            <Ionicons name="arrow-back" size={24} color="#007AFF" />
          </TouchableOpacity>
          <Text style={styles.title}>Saved Trips</Text>
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading your trips...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => {
            console.log('SavedTrips - Navigating back to Home');
            navigation.navigate('Home');
          }}
        >
          <Ionicons name="arrow-back" size={24} color="#007AFF" />
        </TouchableOpacity>
        <Text style={styles.title}>Saved Trips</Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={onRefresh}
        >
          <Ionicons name="refresh" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      {trips.length === 0 ? (
        <ScrollView
          contentContainerStyle={styles.emptyContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          <Ionicons name="airplane-outline" size={80} color="#ccc" />
          <Text style={styles.emptyTitle}>No Saved Trips</Text>
          <Text style={styles.emptySubtitle}>
            Start planning your first trip to see it here!
          </Text>
          <TouchableOpacity
            style={styles.planTripButton}
            onPress={() => navigation.navigate('TripPlanner')}
          >
            <Text style={styles.planTripButtonText}>Plan a Trip</Text>
          </TouchableOpacity>
        </ScrollView>
      ) : (
        <FlatList
          data={trips}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderTripItem}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          showsVerticalScrollIndicator={false}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    padding: 8,
  },
  refreshButton: {
    padding: 8,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
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
    padding: 20,
    paddingBottom: 100,
  },
  tripCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tripHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  tripInfo: {
    flex: 1,
  },
  destination: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  dates: {
    fontSize: 14,
    color: '#007AFF',
    marginBottom: 4,
  },
  activities: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  weather: {
    fontSize: 12,
    color: '#666',
  },
  deleteButton: {
    padding: 8,
  },
  packingStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#f8f9fa',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    fontSize: 12,
    color: '#333',
    marginLeft: 4,
    fontWeight: '500',
  },
  packingPreview: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 12,
    marginBottom: 12,
  },
  packingTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  categorySection: {
    marginBottom: 8,
  },
  categoryHeader: {
    fontSize: 13,
    fontWeight: '600',
    color: '#555',
    marginBottom: 4,
  },
  itemsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  packingItem: {
    fontSize: 12,
    color: '#666',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
    overflow: 'hidden',
  },
  moreItems: {
    fontSize: 11,
    color: '#999',
    fontStyle: 'italic',
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  noItems: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  categoryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  categoryName: {
    fontSize: 12,
    color: '#666',
    flex: 1,
  },
  categoryCount: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
  },
  moreCategories: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
    marginTop: 4,
  },
  packingItems: {
    fontSize: 12,
    color: '#666',
    lineHeight: 18,
  },
  tripFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 12,
  },
  createdDate: {
    fontSize: 12,
    color: '#999',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 10,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
  },
  planTripButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  planTripButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default SavedTripsScreen;
