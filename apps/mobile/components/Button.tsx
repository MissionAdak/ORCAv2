import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
  View,
} from 'react-native';
import { useTheme } from '../theme/ThemeContext';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'outline' | 'sos';

export interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
  textStyle?: TextStyle;
  size?: 'standard' | 'large';
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
  icon,
  style,
  textStyle,
  size = 'standard',
}) => {
  const { colors, typography, spacing, isWetHandMode, touchTargetSize, triggerHaptic } = useTheme();

  const handlePress = () => {
    if (disabled || loading) return;
    triggerHaptic(variant === 'sos' || variant === 'danger' ? 'warning' : 'light');
    onPress();
  };

  const getVariantStyles = (): { button: ViewStyle; text: TextStyle } => {
    switch (variant) {
      case 'primary':
        return {
          button: {
            backgroundColor: colors.accentGold,
            borderColor: colors.accentGold,
          },
          text: {
            color: colors.textInverted,
            fontWeight: '700',
          },
        };
      case 'secondary':
        return {
          button: {
            backgroundColor: colors.backgroundCardElevated,
            borderColor: colors.surfaceBorderActive,
          },
          text: {
            color: colors.textPrimary,
            fontWeight: '600',
          },
        };
      case 'danger':
        return {
          button: {
            backgroundColor: colors.riskHigh,
            borderColor: colors.riskHigh,
          },
          text: {
            color: colors.textPrimary,
            fontWeight: '700',
          },
        };
      case 'sos':
        return {
          button: {
            backgroundColor: colors.sosBackground,
            borderColor: colors.sosBright,
            borderWidth: 2,
          },
          text: {
            color: colors.sosForeground,
            fontWeight: '800',
            letterSpacing: 0.5,
          },
        };
      case 'outline':
      default:
        return {
          button: {
            backgroundColor: 'transparent',
            borderColor: colors.surfaceBorderActive,
            borderWidth: 1.5,
          },
          text: {
            color: colors.accentGold,
            fontWeight: '600',
          },
        };
    }
  };

  const variantStyle = getVariantStyles();
  const minHeight = isWetHandMode ? spacing.touchTargetWetHand : size === 'large' ? 56 : touchTargetSize;

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={handlePress}
      disabled={disabled || loading}
      style={[
        styles.baseButton,
        {
          minHeight,
          paddingHorizontal: isWetHandMode ? spacing.lg : spacing.md,
          borderRadius: spacing.radiusMd,
          opacity: disabled ? 0.5 : 1,
        },
        variantStyle.button,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={variantStyle.text.color} />
      ) : (
        <View style={styles.contentRow}>
          {icon ? <View style={styles.iconContainer}>{icon}</View> : null}
          <Text
            style={[
              isWetHandMode ? typography.buttonLarge : typography.button,
              variantStyle.text,
              textStyle,
            ]}
            numberOfLines={1}
            adjustsFontSizeToFit
          >
            {title}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  baseButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
  },
  contentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    marginRight: 8,
  },
});
