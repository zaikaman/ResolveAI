/**
 * Zustand store for authentication state management with Supabase Google OAuth
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types/user';
import { supabase } from '../services/supabaseClient';

interface AuthState {
  user: User | null;
  session: any | null;
  loading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setSession: (session: any | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      session: null,
      loading: false,
      error: null,

      setUser: (user) => set({ user }),

      setSession: (session) => set({ session }),

      setLoading: (loading) => set({ loading }),

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
          set({ loading: true, error: null });
          const { data, error } = await supabase.auth.getSession();

          if (error) throw error;

          if (data.session) {
            set({ session: data.session });

            // Fetch user profile from our backend
            const response = await fetch('/api/auth/me', {
              headers: {
                'Authorization': `Bearer ${data.session.access_token}`
              }
            });

            if (response.ok) {
              const user = await response.json();
              set({ user });
            }
          } else {
            set({ user: null, session: null });
          }
        } catch (error: any) {
          set({ error: error.message || 'Session refresh failed' });
        } finally {
          set({ loading: false });
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        session: state.session
      })
    }
  )
);
