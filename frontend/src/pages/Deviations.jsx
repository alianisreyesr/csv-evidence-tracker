import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchDeviations, createDeviation, resolveDeviation } from '../api/client'
import StatusBadge from '../components/StatusBadge'

const SEVERITIES = ['Critical', 'High', 'Medium', 'Low']

export default function Deviations() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [resolving, setResolving] = useState(null)
  const [capaRef, setCapaRef] = useState('')
  const [form, setForm] = useState({
    title: '', description: '', severity: 'High',
    reported_by: '', phase_id: '', requirement_id: ''
  })

  const { data = [], isLoading } = useQuery({ queryKey: ['deviations'], queryFn: fetchDeviations })

  const createMut = useMutation({
    mutationFn: createDeviation,
    onSuccess: () => {
      qc.invalidateQueries(['deviations'])
      qc.invalidateQueries(['summary'])
      setShowForm(false)
      setForm({ title: '', description: '', severity: 'High', reported_by: '', phase_id: '', requirement_id: '' })
    }
  })

  const resolveMut = useMutation({
    mutationFn: ({ id, capa }) => resolveDeviation(id, { capa_reference: capa }),
    onSuccess: () => {
      qc.invalidateQueries(['deviations'])
      qc.invalidateQueries(['summary'])
      setResolving(null)
      setCapaRef('')
    }
  })

  if (isLoading) return <div className="text-gray-400 text-sm">Loading deviations…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Deviation Tracker</h1>
          <p className="text-sm text-gray-500 mt-1">Non-conformances · CAPA management · Risk scoring</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(true)}>+ New Deviation</button>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="table-th">ID</th>
              <th className="table-th">Title</th>
              <th className="table-th">Severity</th>
              <th className="table-th">Status</th>
              <th className="table-th">Risk Score</th>
              <th className="table-th">CAPA Ref</th>
              <th className="table-th">Reported By</th>
              <th className="table-th">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map(d => (
              <tr key={d.deviation_id} className="hover:bg-gray-50">
                <td className="table-td font-mono text-xs text-pharma-teal">{d.deviation_id}</td>
                <td className="table-td max-w-xs">
                  <p className="text-sm font-medium truncate">{d.title}</p>
                  <p className="text-xs text-gray-400 truncate">{d.description}</p>
                </td>
                <td className="table-td"><StatusBadge value={d.severity} /></td>
                <td className="table-td"><StatusBadge value={d.status} /></td>
                <td className="table-td">
                  {d.risk_score != null
                    ? <span className={`text-sm font-bold ${
                        d.risk_score >= 8 ? 'text-red-600' : d.risk_score >= 5 ? 'text-orange-500' : 'text-green-700'
                      }`}>{d.risk_score}/10</span>
                    : '—'
                  }
                </td>
                <td className="table-td text-xs">{d.capa_reference ?? '—'}</td>
                <td className="table-td text-xs">{d.reported_by}</td>
                <td className="table-td">
                  {d.status !== 'Resolved' && (
                    <button
                      className="text-xs text-pharma-teal hover:underline font-medium"
                      onClick={() => setResolving(d)}
                    >
                      Resolve
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* New Deviation modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg">
            <h2 className="text-lg font-bold mb-4">New Deviation</h2>
            <div className="space-y-3">
              {[
                { key: 'title', label: 'Title *', ph: 'Brief description of non-conformance' },
                { key: 'reported_by', label: 'Reported By *', ph: 'e.g. A. Reyes' },
                { key: 'phase_id', label: 'Phase ID', ph: 'e.g. IQ-001' },
                { key: 'requirement_id', label: 'Requirement ID', ph: 'e.g. URS-001' },
              ].map(({ key, label, ph }) => (
                <div key={key}>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">{label}</label>
                  <input
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pharma-teal"
                    placeholder={ph}
                    value={form[key]}
                    onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                  />
                </div>
              ))}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Description</label>
                <textarea
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pharma-teal"
                  rows={3}
                  placeholder="Detailed description…"
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Severity *</label>
                <div className="flex gap-2">
                  {SEVERITIES.map(s => (
                    <button key={s}
                      onClick={() => setForm(f => ({ ...f, severity: s }))}
                      className={`px-3 py-1.5 rounded-lg text-sm font-semibold border transition-colors ${
                        form.severity === s ? 'bg-pharma-blue text-white border-pharma-blue' : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >{s}</button>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-5">
              <button
                className="btn-primary flex-1"
                disabled={!form.title || !form.reported_by || createMut.isPending}
                onClick={() => createMut.mutate(form)}
              >
                {createMut.isPending ? 'Creating…' : 'Create Deviation'}
              </button>
              <button className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Resolve modal */}
      {resolving && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
            <h2 className="text-lg font-bold mb-1">Resolve Deviation</h2>
            <p className="text-sm text-gray-500 mb-4 font-mono">{resolving.deviation_id} · {resolving.title}</p>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">CAPA Reference *</label>
              <input
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pharma-teal"
                placeholder="e.g. CAPA-2026-007"
                value={capaRef}
                onChange={e => setCapaRef(e.target.value)}
              />
            </div>
            <div className="flex gap-3 mt-5">
              <button
                className="btn-primary flex-1"
                disabled={!capaRef || resolveMut.isPending}
                onClick={() => resolveMut.mutate({ id: resolving.deviation_id, capa: capaRef })}
              >
                {resolveMut.isPending ? 'Resolving…' : 'Mark Resolved'}
              </button>
              <button className="btn-secondary" onClick={() => setResolving(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
