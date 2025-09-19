import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  Image,
  Modal,
  TextInput,
  ScrollView,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import * as MediaLibrary from 'expo-media-library';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useTheme } from '../themes/ThemeProvider';
import { cameraBackend } from '../utils/storage';
import wardrobeService from '../services/wardrobeService';
import Icon from 'react-native-vector-icons/MaterialIcons';

const AddClothesScreen = ({ navigation, backendConnected }) => {
  const { theme } = useTheme();
  const [permission, requestPermission] = useCameraPermissions();
  const [cameraType, setCameraType] = useState('back');
  const [capturedImage, setCapturedImage] = useState(null);
  const [showCategorizeModal, setShowCategorizeModal] = useState(false);
  const [processedItem, setProcessedItem] = useState(null);
  const [saving, setSaving] = useState(false);
  const [itemDetails, setItemDetails] = useState({
    name: '',
    category: '',
    color: '',
    season: 'all',
    occasion: '',
  });
  const cameraRef = useRef();

  useEffect(() => {
    // Check if we received processed item data from params
    if (navigation.params?.processedItem) {
      const processed = navigation.params.processedItem;
      setProcessedItem(processed);
      setCapturedImage(processed.imageData.localUri);
      
      setItemDetails({
        name: '',
        category: processed.suggestedCategory || '',
        color: processed.suggestedColor || '',
        season: 'all',
        occasion: processed.suggestedOccasion || '',
      });
      
      setShowCategorizeModal(true);
    }
  }, [navigation.params]);

  useEffect(() => {
    getPermissions();
  }, []);

  const getPermissions = async () => {
    if (!permission) {
      await requestPermission();
    }
    const { status: mediaStatus } = await MediaLibrary.requestPermissionsAsync();
    const { status: imagePickerStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();
  };

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.7,
          base64: false,
        });
        
        try {
          const processed = await cameraBackend.processNewClothingItem(photo.uri, {
            captureMethod: 'camera',
            timestamp: new Date().toISOString(),
          });
          
          setProcessedItem(processed);
          setCapturedImage(processed.imageData.localUri);
          
          setItemDetails({
            name: '',
            category: processed.suggestedCategory || '',
            color: processed.suggestedColor || '',
            season: 'all',
            occasion: processed.suggestedOccasion || '',
          });
          
          setShowCategorizeModal(true);
        } catch (error) {
          console.error('Error processing image:', error);
          Alert.alert('Processing Error', 'Failed to process the image. You can still add it manually.', [
            {
              text: 'Add Manually',
              onPress: () => {
                setCapturedImage(photo.uri);
                setShowCategorizeModal(true);
              }
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

 const pickImageFromGallery = async () => {
  try {
    // Request permissions first
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Sorry, we need camera roll permissions to select photos.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.8,
      allowsMultipleSelection: false, // Only single selection
    });

    if (!result.canceled && result.assets && result.assets[0]) {
      const selectedImage = result.assets[0];
      
      // Show processing indicator
      Alert.alert('Processing...', 'Analyzing your clothing item...', [], { cancelable: false });
      
      try {
        const processed = await cameraBackend.processNewClothingItem(selectedImage.uri, {
          captureMethod: 'gallery',
          timestamp: new Date().toISOString(),
        });
        
        setProcessedItem(processed);
        setCapturedImage(processed.imageData.localUri);
        
        setItemDetails({
          name: '',
          category: processed.suggestedCategory || '',
          color: processed.suggestedColor || '',
          season: 'all',
        });
        
        setShowCategorizeModal(true);
        
      } catch (error) {
        console.error('Error processing image:', error);
        Alert.alert('Processing Error', 'Failed to process the selected image. You can still add it manually.', [
          {
            text: 'Add Manually',
            onPress: () => {
              setCapturedImage(selectedImage.uri);
              setShowCategorizeModal(true);
            }
          },
          { text: 'Cancel', style: 'cancel' }
        ]);
      }
    }
  } catch (error) {
    console.error('Gallery error:', error);
    Alert.alert('Error', 'Failed to access gallery. Please try again.');
  }
};
  const saveClothingItem = async () => {
    if (!itemDetails.name || !itemDetails.category) {
      Alert.alert('Missing Information', 'Please fill in at least the item name and category');
      return;
    }

    setSaving(true);

    try {
      const finalItemData = {
        ...processedItem,
        name: itemDetails.name,
        category: itemDetails.category,
        color: itemDetails.color || processedItem?.suggestedColor || '',
        season: itemDetails.season,
        occasion: itemDetails.occasion || processedItem?.suggestedOccasion || '',
        image: capturedImage,
        dateAdded: new Date().toISOString(),
        pendingSync: !backendConnected,
      };

      const result = await wardrobeService.addWardrobeItem(finalItemData);
      
      if (result.source === 'backend') {
        Alert.alert(
          'Success!', 
          'Clothing item saved to your wardrobe!\n\nSynced with backend\nSaved locally as backup',
          [
            {
              text: 'Add Another',
              onPress: resetForm
            },
            {
              text: 'View Wardrobe',
              onPress: () => navigation.navigate('MyWardrobe')
            }
          ]
        );
      } else {
        Alert.alert(
          result.pendingSync ? 'Saved Locally' : 'Saved!', 
          result.message,
          [
            {
              text: 'Add Another',
              onPress: resetForm
            },
            {
              text: 'View Wardrobe',
              onPress: () => navigation.navigate('MyWardrobe')
            }
          ]
        );
      }
      
    } catch (error) {
      console.error('Error saving item:', error);
      Alert.alert(
        'Save Failed', 
        `Failed to save clothing item: ${error.message}\n\nPlease try again or check your connection.`,
        [{ text: 'OK' }]
      );
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setShowCategorizeModal(false);
    setCapturedImage(null);
    setProcessedItem(null);
    setItemDetails({ name: '', category: '', color: '', season: 'all', occasion: '' });
  };

  const categories = [
    { key: 'tops', label: 'Tops', emoji: '👕' },
    { key: 'bottoms', label: 'Bottoms', emoji: '👖' },
    { key: 'dresses', label: 'Dresses', emoji: '👗' },
    { key: 'shoes', label: 'Shoes', emoji: '👟' },
    { key: 'accessories', label: 'Accessories', emoji: '👜' },
    { key: 'outerwear', label: 'Outerwear', emoji: '🧥' },
    { key: 'sportswear', label: 'Sportswear', emoji: '🏃' },
    { key: 'formal', label: 'Formal', emoji: '🤵' },
    { key: 'sleepwear', label: 'Sleepwear', emoji: '🛌' },
    { key: 'underwear', label: 'Underwear', emoji: '🩲' },
  ];

  const colors = [
    'Black', 'White', 'Gray', 'Red', 'Blue', 'Green', 
    'Yellow', 'Pink', 'Purple', 'Brown', 'Orange', 'Beige',
    'Multicolor', 'Metallic', 'Pastel'
  ];
  
  const occasions = [
    { key: 'casual', label: 'Casual', emoji: '🏡' },
    { key: 'formal', label: 'Formal', emoji: '🎭' },
    { key: 'business', label: 'Business', emoji: '💼' },
    { key: 'athletic', label: 'Athletic', emoji: '🏋️' },
    { key: 'beachwear', label: 'Beach', emoji: '🏖️' },
    { key: 'party', label: 'Party', emoji: '🎉' },
    { key: 'datenight', label: 'Date Night', emoji: '💕' },
    { key: 'seasonal', label: 'Seasonal', emoji: '🍂' },
  ];

  const seasons = [
    { key: 'all', label: 'All Seasons' },
    { key: 'spring', label: 'Spring' },
    { key: 'summer', label: 'Summer' },
    { key: 'fall', label: 'Fall' },
    { key: 'winter', label: 'Winter' },
  ];

  if (!permission) {
    return (
      <View style={styles.container}>
        <Text>Requesting permissions...</Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <LinearGradient colors={theme.background} style={styles.container}>
        <View style={styles.permissionContainer}>
          <Text style={[styles.permissionText, { color: theme.text }]}>
            Camera permission needed
          </Text>
          <Text style={[styles.permissionSubtext, { color: theme.text }]}>
            To add clothes to your wardrobe, we need access to your camera and photo library.
          </Text>
          <TouchableOpacity 
            style={[styles.permissionButton, { backgroundColor: theme.primary }]}
            onPress={requestPermission}
          >
            <Text style={styles.permissionButtonText}>Grant Permissions</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Add New Item</Text>
        <View style={styles.placeholder} />
      </View>

      <CameraView 
        style={styles.camera} 
        facing={cameraType}
        ref={cameraRef}
      >
        <View style={styles.cameraContent}>
          
          <View style={styles.topControls}>
            <TouchableOpacity 
              style={styles.flipButton}
              onPress={() => {
                setCameraType(cameraType === 'back' ? 'front' : 'back');
              }}
            >
              <Icon name="flip-camera-ios" size={24} color="white" />
            </TouchableOpacity>
          </View>

          <View style={styles.bottomControls}>
            <TouchableOpacity 
  style={styles.galleryButton}
  onPress={pickImageFromGallery}
>
  <Icon name="photo-library" size={24} color="white" />

</TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.captureButton}
              onPress={takePicture}
            >
              <View style={styles.captureButtonInner} />
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.tipButton}
              onPress={() => Alert.alert('Tips', 'For best results:\n• Good lighting\n• Plain background\n• Item laid flat\n• Fill the frame')}
            >
              <Text style={styles.controlText}>💡</Text>
    
            </TouchableOpacity>
          </View>
        </View>
      </CameraView>

      <Modal
        visible={showCategorizeModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <LinearGradient colors={theme.background} style={styles.modalContainer}>
          <ScrollView style={styles.modalContent}>
            
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: theme.text }]}>
                Categorize Your Item
              </Text>
              <TouchableOpacity 
                onPress={() => setShowCategorizeModal(false)}
                style={styles.closeButton}
              >
                <Text style={styles.closeText}>✕</Text>
              </TouchableOpacity>
            </View>

            {capturedImage && (
              <View style={styles.imagePreviewContainer}>
                <Image source={{ uri: capturedImage }} style={styles.imagePreview} />
              </View>
            )}

            <View style={styles.inputSection}>
              <Text style={[styles.inputLabel, { color: theme.text }]}>Item Name</Text>
              <TextInput
                style={[styles.textInput, { borderColor: '#DCC9A7', color: theme.text }]}
                placeholder="e.g., Blue Cotton T-Shirt"
                placeholderTextColor="rgba(128,128,128,0.7)"
                value={itemDetails.name}
                onChangeText={(text) => setItemDetails(prev => ({ ...prev, name: text }))}
              />
            </View>

            <View style={styles.inputSection}>
              <Text style={[styles.inputLabel, { color: theme.text }]}>Category</Text>
              <View style={styles.categoryGrid}>
                {categories.map((cat) => (
                  <TouchableOpacity
                    key={cat.key}
                    style={[
                      styles.categoryButton,
                      {
                        backgroundColor: itemDetails.category === cat.key 
                          ? '#8A724C' 
                          : 'rgba(255,255,255,0.2)',
                        borderColor: itemDetails.category === cat.key 
                          ? '#8A724C' 
                          : 'transparent',
                      }
                    ]}
                    onPress={() => setItemDetails(prev => ({ ...prev, category: cat.key }))}
                  >
                    <Text style={styles.categoryEmoji}>{cat.emoji}</Text>
                    <Text style={[
                      styles.categoryText,
                      { color: itemDetails.category === cat.key ? 'white' : theme.text }
                    ]}>
                      {cat.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.inputSection}>
              <Text style={[styles.inputLabel, { color: theme.text }]}>Primary Color</Text>
              <View style={styles.colorGrid}>
                {colors.map((color) => (
                  <TouchableOpacity
                    key={color}
                    style={[
                      styles.colorButton,
                      {
                        backgroundColor: itemDetails.color === color 
                          ? '#8A724C' 
                          : 'rgba(255,255,255,0.2)',
                        borderWidth: itemDetails.color === color ? 2 : 1,
                        borderColor: itemDetails.color === color 
                          ? 'white' 
                          : 'rgba(255,255,255,0.3)',
                      }
                    ]}
                    onPress={() => setItemDetails(prev => ({ ...prev, color }))}
                  >
                    <Text style={[
                      styles.colorText,
                      { color: itemDetails.color === color ? 'white' : theme.text }
                    ]}>
                      {color}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.inputSection}>
              <Text style={[styles.inputLabel, { color: theme.text }]}>Best Season</Text>
              <View style={styles.seasonGrid}>
                {seasons.map((season) => (
                  <TouchableOpacity
                    key={season.key}
                    style={[
                      styles.seasonButton,
                      {
                        backgroundColor: itemDetails.season === season.key 
                          ? '#8A724C' 
                          : 'rgba(255,255,255,0.2)',
                      }
                    ]}
                    onPress={() => setItemDetails(prev => ({ ...prev, season: season.key }))}
                  >
                    <Text style={[
                      styles.seasonText,
                      { color: itemDetails.season === season.key ? 'white' : theme.text }
                    ]}>
                      {season.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.inputSection}>
              <Text style={[styles.inputLabel, { color: theme.text }]}>Occasion / Place to Wear</Text>
              <View style={styles.seasonGrid}>
                {occasions.map((occasion) => (
                  <TouchableOpacity
                    key={occasion.key}
                    style={[
                      styles.seasonButton,
                      {
                        backgroundColor: itemDetails.occasion === occasion.key 
                          ? '#8A724C' 
                          : 'rgba(255,255,255,0.2)',
                      }
                    ]}
                    onPress={() => setItemDetails(prev => ({ ...prev, occasion: occasion.key }))}
                  >
                    <Text style={[
                      styles.seasonText,
                      { color: itemDetails.occasion === occasion.key ? 'white' : theme.text }
                    ]}>
                      {occasion.emoji} {occasion.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <TouchableOpacity 
              style={[
                styles.saveButton, 
                { 
                  backgroundColor: saving ? 'rgba(100,100,100,0.6)' : '#DCC9A7',
                  opacity: saving ? 0.6 : 1
                }
              ]}
              onPress={saveClothingItem}
              disabled={saving}
            >
              <Text style={[styles.saveButtonText, { color: '#000' }]}>
                {saving ? 'Saving...' : 'Save to Wardrobe'}
              </Text>
            </TouchableOpacity>

            <View style={styles.connectionIndicator}>
              <Text style={[styles.connectionText, { color: theme.text }]}>
                {backendConnected ? 'Online Mode' : 'Offline Mode'}
              </Text>
            </View>

          </ScrollView>
        </LinearGradient>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 10,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  backButton: {
    padding: 5,
  },
  backText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  headerTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  placeholder: {
    width: 50,
  },
  camera: {
    flex: 1,
  },
  cameraContent: {
    flex: 1,
    backgroundColor: 'transparent',
    justifyContent: 'space-between',
  },
  topControls: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  flipButton: {
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 30,
    padding: 15,
  },
  controlText: {
    fontSize: 24,
  },
  bottomControls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingBottom: 40,
    paddingHorizontal: 20,
  },
  galleryButton: {
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 30,
    padding: 15,
  },
  tipButton: {
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 30,
    padding: 15,
  },
  controlLabel: {
    color: 'white',
    fontSize: 12,
    marginTop: 5,
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 5,
    borderColor: 'white',
  },
  captureButtonInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'white',
  },
  
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 30,
  },
  permissionText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  permissionSubtext: {
    fontSize: 16,
    textAlign: 'center',
    opacity: 0.8,
    marginBottom: 30,
    lineHeight: 24,
  },
  permissionButton: {
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
  },
  permissionButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },

  modalContainer: {
    flex: 1,
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    paddingTop: 20,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  closeButton: {
    padding: 10,
  },
  closeText: {
    fontSize: 24,
    color: 'gray',
  },
  imagePreviewContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  imagePreview: {
    width: 200,
    height: 250,
    borderRadius: 15,
    resizeMode: 'cover',
  },
  inputSection: {
    marginBottom: 25,
  },
  inputLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  textInput: {
    borderWidth: 2,
    borderRadius: 15,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  categoryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 20,
    marginBottom: 5,
    borderWidth: 2,
    minWidth: '45%',
  },
  categoryEmoji: {
    fontSize: 20,
    marginRight: 8,
  },
  categoryText: {
    fontSize: 14,
    fontWeight: '600',
  },
  colorGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  colorButton: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 15,
    marginBottom: 5,
    minWidth: 70,
    alignItems: 'center',
  },
  colorText: {
    fontSize: 12,
    fontWeight: '600',
  },
  seasonGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  seasonButton: {
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 20,
    marginBottom: 5,
    minWidth: '30%',
    alignItems: 'center',
  },
  seasonText: {
    fontSize: 14,
    fontWeight: '600',
  },
  saveButton: {
    paddingVertical: 16,
    borderRadius: 25,
    alignItems: 'center',
    marginVertical: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
  },
  saveButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  connectionIndicator: {
    alignItems: 'center',
    paddingVertical: 10,
  },
  connectionText: {
    fontSize: 12,
    opacity: 0.7,
  },
});

export default AddClothesScreen;