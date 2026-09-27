import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';

export interface StepperProps {
  currentStep: number;
  totalSteps: number;
  stepTitles?: string[];
}

export const Stepper: React.FC<StepperProps> = ({
  currentStep,
  totalSteps,
  stepTitles,
}) => {
  const { colors, typography, spacing } = useTheme();

  return (
    <View style={[styles.container, { marginVertical: spacing.md }]}>
      <View style={styles.stepsRow}>
        {Array.from({ length: totalSteps }).map((_, index) => {
          const stepNumber = index + 1;
          const isCompleted = stepNumber < currentStep;
          const isCurrent = stepNumber === currentStep;

          return (
            <React.Fragment key={stepNumber}>
              {index > 0 && (
                <View
                  style={[
                    styles.connector,
                    {
                      backgroundColor: isCompleted ? colors.accentGold : colors.surfaceBorder,
                    },
                  ]}
                />
              )}

              <View
                style={[
                  styles.circle,
                  {
                    backgroundColor: isCompleted
                      ? colors.accentGold
                      : isCurrent
                      ? colors.backgroundNavy
                      : colors.backgroundCardElevated,
                    borderColor: isCompleted || isCurrent ? colors.accentGold : colors.surfaceBorder,
                  },
                ]}
              >
                {isCompleted ? (
                  <Ionicons name="checkmark" size={14} color={colors.textInverted} />
                ) : (
                  <Text
                    style={[
                      typography.badge,
                      {
                        color: isCurrent ? colors.accentGold : colors.textMuted,
                        fontSize: 12,
                      },
                    ]}
                  >
                    {stepNumber}
                  </Text>
                )}
              </View>
            </React.Fragment>
          );
        })}
      </View>

      <View style={styles.titleContainer}>
        <Text style={[typography.bodySmall, { color: colors.textMuted }]}>
          Step {currentStep} of {totalSteps}
        </Text>
        {stepTitles && stepTitles[currentStep - 1] && (
          <Text style={[typography.h3, { color: colors.textPrimary, marginTop: 2 }]}>
            {stepTitles[currentStep - 1]}
          </Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  stepsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  circle: {
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  connector: {
    flex: 1,
    height: 3,
    marginHorizontal: 4,
    borderRadius: 1.5,
  },
  titleContainer: {
    alignItems: 'center',
    marginTop: 6,
  },
});
