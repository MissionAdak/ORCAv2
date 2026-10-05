import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, ScrollView, ActivityIndicator, Image, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { MarineService } from '../services/marineService';
import { useNavigation } from '@react-navigation/native';

export default function AlertsScreen() {
  const { colors, typography } = useTheme();
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const navigation = useNavigation<any>();

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
              {t('no_active_alerts') || 'No active alerts in your area.'}
            </Text>
          ) : (
            alerts.map((alert: any, index: number) => {
              const lat = alert.lat || alert.latitude || 19.13;
              const lng = alert.lon || alert.longitude || 72.81;
              const mapUrl = `https://staticmap.openstreetmap.de/staticmap.php?center=${lat},${lng}&zoom=12&size=400x200&markers=${lat},${lng}`;

              return (
                <Pressable
                  key={index}
                  onPress={() => navigation.navigate('Map', { focusAlert: { lat, lng, type: alert.title || alert.type, description: alert.description || alert.message } })}
                  style={({ pressed }) => [
                    styles.alertCard,
                    { backgroundColor: colors.backgroundCard, opacity: pressed ? 0.8 : 1 }
                  ]}
                >
                  <Text style={[typography.h3, { color: alert.severity === 'High' ? colors.riskHigh : colors.riskModerate, marginBottom: 8 }]}>
                    {t(alert.title || alert.type) || alert.title || alert.type || 'Alert'}
                  </Text>
                  
                  <Image source={{ uri: mapUrl }} style={styles.miniMap} />

                  <Text style={[typography.bodyMedium, { color: colors.textPrimary, marginVertical: 8 }]}>
                    {t(alert.description || alert.message) || alert.description || alert.message}
                  </Text>
                  <Text style={[typography.bodySmall, { color: colors.textMuted }]}>
                    {t('alert_severity') || 'Severity:'} {t(alert.severity) || alert.severity}
                  </Text>
                </Pressable>
              );
            })
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
  miniMap: {
    width: '100%',
    height: 120,
    borderRadius: 8,
    backgroundColor: '#333'
  },
});
