import { useQuery } from '@tanstack/react-query'
import { fetchPhases } from '../api/client'
import StatusBadge from '../components/StatusBadge'

export default function Phases() {
  const { data = [], isLoading } = useQuery({ queryKey: ['phases'], queryFn: fetchPhases })

  if (isLoading) return <div className="text-gray-400 text-sm">Loading phases…</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Validation Phases</h1>
        <p className="text-sm text-gray-500 mt-1">IQ · OQ · PQ lifecycle</p>
      </div>
      <div className="grid gap-4">
        {data.map(p => (
          <div key={p.id} className="card">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-black text-pharma-blue">{p.name}</span>
                  <StatusBadge value={p.status} />
                </div>
                <p className="text-sm text-gray-500 mt-2">{p.description ?? '—'}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">Phase ID</p>
                <p className="text-sm font-mono text-pharma-teal">{p.id}</p>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
              <div>
                <p className="text-xs text-gray-400">Started</p>
                <p className="text-sm font-medium">{p.started_at ?? '—'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Completed</p>
                <p className="text-sm font-medium">{p.completed_at ?? '—'}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
