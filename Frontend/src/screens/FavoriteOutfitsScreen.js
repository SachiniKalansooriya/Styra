import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
  RefreshControl,
  TextInput,
  Modal
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import favoriteOutfitService from '../services/favoriteOutfitService';

const FavoriteOutfitsScreen = ({ navigation }) => {
  console.log('FavoriteOutfitsScreen component rendering');
  
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedFavorite, setSelectedFavorite] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editName, setEditName] = useState('');
  const [editNotes, setEditNotes] = useState('');

  useEffect(() => {
    console.log('FavoriteOutfitsScreen mounted');
    loadFavorites();
    
    // Add a focus listener to reload data when the screen is focused
    // Check if addListener exists (for React Navigation compatibility)
    if (navigation.addListener) {
      const unsubscribe = navigation.addListener('focus', () => {
        console.log('FavoriteOutfits screen focused - reloading data');
        loadFavorites();
      });
      
      // Cleanup on unmount
      return unsubscribe;
    }
  }, [navigation]);

  const loadFavorites = async () => {
    try {
      setLoading(true);
      console.log('Attempting to load favorites for user id: 1');
      const response = await favoriteOutfitService.getUserFavorites(1);
      
      console.log('Favorites response:', JSON.stringify(response));
      
      if (response && response.status === 'success') {
        setFavorites(response.favorites || []);
        console.log('Favorites loaded successfully:', response.favorites?.length || 0);
      } else {
        console.log('No favorites found or error in response');
        setFavorites([]);
      }
    } catch (error) {
      console.error('Error loading favorites:', error);
      Alert.alert('Error', 'Failed to load favorite outfits. Please try again.');
      setFavorites([]);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadFavorites();
    setRefreshing(false);
  };

  const handleFavoritePress = (favorite) => {
    setSelectedFavorite(favorite);
    setModalVisible(true);
    setEditMode(false);
    setEditName(favorite.name);
    setEditNotes(favorite.notes || '');
  };

  const handleWearFavorite = async (favoriteId) => {
    try {
      Alert.alert(
        'Wear Outfit',
        'Mark this outfit as worn today?',
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Yes',
            onPress: async () => {
              try {
                console.log('Marking outfit as worn:', favoriteId);
                Alert.alert('Success', 'Outfit marked as worn today!');
              } catch (error) {
                console.error('Error marking outfit as worn:', error);
                Alert.alert('Error', 'Failed to mark outfit as worn.');
              }
            }
          }
        ]
      );
    } catch (error) {
      console.error('Error in handleWearFavorite:', error);
    }
  };

  const handleDeleteFavorite = async (favoriteId, favoriteName) => {
    try {
      Alert.alert(
        'Delete Favorite',
        `Are you sure you want to delete "${favoriteName}"?`,
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Delete',
            style: 'destructive',
            onPress: async () => {
              try {
                const response = await favoriteOutfitService.deleteFavorite(1, favoriteId);
                if (response && response.status === 'success') {
                  Alert.alert('Success', 'Favorite outfit deleted successfully');
                  loadFavorites();
                } else {
                  throw new Error(response?.message || 'Failed to delete favorite');
                }
              } catch (error) {
                console.error('Error deleting favorite:', error);
                Alert.alert('Error', 'Failed to delete favorite outfit.');
              }
            }
          }
        ]
      );
    } catch (error) {
      console.error('Error in handleDeleteFavorite:', error);
    }
  };

  const handleSaveEdit = async () => {
    if (!selectedFavorite || !editName.trim()) return;

    try {
      setLoading(true);
      const response = await favoriteOutfitService.updateFavorite(
        1,
        selectedFavorite.id,
        {
          name: editName.trim(),
          notes: editNotes.trim()
        }
      );

      if (response && response.status === 'success') {
        Alert.alert('Success', 'Favorite outfit updated successfully');
        loadFavorites();
        setModalVisible(false);
        setEditMode(false);
      } else {
        throw new Error(response?.message || 'Failed to update favorite');
      }
    } catch (error) {
      console.error('Error updating favorite:', error);
      Alert.alert('Error', 'Failed to update favorite outfit. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderFavoriteItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.favoriteCard} 
      onPress={() => handleFavoritePress(item)}
    >
      <View style={styles.favoriteHeader}>
        <View style={styles.favoriteInfo}>
          <Text style={styles.favoriteName}>{item.name}</Text>
          <Text style={styles.favoriteOccasion}>{item.occasion || 'Casual'}</Text>
          <Text style={styles.favoriteDate}>
            Added {new Date(item.created_at).toLocaleDateString()}
          </Text>
        </View>
        <View style={styles.favoriteStats}>
          <Text style={styles.confidenceText}>{item.confidence}% match</Text>
          <Text style={styles.wornText}>Worn {item.times_worn || 0} times</Text>
        </View>
      </View>
      
      <View style={styles.outfitItemsPreview}>
        {item.items && item.items.slice(0, 4).map((outfitItem, index) => (
          <View key={index} style={styles.previewItem}>
            <Image 
              source={{ 
                uri: outfitItem.image_path ? 
                  `http://172.20.10.7:8000${outfitItem.image_path}` : 
                  'https://via.placeholder.com/60' 
              }} 
              style={styles.previewImage} 
            />
            <Text style={styles.previewItemName} numberOfLines={1}>
              {outfitItem.name}
            </Text>
          </View>
        ))}
        {item.items && item.items.length > 4 && (
          <View style={styles.moreItems}>
            <Text style={styles.moreItemsText}>+{item.items.length - 4}</Text>
          </View>
        )}
      </View>
      
      <View style={styles.favoriteActions}>
        <TouchableOpacity 
          style={styles.wearFavoriteButton}
          onPress={() => handleWearFavorite(item.id)}
        >
          <Ionicons name="checkmark-circle" size={18} color="#fff" />
          <Text style={styles.actionButtonText}>Wear Today</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.deleteFavoriteButton}
          onPress={() => handleDeleteFavorite(item.id, item.name)}
        >
          <Ionicons name="trash" size={18} color="#fff" />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="heart-outline" size={80} color="#ccc" />
      <Text style={styles.emptyTitle}>No Favorite Outfits</Text>
      <Text style={styles.emptyText}>
        Save your favorite outfit combinations from the Get Outfit screen to see them here.
      </Text>
      <TouchableOpacity 
        style={styles.getOutfitButton}
        onPress={() => navigation.navigate('GetOutfit')}
      >
        <Text style={styles.getOutfitButtonText}>Generate Outfits</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Favorite Outfits</Text>
        <View style={styles.placeholder} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FF8C42" />
          <Text style={styles.loadingText}>Loading favorites...</Text>
        </View>
      ) : (
        <FlatList
          data={favorites}
          renderItem={renderFavoriteItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={favorites.length === 0 ? styles.emptyList : styles.listContainer}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={renderEmptyState}
        />
      )}

      {/* Modal for favorite details */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={24} color="#333" />
              </TouchableOpacity>
              <Text style={styles.modalTitle}>
                {editMode ? 'Edit Favorite' : selectedFavorite?.name}
              </Text>
              <View style={{ width: 24 }} />
            </View>

            <View style={styles.modalBody}>
              {editMode ? (
                <>
                  <Text style={styles.inputLabel}>Outfit Name</Text>
                  <TextInput
                    style={styles.textInput}
                    value={editName}
                    onChangeText={setEditName}
                    placeholder="Enter outfit name"
                  />
                  
                  <Text style={styles.inputLabel}>Notes</Text>
                  <TextInput
                    style={[styles.textInput, styles.textArea]}
                    value={editNotes}
                    onChangeText={setEditNotes}
                    placeholder="Add notes about this outfit..."
                    multiline
                  />
                  
                  <View style={styles.editActions}>
                    <TouchableOpacity 
                      style={styles.cancelButton}
                      onPress={() => setEditMode(false)}
                    >
                      <Text style={styles.cancelButtonText}>Cancel</Text>
                    </TouchableOpacity>
                    
                    <TouchableOpacity 
                      style={styles.saveButton}
                      onPress={handleSaveEdit}
                    >
                      <Text style={styles.saveButtonText}>Save</Text>
                    </TouchableOpacity>
                  </View>
                </>
              ) : (
                selectedFavorite && (
                  <>
                    <Text style={styles.detailName}>{selectedFavorite.name}</Text>
                    <Text style={styles.detailOccasion}>{selectedFavorite.occasion || 'Casual'}</Text>
                    <Text style={styles.detailStats}>
                      {selectedFavorite.confidence}% match • Worn {selectedFavorite.times_worn || 0} times
                    </Text>
                    
                    {selectedFavorite.notes && (
                      <View style={styles.notesSection}>
                        <Text style={styles.notesLabel}>Notes</Text>
                        <Text style={styles.notesText}>{selectedFavorite.notes}</Text>
                      </View>
                    )}
                    
                    <View style={styles.modalActions}>
                      <TouchableOpacity 
                        style={styles.editButton}
                        onPress={() => setEditMode(true)}
                      >
                        <Ionicons name="pencil" size={16} color="#fff" />
                        <Text style={styles.editButtonText}>Edit</Text>
                      </TouchableOpacity>
                      
                      <TouchableOpacity 
                        style={styles.wearButton}
                        onPress={() => handleWearFavorite(selectedFavorite.id)}
                      >
                        <Ionicons name="checkmark-circle" size={16} color="#fff" />
                        <Text style={styles.wearButtonText}>Wear Today</Text>
                      </TouchableOpacity>
                    </View>
                  </>
                )
              )}
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    paddingTop: 50,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  placeholder: {
    width: 24,
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
    padding: 15,
  },
  emptyList: {
    flex: 1,
  },
  favoriteCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  favoriteHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  favoriteInfo: {
    flex: 1,
  },
  favoriteName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  favoriteOccasion: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  favoriteDate: {
    fontSize: 12,
    color: '#999',
  },
  favoriteStats: {
    alignItems: 'flex-end',
  },
  confidenceText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF8C42',
    marginBottom: 4,
  },
  wornText: {
    fontSize: 12,
    color: '#666',
  },
  outfitItemsPreview: {
    flexDirection: 'row',
    marginBottom: 15,
  },
  previewItem: {
    alignItems: 'center',
    marginRight: 15,
    width: 60,
  },
  previewImage: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#f0f0f0',
    marginBottom: 5,
  },
  previewItemName: {
    fontSize: 10,
    color: '#666',
    textAlign: 'center',
  },
  moreItems: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  moreItemsText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
  },
  favoriteActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  wearFavoriteButton: {
    flex: 1,
    backgroundColor: '#27ae60',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 10,
    borderRadius: 8,
    marginRight: 10,
  },
  deleteFavoriteButton: {
    backgroundColor: '#e74c3c',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 15,
    borderRadius: 8,
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 5,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333',
    marginTop: 20,
    marginBottom: 10,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
  },
  getOutfitButton: {
    backgroundColor: '#FF8C42',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  getOutfitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingTop: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  modalBody: {
    padding: 20,
  },
  detailName: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  detailOccasion: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  detailStats: {
    fontSize: 14,
    color: '#FF8C42',
    marginBottom: 20,
  },
  notesSection: {
    marginBottom: 20,
  },
  notesLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  notesText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 15,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  editButton: {
    flex: 1,
    backgroundColor: '#9b59b6',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    marginRight: 10,
  },
  editButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 5,
  },
  wearButton: {
    flex: 1,
    backgroundColor: '#27ae60',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
  },
  wearButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 5,
  },
  editActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#666',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    marginRight: 10,
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  saveButton: {
    flex: 1,
    backgroundColor: '#27ae60',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default FavoriteOutfitsScreen;
