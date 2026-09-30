import NetInfo from '@react-native-community/netinfo';

import {
  getPendingSOS,
  markSOSSynced,
  incrementSOSAttempt,
} from './offlineDatabase';

const BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  'https://orca-backend-tkus.onrender.com';

export async function syncSOSQueue() {
  const network = await NetInfo.fetch();

  const online =
    network.isConnected === true &&
    network.isInternetReachable !== false;

  if (!online) {
    return {
      synced: 0,
      pending: 0,
    };
  }

  const queue = await getPendingSOS();

  let synced = 0;

  for (const item of queue) {
    try {
      const payload = JSON.parse(item.payload);

      const response = await fetch(
        `${BASE_URL}/api/sar/create`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      await markSOSSynced(item.id);

      synced++;
    } catch (error) {
      console.error(
        `[ORCA] SOS sync failed for ${item.client_uuid}`,
        error
      );

      await incrementSOSAttempt(item.id);
    }
  }

  const remaining = await getPendingSOS();

  return {
    synced,
    pending: remaining.length,
  };
}