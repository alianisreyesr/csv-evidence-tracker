import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchDeviations, createDeviation, resolveDeviation } from '../api/client'
import StatusBadge from '../components/StatusBadge'

const SEVERITIES = ['Critical', 'Major', 'Minor']

export default function Deviations() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [resolving, setResolving] = useState(null)
  const [resolution, setResolution] = useState({ capa_ref: '', resolution_notes: '', actor: '' })
  const [form, setForm] = useState({
    title: '', description: '', severity: 'Major', assigned_to: '', actor: ''
  })

  const { data = [], isLoading } = useQuery({ queryKey: ['deviations'], queryFn: fetchDeviations })

  const createMut = useMutation({
    mutationFn: createDeviation,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['deviations'] })
      qc.invalidateQueries({ queryKey: ['summary'] })
      setShowForm(false)
      setForm({ title: '', description: '', severity: 'Major', assigned_to: '', actor: '' })
    }
  })

  const resolveMut = useMutation({
    mutationFn: ({ id, body }) => resolveDeviation(id, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['deviations'] })
      qc.invalidateQueries({ queryKey: ['summary'] })
      setResolving(null)
      setResolution({ capa_ref: '', resolution_notes: '', actor: '' })
    }
  })

  if (isLoading) return <div className="text-gray-400 text-sm">Loading deviations…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Deviation Tracker</h1>
          <p className="text-sm text-gray-500 mt-1">Non-conformances · CAPA references · Explainable risk scoring</p>
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
              <th className="table-th">Risk</th>
              <th className="table-th">CAPA Ref</th>
              <th className="table-th">Owner</th>
              <th className="table-th">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map(d => (
              <tr key={d.id} className="hover:bg-gray-50">
                <td className="table-td font-mono text-xs text-pharma-teal">{d.id}</td>
                <td className="table-td max-w-xs">
                  <p className="text-sm font-medium truncate">{d.title}</p>
                  <p className="text-xs text-gray-400 truncate">{d.description}</p>
                </td>
                <td className="table-td"><StatusBadge value={d.severity} /></td>
                <td className="table-td"><StatusBadge value={d.status} /></td>
                <td className="table-td">
                  <div className="text-sm font-bold">{d.risk_score ?? '—'}</div>
                  <div className="text-xs text-gray-500">{d.risk_classification ?? '—'}</div>
                </td>
                <td className="table-td text-xs">{d.capa_ref ?? '—'}</td>
                <td className="table-td text-xs">{d.assigned_to ?? 'Unassigned'}</td>
                <td className="table-td">
                  {d.status !== 'Resolved' && d.status !== 'Accepted with Risk' && (
                    <button className="text-xs text-pharma-teal hover:underline font-medium" onClick={() => setResolving(d)}>
                      Resolve
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg">
            <h2 className="text-lg font-bold mb-4">New Deviation</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Title *</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Description</label>
                <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" rows={3} value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Assigned To</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. A. Reyes" value={form.assigned_to} onChange={e => setForm(f => ({ ...f, assigned_to: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Actor *</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Audit identity" value={form.actor} onChange={e => setForm(f => ({ ...f, actor: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Severity *</label>
                <div className="flex gap-2">
                  {SEVERITIES.map(s => (
                    <button key={s} onClick={() => setForm(f => ({ ...f, severity: s }))} className={`px-3 py-1.5 rounded-lg text-sm font-semibold border ${form.severity === s ? 'bg-pharma-blue text-white border-pharma-blue' : 'border-gray-300 text-gray-700'}`}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-5">
              <button className="btn-primary flex-1" disabled={!form.title || !form.actor || createMut.isPending} onClick={() => createMut.mutate(form)}>
                {createMut.isPending ? 'Creating…' : 'Create Deviation'}
              </button>
              <button className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {resolving && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
            <h2 className="text-lg font-bold mb-1">Resolve Deviation</h2>
            <p className="text-sm text-gray-500 mb-4 font-mono">#{resolving.id} · {resolving.title}</p>
            <div className="space-y-3">
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="CAPA reference" value={resolution.capa_ref} onChange={e => setResolution(r => ({ ...r, capa_ref: e.target.value }))} />
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Actor *" value={resolution.actor} onChange={e => setResolution(r => ({ ...r, actor: e.target.value }))} />
              <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" rows={3} placeholder="Resolution notes (minimum 10 characters) *" value={resolution.resolution_notes} onChange={e => setResolution(r => ({ ...r, resolution_notes: e.target.value }))} />
            </div>
            <div className="flex gap-3 mt-5">
              <button className="btn-primary flex-1" disabled={!resolution.actor || resolution.resolution_notes.length < 10 || resolveMut.isPending} onClick={() => resolveMut.mutate({ id: resolving.id, body: { ...resolution, status: 'Resolved' } })}>
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
