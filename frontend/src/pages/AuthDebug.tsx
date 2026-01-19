/**
 * Debug page to diagnose OAuth callback issues
 * Navigate to /auth/debug to see detailed auth state
 */

import { useEffect, useState } from 'react';
import { supabase } from '../services/supabaseClient';

export default function AuthDebug() {
  const [info, setInfo] = useState<any>({});

  useEffect(() => {
    const checkAuth = async () => {
      const debugInfo: any = {
        timestamp: new Date().toISOString(),
        url: window.location.href,
        hash: window.location.hash,
        search: window.location.search,
        pathname: window.location.pathname,
      };

      // Check localStorage
      const storedKeys = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key) storedKeys.push(key);
      }
      debugInfo.localStorageKeys = storedKeys;
      debugInfo.supabaseStorageKey = localStorage.getItem('resolveai-auth');

      // Get session
      try {
        const { data, error } = await supabase.auth.getSession();
        debugInfo.session = {
          exists: !!data.session,
          userId: data.session?.user?.id,
          email: data.session?.user?.email,
          expiresAt: data.session?.expires_at,
          error: error?.message,
        };
      } catch (err: any) {
        debugInfo.sessionError = err.message;
      }

      // Get user
      try {
        const { data, error } = await supabase.auth.getUser();
        debugInfo.user = {
          exists: !!data.user,
          userId: data.user?.id,
          email: data.user?.email,
          error: error?.message,
        };
      } catch (err: any) {
        debugInfo.userError = err.message;
      }

      setInfo(debugInfo);
    };

    checkAuth();
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">🔍 Auth Debug Info</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-4">
          <h2 className="text-xl font-semibold mb-4">Current State</h2>
          <pre className="bg-slate-50 p-4 rounded overflow-auto text-xs">
            {JSON.stringify(info, null, 2)}
          </pre>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Actions</h2>
          <div className="space-y-2">
            <button
              onClick={() => window.location.href = '/login'}
              className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Go to Login
            </button>
            <button
              onClick={() => {
                localStorage.clear();
                window.location.reload();
              }}
              className="w-full py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Clear Storage & Reload
            </button>
            <button
              onClick={() => window.location.reload()}
              className="w-full py-2 px-4 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
