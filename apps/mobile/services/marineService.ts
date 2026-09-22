import { apiClient } from './apiClient';

/**
 * Service to interact with core ORCA backend endpoints.
 */
export const MarineService = {
  /**
   * GET /api/marine/forecast
   * Fetches the marine forecast for a given location.
   */
  getMarineForecast: async (lat: number, lon: number, date?: string) => {
    const params: Record<string, string> = {
      lat: lat.toString(),
      lon: lon.toString(),
    };
    if (date) {
      params.date = date;
    }
    return apiClient.get('/api/marine/forecast', params);
  },

  /**
   * POST /api/chat
   * Sends voice (audio file) or text to the Bhashini service.
   */
  sendChatIntent: async (audioFile?: any, text?: string) => {
    const formData = new FormData();
    if (audioFile) {
      formData.append('audio', audioFile);
    }
    if (text) {
      formData.append('text', text);
    }
    // Pass isMultipart = true to handle FormData correctly
    return apiClient.post('/api/chat', formData, true);
  },

  /**
   * POST /api/sar/create
   * Creates a new Search and Rescue incident.
   */
  createSARIncident: async (incidentData: {
    object_type: string;
    people_count: number;
    last_known_lat: number;
    last_known_lon: number;
    vessel_id: string;
  }) => {
    return apiClient.post('/api/sar/create', incidentData);
  }
};
