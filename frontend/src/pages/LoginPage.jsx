/**
 * LoginPage.jsx
 * -------------
 * Authentication screen for the CSV Evidence Tracker.
 *
 * Displays a login form pre-populated with synthetic portfolio credentials
 * so reviewers can explore the RBAC system without reading documentation.
 *
 * On success the user is redirected to the dashboard (or the page they
 * originally tried to access via React Router's `state.from` mechanism).
 */
import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FlaskConical, LogIn, AlertCircle } from 'lucide-react'

// Synthetic credentials displayed as quick-select buttons for portfolio demos
const DEMO_USERS = [
  { label: 'Analyst',     username: 'analyst01',     password: 'Analyst01!',   color: 'bg-blue-100 text-blue-800   border-blue-200' },
  { label: 'QA Reviewer', username: 'qa_reviewer01', password: 'QAReview01!',  color: 'bg-purple-100 text-purple-800 border-purple-200' },
  { label: 'Admin',       username: 'admin01',       password: 'Admin01!',     color: 'bg-amber-100  text-amber-800  border-amber-200' },
]

export default function LoginPage() {
  const { login } = useAuth()
  const navigate   = useNavigate()
  const location   = useLocation()
  const from       = location.state?.from?.pathname || '/dashboard'

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fillUser = (u) => {
    setUsername(u.username)
    setPassword(u.password)
    setError('')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-pharma-blue mb-4">
            <FlaskConical size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">CSV Evidence Tracker</h1>
          <p className="text-sm text-gray-500 mt-1">GxP · 21 CFR Part 11 · ALCOA+</p>
        </div>

        {/* Demo role selector */}
        <div className="mb-6">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Quick select — portfolio demo
          </p>
          <div className="flex gap-2 flex-wrap">
            {DEMO_USERS.map((u) => (
              <button
                key={u.username}
                type="button"
                onClick={() => fillUser(u)}
                className={`text-xs font-medium px-3 py-1.5 rounded-full border cursor-pointer transition-opacity hover:opacity-80 ${u.color}`}
              >
                {u.label}
              </button>
            ))}
          </div>
        </div>

        {/* Login form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-4">

          {error && (
            <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              <AlertCircle size={15} />
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="analyst01"
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pharma-blue"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pharma-blue"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-pharma-blue text-white font-medium py-2.5 rounded-lg text-sm hover:opacity-90 transition-opacity disabled:opacity-60"
          >
            <LogIn size={16} />
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="text-center text-xs text-gray-400 mt-6">
          Synthetic data only · Not for regulated use
        </p>
      </div>
    </div>
  )
}
