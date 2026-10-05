import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert, Switch, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';
import { useRoute } from '@react-navigation/native';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';

// Using constants for the mock data fallback or actual API endpoints
const API_BASE = "https://orca-backend-tkus.onrender.com";

export default function MapScreen() {
  const { colors, typography } = useTheme();
  const { t } = useLanguage();
  const webviewRef = useRef<WebView>(null);
  const route = useRoute<any>();
  const focusAlert = route.params?.focusAlert;

  const [loading, setLoading] = useState(true);
  const [selectedFeature, setSelectedFeature] = useState<any>(null);

  // Layer Toggles
  const [showPFZ, setShowPFZ] = useState(true);
  const [showHazards, setShowHazards] = useState(true);
  const [showIMBL, setShowIMBL] = useState(true);
  const [showRescue, setShowRescue] = useState(true);
  const [showRoute, setShowRoute] = useState(true);

  const seaState = {
    windSpeed: `12 ${t('knots')}`,
    windDirection: t('nw'),
    waveLength: `45 ${t('meters')}`,
    waveSpeed: `2.5 ${t('mps')}`,
    temperature: '28°C',
    tide: `${t('high_tide')} (14:30)`
  };

  const initialRegion = {
    latitude: 19.13,
    longitude: 72.81,
  };

  const mapHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Leaflet Map</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      <style>
        body { padding: 0; margin: 0; background-color: #000; }
        html, body, #map { height: 100%; width: 100vw; }
        .leaflet-container { background: #121212; }
      </style>
    </head>
    <body>
      <div id="map"></div>
      <script>
        var map = L.map('map', { zoomControl: false }).setView([${initialRegion.latitude}, ${initialRegion.longitude}], 10);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);

        L.marker([${initialRegion.latitude}, ${initialRegion.longitude}]).addTo(map)
          .bindPopup('<b>Versova Base</b>');

        var layerGroups = {
            pfz: L.layerGroup().addTo(map),
            hazards: L.layerGroup().addTo(map),
            imbl: L.layerGroup().addTo(map),
            rescue: L.layerGroup().addTo(map),
            route: L.layerGroup().addTo(map)
        };

        // Bridge to React Native
        function onFeatureClick(e) {
          if (e.target && e.target.feature) {
             window.ReactNativeWebView.postMessage(JSON.stringify({
                type: 'FEATURE_SELECTED',
                feature: e.target.feature.properties
             }));
          }
        }

        function buildOnEachFeature() {
            return function(feature, layer) {
                layer.on('click', onFeatureClick);
            }
        }

        // Dummy Data Fallbacks in case API 404s
        const mockPFZ = {
            type: "FeatureCollection",
            features: [{
                type: "Feature",
                properties: { name: "${t('high_probability_pfz')}", type: "${t('pfz_type')}", confidence: "92%", source: "INCOIS" },
                geometry: { type: "Polygon", coordinates: [[[72.75, 19.10], [72.70, 19.15], [72.78, 19.18], [72.80, 19.12], [72.75, 19.10]]] }
            }]
        };

        const mockIMBL = {
            type: "FeatureCollection",
            features: [{
                type: "Feature",
                properties: { name: "${t('imbl_buffer')}", type: "${t('boundary_warning')}", warning: "${t('approaching_imbl')}" },
                geometry: { type: "LineString", coordinates: [[72.4, 18.9], [72.3, 19.2], [72.2, 19.5]] }
            }]
        };

        const mockHazards = {
            type: "FeatureCollection",
            features: [{
                type: "Feature",
                properties: { name: "${t('cyclone_warning')}", type: "${t('hazard')}", severity: "High", source: "IMD" },
                geometry: { type: "Polygon", coordinates: [[[72.5, 18.9], [72.6, 18.9], [72.6, 19.0], [72.5, 19.0], [72.5, 18.9]]] }
            }]
        };

        const mockRescue = {
            type: "FeatureCollection",
            features: [{
                type: "Feature",
                properties: { name: "${t('coast_guard_station')}", type: "${t('rescue_type')}", contact: "VHF 16" },
                geometry: { type: "Point", coordinates: [72.82, 19.15] }
            }]
        };

        const mockRoute = {
            type: "FeatureCollection",
            features: [{
                type: "Feature",
                properties: { name: "${t('safe_navigation_route')}", type: "${t('route_type')}", details: "${t('computed_route')}" },
                geometry: { type: "LineString", coordinates: [[72.81, 19.13], [72.78, 19.13], [72.75, 19.15]] }
            }]
        };

        async function fetchAndRenderData() {
            // Potential Fishing Zones
            try {
                let res = await fetch('${API_BASE}/api/pfz/nearby?lat=${initialRegion.latitude}&lon=${initialRegion.longitude}');
                let data = res.ok ? await res.json() : mockPFZ;
                L.geoJSON(data, { 
                    style: { color: '#00E5FF', fillOpacity: 0.3 },
                    onEachFeature: buildOnEachFeature()
                }).addTo(layerGroups.pfz);
            } catch(e) { console.error(e); }

            // Zones & Boundaries
            try {
                let res = await fetch('${API_BASE}/api/geospatial/zones');
                let data = res.ok ? await res.json() : null;
                
                L.geoJSON(data ? data.imbl : mockIMBL, { 
                    style: { color: '#FF3D00', dashArray: '5, 10', weight: 4 },
                    onEachFeature: buildOnEachFeature()
                }).addTo(layerGroups.imbl);

                L.geoJSON(data ? data.hazards : mockHazards, { 
                    style: { color: '#FFD600', fillColor: '#FFD600', fillOpacity: 0.4 },
                    onEachFeature: buildOnEachFeature()
                }).addTo(layerGroups.hazards);
                
                L.geoJSON(data ? data.rescue : mockRescue, { 
                    pointToLayer: (f, latlng) => L.circleMarker(latlng, {radius: 8, color: '#00C853'}),
                    onEachFeature: buildOnEachFeature()
                }).addTo(layerGroups.rescue);

            } catch(e) { console.error(e); }

            // Navigation Route
            L.geoJSON(mockRoute, { 
                style: { color: '#00E676', dashArray: '4, 8', weight: 3 },
                onEachFeature: buildOnEachFeature()
            }).addTo(layerGroups.route);

            window.ReactNativeWebView.postMessage(JSON.stringify({ type: 'MAP_LOADED' }));
        }

        fetchAndRenderData();

        // Listen for React Native Toggle Events
        document.addEventListener('message', function(event) {
            const msg = JSON.parse(event.data);
            if(msg.type === 'TOGGLE_LAYER') {
                if(msg.visible) {
                    map.addLayer(layerGroups[msg.layer]);
                } else {
                    map.removeLayer(layerGroups[msg.layer]);
                }
            }
        });
        window.addEventListener('message', function(event) {
            const msg = JSON.parse(event.data);
            if(msg.type === 'TOGGLE_LAYER') {
                if(msg.visible) {
                    map.addLayer(layerGroups[msg.layer]);
                } else {
                    map.removeLayer(layerGroups[msg.layer]);
                }
            }
        });
      </script>
    </body>
    </html>
  `;

  // Toggle handlers for webview
  const toggleLayer = (layer: string, visible: boolean) => {
    const script = `
      var msg = {type: 'TOGGLE_LAYER', layer: '${layer}', visible: ${visible}};
      window.dispatchEvent(new MessageEvent('message', {data: JSON.stringify(msg)}));
      true;
    `;
    webviewRef.current?.injectJavaScript(script);
  };

  useEffect(() => { toggleLayer('pfz', showPFZ); }, [showPFZ]);
  useEffect(() => { toggleLayer('hazards', showHazards); }, [showHazards]);
  useEffect(() => { toggleLayer('imbl', showIMBL); }, [showIMBL]);
  useEffect(() => { toggleLayer('rescue', showRescue); }, [showRescue]);
  useEffect(() => { toggleLayer('route', showRoute); }, [showRoute]);

  useEffect(() => {
    if (focusAlert && !loading) {
      const script = `
        map.flyTo([${focusAlert.lat}, ${focusAlert.lng}], 14, { animate: true });
        
        var hazardIcon = L.divIcon({
          className: 'custom-hazard-icon',
          html: '<div style="background-color: red; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; border-radius: 4px; border: 2px solid white; color: white; font-weight: bold; font-family: sans-serif;">!</div>',
          iconSize: [24, 24],
          iconAnchor: [12, 12]
        });

        L.marker([${focusAlert.lat}, ${focusAlert.lng}], { icon: hazardIcon })
          .addTo(map)
          .bindPopup('<b>${focusAlert.type.replace(/'/g, "\\'")}</b><br/>${(focusAlert.description || '').replace(/'/g, "\\'")}')
          .openPopup();
          
        true;
      `;
      webviewRef.current?.injectJavaScript(script);
    }
  }, [focusAlert, loading]);

  const handleMessage = (event: any) => {
    try {
      const data = JSON.parse(event.nativeEvent.data);
      if (data.type === 'MAP_LOADED') {
        setLoading(false);
      } else if (data.type === 'FEATURE_SELECTED') {
        setSelectedFeature(data.feature);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.backgroundDark }]}>
      <View style={[styles.header, { backgroundColor: colors.backgroundCard }]}>
        <Text style={[typography.h2, { color: colors.textPrimary }]}>{t('nav_map') || 'Marine Map'}</Text>
      </View>

      <View style={styles.mapContainer}>
        {loading && (
          <View style={styles.loader}>
            <ActivityIndicator size="large" color={colors.accentBlue} />
            <Text style={{color: 'white', marginTop: 10}}>Loading Map Layers...</Text>
          </View>
        )}
        <WebView 
          ref={webviewRef}
          originWhitelist={['*']}
          source={{ html: mapHtml }}
          style={styles.map}
          javaScriptEnabled={true}
          domStorageEnabled={true}
          onMessage={handleMessage}
        />
      </View>

      {/* Sea State Metrics Overlay (Bottom Left) */}
      <View style={styles.metricsContainer}>
        <Text style={styles.metricsTitle}>{t('current_sea_state')}</Text>
        <Text style={styles.metricsText}>{t('wind_speed')} {seaState.windSpeed}</Text>
        <Text style={styles.metricsText}>{t('wind_dir')} {seaState.windDirection}</Text>
        <Text style={styles.metricsText}>{t('wave_length')} {seaState.waveLength}</Text>
        <Text style={styles.metricsText}>{t('wave_speed')} {seaState.waveSpeed}</Text>
        <Text style={styles.metricsText}>{t('temperature')} {seaState.temperature}</Text>
        <Text style={styles.metricsText}>{t('tide')} {seaState.tide}</Text>
      </View>

      {/* Layer Toggles Overlay (Top Right) */}
      <View style={styles.togglesContainer}>
        <View style={styles.toggleRow}><Switch value={showPFZ} onValueChange={setShowPFZ}/><Text style={styles.toggleText}>{t('pfz')}</Text></View>
        <View style={styles.toggleRow}><Switch value={showHazards} onValueChange={setShowHazards}/><Text style={styles.toggleText}>{t('alerts')}</Text></View>
        <View style={styles.toggleRow}><Switch value={showIMBL} onValueChange={setShowIMBL}/><Text style={styles.toggleText}>{t('imbl')}</Text></View>
        <View style={styles.toggleRow}><Switch value={showRescue} onValueChange={setShowRescue}/><Text style={styles.toggleText}>{t('rescue')}</Text></View>
        <View style={styles.toggleRow}><Switch value={showRoute} onValueChange={setShowRoute}/><Text style={styles.toggleText}>{t('safe_route')}</Text></View>
      </View>
      
      {/* Tap-to-Inspect Bottom Sheet */}
      {selectedFeature && (
        <View style={[styles.bottomSheet, { backgroundColor: colors.backgroundCard }]}>
          <Text style={[typography.h3, { color: colors.textPrimary, marginBottom: 8 }]}>
            {selectedFeature.name || t('zone_details')}
          </Text>
          
          <View style={styles.chipRow}>
            <View style={styles.chip}><Text style={styles.chipText}>{selectedFeature.type?.toUpperCase()}</Text></View>
            {selectedFeature.source && <View style={styles.chip}><Text style={styles.chipText}>{selectedFeature.source}</Text></View>}
          </View>
          
          {selectedFeature.details && <Text style={[typography.bodyMedium, { color: colors.accentBlue, marginBottom: 4 }]}>{selectedFeature.details}</Text>}
          {selectedFeature.confidence && <Text style={[typography.bodyMedium, { color: colors.textMuted }]}>{t('confidence')} {selectedFeature.confidence}</Text>}
          {selectedFeature.severity && <Text style={[typography.bodyMedium, { color: 'red' }]}>{t('severity')} {selectedFeature.severity}</Text>}
          {selectedFeature.warning && <Text style={[typography.bodyMedium, { color: 'orange' }]}>{selectedFeature.warning}</Text>}
          {selectedFeature.contact && <Text style={[typography.bodyMedium, { color: colors.textMuted }]}>{t('contact')} {selectedFeature.contact}</Text>}

          <TouchableOpacity style={styles.closeBtn} onPress={() => setSelectedFeature(null)}>
            <Text style={{color: 'white', fontWeight: 'bold'}}>{t('close')}</Text>
          </TouchableOpacity>
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
  loader: { position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, justifyContent: 'center', alignItems: 'center', backgroundColor: '#121212', zIndex: 2 },
  
  metricsContainer: {
    position: 'absolute',
    bottom: 20,
    left: 16,
    backgroundColor: 'rgba(20, 20, 20, 0.85)',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    zIndex: 10
  },
  metricsTitle: { color: '#00E5FF', fontSize: 14, fontWeight: 'bold', marginBottom: 4 },
  metricsText: { color: 'white', fontSize: 12, marginBottom: 2 },

  togglesContainer: {
    position: 'absolute',
    top: 80,
    right: 16,
    backgroundColor: 'rgba(30, 30, 30, 0.85)',
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333'
  },
  toggleRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  toggleText: { color: 'white', marginLeft: 8, fontSize: 12, fontWeight: 'bold', maxWidth: 120 },

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
    borderWidth: 1,
    borderColor: '#333'
  },
  chipRow: { flexDirection: 'row', gap: 8, marginBottom: 8 },
  chip: { backgroundColor: '#333', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4 },
  chipText: { color: 'white', fontSize: 10, fontWeight: 'bold' },
  closeBtn: { marginTop: 12, backgroundColor: '#444', padding: 8, borderRadius: 6, alignItems: 'center' }
});
