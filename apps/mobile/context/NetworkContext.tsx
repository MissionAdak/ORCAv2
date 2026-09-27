import React, {
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react';

import NetInfo from '@react-native-community/netinfo';
import { syncSOSQueue } from '../utils/sosSync';

interface NetworkContextType {
  isOnline: boolean;
  isStale: boolean;
  lastUpdatedText?: string;
  setIsOnline: (online: boolean) => void;
  setStaleStatus: (
    stale: boolean,
    lastUpdated?: string
  ) => void;
}

const NetworkContext =
  createContext<NetworkContextType | undefined>(
    undefined
  );

export function NetworkProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isOnline, setIsOnline] =
    useState<boolean>(true);

  const [isStale, setIsStale] =
    useState<boolean>(false);

  const [lastUpdatedText, setLastUpdatedText] =
    useState<string>();

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(
      async state => {
        const online =
          state.isConnected === true &&
          state.isInternetReachable !== false;

        setIsOnline(online);

        if (online) {
          console.log(
            '[ORCA] Network restored. Syncing SOS queue...'
          );

          try {
            await syncSOSQueue();
          } catch (error) {
            console.error(
              '[ORCA] SOS queue sync failed:',
              error
            );
          }
        }
      }
    );

    NetInfo.fetch().then(state => {
      const online =
        state.isConnected === true &&
        state.isInternetReachable !== false;

      setIsOnline(online);
    });

    return unsubscribe;
  }, []);

  const setStaleStatus = (
    stale: boolean,
    lastUpdated?: string
  ) => {
    setIsStale(stale);

    if (lastUpdated) {
      setLastUpdatedText(lastUpdated);
    }
  };

  return (
    <NetworkContext.Provider
      value={{
        isOnline,
        isStale,
        lastUpdatedText,
        setIsOnline,
        setStaleStatus,
      }}
    >
      {children}
    </NetworkContext.Provider>
  );
}

export function useNetwork() {
  const context = useContext(NetworkContext);

  if (!context) {
    throw new Error(
      'useNetwork must be used inside NetworkProvider'
    );
  }

  return context;
}