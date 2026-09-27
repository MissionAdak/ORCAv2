import React, { useState } from 'react';
import {
  View,
  TextInput,
  Text,
  StyleSheet,
  TextInputProps,
  ViewStyle,
  TextStyle,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';

export interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: keyof typeof Ionicons.glyphMap;
  rightIcon?: keyof typeof Ionicons.glyphMap;
  onRightIconPress?: () => void;
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  icon,
  rightIcon,
  onRightIconPress,
  containerStyle,
  inputStyle,
  secureTextEntry,
  ...rest
}) => {
  const { colors, typography, spacing, isWetHandMode } = useTheme();
  const [isFocused, setIsFocused] = useState(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  const minHeight = isWetHandMode ? spacing.touchTargetWetHand : 52;
  const isPassword = secureTextEntry;

  return (
    <View style={[styles.container, containerStyle]}>
      {label && (
        <Text
          style={[
            typography.label,
            { color: error ? colors.riskHigh : colors.textSecondary, marginBottom: 6 },
          ]}
        >
          {label}
        </Text>
      )}

      <View
        style={[
          styles.inputWrapper,
          {
            backgroundColor: colors.backgroundCardElevated,
            borderColor: error
              ? colors.riskHigh
              : isFocused
              ? colors.accentGold
              : colors.surfaceBorder,
            minHeight,
            borderRadius: spacing.radiusMd,
            paddingHorizontal: spacing.md,
          },
        ]}
      >
        {icon && (
          <Ionicons
            name={icon}
            size={isWetHandMode ? 24 : 20}
            color={error ? colors.riskHigh : isFocused ? colors.accentGold : colors.textMuted}
            style={styles.leadingIcon}
          />
        )}

        <TextInput
          style={[
            styles.textInput,
            typography.bodyMedium,
            { color: colors.textPrimary },
            inputStyle,
          ]}
          placeholderTextColor={colors.textMuted}
          secureTextEntry={isPassword && !isPasswordVisible}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...rest}
        />

        {isPassword ? (
          <TouchableOpacity
            onPress={() => setIsPasswordVisible(!isPasswordVisible)}
            style={styles.trailingIconButton}
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <Ionicons
              name={isPasswordVisible ? 'eye-off-outline' : 'eye-outline'}
              size={20}
              color={colors.textMuted}
            />
          </TouchableOpacity>
        ) : rightIcon ? (
          <TouchableOpacity
            onPress={onRightIconPress}
            disabled={!onRightIconPress}
            style={styles.trailingIconButton}
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <Ionicons name={rightIcon} size={20} color={colors.textMuted} />
          </TouchableOpacity>
        ) : null}
      </View>

      {error ? (
        <View style={styles.messageRow}>
          <Ionicons name="alert-circle" size={14} color={colors.riskHigh} style={{ marginRight: 4 }} />
          <Text style={[typography.bodySmall, { color: colors.riskHigh }]}>{error}</Text>
        </View>
      ) : helperText ? (
        <Text style={[typography.bodySmall, { color: colors.textMuted, marginTop: 4 }]}>
          {helperText}
        </Text>
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
    width: '100%',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1.5,
  },
  leadingIcon: {
    marginRight: 10,
  },
  trailingIconButton: {
    marginLeft: 10,
    padding: 4,
  },
  textInput: {
    flex: 1,
    paddingVertical: 8,
  },
  messageRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
});
