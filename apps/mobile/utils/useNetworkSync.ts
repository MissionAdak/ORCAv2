import { useEffect } from 'react';
import NetInfo from '@react-native-community/netinfo';
import { syncQueue } from './offlineSync';

/**
 * Hook to automatically trigger offline queue synchronization 
 * whenever the device's internet connection is restored.
 */
export const useNetworkSync = () => {
  useEffect(() => {
    // Subscribe to network state updates
    const unsubscribe = NetInfo.addEventListener(state => {
      // If we are online and have internet access
      if (state.isConnected && state.isInternetReachable) {
        console.log('[NetworkListener] Connection restored. Triggering offline sync...');
        syncQueue();
      }
    });

    // Cleanup the subscription on unmount
    return () => {
      unsubscribe();
    };
  }, []);
};
