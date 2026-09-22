import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { useNetwork } from '../context/NetworkContext';
import { BottomTabScreenProps } from '../navigation/types';
import {
  Card,
  Badge,
  Button,
  EvidenceChip,
  OfflineBanner,
} from '../components';

export default function HomeScreen({ navigation }: BottomTabScreenProps<'Home'>) {
  const { colors, typography, spacing, isWetHandMode, toggleWetHandMode } = useTheme();
  const { t } = useLanguage();
  const { isOnline, isStale } = useNetwork();

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: colors.backgroundDark }]}>
      <OfflineBanner isOffline={!isOnline} isStale={isStale} lastUpdatedText="12 mins ago" />

      <ScrollView
        contentContainerStyle={[styles.contentContainer, { padding: spacing.md }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Top Header */}
        <View style={styles.header}>
          <View>
            <Text style={[typography.h2, { color: colors.accentGold }]}>{t('app_title')}</Text>
            <Text style={[typography.bodySmall, { color: colors.textSecondary }]}>
              Versova · Live Marine Decision-Support
            </Text>
          </View>
          <Button
            title={isWetHandMode ? 'Wet Mode ON' : 'Wet Mode'}
            onPress={toggleWetHandMode}
            variant={isWetHandMode ? 'primary' : 'outline'}
            icon={<Ionicons name="water-outline" size={16} color={isWetHandMode ? colors.textInverted : colors.accentGold} />}
          />
        </View>

        {/* Marine Risk Banner */}
        <Card elevated style={{ borderColor: colors.riskModerate }}>
          <View style={styles.riskRow}>
            <View>
              <Text style={[typography.label, { color: colors.textSecondary }]}>Current Marine Risk</Text>
              <Text style={[typography.h1, { color: colors.riskModerate, marginTop: 2 }]}>
                {t('risk_moderate')}
              </Text>
            </View>
            <Badge label="MODERATE" level="MODERATE" size="large" />
          </View>
          <Text style={[typography.bodyMedium, { color: colors.textSecondary, marginTop: 8 }]}>
            Wave height and gusting wind elevated offshore. Suitable for motorized vessels with caution.
          </Text>
          <EvidenceChip
            source="open-meteo"
            timestamp="10:00 UTC"
            confidence={0.88}
          />
        </Card>

        {/* Ocean Conditions Snapshot */}
        <Card
          title={t('ocean_conditions')}
          subtitle="Real-time oceanographic & weather metrics"
          icon={<Ionicons name="analytics-outline" size={20} color={colors.accentBlue} />}
        >
          <View style={styles.metricsGrid}>
            <View style={styles.metricItem}>
              <Text style={[typography.label, { color: colors.textMuted }]}>Wave Height</Text>
              <Text style={[typography.metricValue, { color: colors.textPrimary }]}>1.4</Text>
              <Text style={[typography.metricUnit, { color: colors.textSecondary }]}>meters</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={[typography.label, { color: colors.textMuted }]}>Wind Speed</Text>
              <Text style={[typography.metricValue, { color: colors.textPrimary }]}>18</Text>
              <Text style={[typography.metricUnit, { color: colors.textSecondary }]}>km/h NW</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={[typography.label, { color: colors.textMuted }]}>Sea Surface Temp</Text>
              <Text style={[typography.metricValue, { color: colors.textPrimary }]}>28.5</Text>
              <Text style={[typography.metricUnit, { color: colors.textSecondary }]}>°C</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={[typography.label, { color: colors.textMuted }]}>Tide State</Text>
              <Text style={[typography.metricValue, { color: colors.textSecondary, fontSize: 20 }]}>Unavailable</Text>
              <Text style={[typography.metricUnit, { color: colors.textMuted }]}>No sensor</Text>
            </View>
          </View>
          <EvidenceChip
            source="open-meteo"
            timestamp="Valid until 18:00"
            confidence={0.85}
          />
        </Card>

        {/* Fishing Intelligence Quick Snapshot */}
        <Card
          title={t('fishing_intelligence')}
          subtitle="Nearest validated PFZ candidate"
          icon={<Ionicons name="fish-outline" size={20} color={colors.accentGold} />}
          footer={
            <Button
              title="Inspect On Map"
              onPress={() => navigation.navigate('Map')}
              variant="secondary"
              icon={<Ionicons name="map-outline" size={18} color={colors.textPrimary} />}
            />
          }
        >
          <Text style={[typography.bodyMedium, { color: colors.textPrimary }]}>
            PFZ Zone A — 6.2 nm NW of Versova Jetty
          </Text>
          <Text style={[typography.bodySmall, { color: colors.textSecondary, marginTop: 4 }]}>
            Chlorophyll: 1.8 mg/m³ · SST: 28.1°C · Risk: Low
          </Text>
          <EvidenceChip
            source="incois"
            timestamp="Advisory #44"
            confidence={0.92}
          />
        </Card>

        {/* Ask ORCA Quick Entry */}
        <Card elevated>
          <Button
            title={t('ask_orca')}
            onPress={() => navigation.navigate('AI')}
            variant="primary"
            size="large"
            icon={<Ionicons name="mic" size={22} color={colors.textInverted} />}
          />
        </Card>

        {/* Emergency SOS Control (Bottom-anchored prominent trigger) */}
        <View style={{ marginTop: spacing.md, marginBottom: spacing.xl }}>
          <Button
            title={t('emergency_sos')}
            onPress={() => navigation.navigate('EmergencySOSModal')}
            variant="sos"
            size="large"
            icon={<Ionicons name="alert" size={26} color={colors.sosForeground} />}
          />
          <Text style={[typography.bodySmall, { color: colors.textMuted, textAlign: 'center', marginTop: 8 }]}>
            Long press or tap to open emergency confirmation modal
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  contentContainer: {
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  riskRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginVertical: 8,
  },
  metricItem: {
    width: '48%',
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
});
