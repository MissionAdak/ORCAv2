import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';

export interface EvidenceChipProps {
  source: string;
  timestamp?: string;
  confidence?: number; // 0.0 to 1.0
  isStale?: boolean;
  conflictFlag?: boolean;
  style?: ViewStyle;
}

export const EvidenceChip: React.FC<EvidenceChipProps> = ({
  source,
  timestamp,
  confidence,
  isStale = false,
  conflictFlag = false,
  style,
}) => {
  const { colors, typography, spacing } = useTheme();

  const formattedConfidence =
    confidence !== undefined ? `${Math.round(confidence * 100)}% conf` : null;

  return (
    <View
      style={[
        styles.chipContainer,
        {
          backgroundColor: isStale
            ? 'rgba(255, 183, 3, 0.15)'
            : conflictFlag
            ? 'rgba(230, 57, 70, 0.15)'
            : 'rgba(255, 255, 255, 0.08)',
          borderColor: isStale
            ? colors.riskModerate
            : conflictFlag
            ? colors.riskHigh
            : colors.surfaceBorder,
          borderRadius: spacing.radiusSm,
          paddingHorizontal: spacing.sm,
          paddingVertical: spacing.xs,
        },
        style,
      ]}
    >
      <Ionicons
        name={isStale ? 'time-outline' : conflictFlag ? 'alert-circle-outline' : 'checkmark-circle-outline'}
        size={12}
        color={isStale ? colors.riskModerate : conflictFlag ? colors.riskHigh : colors.accentBlue}
        style={styles.icon}
      />
      <Text style={[typography.bodySmall, { color: colors.textSecondary, fontSize: 11 }]}>
        Src: <Text style={{ color: colors.textPrimary, fontWeight: '600' }}>{source.toUpperCase()}</Text>
        {formattedConfidence ? ` · ${formattedConfidence}` : ''}
        {timestamp ? ` · ${timestamp}` : ''}
        {isStale ? ' (Cached)' : ''}
        {conflictFlag ? ' (Conflict)' : ''}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  chipContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    borderWidth: 1,
    marginTop: 4,
  },
  icon: {
    marginRight: 5,
  },
});
