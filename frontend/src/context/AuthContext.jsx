/**
 * AuthContext.jsx
 * ---------------
 * Global authentication state for the CSV Evidence Tracker UI.
 *
 * Provides:
 *   - token        : raw JWT string (null when unauthenticated)
 *   - user         : { username, role, full_name } decoded from /auth/me
 *   - login()      : POST /auth/login, store token, fetch /auth/me
 *   - logout()     : clear state and sessionStorage
 *   - isLoading    : true while the initial session is being restored
 *
 * Token is persisted in sessionStorage so it survives page refreshes but
 * is discarded when the browser tab is closed (portfolio-appropriate scope).
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext(null)

const API_BASE = '/api'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null)
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Restore session from sessionStorage on mount
  useEffect(() => {
    const stored = sessionStorage.getItem('csv_token')
    if (stored) {
      setToken(stored)
      fetchMe(stored).finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchMe = useCallback(async (jwt) => {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${jwt}` },
      })
      if (res.ok) {
        const data = await res.json()
        setUser(data)
      } else {
        // Token is invalid or expired — clear session
        clearSession()
      }
    } catch {
      clearSession()
    }
  }, [])

  const clearSession = () => {
    setToken(null)
    setUser(null)
    sessionStorage.removeItem('csv_token')
  }

  /**
   * Authenticate with the backend and persist the resulting JWT.
   * Throws an Error with a user-facing message on failure.
   */
  const login = async (username, password) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username, password }),
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || 'Invalid credentials. Please try again.')
    }

    const data = await res.json()
    sessionStorage.setItem('csv_token', data.access_token)
    setToken(data.access_token)
    setUser({ username, role: data.role, full_name: data.full_name })
    return data
  }

  const logout = () => clearSession()

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

/** Hook — throws if used outside <AuthProvider>. */
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
