import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { useUser } from '../context/UserContext';
import { useNetwork } from '../context/NetworkContext';
import { RootStackScreenProps } from '../navigation/types';

export default function SplashScreen({ navigation }: RootStackScreenProps<'Splash'>) {
  const { colors, typography, spacing } = useTheme();
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const { isOnboarded } = useUser();
  const { isOnline } = useNetwork();

  const scaleAnim = useRef(new Animated.Value(0.9)).current;
  const opacityAnim = useRef(new Animated.Value(0.4)).current;

  useEffect(() => {
    // Pulse animation for the emblem
    Animated.parallel([
      Animated.timing(scaleAnim, {
        toValue: 1.05,
        duration: 1200,
        useNativeDriver: true,
      }),
      Animated.timing(opacityAnim, {
        toValue: 1,
        duration: 1200,
        useNativeDriver: true,
      }),
    ]).start();

    // Cold start target <= 3s per PRD NFR 7.1
    const timer = setTimeout(() => {
      if (isAuthLoading) return;

      if (!isOnboarded) {
        navigation.replace('Onboarding');
      } else if (isAuthenticated) {
        navigation.replace('Main', { screen: 'Home' });
      } else {
        navigation.replace('Auth');
      }
    }, 1800);

    return () => clearTimeout(timer);
  }, [isAuthLoading, isAuthenticated, isOnboarded, navigation]);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.backgroundDark }]}>
      <View style={styles.centerContent}>
        <Animated.View
          style={[
            styles.logoCircle,
            {
              backgroundColor: colors.backgroundNavy,
              borderColor: colors.accentGold,
              transform: [{ scale: scaleAnim }],
              opacity: opacityAnim,
              marginBottom: spacing.lg,
            },
          ]}
        >
          <Ionicons name="boat" size={54} color={colors.accentGold} />
        </Animated.View>

        <Text style={[typography.h1, { color: colors.accentGold, letterSpacing: 2, marginBottom: 4 }]}>
          ORCA
        </Text>
        <Text style={[typography.label, { color: colors.textSecondary, letterSpacing: 1.5, textAlign: 'center' }]}>
          Oceanic Reasoning & Collaborative Agents
        </Text>

        <View style={styles.taglineContainer}>
          <Text style={[typography.bodySmall, { color: colors.textMuted, textAlign: 'center' }]}>
            Marine Intelligence & Decision-Support
          </Text>
          <Text style={[typography.bodySmall, { color: colors.textMuted, textAlign: 'center', marginTop: 2 }]}>
            Smart India Hackathon · PS 26176
          </Text>
        </View>

        <View style={styles.footerContainer}>
          <ActivityIndicator size="small" color={colors.accentGold} style={{ marginBottom: 12 }} />
          {!isOnline && (
            <View style={[styles.offlineChip, { borderColor: colors.offlineBorder, backgroundColor: colors.offlineBackground }]}>
              <Ionicons name="cloud-offline-outline" size={14} color={colors.offlineText} style={{ marginRight: 6 }} />
              <Text style={[typography.bodySmall, { color: colors.offlineText, fontSize: 11 }]}>
                Offline Mode Detected — Cache Ready
              </Text>
            </View>
          )}
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  centerContent: {
    alignItems: 'center',
    width: '85%',
    maxWidth: 360,
  },
  logoCircle: {
    width: 108,
    height: 108,
    borderRadius: 54,
    borderWidth: 2.5,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 10,
    shadowColor: '#FFB703',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 12,
  },
  taglineContainer: {
    marginTop: 18,
    paddingHorizontal: 16,
  },
  footerContainer: {
    marginTop: 48,
    alignItems: 'center',
  },
  offlineChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
  },
});
