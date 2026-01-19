/**
 * Axios API client with authentication and error handling
 */

import axios, { AxiosError } from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { ApiError } from '../types/api';
import { supabase } from './supabaseClient';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      // First try to get token from localStorage directly to avoid Supabase lock issues
      // Check both possible storage keys
      const possibleKeys = [
        'resolveai-auth',                          // Our custom key
        'sb-lzruskvkrefnfljhdlfp-auth-token'       // Supabase default key
      ];
      
      for (const storageKey of possibleKeys) {
        const sessionStr = localStorage.getItem(storageKey);
        
        if (sessionStr) {
          try {
            const session = JSON.parse(sessionStr);
            if (session?.access_token) {
              config.headers.Authorization = `Bearer ${session.access_token}`;
              console.log('[API] Using token from localStorage (', storageKey, ') for:', config.url);
              return config;
            }
          } catch (parseErr) {
            console.warn('[API] Failed to parse session from', storageKey);
          }
        }
      }
      
      // Fallback to Supabase getSession if localStorage doesn't have it
      console.log('[API] No token in localStorage, trying Supabase getSession...');
      const { data, error } = await supabase.auth.getSession();

      if (error) {
        console.warn('[API] Failed to get session from Supabase:', error);
      } else if (data?.session?.access_token) {
        config.headers.Authorization = `Bearer ${data.session.access_token}`;
        console.log('[API] Using token from Supabase for:', config.url);
      } else {
        console.warn('[API] No session found for request:', config.url);
      }
    } catch (err: any) {
      console.error('[API] Error in request interceptor:', err.message);
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized - Refresh token
    if (error.response?.status === 401 && originalRequest) {
      try {
        const { data, error: refreshError } = await supabase.auth.refreshSession();

        if (refreshError || !data.session) {
          // Refresh failed, redirect to login
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Retry original request with new token
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${data.session.access_token}`;

        return api(originalRequest);
      } catch (refreshError) {
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    // Handle other errors
    const apiError: ApiError = error.response?.data || {
      error: 'NETWORK_ERROR',
      message: error.message || 'An unexpected error occurred',
    };

    return Promise.reject(apiError);
  }
);

export default api;
