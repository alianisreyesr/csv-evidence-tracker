import { NavLink } from 'react-router-dom'
import { LayoutDashboard, FileText, FlaskConical, AlertTriangle, ScrollText, Layers } from 'lucide-react'
import clsx from 'clsx'

const nav = [
  { to: '/dashboard',  label: 'Dashboard',    icon: LayoutDashboard },
  { to: '/phases',     label: 'Phases',       icon: Layers },
  { to: '/rtm',        label: 'RTM',          icon: FileText },
  { to: '/test-queue', label: 'Test Queue',   icon: FlaskConical },
  { to: '/deviations', label: 'Deviations',   icon: AlertTriangle },
  { to: '/audit',      label: 'Audit Log',    icon: ScrollText },
]

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-60 bg-pharma-blue flex flex-col">
        <div className="px-6 py-5 border-b border-blue-800">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🧬</span>
            <div>
              <p className="text-white font-bold text-sm leading-tight">CSV Evidence</p>
              <p className="text-blue-300 text-xs">Tracker · GxP Suite</p>
            </div>
          </div>
        </div>
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
        <div className="px-4 py-4 border-t border-blue-800">
          <p className="text-blue-400 text-xs">21 CFR Part 11 · GAMP 5</p>
          <p className="text-blue-500 text-xs mt-0.5">ALCOA+ Compliant</p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  )
}
