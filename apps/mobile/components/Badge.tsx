import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';

export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH';
export type SeverityLevel = 'info' | 'warning' | 'critical' | 'normal';

export interface BadgeProps {
  label: string;
  type?: 'risk' | 'severity' | 'status';
  level?: RiskLevel | SeverityLevel;
  iconName?: keyof typeof Ionicons.glyphMap;
  style?: ViewStyle;
  textStyle?: TextStyle;
  size?: 'small' | 'medium' | 'large';
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  type = 'risk',
  level = 'LOW',
  iconName,
  style,
  textStyle,
  size = 'medium',
}) => {
  const { colors, typography, spacing } = useTheme();

  const getThemeForLevel = () => {
    switch (level) {
      case 'LOW':
      case 'normal':
        return {
          backgroundColor: 'rgba(42, 157, 143, 0.2)',
          borderColor: colors.riskLow,
          textColor: '#48CAE4',
          defaultIcon: 'shield-checkmark' as const,
        };
      case 'MODERATE':
      case 'warning':
        return {
          backgroundColor: 'rgba(255, 183, 3, 0.2)',
          borderColor: colors.riskModerate,
          textColor: colors.riskModerate,
          defaultIcon: 'alert-circle' as const,
        };
      case 'HIGH':
      case 'critical':
        return {
          backgroundColor: 'rgba(230, 57, 70, 0.2)',
          borderColor: colors.riskHigh,
          textColor: '#FF6B6B',
          defaultIcon: 'warning' as const,
        };
      case 'info':
      default:
        return {
          backgroundColor: 'rgba(0, 168, 232, 0.2)',
          borderColor: colors.accentBlue,
          textColor: colors.accentBlue,
          defaultIcon: 'information-circle' as const,
        };
    }
  };

  const badgeTheme = getThemeForLevel();
  const icon = iconName || badgeTheme.defaultIcon;

  const getPadding = () => {
    switch (size) {
      case 'small':
        return { paddingHorizontal: spacing.xs + 2, paddingVertical: 2, iconSize: 12 };
      case 'large':
        return { paddingHorizontal: spacing.md, paddingVertical: spacing.sm, iconSize: 18 };
      case 'medium':
      default:
        return { paddingHorizontal: spacing.sm + 2, paddingVertical: spacing.xs, iconSize: 14 };
    }
  };

  const sizeStyles = getPadding();

  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor: badgeTheme.backgroundColor,
          borderColor: badgeTheme.borderColor,
          paddingHorizontal: sizeStyles.paddingHorizontal,
          paddingVertical: sizeStyles.paddingVertical,
          borderRadius: spacing.radiusSm,
        },
        style,
      ]}
    >
      <Ionicons
        name={icon}
        size={sizeStyles.iconSize}
        color={badgeTheme.textColor}
        style={styles.icon}
      />
      <Text
        style={[
          size === 'large' ? typography.button : size === 'small' ? typography.bodySmall : typography.badge,
          { color: badgeTheme.textColor },
          textStyle,
        ]}
      >
        {label}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    borderWidth: 1,
  },
  icon: {
    marginRight: 6,
  },
});
