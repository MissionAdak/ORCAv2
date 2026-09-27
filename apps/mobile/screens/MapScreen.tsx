import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import MapView, { Marker, Callout } from 'react-native-maps';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { MarineService } from '../services/marineService';

export default function MapScreen() {
  const { colors, typography } = useTheme();
  const { t } = useLanguage();
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  
  const initialRegion = {
    latitude: 19.13,
    longitude: 72.81,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  };

  const fetchForecast = async () => {
    setLoading(true);
    try {
      const data = await MarineService.getMarineForecast(19.13, 72.81);
      // Ensure we extract the correct property if it's an array or object
      setForecast(Array.isArray(data) ? data[0] : data);
    } catch (error) {
      console.error("Failed to fetch forecast:", error);
      Alert.alert("Error", "Could not fetch marine forecast.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, []);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.backgroundDark }]}>
      <View style={[styles.header, { backgroundColor: colors.backgroundCard }]}>
        <Text style={[typography.h2, { color: colors.textPrimary }]}>{t('nav_map') || 'Marine Map'}</Text>
      </View>
      <View style={styles.mapContainer}>
        <MapView
          style={styles.map}
          initialRegion={initialRegion}
        >
          <Marker coordinate={{ latitude: 19.13, longitude: 72.81 }} title="Versova" description="Fishing Zone">
            <Callout>
              <View style={styles.callout}>
                {loading ? <ActivityIndicator size="small" /> : (
                  forecast ? (
                    <>
                      <Text style={{ fontWeight: 'bold' }}>Marine Conditions</Text>
                      <Text>Waves: {forecast.value ?? forecast.wave_height} {forecast.unit ?? 'm'}</Text>
                    </>
                  ) : (
                    <Text>No data available</Text>
                  )
                )}
              </View>
            </Callout>
          </Marker>
        </MapView>
      </View>
      
      {forecast && (
        <View style={[styles.bottomSheet, { backgroundColor: colors.backgroundCard }]}>
          <Text style={[typography.h3, { color: colors.textPrimary, marginBottom: 8 }]}>Versova Area Conditions</Text>
          <Text style={[typography.bodyMedium, { color: colors.textMuted }]}>
            {forecast.parameter ? forecast.parameter.replace('_', ' ').toUpperCase() : 'WAVE HEIGHT'}: {forecast.value ?? forecast.wave_height} {forecast.unit ?? 'm'}
          </Text>
          <Text style={[typography.bodySmall, { color: colors.textMuted, marginTop: 4 }]}>
            Source: {forecast.source ?? 'Open-Meteo'}
          </Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { padding: 16, zIndex: 1, elevation: 2 },
  mapContainer: { flex: 1 },
  map: { width: '100%', height: '100%' },
  callout: { padding: 8, width: 150 },
  bottomSheet: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    padding: 16,
    borderRadius: 12,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  }
});
