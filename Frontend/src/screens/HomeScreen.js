import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, Modal, Alert } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';

import { useTheme } from '../themes/ThemeProvider';
import { Card } from '../components/common/Card';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { cameraBackend } from '../utils/storage';
import connectionService from '../services/connectionService';
import apiService from '../services/apiService';
import wardrobeService from '../services/wardrobeService';

export default function HomeScreen({ navigation, backendConnected }) {
  const { theme } = useTheme();
  const [showCameraModal, setShowCameraModal] = useState(false);
  const [permission, requestPermission] = useCameraPermissions();
  const [cameraType, setCameraType] = useState('back');
  const [connectionStatus, setConnectionStatus] = useState(backendConnected);
  const cameraRef = useRef();

  // Test backend connection when component mounts
  useEffect(() => {
    setConnectionStatus(backendConnected);
  }, [backendConnected]);

  // Test API connection
  const testApiConnection = async () => {
    try {
      const result = await connectionService.testAllServices();
      
      if (result.backend.success) {
        Alert.alert(
          '✅ Connection Successful!', 
          `Backend is working perfectly!\n\n• Health: ${result.health?.data?.status || 'Unknown'}\n• Database: ${result.health?.data?.database || 'Unknown'}\n• Status: Online mode active`,
          [{ text: 'Great!' }]
        );
        setConnectionStatus(true);
      } else {
        Alert.alert(
          '📱 Offline Mode Active', 
          `Can't reach backend server, but the app works offline!\n\n• Error: ${result.backend.message}\n• Features: Local storage active\n• Mock data: Available\n\n💡 To fix: Make sure backend is running on http://172.20.10.7:8000`,
          [
            { text: 'Use Offline', style: 'default' },
            { text: 'Retry', onPress: testApiConnection }
          ]
        );
        setConnectionStatus(false);
      }
    } catch (error) {
      Alert.alert(
        '⚠️ Connection Test Failed', 
        `Error testing connection: ${error.message}\n\nThe app will work in offline mode.`,
        [{ text: 'OK' }]
      );
      setConnectionStatus(false);
    }
  };

  // Handle camera action
  const handleCameraAction = async () => {
  Alert.alert(
    'Add Clothing Item',
    'Choose how you want to add a new clothing item:',
    [
      {
        text: '📷 Take Photo',
        onPress: openCamera,
      },
      {
        text: '🖼️ Choose from Gallery',
        onPress: pickImageFromGallery,
      },
      {
        text: '✏️ Add Manually',
        onPress: () => navigation.navigate('AddClothes', { 
          backendConnected: connectionStatus,
          manualEntry: true
        }),
      },
      {
        text: 'Cancel',
        style: 'cancel',
      },
    ]
  );
};
  // Open camera function
  const openCamera = async () => {
  if (!permission) {
    return;
  }

  if (!permission.granted) {
    const response = await requestPermission();
    if (!response.granted) {
      Alert.alert(
        'Camera Permission Required',
        'Please allow camera access to take photos of your clothes.',
        [{ text: 'OK' }]
      );
      return;
    }
  }

  navigation.navigate('AddClothes', { 
    backendConnected: connectionStatus,
    openCamera: true
  });
};
  // Take picture with camera
  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
          base64: false,
          skipProcessing: false,
        });
        
        setShowCameraModal(false);
        
        // Show processing indicator
        Alert.alert('Processing...', 'Analyzing your clothing item...', [], { cancelable: false });
        
        try {
          // Process the image using camera backend
          const processedItem = await cameraBackend.processNewClothingItem(photo.uri, {
            captureMethod: 'camera',
            timestamp: new Date().toISOString(),
          });
          
          // Navigate to AddClothes screen with processed data
          navigation.navigate('AddClothes', { 
            processedItem,
            fromCamera: true,
            backendConnected: connectionStatus
          });
          
        } catch (error) {
          console.error('Error processing image:', error);
          Alert.alert('Processing Error', 'Failed to process the image. You can still add it manually.', [
            {
              text: 'Add Manually',
              onPress: () => navigation.navigate('AddClothes', { 
                capturedImage: photo.uri,
                fromCamera: true,
                backendConnected: connectionStatus
              })
            },
            { text: 'Cancel', style: 'cancel' }
          ]);
        }
        
      } catch (error) {
        console.error('Camera error:', error);
        Alert.alert('Camera Error', 'Failed to take picture. Please try again.');
      }
    }
  };

  // Pick image from gallery
  const pickImageFromGallery = async () => {
  try {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      Alert.alert('Processing...', 'Analyzing your clothing item...', [], { cancelable: false });
      
      try {
        const processedItem = await cameraBackend.processNewClothingItem(result.assets[0].uri, {
          captureMethod: 'gallery',
          timestamp: new Date().toISOString(),
        });
        
        navigation.navigate('AddClothes', { 
          processedItem,
          fromGallery: true,
          backendConnected: connectionStatus
        });
        
      } catch (error) {
        console.error('Error processing gallery image:', error);
        Alert.alert('Processing Error', 'Failed to process the image. You can still add it manually.', [
          {
            text: 'Add Manually',
            onPress: () => navigation.navigate('AddClothes', { 
              capturedImage: result.assets[0].uri,
              fromGallery: true,
              backendConnected: connectionStatus
            })
          },
          { text: 'Cancel', style: 'cancel' }
        ]);
      }
    }
  } catch (error) {
    console.error('Gallery picker error:', error);
    Alert.alert('Gallery Error', 'Failed to access gallery. Please try again.');
  }
};

  const mockOutfits = [
    { 
      id: 1, 
      name: "Sunny Day Casual", 
      confidence: 92, 
      weather: "sunny",
      description: "Perfect for a bright day out"
    },
    { 
      id: 2, 
      name: "Rainy Day Cozy", 
      confidence: 88, 
      weather: "rainy",
      description: "Stay warm and stylish"
    },
    { 
      id: 3, 
      name: "Party Night Glam", 
      confidence: 95, 
      weather: "party",
      description: "Turn heads at any event"
    },
    { 
      id: 4, 
      name: "Professional Look", 
      confidence: 90, 
      weather: "cloudy",
      description: "Confident and business-ready"
    },
  ];

  const quickActions = [
    {
      id: 1,
      title: "Add Clothes",
      icon: "camera-outline",
      color: theme.primary,
      description: "Photograph new items",
      action: () => handleCameraAction(),
    },
    {
      id: 2,
      title: "My Wardrobe",
      icon: "shirt-outline",
      color: theme.secondary,
      description: "Browse your collection",
      action: () => navigation.navigate('MyWardrobe'),
    },
    {
      id: 3,
      title: "Get Outfit",
      icon: "sparkles-outline",
      color: theme.accent,
      description: "AI recommendations",
      action: () => navigation.navigate('GetOutfit'),
    },
    {
      id: 4,
      title: "Trip Planner",
      icon: "airplane-outline",
      color: "#9C27B0",
      description: "Pack smart for travel",
      action: () => navigation.navigate('TripPlanner'),
    },
    {
      id: 5,
      title: "Test Backend",
      icon: connectionStatus ? "checkmark-circle-outline" : "alert-circle-outline",
      color: connectionStatus ? "#4CAF50" : "#FF5722",
      description: connectionStatus ? "Backend connected" : "Test connection",
      action: () => testApiConnection(),
    },
  ];

  return (
    <LinearGradient 
      colors={theme.background} 
      style={styles.container}
    >
      <StatusBar style="auto" />
      
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={[styles.greeting, { color: theme.text }]}>Good Morning! ☀️</Text>
          <Text style={[styles.title, { color: theme.text }]}>✨ Styra</Text>
          <View style={styles.connectionStatus}>
            <Ionicons 
              name={connectionStatus ? "checkmark-circle" : "close-circle"} 
              size={12} 
              color={connectionStatus ? "#4CAF50" : "#FF5722"} 
            />
            <Text style={[styles.connectionText, { color: connectionStatus ? "#4CAF50" : "#FF5722" }]}>
              {connectionStatus ? "Backend Connected" : "Offline Mode"}
            </Text>
          </View>
        </View>
        <TouchableOpacity 
          style={[styles.button, { backgroundColor: theme.primary }]}
          onPress={handleCameraAction}
        >
          <Text style={styles.buttonText}>📷 Add Clothes</Text>
        </TouchableOpacity>
      </View>

      <ScrollView 
        style={styles.content} 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        
        {/* Quick Actions Grid */}
        <Card style={styles.actionsCard}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>⚡ Quick Actions</Text>
          <View style={styles.actionsGrid}>
            {quickActions.map((action) => (
              <TouchableOpacity
                key={action.id}
                style={[styles.actionItem, { borderColor: action.color }]}
                onPress={action.action}
              >
                <View style={[styles.actionIcon, { backgroundColor: action.color }]}>
                  <Ionicons name={action.icon} size={24} color="white" />
                </View>
                <Text style={[styles.actionTitle, { color: theme.text }]}>
                  {action.title}
                </Text>
                <Text style={[styles.actionDescription, { color: theme.text }]}>
                  {action.description}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Card>

        {/* Today's Outfit Suggestions */}
        <Card style={styles.outfitsCard}>
          <View style={styles.cardHeader}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>✨ Today's Picks</Text>
            <TouchableOpacity>
              <Text style={[styles.seeAll, { color: theme.primary }]}>See All</Text>
            </TouchableOpacity>
          </View>
          
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.outfitsList}
            contentContainerStyle={styles.outfitsListContent}
          >
            {mockOutfits.map((outfit) => (
              <View key={outfit.id} style={styles.outfitCard}>
                <View style={styles.outfitImagePlaceholder}>
                  <Ionicons name="shirt-outline" size={40} color={theme.primary} />
                </View>
                
                <View style={styles.outfitInfo}>
                  <View style={styles.outfitHeader}>
                    <Text style={[styles.outfitName, { color: theme.text }]} numberOfLines={1}>
                      {outfit.name}
                    </Text>
                  </View>
                  
                  <Text style={[styles.outfitDescription, { color: theme.text }]} numberOfLines={2}>
                    {outfit.description}
                  </Text>
                  
                  <View style={styles.outfitFooter}>
                    <ConfidenceBadge confidence={outfit.confidence} />
                    <TouchableOpacity style={styles.heartButton}>
                      <Ionicons name="heart-outline" size={20} color={theme.primary} />
                    </TouchableOpacity>
                  </View>
                </View>
              </View>
            ))}
          </ScrollView>
        </Card>

        {/* Weather Info Card */}
        <Card style={styles.weatherCard}>
          <View style={styles.weatherHeader}>
            <View>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>🌡️ Today's Weather</Text>
              <Text style={[styles.weatherLocation, { color: theme.text }]}>
                Negombo, Western Province
              </Text>
            </View>
            <View style={styles.weatherInfo}>
              <Text style={[styles.weatherTemp, { color: theme.primary }]}>28°C</Text>
              <Text style={[styles.weatherCondition, { color: theme.text }]}>Clear</Text>
            </View>
          </View>
          <Text style={[styles.weatherSuggestion, { color: theme.text }]}>
            Perfect weather for light, breathable fabrics! ✨
          </Text>
        </Card>

        {/* Statistics Card */}
        <Card style={styles.statsCard}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>📊 Your Style Stats</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: theme.primary }]}>47</Text>
              <Text style={[styles.statLabel, { color: theme.text }]}>Items</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: theme.primary }]}>23</Text>
              <Text style={[styles.statLabel, { color: theme.text }]}>Outfits</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: theme.primary }]}>12</Text>
              <Text style={[styles.statLabel, { color: theme.text }]}>Favorites</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: theme.primary }]}>89%</Text>
              <Text style={[styles.statLabel, { color: theme.text }]}>Match Rate</Text>
            </View>
          </View>
        </Card>

      </ScrollView>

      {/* Camera Modal */}
      <Modal
        visible={showCameraModal}
        animationType="slide"
        presentationStyle="fullScreen"
      >
        <View style={styles.cameraModal}>
          {!permission ? (
            <View style={styles.permissionContainer}>
              <Text style={styles.permissionText}>Requesting camera permission...</Text>
            </View>
          ) : !permission.granted ? (
            <View style={styles.permissionContainer}>
              <Text style={styles.permissionText}>No camera access</Text>
              <TouchableOpacity
                style={[styles.permissionButton, { backgroundColor: theme.primary }]}
                onPress={requestPermission}
              >
                <Text style={styles.permissionButtonText}>Grant Permission</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <>
              <CameraView
                style={styles.camera}
                facing={cameraType}
                ref={cameraRef}
              >
                <View style={styles.cameraOverlay}>
                  {/* Close button */}
                  <TouchableOpacity
                    style={styles.closeButton}
                    onPress={() => setShowCameraModal(false)}
                  >
                    <Ionicons name="close" size={30} color="white" />
                  </TouchableOpacity>

                  {/* Camera controls */}
                  <View style={styles.cameraControls}>
                    {/* Gallery button */}
                    <TouchableOpacity
                      style={styles.controlButton}
                      onPress={pickImageFromGallery}
                    >
                      <Ionicons name="images" size={30} color="white" />
                    </TouchableOpacity>

                    {/* Capture button */}
                    <TouchableOpacity
                      style={styles.captureButton}
                      onPress={takePicture}
                    >
                      <View style={styles.captureButtonInner} />
                    </TouchableOpacity>

                    {/* Flip camera button */}
                    <TouchableOpacity
                      style={styles.controlButton}
                      onPress={() => {
                        setCameraType(
                          cameraType === 'back' ? 'front' : 'back'
                        );
                      }}
                    >
                      <Ionicons name="camera-reverse" size={30} color="white" />
                    </TouchableOpacity>
                  </View>
                </View>
              </CameraView>
            </>
          )}
        </View>
      </Modal>
    </LinearGradient>
  );
}

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
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  connectionText: {
    fontSize: 10,
    marginLeft: 4,
    fontWeight: '500',
  },
  greeting: {
    fontSize: 16,
    opacity: 0.8,
    marginBottom: 4,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  button: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  buttonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  profileButton: {
    padding: 8,
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 30,
  },
  
  // Card Styles
  actionsCard: {
    marginBottom: 16,
  },
  outfitsCard: {
    marginBottom: 16,
  },
  weatherCard: {
    marginBottom: 16,
  },
  statsCard: {
    marginBottom: 16,
  },
  
  // Header Styles
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  sectionSubtitle: {
    fontSize: 14,
    opacity: 0.7,
    marginTop: 2,
  },
  seeAll: {
    fontSize: 14,
    fontWeight: '600',
  },

  // Quick Actions
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  actionItem: {
    width: '48%',
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 16,
    borderRadius: 16,
    borderWidth: 2,
    marginBottom: 12,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  actionIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
    textAlign: 'center',
  },
  actionDescription: {
    fontSize: 12,
    opacity: 0.7,
    textAlign: 'center',
  },

  // Outfits List
  outfitsList: {
    marginTop: 8,
  },
  outfitsListContent: {
    paddingRight: 16,
  },
  outfitCard: {
    width: 180,
    marginRight: 16,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 16,
    overflow: 'hidden',
  },
  outfitImagePlaceholder: {
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  outfitInfo: {
    padding: 12,
  },
  outfitHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  outfitName: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  outfitDescription: {
    fontSize: 12,
    opacity: 0.8,
    marginBottom: 12,
    lineHeight: 16,
  },
  outfitFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  heartButton: {
    padding: 4,
  },

  // Weather Card
  weatherHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  weatherLocation: {
    fontSize: 14,
    opacity: 0.7,
    marginTop: 2,
  },
  weatherInfo: {
    alignItems: 'flex-end',
  },
  weatherTemp: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  weatherCondition: {
    fontSize: 14,
    opacity: 0.8,
  },
  weatherSuggestion: {
    fontSize: 14,
    fontStyle: 'italic',
    opacity: 0.8,
    textAlign: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.2)',
  },

  // Stats Grid
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    opacity: 0.8,
  },

  // Camera Modal Styles
  cameraModal: {
    flex: 1,
    backgroundColor: 'black',
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
    backgroundColor: 'transparent',
    justifyContent: 'space-between',
  },
  closeButton: {
    position: 'absolute',
    top: 50,
    left: 20,
    zIndex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 25,
    width: 50,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cameraControls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingBottom: 40,
    paddingHorizontal: 20,
  },
  controlButton: {
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 30,
    width: 60,
    height: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButton: {
    backgroundColor: 'white',
    borderRadius: 40,
    width: 80,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: 'rgba(255,255,255,0.3)',
  },
  captureButtonInner: {
    backgroundColor: 'white',
    borderRadius: 30,
    width: 60,
    height: 60,
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  permissionText: {
    color: 'white',
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
  },
  permissionButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});