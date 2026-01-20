/**
 * Main App component with routing and auth state management
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { useEffect } from 'react';
import { useAuthStore } from './stores/authStore';
import { supabase } from './services/supabaseClient';
import api from './services/api';
import type { User } from './types/user';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AuthCallback from './pages/AuthCallback';
import AuthDebug from './pages/AuthDebug';
import { AppShell } from './components/layout/AppShell';

// Lazy load protected pages
import Debts from './pages/Debts';
import Plan from './pages/Plan';
import Progress from './pages/Progress';

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading, initializing } = useAuthStore();

  if (loading || initializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-main mx-auto mb-4"></div>
          <p className="text-slate-500">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

// Require onboarding complete
function RequireOnboarding({ children }: { children: React.ReactNode }) {
  const { user, loading, initializing } = useAuthStore();
  const needsOnboarding = user && !user.onboarding_completed;

  if (loading || initializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-main mx-auto mb-4"></div>
          <p className="text-slate-500">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  if (needsOnboarding) {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
}



import Onboarding from './pages/Onboarding';


function App() {
  const { refreshSession, setSession, setUser, setLoading } = useAuthStore();

  useEffect(() => {
    // Only run once on initial mount
    // Skip initialization if we're on the callback page (let AuthCallback handle it)
    const isOnCallbackPage = window.location.pathname === '/auth/callback';

    if (!isOnCallbackPage) {
      console.log('[App] Initializing auth...');
      refreshSession();
    } else {
      console.log('[App] Skipping auth init - on callback page');
    }

    // Global auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('[App] Auth state changed:', event, session?.user?.id);

      // Skip handling SIGNED_IN if we're on the callback page (let AuthCallback handle it)
      if (window.location.pathname === '/auth/callback' && event === 'SIGNED_IN') {
        console.log('[App] SIGNED_IN event on callback page - letting AuthCallback handle it');
        return;
      }

      // Ignore TOKEN_REFRESHED and SIGNED_IN events if we already have a user profile
      // These are just token refreshes, not new sign-ins
      if ((event === 'TOKEN_REFRESHED' || event === 'SIGNED_IN') && session) {
        const currentUser = useAuthStore.getState().user;
        if (currentUser && currentUser.id === session.user.id) {
          console.log('[App] Token refreshed/re-authenticated - user already loaded, skipping profile fetch');
          setSession(session); // Just update the session token
          return;
        }
      }

      // Update session in store
      setSession(session);

      if (event === 'SIGNED_IN' && session) {
        // User just signed in for the first time - fetch profile
        console.log('[App] New SIGNED_IN event - fetching user profile');
        setLoading(true);
        try {
          const response = await api.get<User>('/auth/me');
          if (response.data) {
            console.log('[App] User profile loaded:', response.data.id);
            setUser(response.data);
          }
        } catch (error: any) {
          console.error('[App] Failed to load user profile:', error);
        } finally {
          setLoading(false);
        }
      } else if (event === 'SIGNED_OUT' || !session) {
        console.log('[App] Signed out or no session');
        setUser(null);
      }
    });

    return () => {
      console.log('[App] Unsubscribing from auth changes');
      subscription.unsubscribe();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps - only run once on mount

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/auth/debug" element={<AuthDebug />} />

        {/* Onboarding (protected but no shell) */}
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <Onboarding />
            </ProtectedRoute>
          }
        />

        {/* Protected routes with AppShell layout */}
        <Route
          element={
            <RequireOnboarding>
              <AppShell />
            </RequireOnboarding>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/debts" element={<Debts />} />
          <Route path="/plan" element={<Plan />} />
          <Route path="/progress" element={<Progress />} />
          {/* Additional routes will be added here */}
          <Route path="/insights" element={<div className="p-6"><h1 className="text-2xl font-bold">Insights</h1><p className="text-slate-500">Coming soon...</p></div>} />
          <Route path="/negotiate" element={<div className="p-6"><h1 className="text-2xl font-bold">Negotiate</h1><p className="text-slate-500">Coming soon...</p></div>} />
          <Route path="/settings" element={<div className="p-6"><h1 className="text-2xl font-bold">Settings</h1><p className="text-slate-500">Coming soon...</p></div>} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
