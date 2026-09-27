import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Button } from './Button';

export interface EmptyStateProps {
  title: string;
  description: string;
  iconName?: keyof typeof Ionicons.glyphMap;
  actionText?: string;
  onAction?: () => void;
  style?: ViewStyle;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  iconName = 'compass-outline',
  actionText,
  onAction,
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
            backgroundColor: 'rgba(0, 168, 232, 0.12)',
            borderColor: colors.surfaceBorderActive,
            marginBottom: spacing.md,
          },
        ]}
      >
        <Ionicons name={iconName} size={36} color={colors.accentBlue} />
      </View>

      <Text
        style={[
          typography.h3,
          { color: colors.textPrimary, textAlign: 'center', marginBottom: spacing.xs },
        ]}
      >
        {title}
      </Text>

      <Text
        style={[
          typography.bodyMedium,
          { color: colors.textSecondary, textAlign: 'center', marginBottom: onAction ? spacing.lg : 0 },
        ]}
      >
        {description}
      </Text>

      {actionText && onAction && (
        <Button
          title={actionText}
          onPress={onAction}
          variant="secondary"
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
    borderWidth: 1,
  },
});
