// src/screens/MyWardrobeScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Image,
  TouchableOpacity,
  TextInput,
  Alert,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useTheme } from '../themes/ThemeProvider';
import { storage, cameraBackend } from '../utils/storage';

const MyWardrobeScreen = ({ navigation }) => {
  const { theme } = useTheme();
  const [wardrobeItems, setWardrobeItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredItems, setFilteredItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  // Mock data - replace with actual data from your storage/API
  const mockWardrobeItems = [
    {
      id: '1',
      name: 'Blue Denim Jacket',
      category: 'Outerwear',
      color: 'Blue',
      season: 'Spring',
      image: 'https://via.placeholder.com/150',
      lastWorn: '2025-09-01',
      timesWorn: 5,
    },
    {
      id: '2',
      name: 'White Cotton T-Shirt',
      category: 'Tops',
      color: 'White',
      season: 'All',
      image: 'https://via.placeholder.com/150',
      lastWorn: '2025-08-30',
      timesWorn: 12,
    },
    {
      id: '3',
      name: 'Black Formal Pants',
      category: 'Bottoms',
      color: 'Black',
      season: 'All',
      image: 'https://via.placeholder.com/150',
      lastWorn: '2025-08-28',
      timesWorn: 8,
    },
    {
      id: '4',
      name: 'Red Summer Dress',
      category: 'Dresses',
      color: 'Red',
      season: 'Summer',
      image: 'https://via.placeholder.com/150',
      lastWorn: '2025-08-25',
      timesWorn: 3,
    },
  ];

  const categories = ['All', 'Tops', 'Bottoms', 'Dresses', 'Shoes', 'Accessories', 'Outerwear'];

  useEffect(() => {
    loadWardrobeItems();
  }, []);

  useEffect(() => {
    filterItems();
  }, [searchQuery, selectedCategory, wardrobeItems]);

  const loadWardrobeItems = async () => {
    try {
      setLoading(true);
      const items = await storage.getWardrobeItems();
      if (items.length === 0) {
        // If no items exist, add some mock data for demonstration
        setWardrobeItems(mockWardrobeItems);
        await storage.saveWardrobeItems(mockWardrobeItems);
      } else {
        setWardrobeItems(items);
      }
    } catch (error) {
      console.error('Error loading wardrobe items:', error);
      Alert.alert('Error', 'Failed to load wardrobe items');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadWardrobeItems();
    setRefreshing(false);
  };

  const handleDeleteItem = async (itemId) => {
    Alert.alert(
      'Delete Item',
      'Are you sure you want to delete this item?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              const success = await cameraBackend.deleteClothingItem(itemId);
              if (success) {
                await loadWardrobeItems();
              } else {
                Alert.alert('Error', 'Failed to delete item');
              }
            } catch (error) {
              console.error('Error deleting item:', error);
              Alert.alert('Error', 'Failed to delete item');
            }
          },
        },
      ]
    );
  };

  const handleMarkAsWorn = async (itemId) => {
    const success = await storage.markItemAsWorn(itemId);
    if (success) {
      await loadWardrobeItems();
      Alert.alert('Success', 'Item marked as worn!');
    } else {
      Alert.alert('Error', 'Failed to update item');
    }
  };

  const filterItems = () => {
    let filtered = wardrobeItems;

    if (selectedCategory !== 'All') {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.color.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredItems(filtered);
  };

  const renderWardrobeItem = ({ item }) => {
    // Get the correct image URI
    const imageUri = item.imageData?.localUri || item.image || item.imageUri || 'https://via.placeholder.com/150';
    
    return (
      <TouchableOpacity
        style={[styles.itemCard, { backgroundColor: theme.cardBackground || 'rgba(255,255,255,0.9)' }]}
        onPress={() => {
          Alert.alert(
            item.name,
            `Category: ${item.category}\nColor: ${item.color}\nTimes worn: ${item.timesWorn || 0}`,
            [
              { text: 'Cancel', style: 'cancel' },
              { text: 'Mark as Worn', onPress: () => handleMarkAsWorn(item.id) },
              { text: 'Delete', style: 'destructive', onPress: () => handleDeleteItem(item.id) },
            ]
          );
        }}
      >
        <Image 
          source={{ uri: imageUri }} 
          style={styles.itemImage}
          defaultSource={require('../../assets/adaptive-icon.png')}
          onError={() => console.log('Failed to load image:', imageUri)}
        />
        <View style={styles.itemInfo}>
          <Text style={[styles.itemName, { color: theme.text }]} numberOfLines={1}>
            {item.name}
          </Text>
          <Text style={[styles.itemCategory, { color: theme.primary }]}>
            {item.category}
          </Text>
          <Text style={[styles.itemStats, { color: theme.textSecondary || '#666' }]}>
            Worn {item.timesWorn || 0} times
          </Text>
          {item.lastWorn && (
            <Text style={[styles.itemStats, { color: theme.textSecondary || '#666' }]}>
              Last worn: {item.lastWorn}
            </Text>
          )}
        </View>
        
        {/* Action buttons */}
        <View style={styles.itemActions}>
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: theme.primary }]}
            onPress={(e) => {
              e.stopPropagation();
              handleMarkAsWorn(item.id);
            }}
          >
            <Ionicons name="checkmark" size={16} color="white" />
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    );
  };

  const renderCategoryFilter = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.categoryButton,
        { backgroundColor: selectedCategory === item ? theme.primary : '#f0f0f0' }
      ]}
      onPress={() => setSelectedCategory(item)}
    >
      <Text style={[
        styles.categoryButtonText,
        { color: selectedCategory === item ? '#fff' : '#666' }
      ]}>
        {item}
      </Text>
    </TouchableOpacity>
  );

  return (
    <LinearGradient colors={theme.background} style={[styles.container]}>
      <StatusBar style="auto" />
      
      <View style={[styles.header, { borderBottomColor: theme.border || '#f0f0f0' }]}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color={theme.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: theme.text }]}>My Wardrobe</Text>
        <TouchableOpacity onPress={() => navigation.navigate('AddClothes')}>
          <Ionicons name="add" size={24} color={theme.primary} />
        </TouchableOpacity>
      </View>

      <View style={[styles.searchContainer, { backgroundColor: theme.cardBackground || 'rgba(255,255,255,0.9)' }]}>
        <Ionicons name="search" size={20} color={theme.textSecondary || '#666'} style={styles.searchIcon} />
        <TextInput
          style={[styles.searchInput, { color: theme.text }]}
          placeholder="Search items by name or color..."
          placeholderTextColor={theme.textSecondary || '#666'}
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      <FlatList
        data={categories}
        renderItem={renderCategoryFilter}
        keyExtractor={(item) => item}
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoryList}
        contentContainerStyle={styles.categoryListContent}
      />

      <View style={styles.statsContainer}>
        <Text style={[styles.statsText, { color: theme.textSecondary || '#666' }]}>
          {filteredItems.length} items {selectedCategory !== 'All' ? `in ${selectedCategory}` : 'total'}
        </Text>
      </View>

      <FlatList
        data={filteredItems}
        renderItem={renderWardrobeItem}
        keyExtractor={(item) => item.id}
        numColumns={2}
        contentContainerStyle={styles.itemsList}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      />
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
    paddingHorizontal: 20,
    paddingVertical: 15,
    paddingTop: 50,
    borderBottomWidth: 1,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: 20,
    paddingHorizontal: 15,
    borderRadius: 10,
    height: 45,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
  },
  categoryList: {
    maxHeight: 50,
  },
  categoryListContent: {
    paddingHorizontal: 20,
  },
  categoryButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
  },
  categoryButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  statsContainer: {
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  statsText: {
    fontSize: 14,
  },
  itemsList: {
    paddingHorizontal: 10,
  },
  itemCard: {
    flex: 1,
    borderRadius: 12,
    margin: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  itemImage: {
    width: '100%',
    height: 120,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
    backgroundColor: '#f0f0f0',
  },
  itemInfo: {
    padding: 12,
  },
  itemName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  itemCategory: {
    fontSize: 14,
    marginBottom: 4,
  },
  itemStats: {
    fontSize: 12,
    marginBottom: 2,
  },
  itemActions: {
    position: 'absolute',
    top: 8,
    right: 8,
    flexDirection: 'row',
  },
  actionButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 4,
  },
});

export default MyWardrobeScreen;