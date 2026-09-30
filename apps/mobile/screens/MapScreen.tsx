import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';
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

  const mapHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Leaflet Map</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      <style>
        body { padding: 0; margin: 0; }
        html, body, #map { height: 100%; width: 100vw; }
      </style>
    </head>
    <body>
      <div id="map"></div>
      <script>
        var map = L.map('map').setView([${initialRegion.latitude}, ${initialRegion.longitude}], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);
        
        L.marker([${initialRegion.latitude}, ${initialRegion.longitude}]).addTo(map)
            .bindPopup('Versova<br>Fishing Zone').openPopup();
      </script>
    </body>
    </html>
  `;

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.backgroundDark }]}>
      <View style={[styles.header, { backgroundColor: colors.backgroundCard }]}>
        <Text style={[typography.h2, { color: colors.textPrimary }]}>{t('nav_map') || 'Marine Map'}</Text>
      </View>
      <View style={styles.mapContainer}>
        {loading && !forecast ? (
          <View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
            <ActivityIndicator size="large" color={colors.accentBlue} />
          </View>
        ) : (
          <WebView 
            originWhitelist={['*']}
            source={{ html: mapHtml }}
            style={styles.map}
          />
        )}
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
  map: { flex: 1, width: '100%', height: '100%' },
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
