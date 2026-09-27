import { Linking, Alert } from 'react-native';

export interface IncidentData {
  object_type: string;
  people_count: number;
  last_known_lat: number;
  last_known_lon: number;
  vessel_id: string;
}

const EMERGENCY_NUMBER = '112'; // General maritime/emergency number

export const sendEmergencySMS = async (incidentData: IncidentData) => {
  try {
    // Compress data to a short 120-character format for 2G SMS transmission
    const payload = `SOS|Vessel:${incidentData.vessel_id.substring(0, 10)}|Lat:${incidentData.last_known_lat.toFixed(4)}|Lon:${incidentData.last_known_lon.toFixed(4)}|Crew:${incidentData.people_count}`;
    
    const url = `sms:${EMERGENCY_NUMBER}?body=${encodeURIComponent(payload)}`;
    
    const canOpen = await Linking.canOpenURL(url);
    if (canOpen) {
      await Linking.openURL(url);
    } else {
      Alert.alert('Error', 'SMS is not available on this device');
    }
  } catch (error) {
    console.error('Failed to trigger SMS fallback:', error);
  }
};
