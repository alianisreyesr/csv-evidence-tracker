/**
 * App.jsx
 * -------
 * Root routing configuration.
 *
 * All application routes are wrapped in:
 *   1. <AuthProvider>  — provides global auth state (token, user, login, logout)
 *   2. <ProtectedRoute> — redirects to /login if no valid token is present
 *
 * The /login route is intentionally outside <ProtectedRoute> so
 * unauthenticated users can reach it without a redirect loop.
 */
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import RTM from './pages/RTM'
import TestQueue from './pages/TestQueue'
import Deviations from './pages/Deviations'
import AuditLog from './pages/AuditLog'
import Phases from './pages/Phases'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public route — no authentication required */}
        <Route path="/login" element={<LoginPage />} />

        {/* All other routes require a valid JWT */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard"  element={<Dashboard />} />
                  <Route path="/phases"     element={<Phases />} />
                  <Route path="/rtm"        element={<RTM />} />
                  <Route path="/test-queue" element={<TestQueue />} />
                  <Route path="/deviations" element={<Deviations />} />
                  <Route path="/audit"      element={<AuditLog />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthProvider>
  )
}
