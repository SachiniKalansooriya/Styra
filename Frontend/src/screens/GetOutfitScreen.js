// screens/GetOutfitScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  Image,
  Alert,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const GetOutfitScreen = ({ navigation }) => {
  const [currentOutfit, setCurrentOutfit] = useState(null);
  const [loading, setLoading] = useState(false);
  const [weatherInfo, setWeatherInfo] = useState(null);
  const [occasion, setOccasion] = useState('casual');

  const occasions = [
    { id: 'casual', name: 'Casual', icon: 'shirt' },
    { id: 'work', name: 'Work', icon: 'briefcase' },
    { id: 'formal', name: 'Formal', icon: 'business' },
    { id: 'workout', name: 'Workout', icon: 'fitness' },
    { id: 'date', name: 'Date Night', icon: 'heart' },
  ];

  // Mock weather data - replace with actual weather API
  const mockWeatherData = {
    temperature: 22,
    condition: 'sunny',
    description: 'Sunny',
    humidity: 45,
    windSpeed: 15,
  };

  // Mock outfit data
  const mockOutfits = {
    casual: {
      id: '1',
      items: [
        {
          id: 'top1',
          name: 'White Cotton T-Shirt',
          category: 'Top',
          image: 'https://via.placeholder.com/150',
        },
        {
          id: 'bottom1',
          name: 'Blue Denim Jeans',
          category: 'Bottom',
          image: 'https://via.placeholder.com/150',
        },
        {
          id: 'shoes1',
          name: 'White Sneakers',
          category: 'Shoes',
          image: 'https://via.placeholder.com/150',
        },
      ],
      confidence: 92,
      reason: 'Perfect for comfortable daily activities with sunny weather',
    },
    work: {
      id: '2',
      items: [
        {
          id: 'top2',
          name: 'Blue Button Shirt',
          category: 'Top',
          image: 'https://via.placeholder.com/150',
        },
        {
          id: 'bottom2',
          name: 'Black Formal Pants',
          category: 'Bottom',
          image: 'https://via.placeholder.com/150',
        },
        {
          id: 'shoes2',
          name: 'Black Formal Shoes',
          category: 'Shoes',
          image: 'https://via.placeholder.com/150',
        },
      ],
      confidence: 88,
      reason: 'Professional look suitable for office meetings',
    },
  };

  useEffect(() => {
    fetchWeatherInfo();
    generateOutfit();
  }, []);

  useEffect(() => {
    generateOutfit();
  }, [occasion]);

  const fetchWeatherInfo = () => {
    // In a real app, you'd fetch from a weather API
    setWeatherInfo(mockWeatherData);
  };

  const generateOutfit = () => {
    setLoading(true);
    
    // Simulate AI processing time
    setTimeout(() => {
      const outfit = mockOutfits[occasion] || mockOutfits.casual;
      setCurrentOutfit(outfit);
      setLoading(false);
    }, 1500);
  };

  const handleLikeOutfit = () => {
    Alert.alert('Outfit Liked!', 'This outfit has been saved to your favorites.');
  };

  const handleDislikeOutfit = () => {
    generateOutfit(); // Generate a new outfit
  };

  const handleWearOutfit = () => {
    Alert.alert(
      'Outfit Selected!',
      'This outfit has been marked as worn today.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Confirm', onPress: () => navigation.goBack() },
      ]
    );
  };

  const renderOccasionSelector = () => (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false}
      style={styles.occasionSelector}
      contentContainerStyle={styles.occasionSelectorContent}
    >
      {occasions.map((occ) => (
        <TouchableOpacity
          key={occ.id}
          style={[
            styles.occasionButton,
            occasion === occ.id && styles.selectedOccasionButton
          ]}
          onPress={() => setOccasion(occ.id)}
        >
          <Ionicons 
            name={occ.icon} 
            size={20} 
            color={occasion === occ.id ? '#fff' : '#666'} 
          />
          <Text style={[
            styles.occasionButtonText,
            occasion === occ.id && styles.selectedOccasionButtonText
          ]}>
            {occ.name}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  const renderWeatherCard = () => (
    <View style={styles.weatherCard}>
      <View style={styles.weatherInfo}>
        <Ionicons name="sunny" size={24} color="#FFD700" />
        <Text style={styles.temperature}>{weatherInfo?.temperature}°C</Text>
        <Text style={styles.weatherDescription}>{weatherInfo?.description}</Text>
      </View>
      <Text style={styles.weatherDetails}>
        Humidity: {weatherInfo?.humidity}% • Wind: {weatherInfo?.windSpeed} km/h
      </Text>
    </View>
  );

  const renderOutfitItems = () => (
    <View style={styles.outfitContainer}>
      <Text style={styles.outfitTitle}>Today's Recommendation</Text>
      
      {currentOutfit && (
        <>
          <View style={styles.confidenceContainer}>
            <Text style={styles.confidenceText}>
              {currentOutfit.confidence}% match confidence
            </Text>
            <View style={styles.confidenceBar}>
              <View 
                style={[
                  styles.confidenceFill, 
                  { width: `${currentOutfit.confidence}%` }
                ]} 
              />
            </View>
          </View>

          <View style={styles.itemsContainer}>
            {currentOutfit.items.map((item, index) => (
              <View key={item.id} style={styles.outfitItem}>
                <Image source={{ uri: item.image }} style={styles.itemImage} />
                <Text style={styles.itemName}>{item.name}</Text>
                <Text style={styles.itemCategory}>{item.category}</Text>
              </View>
            ))}
          </View>

          <View style={styles.reasonContainer}>
            <Text style={styles.reasonTitle}>Why this outfit?</Text>
            <Text style={styles.reasonText}>{currentOutfit.reason}</Text>
          </View>
        </>
      )}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Get Outfit</Text>
        <TouchableOpacity onPress={generateOutfit}>
          <Ionicons name="refresh" size={24} color="#FF8C42" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {weatherInfo && renderWeatherCard()}
        
        {renderOccasionSelector()}

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FF8C42" />
            <Text style={styles.loadingText}>Generating your perfect outfit...</Text>
          </View>
        ) : (
          currentOutfit && renderOutfitItems()
        )}
      </ScrollView>

      {!loading && currentOutfit && (
        <View style={styles.actionButtons}>
          <TouchableOpacity 
            style={styles.dislikeButton} 
            onPress={handleDislikeOutfit}
          >
            <Ionicons name="thumbs-down" size={20} color="#fff" />
            <Text style={styles.buttonText}>Try Again</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.likeButton} 
            onPress={handleLikeOutfit}
          >
            <Ionicons name="heart" size={20} color="#fff" />
            <Text style={styles.buttonText}>Save</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.wearButton} 
            onPress={handleWearOutfit}
          >
            <Ionicons name="checkmark" size={20} color="#fff" />
            <Text style={styles.buttonText}>Wear This</Text>
          </TouchableOpacity>
        </View>
      )}
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
  content: {
    flex: 1,
  },
  weatherCard: {
    backgroundColor: '#f8f9ff',
    margin: 20,
    padding: 15,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#FF8C42',
  },
  weatherInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  temperature: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 10,
  },
  weatherDescription: {
    fontSize: 16,
    color: '#666',
    marginLeft: 10,
  },
  weatherDetails: {
    fontSize: 14,
    color: '#666',
  },
  occasionSelector: {
    maxHeight: 60,
  },
  occasionSelectorContent: {
    paddingHorizontal: 20,
  },
  occasionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 10,
  },
  selectedOccasionButton: {
    backgroundColor: '#FF8C42',
  },
  occasionButtonText: {
    color: '#666',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 5,
  },
  selectedOccasionButtonText: {
    color: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  outfitContainer: {
    margin: 20,
  },
  outfitTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  confidenceContainer: {
    marginBottom: 20,
  },
  confidenceText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  confidenceBar: {
    height: 6,
    backgroundColor: '#f0f0f0',
    borderRadius: 3,
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#FF8C42',
    borderRadius: 3,
  },
  itemsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
  },
  outfitItem: {
    alignItems: 'center',
    flex: 1,
  },
  itemImage: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#f0f0f0',
    marginBottom: 8,
  },
  itemName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
    marginBottom: 2,
  },
  itemCategory: {
    fontSize: 10,
    color: '#666',
    textAlign: 'center',
  },
  reasonContainer: {
    backgroundColor: '#f8f8f8',
    padding: 15,
    borderRadius: 10,
  },
  reasonTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  reasonText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  dislikeButton: {
    flex: 1,
    backgroundColor: '#666',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    marginRight: 5,
  },
  likeButton: {
    flex: 1,
    backgroundColor: '#e74c3c',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    marginHorizontal: 5,
  },
  wearButton: {
    flex: 1,
    backgroundColor: '#27ae60',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    marginLeft: 5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 5,
  },
});

export default GetOutfitScreen;