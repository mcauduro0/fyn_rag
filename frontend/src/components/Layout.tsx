import { Outlet, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  History,
  Settings,
  Activity,
  Zap
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { healthCheck } from '../lib/api'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/analysis', label: 'Analysis', icon: TrendingUp },
  { path: '/history', label: 'History', icon: History },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
    refetchInterval: 30000,
  })

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-fyn-surface border-r-2 border-fyn-border flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b-2 border-fyn-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-fyn-accent flex items-center justify-center">
              <Zap className="w-6 h-6 text-fyn-bg" />
            </div>
            <div>
              <h1 className="text-lg font-bold">FYN RAG</h1>
              <p className="text-xs text-fyn-text-dim">Investment Committee</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map(({ path, label, icon: Icon }) => (
              <li key={path}>
                <NavLink
                  to={path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 border-2 transition-all ${
                      isActive
                        ? 'bg-fyn-accent text-fyn-bg border-fyn-accent'
                        : 'border-transparent hover:border-fyn-border text-fyn-text-dim hover:text-fyn-text'
                    }`
                  }
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* System Status */}
        <div className="p-4 border-t-2 border-fyn-border">
          <div className="flex items-center gap-2">
            <Activity
              className={`w-4 h-4 ${
                health?.status === 'healthy' ? 'text-fyn-accent' : 'text-fyn-danger'
              }`}
            />
            <span className="text-xs text-fyn-text-dim uppercase">
              System: {health?.status || 'checking...'}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-fyn-surface border-b-2 border-fyn-border flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <span className="text-fyn-text-dim text-sm">
              Powered by Claude Advanced Tool Use
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="status-badge status-success">
              <span className="w-2 h-2 rounded-full bg-fyn-accent mr-2"></span>
              138 Frameworks
            </div>
            <div className="status-badge status-success">
              <span className="w-2 h-2 rounded-full bg-fyn-accent mr-2"></span>
              5 Agents Online
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
