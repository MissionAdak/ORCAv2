import React, { createContext, useContext, useState } from 'react';

interface NetworkContextType {
  isOnline: boolean;
  isStale: boolean;
  lastUpdatedText?: string;
  setIsOnline: (online: boolean) => void;
  setStaleStatus: (stale: boolean, lastUpdated?: string) => void;
}

const NetworkContext = createContext<NetworkContextType | undefined>(undefined);

export const NetworkProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [isStale, setIsStale] = useState<boolean>(false);
  const [lastUpdatedText, setLastUpdatedText] = useState<string | undefined>(undefined);

  const setStaleStatus = (stale: boolean, lastUpdated?: string) => {
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
};

export const useNetwork = (): NetworkContextType => {
  const context = useContext(NetworkContext);
  if (!context) {
    throw new Error('useNetwork must be used within a NetworkProvider');
  }
  return context;
};
