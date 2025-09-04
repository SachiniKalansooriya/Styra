import wardrobeService from '../services/wardrobeService';
import connectionService from '../services/connectionService';
import { Alert } from 'react-native';

class SyncManager {
  constructor() {
    this.syncing = false;
  }

  async checkAndSync() {
    if (this.syncing) return;

    try {
      this.syncing = true;
      
      const isOnline = await connectionService.isBackendAvailable();
      
      if (isOnline) {
        console.log('Backend available - starting sync...');
        const syncResults = await wardrobeService.syncLocalItems();
        
        const successCount = syncResults.filter(r => r.success).length;
        const failCount = syncResults.filter(r => !r.success).length;
        
        if (successCount > 0) {
          console.log(`Synced ${successCount} items to backend`);
          
          Alert.alert(
            'Sync Complete', 
            `${successCount} clothing items synced to backend!`,
            [{ text: 'OK' }],
            { cancelable: true }
          );
        }
        
        if (failCount > 0) {
          console.log(`Failed to sync ${failCount} items`);
        }
      }
    } catch (error) {
      console.error('Sync error:', error);
    } finally {
      this.syncing = false;
    }
  }
}

export default new SyncManager();