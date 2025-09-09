// screens/OutfitHistoryScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  FlatList,
  Image,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import outfitHistoryService from '../services/outfitHistoryService';

const OutfitHistoryScreen = ({ navigation }) => {
  const [outfitHistory, setOutfitHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({});

  useEffect(() => {
    loadOutfitHistory();
  }, []);

  const loadOutfitHistory = async () => {
    try {
      setLoading(true);
      const response = await outfitHistoryService.getOutfitHistory(50);
      
      if (response.status === 'success') {
        setOutfitHistory(response.history || []);
        setStats(response.stats || {});
      } else {
        Alert.alert('Error', 'Failed to load outfit history');
      }
    } catch (error) {
      console.error('Error loading outfit history:', error);
      Alert.alert('Error', 'Failed to load outfit history');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadOutfitHistory();
    setRefreshing(false);
  };

  const handleRateOutfit = async (outfitId, rating) => {
    try {
      const result = await outfitHistoryService.rateOutfit(outfitId, rating);
      if (result.status === 'success') {
        // Refresh the list to show updated rating
        await loadOutfitHistory();
        Alert.alert('Success', 'Outfit rated successfully!');
      }
    } catch (error) {
      console.error('Error rating outfit:', error);
      Alert.alert('Error', 'Failed to rate outfit');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const renderStarsRating = (outfitId, currentRating = 0) => {
    return (
      <View style={styles.starsContainer}>
        {[1, 2, 3, 4, 5].map((star) => (
          <TouchableOpacity
            key={star}
            onPress={() => handleRateOutfit(outfitId, star)}
            style={styles.starButton}
          >
            <Ionicons
              name={star <= currentRating ? 'star' : 'star-outline'}
              size={16}
              color={star <= currentRating ? '#FFD700' : '#ccc'}
            />
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  const renderOutfitItem = ({ item }) => {
    const outfitData = item.outfit_data || {};
    const items = outfitData.items || [];
    
    return (
      <View style={styles.historyItem}>
        <View style={styles.historyHeader}>
          <View style={styles.dateContainer}>
            <Text style={styles.dateText}>{formatDate(item.worn_date)}</Text>
            {item.occasion && (
              <Text style={styles.occasionText}>{item.occasion}</Text>
            )}
          </View>
          <View style={styles.ratingContainer}>
            {renderStarsRating(item.id, item.rating)}
          </View>
        </View>

        <View style={styles.outfitItemsContainer}>
          {items.slice(0, 4).map((outfitItem, index) => (
            <View key={index} style={styles.outfitItemWrapper}>
              <Image
                source={{ uri: outfitItem.image_url }}
                style={styles.outfitItemImage}
                resizeMode="cover"
              />
              <Text style={styles.outfitItemName} numberOfLines={1}>
                {outfitItem.name || outfitItem.category}
              </Text>
            </View>
          ))}
          {items.length > 4 && (
            <View style={styles.moreItemsIndicator}>
              <Text style={styles.moreItemsText}>+{items.length - 4}</Text>
            </View>
          )}
        </View>

        <View style={styles.outfitDetails}>
          {item.weather && (
            <View style={styles.detailItem}>
              <Ionicons name="partly-sunny" size={14} color="#666" />
              <Text style={styles.detailText}>{item.weather}</Text>
            </View>
          )}
          {item.location && (
            <View style={styles.detailItem}>
              <Ionicons name="location" size={14} color="#666" />
              <Text style={styles.detailText}>{item.location}</Text>
            </View>
          )}
          {outfitData.confidence && (
            <View style={styles.detailItem}>
              <Ionicons name="trending-up" size={14} color="#666" />
              <Text style={styles.detailText}>{Math.round(outfitData.confidence)}% match</Text>
            </View>
          )}
        </View>

        {item.notes && (
          <Text style={styles.notesText}>{item.notes}</Text>
        )}
      </View>
    );
  };

  const renderStatsCard = () => (
    <View style={styles.statsCard}>
      <Text style={styles.statsTitle}>Your Style Stats</Text>
      <View style={styles.statsGrid}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.total_outfits || 0}</Text>
          <Text style={styles.statLabel}>Outfits</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.days_tracked || 0}</Text>
          <Text style={styles.statLabel}>Days</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.avg_rating ? stats.avg_rating.toFixed(1) : '0'}</Text>
          <Text style={styles.statLabel}>Avg Rating</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.liked_outfits || 0}</Text>
          <Text style={styles.statLabel}>Favorites</Text>
        </View>
      </View>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.title}>Outfit History</Text>
          <View style={{ width: 24 }} />
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FF8C42" />
          <Text style={styles.loadingText}>Loading your style history...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Outfit History</Text>
        <TouchableOpacity onPress={onRefresh}>
          <Ionicons name="refresh" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={outfitHistory}
        renderItem={renderOutfitItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListHeaderComponent={renderStatsCard}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="shirt" size={64} color="#ccc" />
            <Text style={styles.emptyTitle}>No Outfit History</Text>
            <Text style={styles.emptyText}>
              Start wearing AI-generated outfits to build your style history!
            </Text>
            <TouchableOpacity
              style={styles.generateButton}
              onPress={() => navigation.navigate('GetOutfit')}
            >
              <Text style={styles.generateButtonText}>Generate Outfit</Text>
            </TouchableOpacity>
          </View>
        }
      />
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
  title: {
    fontSize: 20,
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
  },
  statsCard: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF8C42',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  historyItem: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  dateContainer: {
    flex: 1,
  },
  dateText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  occasionText: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  ratingContainer: {
    alignItems: 'flex-end',
  },
  starsContainer: {
    flexDirection: 'row',
  },
  starButton: {
    padding: 2,
  },
  outfitItemsContainer: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  outfitItemWrapper: {
    marginRight: 10,
    alignItems: 'center',
    width: 60,
  },
  outfitItemImage: {
    width: 50,
    height: 50,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  outfitItemName: {
    fontSize: 10,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  moreItemsIndicator: {
    width: 50,
    height: 50,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  moreItemsText: {
    fontSize: 12,
    color: '#666',
    fontWeight: 'bold',
  },
  outfitDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 15,
    marginBottom: 5,
  },
  detailText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  notesText: {
    fontSize: 14,
    color: '#333',
    fontStyle: 'italic',
    backgroundColor: '#f8f9fa',
    padding: 10,
    borderRadius: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 10,
    marginHorizontal: 40,
  },
  generateButton: {
    backgroundColor: '#FF8C42',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default OutfitHistoryScreen;
