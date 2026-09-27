import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { Card, Button } from '../components';

export default function ProfileScreen() {
  const { colors, typography, spacing, isWetHandMode, toggleWetHandMode } = useTheme();
  const { t, language, setLanguage, supportedLanguages } = useLanguage();

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: colors.backgroundDark }]}>
      <ScrollView contentContainerStyle={[styles.container, { padding: spacing.md }]}>
        <Text style={[typography.h2, { color: colors.textPrimary, marginBottom: spacing.md }]}>
          {t('nav_profile')}
        </Text>

        {/* Wet-Hand Mode Setting */}
        <Card
          title={t('wet_hand_mode')}
          subtitle="Enlarges tap targets to 64dp and enforces high-glare contrast"
          icon={<Ionicons name="hand-right-outline" size={20} color={colors.accentGold} />}
        >
          <Button
            title={isWetHandMode ? 'Enabled (64dp Target Active)' : 'Disabled (Standard 48dp)'}
            onPress={toggleWetHandMode}
            variant={isWetHandMode ? 'primary' : 'outline'}
          />
        </Card>

        {/* Language Selector */}
        <Card
          title="Language / भाषा"
          subtitle="Select application interface language"
          icon={<Ionicons name="language-outline" size={20} color={colors.accentBlue} />}
        >
          <View style={styles.langGrid}>
            {supportedLanguages.map((item) => (
              <Button
                key={item.code}
                title={`${item.nativeLabel} (${item.label})`}
                onPress={() => setLanguage(item.code)}
                variant={language === item.code ? 'primary' : 'secondary'}
                style={styles.langButton}
              />
            ))}
          </View>
        </Card>

        {/* Profile features note */}
        <Card subtitle="Phase 8: Vessel Profile, Emergency Contacts, Saved Locations" elevated>
          <Text style={[typography.bodySmall, { color: colors.textMuted }]}>
            ORCA Maritime Decision-Support Platform · SIH 26176
          </Text>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    paddingBottom: 40,
  },
  langGrid: {
    gap: 8,
    marginVertical: 4,
  },
  langButton: {
    width: '100%',
  },
});
