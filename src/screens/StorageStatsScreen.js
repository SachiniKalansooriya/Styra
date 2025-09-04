// src/screens/StorageStatsScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useTheme } from '../themes/ThemeProvider';
import { cameraBackend } from '../utils/storage';

const StorageStatsScreen = ({ navigation }) => {
  const { theme } = useTheme();
  const [stats, setStats] = useState({
    totalItems: 0,
    totalImageSize: 0,
    storageLocation: '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const storageStats = await cameraBackend.getStorageStats();
      setStats(storageStats);
    } catch (error) {
      console.error('Error loading storage stats:', error);
      Alert.alert('Error', 'Failed to load storage statistics');
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async () => {
    Alert.alert(
      'Clean Up Storage',
      'This will remove orphaned image files that are no longer associated with wardrobe items. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clean Up',
          onPress: async () => {
            try {
              const deletedCount = await cameraBackend.cleanupOrphanedImages();
              await loadStats(); // Refresh stats
              Alert.alert(
                'Cleanup Complete',
                `Removed ${deletedCount} orphaned image files.`
              );
            } catch (error) {
              console.error('Error during cleanup:', error);
              Alert.alert('Error', 'Failed to clean up storage');
            }
          },
        },
      ]
    );
  };

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 MB';
    const mb = bytes;
    return `${mb.toFixed(2)} MB`;
  };

  if (loading) {
    return (
      <LinearGradient colors={theme.background} style={styles.container}>
        <StatusBar style="auto" />
        <View style={styles.loadingContainer}>
          <Text style={[styles.loadingText, { color: theme.text }]}>
            Loading storage statistics...
          </Text>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={theme.background} style={styles.container}>
      <StatusBar style="auto" />
      
      <View style={[styles.header, { borderBottomColor: theme.border || '#f0f0f0' }]}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color={theme.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: theme.text }]}>Storage Stats</Text>
        <TouchableOpacity onPress={loadStats}>
          <Ionicons name="refresh" size={24} color={theme.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>📊 Overview</Text>
          
          <View style={[styles.statCard, { backgroundColor: theme.cardBackground || 'rgba(255,255,255,0.9)' }]}>
            <View style={styles.statRow}>
              <View style={styles.statInfo}>
                <Ionicons name="shirt-outline" size={24} color={theme.primary} />
                <Text style={[styles.statLabel, { color: theme.text }]}>Total Items</Text>
              </View>
              <Text style={[styles.statValue, { color: theme.primary }]}>
                {stats.totalItems}
              </Text>
            </View>
          </View>

          <View style={[styles.statCard, { backgroundColor: theme.cardBackground || 'rgba(255,255,255,0.9)' }]}>
            <View style={styles.statRow}>
              <View style={styles.statInfo}>
                <Ionicons name="cloud-outline" size={24} color={theme.primary} />
                <Text style={[styles.statLabel, { color: theme.text }]}>Storage Used</Text>
              </View>
              <Text style={[styles.statValue, { color: theme.primary }]}>
                {formatSize(stats.totalImageSize)}
              </Text>
            </View>
          </View>

          <View style={[styles.statCard, { backgroundColor: theme.cardBackground || 'rgba(255,255,255,0.9)' }]}>
            <View style={styles.statRow}>
              <View style={styles.statInfo}>
                <Ionicons name="folder-outline" size={24} color={theme.primary} />
                <Text style={[styles.statLabel, { color: theme.text }]}>Storage Location</Text>
              </View>
            </View>
            <Text style={[styles.locationText, { color: theme.textSecondary || '#666' }]}>
              {stats.storageLocation}
            </Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>🛠️ Maintenance</Text>
          
          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: theme.cardBackground || 'rgba(255,255,255,0.9)' }]}
            onPress={handleCleanup}
          >
            <View style={styles.actionInfo}>
              <Ionicons name="trash-outline" size={24} color="#FF6B6B" />
              <View style={styles.actionTextContainer}>
                <Text style={[styles.actionTitle, { color: theme.text }]}>
                  Clean Up Storage
                </Text>
                <Text style={[styles.actionDescription, { color: theme.textSecondary || '#666' }]}>
                  Remove orphaned image files to free up space
                </Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color={theme.textSecondary || '#666'} />
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: theme.cardBackground || 'rgba(255,255,255,0.9)' }]}
            onPress={loadStats}
          >
            <View style={styles.actionInfo}>
              <Ionicons name="refresh-outline" size={24} color={theme.primary} />
              <View style={styles.actionTextContainer}>
                <Text style={[styles.actionTitle, { color: theme.text }]}>
                  Refresh Statistics
                </Text>
                <Text style={[styles.actionDescription, { color: theme.textSecondary || '#666' }]}>
                  Update storage usage information
                </Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color={theme.textSecondary || '#666'} />
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>ℹ️ Information</Text>
          
          <View style={[styles.infoCard, { backgroundColor: theme.cardBackground || 'rgba(255,255,255,0.9)' }]}>
            <Ionicons name="information-circle-outline" size={24} color={theme.primary} />
            <Text style={[styles.infoText, { color: theme.text }]}>
              Images are stored locally on your device and processed automatically when you add new clothes. 
              Regular cleanup helps maintain optimal performance.
            </Text>
          </View>
        </View>
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
    paddingHorizontal: 20,
    paddingVertical: 15,
    paddingTop: 50,
    borderBottomWidth: 1,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
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
    fontSize: 16,
  },
  section: {
    marginVertical: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  statCard: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 16,
    marginLeft: 12,
    fontWeight: '500',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  locationText: {
    fontSize: 12,
    marginTop: 8,
    fontFamily: 'monospace',
  },
  actionCard: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  actionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  actionTextContainer: {
    marginLeft: 12,
    flex: 1,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  actionDescription: {
    fontSize: 14,
  },
  infoCard: {
    padding: 20,
    borderRadius: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    marginLeft: 12,
    lineHeight: 20,
  },
});

export default StorageStatsScreen;
