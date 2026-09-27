import AsyncStorage from '@react-native-async-storage/async-storage';

const OFFLINE_QUEUE_KEY = '@orca_offline_queue';

export interface FailedRequest {
  endpoint: string;
  method: 'GET' | 'POST';
  payload: any;
  timestamp: string;
}

export const queueFailedRequest = async (endpoint: string, method: 'GET' | 'POST', payload: any) => {
  try {
    const existingQueueStr = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
    const existingQueue: FailedRequest[] = existingQueueStr ? JSON.parse(existingQueueStr) : [];
    
    const newRequest: FailedRequest = {
      endpoint,
      method,
      payload,
      timestamp: new Date().toISOString(),
    };
    
    existingQueue.push(newRequest);
    await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(existingQueue));
    console.log(`[OfflineSync] Queued failed request for ${endpoint}`);
  } catch (error) {
    console.error('[OfflineSync] Failed to queue request:', error);
  }
};

export const syncQueue = async () => {
  try {
    const existingQueueStr = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
    if (!existingQueueStr) return;
    
    const existingQueue: FailedRequest[] = JSON.parse(existingQueueStr);
    if (existingQueue.length === 0) return;
    
    console.log(`[OfflineSync] Attempting to sync ${existingQueue.length} queued items...`);
    
    // Dynamic import to avoid circular dependency with apiClient.ts
    const { apiClient } = await import('../services/apiClient');
    
    const remainingQueue: FailedRequest[] = [];

    for (const request of existingQueue) {
      try {
        if (request.method === 'GET') {
          await apiClient.get(request.endpoint, request.payload);
        } else if (request.method === 'POST') {
          // Note: Assuming JSON for queued POSTs, multipart caching requires file storage
          await apiClient.post(request.endpoint, request.payload);
        }
        console.log(`[OfflineSync] Successfully synced: ${request.endpoint}`);
      } catch (err) {
        console.error(`[OfflineSync] Retry failed for ${request.endpoint}:`, err);
        // Keep in queue if it fails again
        remainingQueue.push(request);
      }
    }
    
    if (remainingQueue.length === 0) {
      await AsyncStorage.removeItem(OFFLINE_QUEUE_KEY);
    } else {
      await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(remainingQueue));
    }
    
    console.log(`[OfflineSync] Sync complete. ${remainingQueue.length} items remain in queue.`);
  } catch (error) {
    console.error('[OfflineSync] Sync failed:', error);
  }
};
