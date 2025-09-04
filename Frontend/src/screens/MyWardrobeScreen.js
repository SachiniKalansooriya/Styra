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

  useEffect(() => {
    loadWardrobe();
  }, []);

  const loadWardrobe = async () => {
    try {
      setLoading(true);
      const wardrobeItems = await storage.getWardrobeItems();
      setItems(wardrobeItems);
    } catch (error) {
      console.error('Error loading wardrobe:', error);
      Alert.alert('Error', 'Failed to load wardrobe items');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadWardrobe();
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

  const renderItem = (item) => (
    <View key={item.id} style={[styles.itemCard, { backgroundColor: 'rgba(255,255,255,0.1)' }]}>
      {item.imageData?.localUri && (
        <Image source={{ uri: item.imageData.localUri }} style={styles.itemImage} />
      )}
      <View style={styles.itemDetails}>
        <Text style={[styles.itemName, { color: theme.text }]}>{item.name}</Text>
        <Text style={[styles.itemCategory, { color: theme.text, opacity: 0.8 }]}>
          {item.category} • {item.color}
        </Text>
        <Text style={[styles.itemSeason, { color: theme.text, opacity: 0.6 }]}>
          {item.season} • Worn {item.timesWorn || 0} times
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
          style={[styles.addButton, { backgroundColor: theme.primary }]}
          onPress={() => navigation.navigate('AddClothes')}
        >
          <Text style={styles.addButtonText}>+</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.statsContainer}>
        <Text style={[styles.statsText, { color: theme.text }]}>
          {items.length} items • {items.filter(i => i.pendingSync).length} pending sync
        </Text>
      </View>

      <ScrollView 
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {items.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={[styles.emptyTitle, { color: theme.text }]}>Your wardrobe is empty</Text>
            <Text style={[styles.emptySubtitle, { color: theme.text, opacity: 0.7 }]}>
              Start adding clothes to build your digital wardrobe
            </Text>
            <TouchableOpacity 
              style={[styles.addFirstButton, { backgroundColor: theme.primary }]}
              onPress={() => navigation.navigate('AddClothes')}
            >
              <Text style={styles.addFirstButtonText}>Add Your First Item</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.itemsContainer}>
            {items.map(renderItem)}
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