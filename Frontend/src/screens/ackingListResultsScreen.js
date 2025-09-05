// screens/PackingListResultsScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
  FlatList,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import tripPlannerService from '../services/tripPlannerService';

const PackingListResultsScreen = ({ navigation, route }) => {
  const { tripDetails } = route.params;
  const [packingList, setPackingList] = useState([]);
  const [checkedItems, setCheckedItems] = useState({});
  const [loading, setLoading] = useState(true);
  const [wardrobeMatches, setWardrobeMatches] = useState({});

  useEffect(() => {
    generateSmartPackingList();
  }, []);

  const generateSmartPackingList = async () => {
    setLoading(true);
    try {
      const result = await tripPlannerService.generateSmartPackingList(tripDetails);
      setPackingList(result);
      
      // Extract wardrobe matches for quick access
      const matches = {};
      result.forEach((category, categoryIndex) => {
        category.items.forEach((item, itemIndex) => {
          if (item.wardrobeMatches && item.wardrobeMatches.length > 0) {
            matches[`${categoryIndex}-${itemIndex}`] = item.wardrobeMatches;
          }
        });
      });
      setWardrobeMatches(matches);
      
    } catch (error) {
      Alert.alert('Error', 'Failed to generate packing list');
    } finally {
      setLoading(false);
    }
  };

  const toggleItemCheck = (categoryIndex, itemIndex) => {
    const key = `${categoryIndex}-${itemIndex}`;
    setCheckedItems(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const getCheckedCount = () => {
    return Object.values(checkedItems).filter(Boolean).length;
  };

  const getTotalItems = () => {
    return packingList.reduce((total, category) => total + category.items.length, 0);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'available': return '#4CAF50';
      case 'needed': return '#FF9800';
      case 'required': return '#2196F3';
      default: return '#666';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'available': return 'checkmark-circle';
      case 'needed': return 'add-circle';
      case 'required': return 'information-circle';
      default: return 'help-circle';
    }
  };

  const renderWardrobeMatch = (item, categoryIndex, itemIndex) => {
    const key = `${categoryIndex}-${itemIndex}`;
    const matches = wardrobeMatches[key];
    
    if (!matches || matches.length === 0) return null;

    return (
      <View style={styles.wardrobeMatches}>
        <Text style={styles.matchLabel}>From your wardrobe:</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {matches.slice(0, 3).map((match, index) => (
            <TouchableOpacity 
              key={index} 
              style={styles.matchItem}
              onPress={() => {
                // Toggle this item as "packed from wardrobe"
                toggleItemCheck(categoryIndex, itemIndex);
              }}
            >
              {match.image_url ? (
                <Image 
                  source={{ uri: `http://172.20.10.1:8000${match.image_url}` }}
                  style={styles.matchImage}
                />
              ) : (
                <View style={styles.matchPlaceholder}>
                  <Ionicons name="shirt-outline" size={16} color="#666" />
                </View>
              )}
              <Text style={styles.matchName} numberOfLines={1}>
                {match.name}
              </Text>
              <Text style={styles.matchCategory}>
                {match.color} {match.category}
              </Text>
            </TouchableOpacity>
          ))}
          {matches.length > 3 && (
            <View style={styles.moreMatches}>
              <Text style={styles.moreMatchesText}>+{matches.length - 3}</Text>
            </View>
          )}
        </ScrollView>
      </View>
    );
  };

  const renderCategory = ({ item: category, index: categoryIndex }) => (
    <View style={styles.categoryContainer}>
      <Text style={styles.categoryTitle}>{category.category}</Text>
      {category.items.map((item, itemIndex) => {
        const key = `${categoryIndex}-${itemIndex}`;
        const isChecked = checkedItems[key];
        
        return (
          <View key={itemIndex} style={styles.itemContainer}>
            <TouchableOpacity
              style={styles.itemHeader}
              onPress={() => toggleItemCheck(categoryIndex, itemIndex)}
            >
              <View style={[styles.checkbox, isChecked && styles.checkedBox]}>
                {isChecked && <Ionicons name="checkmark" size={16} color="#fff" />}
              </View>
              
              <View style={styles.itemInfo}>
                <Text style={[styles.itemText, isChecked && styles.checkedText]}>
                  {item.name}
                </Text>
                
                <View style={styles.itemStatus}>
                  <Ionicons 
                    name={getStatusIcon(item.status)} 
                    size={16} 
                    color={getStatusColor(item.status)} 
                  />
                  <Text style={[styles.statusText, { color: getStatusColor(item.status) }]}>
                    {item.status === 'available' ? 'In wardrobe' : 
                     item.status === 'needed' ? 'Need to buy' : 'Required'}
                  </Text>
                </View>
              </View>
            </TouchableOpacity>
            
            {renderWardrobeMatch(item, categoryIndex, itemIndex)}
          </View>
        );
      })}
    </View>
  );

  const renderShoppingList = () => {
    const neededItems = [];
    packingList.forEach((category, categoryIndex) => {
      category.items.forEach((item, itemIndex) => {
        if (item.status === 'needed') {
          neededItems.push({
            ...item,
            category: category.category
          });
        }
      });
    });

    if (neededItems.length === 0) return null;

    return (
      <View style={styles.shoppingSection}>
        <Text style={styles.shoppingSectionTitle}>Shopping List</Text>
        <Text style={styles.shoppingSectionSubtitle}>
          Items you might need to buy for this trip
        </Text>
        {neededItems.map((item, index) => (
          <View key={index} style={styles.shoppingItem}>
            <Ionicons name="bag-outline" size={20} color="#FF9800" />
            <Text style={styles.shoppingItemText}>
              {item.name} ({item.category})
            </Text>
          </View>
        ))}
      </View>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Ionicons name="bag" size={48} color="#FF8C42" />
          <Text style={styles.loadingText}>Analyzing your wardrobe...</Text>
          <Text style={styles.loadingSubtext}>
            Creating smart packing list for {tripDetails.destination}
          </Text>
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
        <Text style={styles.headerTitle}>Smart Packing List</Text>
        <TouchableOpacity onPress={() => Alert.alert('Feature coming soon!')}>
          <Ionicons name="share-outline" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      <View style={styles.tripSummary}>
        <Text style={styles.destination}>{tripDetails.destination}</Text>
        <Text style={styles.duration}>
          {Math.ceil((tripDetails.endDate - tripDetails.startDate) / (1000 * 60 * 60 * 24))} days • {tripDetails.packingStyle}
        </Text>
        <Text style={styles.activities}>
          {tripDetails.activities.slice(0, 2).join(', ')}
          {tripDetails.activities.length > 2 && ` +${tripDetails.activities.length - 2} more`}
        </Text>
      </View>

      <View style={styles.progressContainer}>
        <Text style={styles.progressText}>
          {getCheckedCount()} of {getTotalItems()} items packed
        </Text>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill, 
              { width: `${(getCheckedCount() / getTotalItems()) * 100}%` }
            ]} 
          />
        </View>
      </View>

      <FlatList
        data={packingList}
        renderItem={renderCategory}
        keyExtractor={(item, index) => index.toString()}
        style={styles.listContainer}
        showsVerticalScrollIndicator={false}
        ListFooterComponent={renderShoppingList}
      />

      <View style={styles.bottomActions}>
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => navigation.navigate('MyWardrobe')}
        >
          <Ionicons name="shirt" size={20} color="#FF8C42" />
          <Text style={styles.actionButtonText}>View Wardrobe</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.actionButton, styles.primaryButton]}
          onPress={async () => {
            try {
              await tripPlannerService.saveTrip({
                ...tripDetails,
                packingList,
                checkedItems
              });
              Alert.alert('Success!', 'Trip and packing list saved!');
            } catch (error) {
              Alert.alert('Error', 'Failed to save trip');
            }
          }}
        >
          <Ionicons name="save" size={20} color="#fff" />
          <Text style={[styles.actionButtonText, styles.primaryButtonText]}>Save Trip</Text>
        </TouchableOpacity>
      </View>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  loadingText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginTop: 20,
    textAlign: 'center',
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
  tripSummary: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#f8f9fa',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  destination: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  duration: {
    fontSize: 14,
    color: '#FF8C42',
    fontWeight: '600',
    marginTop: 2,
  },
  activities: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  progressContainer: {
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  progressText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8,
    fontWeight: '600',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FF8C42',
    borderRadius: 4,
  },
  listContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  categoryContainer: {
    marginBottom: 25,
  },
  categoryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
    paddingBottom: 8,
    borderBottomWidth: 2,
    borderBottomColor: '#FF8C42',
  },
  itemContainer: {
    marginBottom: 15,
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 5,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ddd',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkedBox: {
    backgroundColor: '#FF8C42',
    borderColor: '#FF8C42',
  },
  itemInfo: {
    flex: 1,
  },
  itemText: {
    fontSize: 16,
    color: '#333',
    marginBottom: 4,
  },
  checkedText: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
  itemStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 12,
    marginLeft: 4,
    fontWeight: '500',
  },
  wardrobeMatches: {
    marginLeft: 36,
    marginTop: 8,
    paddingLeft: 12,
    borderLeftWidth: 2,
    borderLeftColor: '#f0f0f0',
  },
  matchLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
    fontWeight: '500',
  },
  matchItem: {
    width: 80,
    marginRight: 12,
    alignItems: 'center',
  },
  matchImage: {
    width: 60,
    height: 75,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  matchPlaceholder: {
    width: 60,
    height: 75,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  matchName: {
    fontSize: 10,
    color: '#333',
    marginTop: 4,
    textAlign: 'center',
    fontWeight: '500',
  },
  matchCategory: {
    fontSize: 9,
    color: '#666',
    textAlign: 'center',
  },
  moreMatches: {
    width: 60,
    height: 75,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  moreMatchesText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  shoppingSection: {
    marginTop: 20,
    padding: 16,
    backgroundColor: '#fff5f2',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#FF8C42',
    marginBottom: 20,
  },
  shoppingSectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FF8C42',
    marginBottom: 4,
  },
  shoppingSectionSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  shoppingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
  },
  shoppingItemText: {
    fontSize: 14,
    color: '#333',
    marginLeft: 8,
  },
  bottomActions: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    gap: 10,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FF8C42',
    backgroundColor: '#fff',
  },
  primaryButton: {
    backgroundColor: '#FF8C42',
    borderColor: '#FF8C42',
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FF8C42',
    marginLeft: 8,
  },
  primaryButtonText: {
    color: '#fff',
  },
});

export default PackingListResultsScreen;