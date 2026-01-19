/**
 * Main App component with routing and auth state management
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
// import { useAuth } from './hooks/useAuth'; // Reserved for Phase 2+
import LandingPage from './pages/LandingPage';
import AuthCallback from './pages/AuthCallback';

// Protected route wrapper - Reserved for Phase 2+
// function ProtectedRoute({ children }: { children: React.ReactNode }) {
//   const { user, loading } = useAuth();

//   if (loading) {
//     return (
//       <div className="min-h-screen flex items-center justify-center">
//         <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
//       </div>
//     );
//   }

//   if (!user) {
//     return <Navigate to="/" replace />;
//   }

//   return <>{children}</>;
// }

// Require onboarding complete - Reserved for Phase 2+
// function RequireOnboarding({ children }: { children: React.ReactNode }) {
//   const { user, loading, needsOnboarding } = useAuth();

//   if (loading) {
//     return (
//       <div className="min-h-screen flex items-center justify-center">
//         <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
//       </div>
//     );
//   }

//   if (!user) {
//     return <Navigate to="/" replace />;
//   }

//   if (needsOnboarding) {
//     return <Navigate to="/onboarding" replace />;
//   }

//   return <>{children}</>;
// }

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth/callback" element={<AuthCallback />} />

        {/* Protected routes - Phase 2+ will add these */}
        {/* <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <Onboarding />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <RequireOnboarding>
              <Dashboard />
            </RequireOnboarding>
          }
        />
        <Route
          path="/debts"
          element={
            <RequireOnboarding>
              <Debts />
            </RequireOnboarding>
          }
        />
        <Route
          path="/plan"
          element={
            <RequireOnboarding>
              <Plan />
            </RequireOnboarding>
          }
        /> */}

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

