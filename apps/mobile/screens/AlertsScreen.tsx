import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, ScrollView, ActivityIndicator, Image, Pressable, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { MarineService } from '../services/marineService';
import { useNavigation } from '@react-navigation/native';

const AlertCard = ({ alert, index, colors, typography, t, navigation }: any) => {
  const [visible, setVisible] = useState(true);
  const [hasVoted, setHasVoted] = useState(false);
  const [upvotes, setUpvotes] = useState(() => Math.floor(Math.random() * 16) + 5);

  if (!visible) return null;

  const lat = alert.lat || alert.latitude || 19.13;
  const lng = alert.lon || alert.longitude || 72.81;
  const mapUrl = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Map_placeholder.png/800px-Map_placeholder.png';

  const handleVerify = () => {
    if (!hasVoted) {
      setUpvotes(prev => prev + 1);
      setHasVoted(true);
    }
  };

  const handleSpam = () => {
    setVisible(false);
  };

  const getTypeDisplay = (type: string, severity: string) => {
    const raw = t(type) || type || 'Alert';
    const upper = typeof raw === 'string' ? raw.toUpperCase() : raw;
    if (severity === 'High') return `🚨 ${upper}`;
    if (severity === 'Moderate') return `⚠️ ${upper}`;
    return `ℹ️ ${upper}`;
  };

  return (
    <Pressable
      key={index}
      onPress={() => navigation.navigate('Map', { focusAlert: { lat, lng, type: alert.title || alert.type, description: alert.description || alert.message } })}
      style={({ pressed }) => [
        styles.alertCard,
        { backgroundColor: colors.backgroundCard, opacity: pressed ? 0.8 : 1 }
      ]}
    >
      <Text style={[typography.h2, { fontWeight: '900', fontSize: 18, color: alert.severity === 'High' ? colors.riskHigh : colors.riskModerate, marginBottom: 8 }]}>
        {getTypeDisplay(alert.title || alert.type, alert.severity)}
      </Text>
      
      <Image source={{ uri: mapUrl }} style={[styles.miniMap, { width: '100%', height: 150 }]} resizeMode="cover" />

      <Text style={[typography.bodyMedium, { color: colors.textPrimary, marginVertical: 8, fontSize: 15 }]}>
        {t(alert.description || alert.message) || alert.description || alert.message}
      </Text>
      <Text style={[typography.bodyMedium, { color: alert.severity === 'High' ? '#FF3B30' : '#FF9500', fontWeight: 'bold' }]}>
        {t('alert_severity') || 'Severity:'} {t(alert.severity) || alert.severity}
      </Text>

      <View style={styles.actionFooter}>
        <Text style={[typography.bodySmall, { color: colors.textMuted, flex: 1 }]}>
          {upvotes} {t('fishers_verified') || 'Fishers Verified'}
        </Text>
        
        <TouchableOpacity 
          onPress={handleVerify} 
          disabled={hasVoted}
          style={[styles.actionButton, { backgroundColor: hasVoted ? '#555' : '#4CAF50' }]}
        >
          <Text style={styles.actionButtonText}>{hasVoted ? (t('verified') || 'Verified') : (t('verify') || '✓ Verify')}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          onPress={handleSpam} 
          style={[styles.actionButton, { backgroundColor: '#F44336', marginLeft: 8 }]}
        >
          <Text style={styles.actionButtonText}>{t('spam') || '✕ Spam'}</Text>
        </TouchableOpacity>
      </View>
    </Pressable>
  );
};


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
            alerts.map((alert: any, index: number) => (
              <AlertCard 
                key={index} 
                alert={alert} 
                index={index} 
                colors={colors} 
                typography={typography} 
                t={t} 
                navigation={navigation} 
              />
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
  miniMap: {
    width: '100%',
    height: 120,
    borderRadius: 8,
    backgroundColor: '#333'
  },
  actionFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#333',
    paddingTop: 12,
  },
  actionButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  }
});
