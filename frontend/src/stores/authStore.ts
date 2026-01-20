/**
 * Zustand store for authentication state management with Supabase Google OAuth
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types/user';
import { supabase } from '../services/supabaseClient';
import api from '../services/api';

interface AuthState {
  user: User | null;
  session: any | null;
  loading: boolean;
  initializing: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setSession: (session: any | null) => void;
  setLoading: (loading: boolean) => void;
  setInitializing: (initializing: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      session: null,
      loading: true,
      initializing: true,
      error: null,

      setUser: (user) => set({ user }),

      setSession: (session) => set({ session }),

      setLoading: (loading) => set({ loading }),

      setInitializing: (initializing) => set({ initializing }),

      setError: (error) => set({ error }),

      logout: async () => {
        try {
          set({ loading: true, error: null });
          await supabase.auth.signOut();
          set({ user: null, session: null });
        } catch (error: any) {
          set({ error: error.message || 'Logout failed' });
        } finally {
          set({ loading: false });
        }
      },

      refreshSession: async () => {
        try {
          console.log('[AuthStore] refreshSession: Starting...');
          // Use initializing instead of loading for initial checks to avoid showing loading screen on tab switch
          const isInitialLoad = get().initializing;
          if (isInitialLoad) {
            set({ loading: true, error: null });
          } else {
            // Silent refresh - don't trigger loading state
            set({ error: null });
          }
          
          const { data, error } = await supabase.auth.getSession();

          if (error) {
            // Ignore abort errors - they're caused by lock contention
            if (error.message?.includes('abort')) {
              console.log('[AuthStore] refreshSession: Aborted (likely lock contention), ignoring');
              set({ loading: false, initializing: false });
              return;
            }
            console.error('[AuthStore] refreshSession: Supabase getSession error:', error);
            set({ user: null, session: null, error: error.message });
            return;
          }

          if (data.session) {
            console.log('[AuthStore] refreshSession: Session found', data.session.user.id);
            set({ session: data.session });

            // Only fetch user profile if we don't have it or it's stale
            const currentUser = get().user;
            if (!currentUser || currentUser.id !== data.session.user.id) {
              console.log('[AuthStore] refreshSession: Fetching user profile from backend...');
              try {
                const response = await api.get('/auth/me');
                console.log('[AuthStore] refreshSession: Backend response status:', response.status);

                if (response.data) {
                  console.log('[AuthStore] refreshSession: User profile loaded', response.data.id);
                  set({ user: response.data });
                }
              } catch (err: any) {
                console.error('[AuthStore] refreshSession: Failed to fetch backend profile', err);
                // Don't throw - session is valid, user will be created lazily
                if (err.response?.status !== 401) {
                  set({ error: 'Failed to load profile' });
                }
              }
            } else {
              console.log('[AuthStore] refreshSession: User already loaded, skipping fetch');
            }
          } else {
            console.log('[AuthStore] refreshSession: No session found');
            set({ user: null, session: null });
          }
        } catch (error: any) {
          // Catch any abort errors that slip through
          if (error.name === 'AbortError' || error.message?.includes('abort')) {
            console.log('[AuthStore] refreshSession: Caught AbortError, ignoring');
            set({ loading: false, initializing: false });
            return;
          }
          console.error('[AuthStore] refreshSession: Error', error);
          set({ user: null, session: null, error: error.message || 'Session refresh failed' });
        } finally {
          console.log('[AuthStore] refreshSession: Finished');
          const isInitialLoad = get().initializing;
          if (isInitialLoad) {
            set({ loading: false, initializing: false });
          } else {
            // Silent refresh - loading state wasn't changed, just mark as initialized
            set({ initializing: false });
          }
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        // Only persist user, not session (session should come from Supabase)
        user: state.user
      })
    }
  )
);
