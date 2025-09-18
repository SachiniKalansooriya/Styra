// screens/BuyRecommendationsScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../themes/ThemeProvider';
import buyRecommendationService from '../services/buyRecommendationService';

const { width } = Dimensions.get('window');

const BuyRecommendationsScreen = ({ navigation }) => {
  const { theme } = useTheme();
  const [recommendations, setRecommendations] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let result = await buyRecommendationService.getBuyingRecommendations(1);
      
      // If API fails, use mock data
      if (!result.success) {
        console.log('API failed, using mock data:', result.error);
        result = buyRecommendationService.getMockRecommendations();
      }
      
      setRecommendations(result.recommendations || []);
      setAnalytics(result.analytics || {});
      
    } catch (error) {
      console.error('Error loading recommendations:', error);
      setError('Failed to load recommendations');
      
      // Fallback to mock data
      const mockResult = buyRecommendationService.getMockRecommendations();
      setRecommendations(mockResult.recommendations);
      setAnalytics(mockResult.analytics);
      
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'low': return '#27ae60';
      default: return '#95a5a6';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'outerwear': return 'shirt-outline';
      case 'bottoms': return 'fitness-outline';
      case 'shoes': return 'footsteps-outline';
      case 'tops': return 'shirt-outline';
      case 'accessories': return 'watch-outline';
      default: return 'bag-outline';
    }
  };

  const renderRecommendationCard = (item, index) => (
    <View key={item.id || index} style={styles.recommendationCard}>
      <View style={styles.cardHeader}>
        <View style={styles.categoryInfo}>
          <Ionicons 
            name={getCategoryIcon(item.category)} 
            size={24} 
            color="#3498db" 
          />
          <View style={styles.categoryText}>
            <Text style={styles.itemType}>{item.item_type}</Text>
            <Text style={styles.category}>{item.category}</Text>
          </View>
        </View>
        <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(item.priority) }]}>
          <Text style={styles.priorityText}>{item.priority?.toUpperCase()}</Text>
        </View>
      </View>

      <Text style={styles.reason}>{item.reason}</Text>

      <View style={styles.detailsRow}>
        <View style={styles.detailItem}>
          <Ionicons name="pricetag-outline" size={16} color="#7f8c8d" />
          <Text style={styles.detailText}>{item.estimated_price}</Text>
        </View>
        <View style={styles.detailItem}>
          <Ionicons name="analytics-outline" size={16} color="#7f8c8d" />
          <Text style={styles.detailText}>{item.style_match}% match</Text>
        </View>
      </View>

      {item.color_suggestions && item.color_suggestions.length > 0 && (
        <View style={styles.colorsSection}>
          <Text style={styles.colorsTitle}>Suggested Colors:</Text>
          <View style={styles.colorTags}>
            {item.color_suggestions.map((color, idx) => (
              <View key={idx} style={styles.colorTag}>
                <Text style={styles.colorText}>{color}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      <TouchableOpacity 
        style={styles.shopButton}
        onPress={() => Alert.alert('Shopping', `Looking for ${item.item_type}...`, [
          { text: 'Online Stores', onPress: () => console.log('Navigate to online stores') },
          { text: 'Local Stores', onPress: () => console.log('Navigate to local stores') },
          { text: 'Cancel' }
        ])}
      >
        <Text style={styles.shopButtonText}>Find Stores</Text>
        <Ionicons name="storefront-outline" size={16} color="#fff" />
      </TouchableOpacity>
    </View>
  );

  const renderAnalytics = () => (
    <View style={styles.analyticsCard}>
      <Text style={styles.analyticsTitle}>Wardrobe Analysis</Text>
      
      {analytics.versatility_score !== undefined && (
        <View style={styles.scoreContainer}>
          <View style={styles.scoreCircle}>
            <Text style={styles.scoreValue}>{analytics.versatility_score}</Text>
          </View>
          <Text style={styles.scoreLabel}>Versatility Score</Text>
        </View>
      )}
      
      {analytics.wardrobe_gaps && analytics.wardrobe_gaps.length > 0 && (
        <View style={styles.analyticsRow}>
          <Ionicons name="alert-circle-outline" size={20} color="#e74c3c" />
          <Text style={styles.analyticsText}>
            Missing: {analytics.wardrobe_gaps.join(', ')}
          </Text>
        </View>
      )}
      
      {analytics.style_preference && (
        <View style={styles.analyticsRow}>
          <Ionicons name="person-outline" size={20} color="#3498db" />
          <Text style={styles.analyticsText}>
            Style: {analytics.style_preference}
          </Text>
        </View>
      )}
      
      {analytics.focus_areas && analytics.focus_areas.length > 0 && (
        <View style={styles.analyticsRow}>
          <Ionicons name="compass-outline" size={20} color="#9b59b6" />
          <Text style={styles.analyticsText}>
            Focus on: {analytics.focus_areas.join(', ')}
          </Text>
        </View>
      )}
      
      {analytics.budget_recommendation && (
        <View style={styles.analyticsRow}>
          <Ionicons name="wallet-outline" size={20} color="#27ae60" />
          <Text style={styles.analyticsText}>
            Budget: {analytics.budget_recommendation}
          </Text>
        </View>
      )}
      
      {analytics.color_palette && analytics.color_palette.dominant && (
        <View style={styles.colorPaletteSection}>
          <Text style={styles.colorPaletteTitle}>Your Color Palette</Text>
          <View style={styles.colorPaletteRow}>
            <View style={[styles.dominantColorCircle, { backgroundColor: getColorCode(analytics.color_palette.dominant) }]} />
            <View style={styles.accentColorsContainer}>
              {analytics.color_palette.suggested_accents && 
                analytics.color_palette.suggested_accents.map((color, index) => (
                  <View 
                    key={index} 
                    style={[
                      styles.accentColorCircle, 
                      { backgroundColor: getColorCode(color) }
                    ]} 
                  />
                ))
              }
            </View>
          </View>
          <Text style={styles.colorPaletteText}>
            Your dominant color is <Text style={styles.colorHighlight}>{analytics.color_palette.dominant}</Text>.
            Try adding accent colors for versatility.
          </Text>
        </View>
      )}
    </View>
  );

  const getColorCode = (colorName) => {
    const colorMap = {
      'black': '#000000',
      'white': '#ffffff',
      'red': '#e74c3c',
      'blue': '#3498db',
      'navy': '#2c3e50',
      'light blue': '#85c1e9',
      'green': '#2ecc71',
      'yellow': '#f1c40f',
      'purple': '#9b59b6',
      'pink': '#e84393',
      'gray': '#95a5a6',
      'grey': '#95a5a6',
      'beige': '#f5f5dc',
      'brown': '#8b4513',
      'orange': '#e67e22',
      'burgundy': '#800020',
      'burgundy red': '#800020',
      'deep red': '#8b0000',
      'crimson': '#dc143c',
      'off-white': '#f5f5f5',
    };
    
    return colorMap[colorName.toLowerCase()] || '#95a5a6'; // Default to gray if color not found
  };

  if (loading) {
    return (
      <LinearGradient colors={theme.background} style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <View style={styles.header}>
            <TouchableOpacity onPress={() => navigation.goBack()}>
              <Ionicons name="arrow-back" size={24} color={theme.text} />
            </TouchableOpacity>
            <Text style={[styles.headerTitle, { color: theme.text }]}>AI Shopping Assistant</Text>
            <View style={{ width: 24 }} />
          </View>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#3498db" />
            <Text style={[styles.loadingText, { color: theme.text }]}>
              Analyzing your wardrobe...
            </Text>
          </View>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={theme.background} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color={theme.text} />
          </TouchableOpacity>
          <Text style={[styles.headerTitle, { color: theme.text }]}>AI Shopping Assistant</Text>
          <TouchableOpacity onPress={loadRecommendations}>
            <Ionicons name="refresh" size={24} color={theme.text} />
          </TouchableOpacity>
        </View>

        <ScrollView 
          style={styles.content}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >
          {/* Analytics Section */}
          {Object.keys(analytics).length > 0 && renderAnalytics()}

          {/* Recommendations Header */}
          <View style={styles.sectionHeader}>
            <Ionicons name="bulb-outline" size={24} color="#f39c12" />
            <Text style={[styles.sectionTitle, { color: theme.text }]}>
              Personalized Recommendations
            </Text>
          </View>

          {/* Recommendations List */}
          {recommendations.length > 0 ? (
            recommendations.map((item, index) => renderRecommendationCard(item, index))
          ) : (
            <View style={styles.emptyState}>
              <Ionicons name="bag-outline" size={64} color="#bdc3c7" />
              <Text style={styles.emptyTitle}>No Recommendations</Text>
              <Text style={styles.emptySubtitle}>
                Add more items to your wardrobe to get personalized shopping suggestions
              </Text>
              <TouchableOpacity 
                style={styles.addItemsButton}
                onPress={() => navigation.navigate('AddClothes')}
              >
                <Text style={styles.addItemsButtonText}>Add Items</Text>
              </TouchableOpacity>
            </View>
          )}

          <View style={styles.bottomSpacing} />
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
  },
  analyticsCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  analyticsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  scoreContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  scoreCircle: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#3498db',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  scoreValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  scoreLabel: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  analyticsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  analyticsText: {
    marginLeft: 10,
    fontSize: 14,
    color: '#34495e',
    flex: 1,
  },
  colorPaletteSection: {
    marginTop: 15,
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
  },
  colorPaletteTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 12,
  },
  colorPaletteRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  dominantColorCircle: {
    width: 35,
    height: 35,
    borderRadius: 18,
    marginRight: 15,
    borderWidth: 1,
    borderColor: '#ecf0f1',
  },
  accentColorsContainer: {
    flexDirection: 'row',
  },
  accentColorCircle: {
    width: 25,
    height: 25,
    borderRadius: 13,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#ecf0f1',
  },
  colorPaletteText: {
    fontSize: 13,
    color: '#7f8c8d',
    lineHeight: 18,
  },
  colorHighlight: {
    fontWeight: 'bold',
    color: '#34495e',
    textTransform: 'capitalize',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  recommendationCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  categoryInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  categoryText: {
    marginLeft: 12,
  },
  itemType: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    textTransform: 'capitalize',
  },
  category: {
    fontSize: 14,
    color: '#7f8c8d',
    textTransform: 'capitalize',
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#fff',
  },
  reason: {
    fontSize: 15,
    color: '#34495e',
    lineHeight: 22,
    marginBottom: 15,
  },
  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailText: {
    marginLeft: 6,
    fontSize: 14,
    color: '#7f8c8d',
  },
  colorsSection: {
    marginBottom: 15,
  },
  colorsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 8,
  },
  colorTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  colorTag: {
    backgroundColor: '#ecf0f1',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 4,
  },
  colorText: {
    fontSize: 12,
    color: '#34495e',
    textTransform: 'capitalize',
  },
  shopButton: {
    backgroundColor: '#3498db',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 25,
  },
  shopButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 8,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginTop: 20,
    marginBottom: 10,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#7f8c8d',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
  },
  addItemsButton: {
    backgroundColor: '#3498db',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 25,
  },
  addItemsButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  bottomSpacing: {
    height: 20,
  },
});

export default BuyRecommendationsScreen;
