import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

export interface CardProps {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  headerRight?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  style?: ViewStyle;
  contentStyle?: ViewStyle;
  elevated?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  icon,
  headerRight,
  children,
  footer,
  style,
  contentStyle,
  elevated = false,
}) => {
  const { colors, typography, spacing } = useTheme();

  return (
    <View
      style={[
        styles.cardContainer,
        {
          backgroundColor: elevated ? colors.backgroundCardElevated : colors.backgroundCard,
          borderColor: colors.surfaceBorder,
          borderRadius: spacing.radiusMd,
          padding: spacing.md,
          marginBottom: spacing.md,
        },
        style,
      ]}
    >
      {(title || icon || headerRight) && (
        <View style={styles.header}>
          <View style={styles.titleRow}>
            {icon ? <View style={styles.icon}>{icon}</View> : null}
            <View style={styles.titleTextContainer}>
              {title ? (
                <Text style={[typography.h3, { color: colors.textPrimary }]}>{title}</Text>
              ) : null}
              {subtitle ? (
                <Text style={[typography.bodySmall, { color: colors.textSecondary }]}>
                  {subtitle}
                </Text>
              ) : null}
            </View>
          </View>
          {headerRight ? <View style={styles.headerRight}>{headerRight}</View> : null}
        </View>
      )}

      <View style={[styles.body, contentStyle]}>{children}</View>

      {footer && (
        <View
          style={[
            styles.footer,
            {
              borderTopColor: colors.divider,
              paddingTop: spacing.sm,
              marginTop: spacing.sm,
            },
          ]}
        >
          {footer}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  cardContainer: {
    borderWidth: 1,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  icon: {
    marginRight: 10,
  },
  titleTextContainer: {
    flex: 1,
  },
  headerRight: {
    marginLeft: 8,
  },
  body: {
    width: '100%',
  },
  footer: {
    borderTopWidth: 1,
    width: '100%',
  },
});
