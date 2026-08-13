import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchTestCases, fetchExecutions, createExecution } from '../api/client'
import StatusBadge from '../components/StatusBadge'

const RESULTS = ['PASS', 'FAIL', 'BLOCKED']

export default function TestQueue() {
  const qc = useQueryClient()
  const [filter, setFilter] = useState('')
  const [executing, setExecuting] = useState(null)
  const [form, setForm] = useState({ result: 'PASS', executed_by: '', notes: '' })

  const { data: tests = [] } = useQuery({ queryKey: ['test-cases'], queryFn: fetchTestCases })
  const { data: execs = [] } = useQuery({ queryKey: ['executions'], queryFn: fetchExecutions })

  const lastResult = (tcId) => {
    const hits = execs.filter(e => e.test_case_id === tcId)
    return hits.length ? hits.sort((a,b) => b.execution_id - a.execution_id)[0].result : null
  }

  const mutation = useMutation({
    mutationFn: createExecution,
    onSuccess: () => {
      qc.invalidateQueries(['executions'])
      qc.invalidateQueries(['summary'])
      setExecuting(null)
      setForm({ result: 'PASS', executed_by: '', notes: '' })
    }
  })

  const filtered = tests.filter(t =>
    !filter ||
    t.test_case_id.toLowerCase().includes(filter.toLowerCase()) ||
    t.title.toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Test Execution Queue</h1>
          <p className="text-sm text-gray-500 mt-1">Record test results · ALCOA+ traceability</p>
        </div>
        <input
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-56 focus:outline-none focus:ring-2 focus:ring-pharma-teal"
          placeholder="Search test cases…"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="table-th">Test Case ID</th>
              <th className="table-th">Title</th>
              <th className="table-th">Type</th>
              <th className="table-th">Phase</th>
              <th className="table-th">Last Result</th>
              <th className="table-th">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map(tc => (
              <tr key={tc.test_case_id} className="hover:bg-gray-50">
                <td className="table-td font-mono text-xs text-pharma-teal">{tc.test_case_id}</td>
                <td className="table-td max-w-xs">
                  <p className="text-sm font-medium truncate">{tc.title}</p>
                  <p className="text-xs text-gray-400 truncate">{tc.description}</p>
                </td>
                <td className="table-td text-xs text-gray-500">{tc.test_type}</td>
                <td className="table-td text-xs">{tc.phase_id}</td>
                <td className="table-td">
                  {lastResult(tc.test_case_id)
                    ? <StatusBadge value={lastResult(tc.test_case_id)} />
                    : <span className="text-xs text-gray-400">Not run</span>
                  }
                </td>
                <td className="table-td">
                  <button
                    className="btn-primary text-xs"
                    onClick={() => setExecuting(tc)}
                  >
                    Execute
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Execution modal */}
      {executing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
            <h2 className="text-lg font-bold mb-1">Record Execution</h2>
            <p className="text-sm text-gray-500 mb-4 font-mono">{executing.test_case_id} · {executing.title}</p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Result *</label>
                <div className="flex gap-2">
                  {RESULTS.map(r => (
                    <button
                      key={r}
                      onClick={() => setForm(f => ({ ...f, result: r }))}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold border transition-colors ${
                        form.result === r ? 'bg-pharma-blue text-white border-pharma-blue' : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Executed By *</label>
                <input
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pharma-teal"
                  placeholder="e.g. A. Reyes"
                  value={form.executed_by}
                  onChange={e => setForm(f => ({ ...f, executed_by: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Notes</label>
                <textarea
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pharma-teal"
                  rows={3}
                  placeholder="Observations, evidence reference…"
                  value={form.notes}
                  onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                className="btn-primary flex-1"
                disabled={!form.executed_by || mutation.isPending}
                onClick={() => mutation.mutate({
                  test_case_id: executing.test_case_id,
                  ...form
                })}
              >
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
