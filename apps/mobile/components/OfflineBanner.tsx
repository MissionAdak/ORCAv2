import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';

export interface OfflineBannerProps {
  isOffline?: boolean;
  isStale?: boolean;
  lastUpdatedText?: string;
  style?: ViewStyle;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({
  isOffline = false,
  isStale = false,
  lastUpdatedText,
  style,
}) => {
  const { colors, typography, spacing } = useTheme();

  if (!isOffline && !isStale) {
    return null;
  }

  const bgColor = isOffline ? colors.offlineBackground : colors.staleBackground;
  const borderColor = isOffline ? colors.offlineBorder : colors.staleBorder;
  const textColor = isOffline ? colors.offlineText : colors.staleText;
  const iconName = isOffline ? 'cloud-offline-outline' : 'alert-circle-outline';

  const message = isOffline
    ? `OFFLINE MODE — Using cached data${lastUpdatedText ? ` · Last updated: ${lastUpdatedText}` : ''}`
    : `CACHED / STALE DATA${lastUpdatedText ? ` · Last updated: ${lastUpdatedText}` : ''}`;

  return (
    <View
      style={[
        styles.banner,
        {
          backgroundColor: bgColor,
          borderBottomColor: borderColor,
          paddingVertical: spacing.sm,
          paddingHorizontal: spacing.md,
        },
        style,
      ]}
    >
      <Ionicons name={iconName} size={18} color={textColor} style={styles.icon} />
      <Text
        style={[
          typography.bodySmall,
          {
            color: textColor,
            fontWeight: '700',
            flex: 1,
          },
        ]}
        numberOfLines={2}
      >
        {message}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    width: '100%',
    zIndex: 100,
  },
  icon: {
    marginRight: 10,
  },
});
