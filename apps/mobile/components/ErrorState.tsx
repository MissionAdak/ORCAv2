import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Button } from './Button';

export interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryButtonText?: string;
  iconName?: keyof typeof Ionicons.glyphMap;
  style?: ViewStyle;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Unable to Load Data',
  message,
  onRetry,
  retryButtonText = 'Retry Now',
  iconName = 'cloud-offline-outline',
  style,
}) => {
  const { colors, typography, spacing } = useTheme();

  return (
    <View
      style={[
        styles.container,
        {
          padding: spacing.xl,
        },
        style,
      ]}
    >
      <View
        style={[
          styles.iconCircle,
          {
            backgroundColor: 'rgba(230, 57, 70, 0.15)',
            borderColor: colors.riskHigh,
            marginBottom: spacing.md,
          },
        ]}
      >
        <Ionicons name={iconName} size={36} color={colors.riskHigh} />
      </View>

      <Text style={[typography.h3, { color: colors.textPrimary, textAlign: 'center', marginBottom: spacing.xs }]}>
        {title}
      </Text>

      <Text
        style={[
          typography.bodyMedium,
          { color: colors.textSecondary, textAlign: 'center', marginBottom: spacing.lg },
        ]}
      >
        {message}
      </Text>

      {onRetry && (
        <Button
          title={retryButtonText}
          onPress={onRetry}
          variant="outline"
          icon={<Ionicons name="refresh-outline" size={18} color={colors.accentGold} />}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  iconCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
  },
});
