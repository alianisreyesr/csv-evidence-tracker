import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchTestCases, fetchExecutions, fetchPhases, createExecution } from '../api/client'
import StatusBadge from '../components/StatusBadge'

const RESULTS = ['PASS', 'FAIL', 'BLOCKED']

export default function TestQueue() {
  const qc = useQueryClient()
  const [filter, setFilter] = useState('')
  const [executing, setExecuting] = useState(null)
  const [form, setForm] = useState({ result: 'PASS', executed_by: '', actual_result: '', evidence_ref: '', notes: '' })

  const { data: tests = [] } = useQuery({ queryKey: ['test-cases'], queryFn: fetchTestCases })
  const { data: execs = [] } = useQuery({ queryKey: ['executions'], queryFn: fetchExecutions })
  const { data: phases = [] } = useQuery({ queryKey: ['phases'], queryFn: fetchPhases })

  const lastResult = (tcId) => {
    const hits = execs.filter(e => e.test_case_id === tcId)
    return hits.length ? [...hits].sort((a, b) => b.id - a.id)[0].result : null
  }

  const mutation = useMutation({
    mutationFn: createExecution,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['executions'] })
      qc.invalidateQueries({ queryKey: ['summary'] })
      qc.invalidateQueries({ queryKey: ['rtm'] })
      setExecuting(null)
      setForm({ result: 'PASS', executed_by: '', actual_result: '', evidence_ref: '', notes: '' })
    }
  })

  const filtered = tests.filter(t => {
    const haystack = [t.code, t.title, t.requirement_code, t.requirement_title].filter(Boolean).join(' ').toLowerCase()
    return !filter || haystack.includes(filter.toLowerCase())
  })

  const phaseIdFor = (testCase) => phases.find(p => p.name === testCase.requirement_phase)?.id

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Test Execution Queue</h1>
          <p className="text-sm text-gray-500 mt-1">Record test results · ALCOA+ traceability</p>
        </div>
        <input className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-56" placeholder="Search test cases…" value={filter} onChange={e => setFilter(e.target.value)} />
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="table-th">Test Case</th>
              <th className="table-th">Title</th>
              <th className="table-th">Type</th>
              <th className="table-th">Phase</th>
              <th className="table-th">Last Result</th>
              <th className="table-th">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map(tc => (
              <tr key={tc.id} className="hover:bg-gray-50">
                <td className="table-td">
                  <p className="font-mono text-xs text-pharma-teal">{tc.code}</p>
                  <p className="text-xs text-gray-400">{tc.requirement_code}</p>
                </td>
                <td className="table-td max-w-xs">
                  <p className="text-sm font-medium truncate">{tc.title}</p>
                  <p className="text-xs text-gray-400 truncate">{tc.description}</p>
                </td>
                <td className="table-td text-xs text-gray-500">{tc.test_type ?? '—'}</td>
                <td className="table-td text-xs">{tc.requirement_phase ?? '—'}</td>
                <td className="table-td">{lastResult(tc.id) ? <StatusBadge value={lastResult(tc.id)} /> : <span className="text-xs text-gray-400">Not run</span>}</td>
                <td className="table-td">
                  <button className="btn-primary text-xs" disabled={!phaseIdFor(tc)} onClick={() => setExecuting(tc)}>Execute</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {executing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
            <h2 className="text-lg font-bold mb-1">Record Execution</h2>
            <p className="text-sm text-gray-500 mb-4 font-mono">{executing.code} · {executing.title}</p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Result *</label>
                <div className="flex gap-2">
                  {RESULTS.map(r => (
                    <button key={r} onClick={() => setForm(f => ({ ...f, result: r }))} className={`px-4 py-2 rounded-lg text-sm font-semibold border ${form.result === r ? 'bg-pharma-blue text-white border-pharma-blue' : 'border-gray-300 text-gray-700'}`}>
                      {r}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Executed By *</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.executed_by} onChange={e => setForm(f => ({ ...f, executed_by: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Actual Result</label>
                <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" rows={2} value={form.actual_result} onChange={e => setForm(f => ({ ...f, actual_result: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Evidence Reference</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={form.evidence_ref} onChange={e => setForm(f => ({ ...f, evidence_ref: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Notes</label>
                <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" rows={2} value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button className="btn-primary flex-1" disabled={!form.executed_by || mutation.isPending} onClick={() => mutation.mutate({ test_case_id: executing.id, phase_id: phaseIdFor(executing), ...form })}>
                {mutation.isPending ? 'Saving…' : 'Record Result'}
              </button>
              <button className="btn-secondary" onClick={() => setExecuting(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
