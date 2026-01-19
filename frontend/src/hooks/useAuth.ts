/**
 * Custom hook for authentication with Supabase Google OAuth
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { supabase } from '../services/supabaseClient';
import api from '../services/api';
import type { User, OnboardingData, UserUpdate } from '../types/user';

export function useAuth() {
  const { user, session, loading, error, setUser, setSession, setLoading, setError, logout, refreshSession } = useAuthStore();
  const navigate = useNavigate();

  // Initialize auth state on mount
  useEffect(() => {
    refreshSession();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setSession(session);

      if (session) {
        try {
          // Fetch user profile from backend
          const response = await api.get<User>('/auth/me');
          setUser(response.data);
        } catch (error: any) {
          console.error('Failed to fetch user profile:', error);
          setError(error.message || 'Failed to fetch user profile');
        }
      } else {
        setUser(null);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  /**
   * Sign in with Google OAuth
   */
  const signInWithGoogle = async () => {
    try {
      setLoading(true);
      setError(null);

      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      });

      if (error) throw error;
    } catch (error: any) {
      setError(error.message || 'Google sign-in failed');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update user profile
   */
  const updateProfile = async (updates: UserUpdate): Promise<User> => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.put<User>('/auth/me', updates);
      setUser(response.data);

      return response.data;
    } catch (error: any) {
      setError(error.message || 'Failed to update profile');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Complete onboarding with financial data
   */
  const completeOnboarding = async (data: OnboardingData): Promise<User> => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.post<User>('/auth/onboarding/complete', data);
      setUser(response.data);

      return response.data;
    } catch (error: any) {
      setError(error.message || 'Failed to complete onboarding');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Check onboarding status
   */
  const checkOnboardingStatus = async (): Promise<{ completed: boolean; has_financial_data: boolean }> => {
    try {
      const response = await api.get('/auth/onboarding/status');
      return response.data;
    } catch (error: any) {
      console.error('Failed to check onboarding status:', error);
      throw error;
    }
  };

  /**
   * Delete user account
   */
  const deleteAccount = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      await api.delete('/auth/me');
      await logout();
      navigate('/');
    } catch (error: any) {
      setError(error.message || 'Failed to delete account');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    session,
    loading,
    error,
    signInWithGoogle,
    logout,
    updateProfile,
    completeOnboarding,
    checkOnboardingStatus,
    deleteAccount,
    isAuthenticated: !!user,
    needsOnboarding: user && !user.onboarding_completed,
  };
}
