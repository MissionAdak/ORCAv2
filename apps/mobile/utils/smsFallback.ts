import { Linking, Alert } from 'react-native';

export interface IncidentData {
  object_type: string;
  people_count: number;
  last_known_lat: number;
  last_known_lon: number;
  vessel_id: string;
}

const EMERGENCY_NUMBER = '112';

function getTypeCode(type: string): string {
  switch (type) {
    case 'person_in_water':
      return 'PIW';
    case 'capsized_hull':
      return 'CAP';
    case 'drifting_vessel':
      return 'ADR';
    default:
      return 'UNK';
  }
}

export function buildSOSPayload(
  incident: IncidentData
): string {
  const vessel = (incident.vessel_id || 'UNKNOWN')
    .replace(/[^A-Za-z0-9]/g, '')
    .substring(0, 10);

  const payload =
    `ORCA|SOS|${incident.last_known_lat.toFixed(4)}N|` +
    `${incident.last_known_lon.toFixed(4)}E|` +
    `C${incident.people_count}|V:${vessel}|` +
    `T:${getTypeCode(incident.object_type)}`;

  return payload.substring(0, 120);
}

export async function sendEmergencySMS(
  incident: IncidentData
): Promise<boolean> {
  try {
    const payload = buildSOSPayload(incident);

    console.log(
      `[ORCA] SMS payload (${payload.length} chars): ${payload}`
    );

    const smsUrl =
      `sms:${EMERGENCY_NUMBER}?body=${encodeURIComponent(payload)}`;

    await Linking.openURL(smsUrl);

    return true;
  } catch (error) {
    console.error('[ORCA] SMS fallback failed:', error);

    Alert.alert(
      'SMS unavailable',
      'The emergency messaging application could not be opened.'
    );

    return false;
  }
}