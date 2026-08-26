/**
 * Layout.jsx
 * ----------
 * Application shell — sidebar navigation + main content area.
 *
 * Sidebar footer displays:
 *   - Current user's full name and username
 *   - Role badge (color-coded by role)
 *   - Logout button that clears the session and redirects to /login
 */
import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, FlaskConical, AlertTriangle, ScrollText, Layers, LogOut } from 'lucide-react'
import clsx from 'clsx'
import { useAuth } from '../context/AuthContext'
import RoleBadge from './RoleBadge'

const nav = [
  { to: '/dashboard',  label: 'Dashboard',  icon: LayoutDashboard },
  { to: '/phases',     label: 'Phases',     icon: Layers },
  { to: '/rtm',        label: 'RTM',        icon: FileText },
  { to: '/test-queue', label: 'Test Queue', icon: FlaskConical },
  { to: '/deviations', label: 'Deviations', icon: AlertTriangle },
  { to: '/audit',      label: 'Audit Log',  icon: ScrollText },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-60 bg-pharma-blue flex flex-col">

        {/* Brand */}
        <div className="px-6 py-5 border-b border-blue-800">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🧬</span>
            <div>
              <p className="text-white font-bold text-sm leading-tight">CSV Evidence</p>
              <p className="text-blue-300 text-xs">Tracker · GxP Suite</p>
            </div>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-white/15 text-white'
                    : 'text-blue-200 hover:bg-white/10 hover:text-white'
                )
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* User identity + logout */}
        <div className="px-4 py-4 border-t border-blue-800 space-y-3">
          {user && (
            <div className="space-y-1">
              <p className="text-white text-xs font-semibold truncate">
                {user.full_name || user.username}
              </p>
              <p className="text-blue-400 text-xs truncate">@{user.username}</p>
              <RoleBadge role={user.role} />
            </div>
          )}

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-blue-300 hover:text-white text-xs transition-colors w-full"
          >
            <LogOut size={13} />
            Sign out
          </button>

          <p className="text-blue-500 text-xs">21 CFR Part 11 · GAMP 5</p>
          <p className="text-blue-600 text-xs">ALCOA+ concepts · portfolio only</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="border-b border-amber-200 bg-amber-50 px-8 py-2 text-sm text-amber-900">
          Synthetic evidence only · Not validated software · Not for regulated decisions
        </div>
        <div className="max-w-7xl mx-auto px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  )
}
