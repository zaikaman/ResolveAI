/**
 * OAuth callback handler page
 */

import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import api from '../services/api';
import type { User } from '../types/user';

/**
 * Parse the URL hash to extract OAuth tokens
 */
function parseHashParams(hash: string): Record<string, string> {
  const params: Record<string, string> = {};
  if (!hash || hash.length <= 1) return params;

  const hashContent = hash.substring(1); // Remove the #
  const pairs = hashContent.split('&');

  for (const pair of pairs) {
    const [key, value] = pair.split('=');
    if (key && value) {
      params[decodeURIComponent(key)] = decodeURIComponent(value);
    }
  }

  return params;
}

export default function AuthCallback() {
  const navigate = useNavigate();
  const { setUser, setSession, setLoading, setError, setInitializing } = useAuthStore();
  const [isProcessing, setIsProcessing] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);
  const hasRun = useRef(false); // Prevent double execution in Strict Mode

  useEffect(() => {
    const handleCallback = async () => {
      if (hasRun.current) return;
      hasRun.current = true;

      try {
        console.log('[AuthCallback] Processing OAuth callback...');
        setLoading(true);
        setInitializing(true);

        // Parse tokens from URL hash
        const hashParams = parseHashParams(window.location.hash);
        console.log('[AuthCallback] Parsed hash params:', Object.keys(hashParams));

        if (!hashParams.access_token) {
          throw new Error('No access token found in callback URL');
        }

        // WORKAROUND for Supabase Auth-JS deadlock issue (https://github.com/supabase/supabase-js/issues/2013)
        // Instead of using setSession() which causes Navigator Lock deadlock,
        // manually store the session and update the store
        console.log('[AuthCallback] Manually storing session to avoid deadlock...');
        
        // Calculate expiry timestamp
        const expiresIn = parseInt(hashParams.expires_in || '3600', 10);
        const expiresAt = Math.floor(Date.now() / 1000) + expiresIn;

        // Create session object matching Supabase Session type
        const session = {
          access_token: hashParams.access_token,
          refresh_token: hashParams.refresh_token,
          expires_in: expiresIn,
          expires_at: expiresAt,
          token_type: hashParams.token_type || 'bearer',
          user: null, // Will be populated from API call
        };

        // Store session in localStorage (matching Supabase's storage key)
        const storageKey = 'resolveai-auth';
        localStorage.setItem(storageKey, JSON.stringify(session));
        console.log('[AuthCallback] Session stored in localStorage');

        // Update Zustand store with session
        setSession(session as any);

        // Clear the hash from URL (for security and to prevent re-processing)
        window.history.replaceState(null, '', window.location.pathname);

        // Wait a bit for storage to sync
        await new Promise(resolve => setTimeout(resolve, 200));

        // Fetch user profile using the access token directly
        console.log('[AuthCallback] Fetching user profile...');
        const response = await api.get<User>('/auth/me');

        if (!response.data) {
          throw new Error('Failed to load user profile');
        }

        console.log('[AuthCallback] User profile loaded:', response.data.id);
        setUser(response.data);
        setError(null);
        setLoading(false);
        setIsProcessing(false);

        // Navigate based on onboarding status
        if (response.data.onboarding_completed) {
          console.log('[AuthCallback] Redirecting to dashboard');
          navigate('/dashboard', { replace: true });
        } else {
          console.log('[AuthCallback] Redirecting to onboarding');
          navigate('/onboarding', { replace: true });
        }
      } catch (err: any) {
        console.error('[AuthCallback] Error during callback:', err);
        const errorMsg = err.response?.data?.message || err.message || 'Authentication failed. Please try again.';
        setAuthError(errorMsg);
        setError(errorMsg);
        setLoading(false);
        setIsProcessing(false);
      } finally {
        setInitializing(false);
      }
    };

    handleCallback();
  }, [navigate, setUser, setSession, setLoading, setError, setInitializing]);

  if (isProcessing && !authError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Completing sign in...</p>
        </div>
      </div>
    );
  }

  // Error State
  if (authError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Sign In Failed</h2>
          <p className="text-gray-600 mb-6">{authError}</p>
          <button
            onClick={() => navigate('/login')}
            className="w-full py-3 px-4 bg-main text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // This shouldn't be reached, but just in case
  return null;
}
