import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { ThemeProvider } from './theme/ThemeContext';
import { LanguageProvider } from './context/LanguageContext';
import { NetworkProvider } from './context/NetworkContext';
import { AuthProvider } from './context/AuthContext';
import { UserProvider } from './context/UserContext';
import RootNavigator from './navigation/RootNavigator';
import { useNetworkSync } from './utils/useNetworkSync';

function SyncManager({ children }: { children: React.ReactNode }) {
  useNetworkSync();
  return <>{children}</>;
}

export default function App() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <LanguageProvider>
          <NetworkProvider>
            <AuthProvider>
              <UserProvider>
                <SyncManager>
                  <NavigationContainer>
                    <StatusBar style="light" />
                    <RootNavigator />
                  </NavigationContainer>
                </SyncManager>
              </UserProvider>
            </AuthProvider>
          </NetworkProvider>
        </LanguageProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
