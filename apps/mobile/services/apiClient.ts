/**
 * Core API Client for ORCA Mobile Application.
 * Built with native Fetch and basic try/catch wrappers designed to integrate 
 * with the offline SQLite cache queue.
 */

// Default to Render Production API
const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://orca-backend-tkus.onrender.com'; 

import { queueFailedRequest } from '../utils/offlineSync';

export const apiClient = {
  get: async (endpoint: string, params?: Record<string, string>) => {
    try {
      const url = new URL(`${BASE_URL}${endpoint}`);
      if (params) {
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
      }
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`[API GET Error] ${endpoint}:`, error);
      await queueFailedRequest(endpoint, 'GET', params);
      throw error;
    }
  },

  post: async (endpoint: string, data: any, isMultipart = false) => {
    try {
      const headers: Record<string, string> = {};
      // Fetch automatically sets the correct boundary for multipart/form-data
      // if we DO NOT explicitly set the Content-Type header.
      if (!isMultipart) {
        headers['Content-Type'] = 'application/json';
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: headers,
        body: isMultipart ? data : JSON.stringify(data),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`[API POST Error] ${endpoint}:`, error);
      await queueFailedRequest(endpoint, 'POST', data);
      throw error;
    }
  }
};
