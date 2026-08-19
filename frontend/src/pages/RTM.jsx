import { useQuery } from '@tanstack/react-query'
import { fetchRTM } from '../api/client'
import StatusBadge from '../components/StatusBadge'

export default function RTM() {
  const { data = [], isLoading } = useQuery({ queryKey: ['rtm'], queryFn: fetchRTM })

  if (isLoading) return <div className="text-gray-400 text-sm">Building traceability matrix…</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Requirements Traceability Matrix</h1>
        <p className="text-sm text-gray-500 mt-1">URS → Test Case → Execution Status · ALCOA+</p>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="table-th">Requirement</th>
              <th className="table-th">Description</th>
              <th className="table-th">Priority</th>
              <th className="table-th">Phase</th>
              <th className="table-th">Test Cases</th>
              <th className="table-th">Coverage</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map(row => (
              <tr key={row.id} className="hover:bg-gray-50">
                <td className="table-td">
                  <p className="font-mono text-xs text-pharma-teal">{row.code}</p>
                  <p className="text-xs text-gray-500 mt-1">{row.title}</p>
                </td>
                <td className="table-td max-w-xs">
                  <p className="text-sm text-gray-800">{row.description}</p>
                  <p className="text-xs text-gray-400 mt-1">{row.category}</p>
                </td>
                <td className="table-td"><StatusBadge value={row.priority} /></td>
                <td className="table-td text-xs">{row.phase}</td>
                <td className="table-td">
                  {(row.test_cases ?? []).length === 0
                    ? <span className="text-xs text-gray-400">No tests</span>
                    : (
                      <div className="space-y-1">
                        {row.test_cases.slice(0, 3).map(tc => (
                          <div key={tc.id} className="flex items-center gap-2">
                            <span className="text-xs font-mono text-gray-500">{tc.code}</span>
                            <StatusBadge value={tc.latest_execution?.result ?? 'PENDING'} />
                          </div>
                        ))}
                        {row.test_cases.length > 3 && (
                          <p className="text-xs text-gray-400">+{row.test_cases.length - 3} more</p>
                        )}
                      </div>
                    )
                  }
                </td>
                <td className="table-td">
                  <span className={`text-xs font-semibold ${row.coverage_pct === 100 ? 'text-green-700' : 'text-orange-600'}`}>
                    {row.coverage_pct ?? 0}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
