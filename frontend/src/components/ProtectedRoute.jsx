/**
 * ProtectedRoute.jsx
 * ------------------
 * Wrapper that redirects unauthenticated users to /login.
 *
 * Saves the attempted location in router state so LoginPage can redirect
 * back to it after a successful login (standard React Router v6 pattern).
 *
 * While the auth session is being restored from sessionStorage (isLoading),
 * renders nothing to avoid a flash of the login page for returning users.
 */
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { token, isLoading } = useAuth()
  const location = useLocation()

  // Wait for session restoration before deciding to redirect
  if (isLoading) return null

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}
