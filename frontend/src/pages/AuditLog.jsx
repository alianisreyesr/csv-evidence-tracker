import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchAuditLog } from '../api/client'

export default function AuditLog() {
  const [filter, setFilter] = useState('')
  const { data = [], isLoading } = useQuery({ queryKey: ['audit'], queryFn: fetchAuditLog })

  const filtered = data.filter(e => {
    const haystack = [e.action, e.actor, e.table_affected, e.record_id].filter(Boolean).join(' ').toLowerCase()
    return !filter || haystack.includes(filter.toLowerCase())
  })

  if (isLoading) return <div className="text-gray-400 text-sm">Loading audit trail…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Trail</h1>
          <p className="text-sm text-gray-500 mt-1">Append-oriented audit evidence · ALCOA+</p>
        </div>
        <input
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-56 focus:outline-none focus:ring-2 focus:ring-pharma-teal"
          placeholder="Filter by actor, action, table…"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
      </div>

      <div className="bg-gray-900 rounded-xl overflow-hidden">
        <div className="px-4 py-2 bg-gray-800 flex items-center gap-2">
          <span className="text-gray-400 text-xs font-mono">audit_log · read-only API</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                {['Timestamp', 'Actor', 'Action', 'Table', 'Record', 'Status', 'Latency'].map(h => (
                  <th key={h} className="px-4 py-2 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {filtered.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-6 text-center text-gray-500 text-sm">No audit entries found</td></tr>
              )}
              {filtered.map(e => (
                <tr key={e.id} className="hover:bg-gray-800/50 transition-colors">
                  <td className="px-4 py-2 text-xs font-mono text-gray-400">{e.created_at ? new Date(e.created_at).toLocaleString() : '—'}</td>
                  <td className="px-4 py-2 text-xs text-gray-300">{e.actor ?? 'system'}</td>
                  <td className="px-4 py-2 text-xs font-mono text-blue-300">{e.action}</td>
                  <td className="px-4 py-2 text-xs text-gray-400">{e.table_affected ?? '—'}</td>
                  <td className="px-4 py-2 text-xs text-gray-400">{e.record_id ?? '—'}</td>
                  <td className="px-4 py-2 text-xs text-gray-400">{e.status_code ?? '—'}</td>
                  <td className="px-4 py-2 text-xs text-gray-400">{e.latency_ms != null ? `${e.latency_ms} ms` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
