import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchAuditLog } from '../api/client'

export default function AuditLog() {
  const [filter, setFilter] = useState('')
  const { data = [], isLoading } = useQuery({ queryKey: ['audit'], queryFn: fetchAuditLog })

  const filtered = data.filter(e =>
    !filter ||
    e.action?.toLowerCase().includes(filter.toLowerCase()) ||
    e.endpoint?.toLowerCase().includes(filter.toLowerCase()) ||
    e.user_id?.toLowerCase().includes(filter.toLowerCase())
  )

  if (isLoading) return <div className="text-gray-400 text-sm">Loading audit trail…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Trail</h1>
          <p className="text-sm text-gray-500 mt-1">21 CFR Part 11 · Immutable · ALCOA+</p>
        </div>
        <input
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-56 focus:outline-none focus:ring-2 focus:ring-pharma-teal"
          placeholder="Filter by action, endpoint…"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
      </div>

      <div className="bg-gray-900 rounded-xl overflow-hidden">
        <div className="px-4 py-2 bg-gray-800 flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-400" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-gray-400 text-xs ml-2 font-mono">audit_log · read-only</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                {['Timestamp', 'Method', 'Endpoint', 'Status', 'User', 'Details'].map(h => (
                  <th key={h} className="px-4 py-2 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {filtered.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-6 text-center text-gray-500 text-sm">No audit entries found</td></tr>
              )}
              {filtered.map((e, i) => (
                <tr key={i} className="hover:bg-gray-800/50 transition-colors">
                  <td className="px-4 py-2 text-xs font-mono text-gray-400">
                    {e.timestamp ? new Date(e.timestamp).toLocaleString() : '—'}
                  </td>
                  <td className="px-4 py-2">
                    <span className={`text-xs font-bold font-mono ${
                      e.method === 'POST' ? 'text-green-400' :
                      e.method === 'PUT'  ? 'text-yellow-400' :
                      e.method === 'DELETE' ? 'text-red-400' : 'text-blue-400'
                    }`}>{e.method}</span>
                  </td>
                  <td className="px-4 py-2 text-xs font-mono text-gray-300">{e.endpoint}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs font-semibold ${
                      e.status_code < 300 ? 'text-green-400' :
                      e.status_code < 400 ? 'text-yellow-400' : 'text-red-400'
                    }`}>{e.status_code}</span>
                  </td>
                  <td className="px-4 py-2 text-xs text-gray-400">{e.user_id ?? 'system'}</td>
                  <td className="px-4 py-2 text-xs text-gray-500 font-mono truncate max-w-xs">{e.details ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
