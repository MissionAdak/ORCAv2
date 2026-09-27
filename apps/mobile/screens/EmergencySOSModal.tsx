import React, { useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Button } from '../components/Button';
import { RootStackScreenProps } from '../navigation/types';
import { MarineService } from '../services/marineService';
import { sendEmergencySMS } from '../utils/smsFallback';

export default function EmergencySOSModal({ navigation }: RootStackScreenProps<'EmergencySOSModal'>) {
  const { colors, typography } = useTheme();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSOSSubmit = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Data Mapping: default object_type and mocked last known GPS for now
      // In production, this would come from a useLocation hook
      await MarineService.createSARIncident({
        object_type: 'drifting_vessel',
        people_count: 1, // Defaulting to 1 for now
        last_known_lat: 19.1136, // Mock location (e.g. Mumbai coast)
        last_known_lon: 72.8090,
        vessel_id: 'UNKNOWN', // Or pull from user profile
      });
      
      Alert.alert("SOS Sent", "Search and Rescue forces have been notified.");
      navigation.goBack();
    } catch (err) {
      console.error("SOS failed, falling back to SMS...", err);
      setError("Network failed. Connecting to offline SMS fallback...");
      
      const mockIncidentData = {
        object_type: 'drifting_vessel',
        people_count: 1,
        last_known_lat: 19.1136,
        last_known_lon: 72.8090,
        vessel_id: 'UNKNOWN',
      };
      await sendEmergencySMS(mockIncidentData);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.sosBackground }]}>
      <Text style={[typography.h1, { color: colors.sosForeground, marginBottom: 8 }]}>
        EMERGENCY SOS
      </Text>
      
      {error ? (
        <Text style={[typography.bodyMedium, { color: 'white', backgroundColor: 'red', padding: 10, marginBottom: 24, textAlign: 'center' }]}>
          {error}
        </Text>
      ) : (
        <Text style={[typography.bodyMedium, { color: colors.sosForeground, textAlign: 'center', marginBottom: 24 }]}>
          Press to confirm emergency. This will alert local authorities and nearby vessels.
        </Text>
      )}

      {isLoading ? (
        <ActivityIndicator size="large" color={colors.sosForeground} />
      ) : (
        <View style={styles.buttonContainer}>
          <Button
            title="CONFIRM SOS"
            onPress={handleSOSSubmit}
            variant="primary"
          />
          <View style={{ height: 16 }} />
          <Button
            title="Cancel"
            onPress={() => navigation.goBack()}
            variant="secondary"
          />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  buttonContainer: {
    width: '100%',
    alignItems: 'center',
  }
});
