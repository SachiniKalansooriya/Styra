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
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const PackingListResultsScreen = ({ navigation, route }) => {
  console.log('PackingListResults - Route params:', route?.params);
  
  const { tripDetails, packingResult } = route?.params || {};
  
  const [loading, setLoading] = useState(false);
  const [checkedItems, setCheckedItems] = useState({});

  // Error handling for missing data
  if (!tripDetails) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Error</Text>
        </View>
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>Trip details not found</Text>
          <TouchableOpacity 
            style={styles.button}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.buttonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Extract categories safely
  const categories = packingResult?.categories || [];
  console.log('Categories found:', categories.length);

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
    return categories.reduce((total, category) => {
      return total + (category.items?.length || 0);
    }, 0);
  };

  const formatDate = (date) => {
    if (!date) return 'Unknown';
    try {
      const dateObj = typeof date === 'string' ? new Date(date) : date;
      return dateObj.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return 'Invalid Date';
    }
  };

  const getDuration = () => {
    try {
      if (!tripDetails.startDate || !tripDetails.endDate) return 0;
      const start = typeof tripDetails.startDate === 'string' 
        ? new Date(tripDetails.startDate) 
        : tripDetails.startDate;
      const end = typeof tripDetails.endDate === 'string' 
        ? new Date(tripDetails.endDate) 
        : tripDetails.endDate;
      const diffTime = Math.abs(end - start);
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    } catch {
      return 0;
    }
  };

  const renderCategory = (category, categoryIndex) => {
    if (!category || !category.items) {
      return (
        <View key={categoryIndex} style={styles.categoryCard}>
          <Text style={styles.categoryTitle}>{category?.category || 'Unknown Category'}</Text>
          <Text style={styles.errorText}>No items in this category</Text>
        </View>
      );
    }

    const categoryCompletion = category.items.filter((_, itemIndex) => 
      checkedItems[`${categoryIndex}-${itemIndex}`]
    ).length;

    return (
      <View key={categoryIndex} style={styles.categoryCard}>
        <View style={styles.categoryHeader}>
          <Text style={styles.categoryTitle}>{category.category}</Text>
          <Text style={styles.categoryProgress}>
            {categoryCompletion}/{category.items.length} packed
          </Text>
        </View>
        
        {category.reasoning && (
          <Text style={styles.categoryReasoning}>{category.reasoning}</Text>
        )}

        {category.items.map((item, itemIndex) => {
          const key = `${categoryIndex}-${itemIndex}`;
          const isChecked = checkedItems[key];
          
          return (
            <TouchableOpacity
              key={itemIndex}
              style={styles.itemRow}
              onPress={() => toggleItemCheck(categoryIndex, itemIndex)}
            >
              <View style={[styles.checkbox, isChecked && styles.checkedBox]}>
                {isChecked && <Ionicons name="checkmark" size={16} color="#fff" />}
              </View>
              
              <View style={styles.itemContent}>
                <Text style={[styles.itemName, isChecked && styles.checkedItemName]}>
                  {item.name}
                  {item.quantity && item.quantity > 1 && ` (${item.quantity})`}
                </Text>
                
                {item.status && (
                  <Text style={styles.itemStatus}>
                    {item.status === 'available' ? '✓ Available in wardrobe' : 
                     item.status === 'needed' ? '🛒 Need to buy' : 
                     '📋 Required'}
                  </Text>
                )}
              </View>
            </TouchableOpacity>
          );
        })}
      </View>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#FF8C42" />
          <Text style={styles.loadingText}>Loading packing list...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!categories || categories.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Packing List</Text>
        </View>
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>No packing recommendations found</Text>
          <Text style={styles.errorSubtext}>
            Categories: {categories?.length || 0}
          </Text>
          <TouchableOpacity 
            style={styles.button}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.buttonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Packing List</Text>
        <View style={{ width: 24 }} />
      </View>

      {/* Trip Summary */}
      <View style={styles.tripSummary}>
        <Text style={styles.destination}>{tripDetails.destination}</Text>
        <Text style={styles.tripDetails}>
          {getDuration()} days • {tripDetails.packingStyle} • {tripDetails.weatherExpected}
        </Text>
        {tripDetails.activities && tripDetails.activities.length > 0 && (
          <Text style={styles.activities}>
            {tripDetails.activities.slice(0, 3).join(', ')}
            {tripDetails.activities.length > 3 && ` +${tripDetails.activities.length - 3} more`}
          </Text>
        )}
      </View>

      {/* Progress */}
      <View style={styles.progressSection}>
        <Text style={styles.progressText}>
          Progress: {getCheckedCount()}/{getTotalItems()} items packed
        </Text>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill, 
              { 
                width: getTotalItems() > 0 
                  ? `${(getCheckedCount() / getTotalItems()) * 100}%` 
                  : '0%' 
              }
            ]} 
          />
        </View>
      </View>

      {/* Categories List */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {categories.map((category, index) => renderCategory(category, index))}
        
        {/* Debug Info */}
        <View style={styles.debugSection}>
          <Text style={styles.debugTitle}>Debug Info:</Text>
          <Text style={styles.debugText}>Categories: {categories.length}</Text>
          <Text style={styles.debugText}>Source: {packingResult?.source}</Text>
          <Text style={styles.debugText}>Total Items: {getTotalItems()}</Text>
        </View>
      </ScrollView>

      {/* Bottom Actions */}
      <View style={styles.bottomActions}>
        <TouchableOpacity 
          style={styles.secondaryButton}
          onPress={() => navigation.navigate('MyWardrobe')}
        >
          <Text style={styles.secondaryButtonText}>My Wardrobe</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.primaryButton}
          onPress={() => {
            Alert.alert('Success!', 'Packing list ready!');
          }}
        >
          <Text style={styles.primaryButtonText}>Save Trip</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 15,
  },
  errorText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
    marginBottom: 10,
  },
  errorSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#FF8C42',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  tripSummary: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  destination: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  tripDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  activities: {
    fontSize: 14,
    color: '#FF8C42',
  },
  progressSection: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  progressText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FF8C42',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  categoryCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  categoryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  categoryTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  categoryProgress: {
    fontSize: 14,
    color: '#FF8C42',
    fontWeight: '600',
  },
  categoryReasoning: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
    marginBottom: 15,
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ddd',
    marginRight: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkedBox: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  itemContent: {
    flex: 1,
  },
  itemName: {
    fontSize: 16,
    color: '#333',
    marginBottom: 4,
  },
  checkedItemName: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
  itemStatus: {
    fontSize: 12,
    color: '#666',
  },
  debugSection: {
    backgroundColor: '#f0f0f0',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  debugText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  bottomActions: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    gap: 10,
  },
  secondaryButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FF8C42',
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: '#FF8C42',
    fontSize: 16,
    fontWeight: '600',
  },
  primaryButton: {
    flex: 1,
    backgroundColor: '#FF8C42',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default PackingListResultsScreen;