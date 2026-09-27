import React, { useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Button } from '../components/Button';
import { RootStackScreenProps } from '../navigation/types';
import { MarineService } from '../services/marineService';
import { sendEmergencySMS } from '../utils/smsFallback';
import * as Location from 'expo-location';
import NetInfo from '@react-native-community/netinfo';

import { queueSOS } from '../utils/offlineDatabase';
import { syncSOSQueue } from '../utils/sosSync';

export default function EmergencySOSModal({ navigation }: RootStackScreenProps<'EmergencySOSModal'>) {
  const { colors, typography } = useTheme();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSOSSubmit = async () => {
  setIsLoading(true);
  setError(null);

  try {
    const permission =
      await Location.requestForegroundPermissionsAsync();

    if (permission.status !== 'granted') {
      throw new Error('Location permission denied');
    }

    const location =
      await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

    const incidentData = {
      object_type: 'drifting_vessel',
      people_count: 1,
      last_known_lat: location.coords.latitude,
      last_known_lon: location.coords.longitude,
      vessel_id: 'UNKNOWN',
    };

    console.log(
      '[ORCA] SOS location:',
      incidentData.last_known_lat,
      incidentData.last_known_lon
    );

    const clientUuid =
      `sos-${Date.now()}-${Math.random()
        .toString(36)
        .substring(2, 10)}`;

    const network = await NetInfo.fetch();

    const online =
      network.isConnected === true &&
      network.isInternetReachable !== false;

    if (online) {
      try {
        await MarineService.createSARIncident(
          incidentData
        );

        Alert.alert(
          'SOS Sent',
          'Emergency incident registered successfully.'
        );

        navigation.goBack();
        return;
      } catch (error) {
        console.error(
          '[ORCA] Backend SOS failed:',
          error
        );
      }
    }

    const smsOpened =
      await sendEmergencySMS(incidentData);

    await queueSOS(
      clientUuid,
      incidentData
    );

    if (smsOpened) {
      setError(
        'Emergency SMS opened. SOS is also saved locally for synchronization.'
      );
    } else {
      setError(
        'Network and SMS unavailable. SOS saved locally and will sync when internet returns.'
      );
    }

    await syncSOSQueue();

  } catch (error) {
    console.error(
      '[ORCA] SOS processing failed:',
      error
    );

    setError(
      'Unable to obtain your location or process the SOS.'
    );
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
