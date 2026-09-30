import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, ScrollView, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { MarineService } from '../services/marineService';

export default function AlertsScreen() {
  const { colors, typography } = useTheme();
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const data = await MarineService.getNearbyAlerts(19.13, 72.81, 50);
        // Safely handle if data is undefined or not an array
        if (Array.isArray(data)) {
          setAlerts(data);
        } else if (data && Array.isArray(data.alerts)) {
          setAlerts(data.alerts);
        } else {
          setAlerts([]);
        }
      } catch (err) {
        console.error("Failed to fetch alerts:", err);
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.backgroundDark }]}>
      <Text style={[typography.h2, { color: colors.textPrimary, padding: 16 }]}>
        {t('nav_alerts')}
      </Text>
      
      {loading ? (
        <ActivityIndicator size="large" color={colors.accentBlue} style={{ marginTop: 20 }} />
      ) : (
        <ScrollView style={styles.list}>
          {(!alerts || alerts.length === 0) ? (
            <Text style={[typography.bodyMedium, { color: colors.textMuted, textAlign: 'center', marginTop: 20 }]}>
              No active alerts in your area.
            </Text>
          ) : (
            alerts.map((alert: any, index: number) => (
              <View key={index} style={[styles.alertCard, { backgroundColor: colors.backgroundCard }]}>
                <Text style={[typography.h3, { color: alert.severity === 'High' ? colors.riskHigh : colors.riskModerate }]}>
                  {alert.title || alert.type || 'Alert'}
                </Text>
                <Text style={[typography.bodyMedium, { color: colors.textPrimary, marginVertical: 4 }]}>
                  {alert.description || alert.message}
                </Text>
                <Text style={[typography.bodySmall, { color: colors.textMuted }]}>
                  Severity: {alert.severity}
                </Text>
              </View>
            ))
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  list: { paddingHorizontal: 16 },
  alertCard: {
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
});
