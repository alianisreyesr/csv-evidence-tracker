import { useQuery } from '@tanstack/react-query'
import { fetchPhases } from '../api/client'
import StatusBadge from '../components/StatusBadge'

const PHASE_DESC = {
  IQ: 'Installation Qualification — verifies system is installed per specifications.',
  OQ: 'Operational Qualification — verifies system operates within defined parameters.',
  PQ: 'Performance Qualification — verifies system performs consistently under real conditions.'
}

export default function Phases() {
  const { data = [], isLoading } = useQuery({ queryKey: ['phases'], queryFn: fetchPhases })

  if (isLoading) return <div className="text-gray-400 text-sm">Loading phases…</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Validation Phases</h1>
        <p className="text-sm text-gray-500 mt-1">IQ · OQ · PQ lifecycle per GAMP 5</p>
      </div>
      <div className="grid gap-4">
        {data.map(p => (
          <div key={p.phase_id} className="card">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-black text-pharma-blue">{p.phase_name}</span>
                  <StatusBadge value={p.status} />
                </div>
                <p className="text-sm text-gray-500 mt-1">{PHASE_DESC[p.phase_name] ?? ''}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">Owner</p>
                <p className="text-sm font-medium">{p.owner}</p>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
              <div>
                <p className="text-xs text-gray-400">Start Date</p>
                <p className="text-sm font-medium">{p.start_date ?? '—'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">End Date</p>
                <p className="text-sm font-medium">{p.end_date ?? '—'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Phase ID</p>
                <p className="text-sm font-mono text-pharma-teal">{p.phase_id}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
