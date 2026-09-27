import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Haptics from 'expo-haptics';
import { colors } from './colors';
import { typography } from './typography';
import { spacing } from './spacing';

interface ThemeContextType {
  colors: typeof colors;
  typography: typeof typography;
  spacing: typeof spacing;
  isWetHandMode: boolean;
  touchTargetSize: number;
  toggleWetHandMode: () => Promise<void>;
  triggerHaptic: (type?: 'light' | 'medium' | 'heavy' | 'warning' | 'success') => void;
}

const STORAGE_KEY_WET_MODE = '@orca_wet_hand_mode';

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isWetHandMode, setIsWetHandMode] = useState<boolean>(false);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY_WET_MODE)
      .then((val) => {
        if (val !== null) {
          setIsWetHandMode(val === 'true');
        }
      })
      .catch((err) => {
        console.warn('Failed to load wet hand mode setting:', err);
      });
  }, []);

  const triggerHaptic = (type: 'light' | 'medium' | 'heavy' | 'warning' | 'success' = 'light') => {
    try {
      switch (type) {
        case 'light':
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          break;
        case 'medium':
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
          break;
        case 'heavy':
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
          break;
        case 'warning':
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
          break;
        case 'success':
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
          break;
      }
    } catch {
      // Ignore if haptics are not supported on the target platform/environment
    }
  };

  const toggleWetHandMode = async () => {
    const nextState = !isWetHandMode;
    setIsWetHandMode(nextState);
    triggerHaptic(nextState ? 'heavy' : 'light');
    try {
      await AsyncStorage.setItem(STORAGE_KEY_WET_MODE, String(nextState));
    } catch (err) {
      console.warn('Failed to save wet hand mode setting:', err);
    }
  };

  const touchTargetSize = isWetHandMode ? spacing.touchTargetWetHand : spacing.touchTargetStandard;

  return (
    <ThemeContext.Provider
      value={{
        colors,
        typography,
        spacing,
        isWetHandMode,
        touchTargetSize,
        toggleWetHandMode,
        triggerHaptic,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
