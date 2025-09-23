// src/screens/MyWardrobeScreen.js
import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
  RefreshControl,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useTheme } from '../themes/ThemeProvider';
import { storage } from '../utils/storage';
import wardrobeService from '../services/wardrobeService';

const MyWardrobeScreen = ({ navigation, backendConnected }) => {
  const { theme } = useTheme();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState(null);
  useEffect(() => {
    loadWardrobe();
  }, []);

  // In wardrobeService.js
  const loadUserAndWardrobe = async () => {
    try {
      // Get user data from storage
      const userData = await storage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        setUserId(user.id);
        await loadWardrobe(user.id);
      } else {
        console.error('No user data found');
        // Redirect to login or handle unauthenticated state
        navigation.navigate('Login');
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const loadWardrobe = async (user_id = null) => {
    try {
      setLoading(true);
      // Pass user_id if available
      const wardrobeItems = await wardrobeService.getWardrobeItems(user_id);
      
      if (Array.isArray(wardrobeItems)) {
        setItems(wardrobeItems);
      } else {
        console.warn('Expected array but got:', typeof wardrobeItems, wardrobeItems);
        setItems([]);
      }
    } catch (error) {
      console.error('Error loading wardrobe:', error);
      setItems([]);
      Alert.alert('Error', 'Failed to load wardrobe items');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadWardrobe(userId);
    setRefreshing(false);
  };

  const deleteItem = async (itemId) => {
    Alert.alert(
      'Delete Item',
      'Are you sure you want to delete this clothing item?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await storage.deleteWardrobeItem(itemId);
              await loadWardrobe(); // Reload the list
              Alert.alert('Success', 'Item deleted successfully');
            } catch (error) {
              Alert.alert('Error', 'Failed to delete item');
            }
          }
        }
      ]
    );
  };

  const renderItem = (item) => {
    // Get the image URI - prioritize backend image_url, then fall back to local imageData
    const getImageUri = () => {
      // Check if we have a backend-provided image URL
      if (item.image_url && !item.image_url.startsWith('file://')) {
        // Backend provided image URL - construct full URL
        const apiUrl = 'http://172.20.10.7:8000'; // Match the primary API URL
        if (item.image_url.startsWith('http')) {
          return item.image_url; // Already full URL
        } else {
          return `${apiUrl}${item.image_url}`; // Relative URL, add base
        }
      } else if (item.imageData?.localUri && !item.imageData.localUri.startsWith('file:///var/mobile')) {
        // Local image data (for offline items) - but not mobile container paths
        return item.imageData.localUri;
      }
      // Skip file:// URLs from mobile containers as they're not accessible
      return null;
    };

    const imageUri = getImageUri();

    return (
      <View key={item.id} style={[styles.itemCard, { backgroundColor: 'rgba(255,255,255,0.1)' }]}>
        {imageUri ? (
          <Image 
            source={{ uri: imageUri }} 
            style={styles.itemImage} 
            onError={(error) => {
              console.log('Image load error for:', imageUri, error);
            }}
            onLoad={() => {
              console.log('Image loaded successfully:', imageUri);
            }}
          />
        ) : (
          <View style={[styles.itemImage, styles.placeholderImage]}>
            <Text style={styles.placeholderText}>📷</Text>
          </View>
        )}
        <View style={styles.itemDetails}>
          <Text style={[styles.itemName, { color: theme.text }]}>{item.name}</Text>
          <Text style={[styles.itemCategory, { color: theme.text, opacity: 0.8 }]}>
            {item.category} • {item.color}
          </Text>
          <Text style={[styles.itemSeason, { color: theme.text, opacity: 0.6 }]}>
            {item.season} • {item.occasion || 'casual'} • Worn {item.timesWorn || 0} times
          </Text>
          {item.pendingSync && (
            <Text style={[styles.syncStatus, { color: '#FFA500' }]}>
              ⏳ Pending sync
            </Text>
          )}
        </View>
        <TouchableOpacity 
          style={styles.deleteButton}
          onPress={() => deleteItem(item.id)}
        >
          <Text style={styles.deleteText}>×</Text>
        </TouchableOpacity>
      </View>
    );
  };

  if (loading && items.length === 0) {
    return (
      <LinearGradient colors={theme.background} style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={[styles.loadingText, { color: theme.text }]}>Loading your wardrobe...</Text>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={theme.background} style={styles.container}>
      <StatusBar style="auto" />
      
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={[styles.backText, { color: theme.text }]}>← Back</Text>
        </TouchableOpacity>
        <Text style={[styles.title, { color: theme.text }]}>My Wardrobe</Text>
        <TouchableOpacity 
          style={[styles.addButton, { backgroundColor: '#8A724C' }]}
          onPress={() => navigation.navigate('AddClothes')}
        >
          <Text style={styles.addButtonText}>+</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.statsContainer}>
        <Text style={[styles.statsText, { color: theme.text }]}>
          {Array.isArray(items) ? items.length : 0} items • {Array.isArray(items) ? items.filter(i => i.pendingSync).length : 0} pending sync
        </Text>
      </View>

      <ScrollView 
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {!Array.isArray(items) || items.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={[styles.emptyTitle, { color: theme.text }]}>Your wardrobe is empty</Text>
            <Text style={[styles.emptySubtitle, { color: theme.text, opacity: 0.7 }]}>
              Start adding clothes to build your digital wardrobe
            </Text>
            <TouchableOpacity 
              style={[styles.addFirstButton, { backgroundColor: '#8A724C' }]}
              onPress={() => navigation.navigate('AddClothes')}
            >
              <Text style={styles.addFirstButtonText}>Add Your First Item</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.itemsContainer}>
            {Array.isArray(items) && items.map(renderItem)}
          </View>
        )}
      </ScrollView>
    </LinearGradient>
  );
};

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
    backgroundColor:'#F7F3E8'
  },
  backButton: {
    padding: 5,
  },
  backText: {
    fontSize: 16,
    fontWeight: '600',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addButtonText: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  statsContainer: {
    paddingHorizontal: 20,
    paddingBottom: 10,
  },
  statsText: {
    fontSize: 14,
    opacity: 0.8,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 100,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  emptySubtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
  },
  addFirstButton: {
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
  },
  addFirstButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  itemsContainer: {
    paddingBottom: 20,
  },
  itemCard: {
    flexDirection: 'row',
    padding: 15,
    marginBottom: 15,
    borderRadius: 15,
    alignItems: 'center',
  },
  itemImage: {
    width: 80,
    height: 100,
    borderRadius: 10,
    marginRight: 15,
  },
  placeholderImage: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderText: {
    fontSize: 30,
    opacity: 0.5,
  },
  itemDetails: {
    flex: 1,
  },
  itemName: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  itemCategory: {
    fontSize: 14,
    marginBottom: 3,
    textTransform: 'capitalize',
  },
  itemSeason: {
    fontSize: 12,
    textTransform: 'capitalize',
  },
  syncStatus: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 5,
  },
  deleteButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: 'rgba(255,0,0,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  deleteText: {
    color: '#FF0000',
    fontSize: 20,
    fontWeight: 'bold',
  },
});

export default MyWardrobeScreen;