import { useQuery } from '@tanstack/react-query'
import { fetchSummary } from '../api/client'
import StatCard from '../components/StatCard'
import { PieChart, Pie, Cell, Legend, ResponsiveContainer, Tooltip } from 'recharts'

const PIE_COLORS = ['#2E7D32', '#DC2626', '#F59E0B']

export default function Dashboard() {
  const { data, isLoading } = useQuery({ queryKey: ['summary'], queryFn: fetchSummary })

  if (isLoading) return <div className="text-gray-400 text-sm">Loading dashboard…</div>

  const executions = data?.executions ?? {}
  const execData = [
    { name: 'PASS', value: executions.passed ?? 0 },
    { name: 'FAIL', value: executions.failed ?? 0 },
    { name: 'BLOCKED', value: executions.blocked ?? 0 },
  ]

  const passRate = executions.total
    ? Math.round(((executions.passed ?? 0) / executions.total) * 100)
    : 0

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Validation Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">GxP · Computer System Validation · ALCOA+</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Requirements" value={data?.requirements ?? 0} />
        <StatCard label="Test Cases" value={data?.test_cases ?? 0} />
        <StatCard label="Execution Coverage" value={`${data?.test_coverage_pct ?? 0}%`} />
        <StatCard
          label="Pass Rate"
          value={`${passRate}%`}
          sub={`${executions.passed ?? 0} / ${executions.total ?? 0} executed`}
          color={passRate >= 80 ? 'text-green-700' : 'text-red-600'}
        />
      </div>

      <div className="card max-w-2xl">
        <h2 className="text-sm font-semibold text-gray-600 mb-4">Execution Results</h2>
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie data={execData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={85} label>
              {execData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
            </Pie>
            <Legend />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {(data?.open_deviations ?? 0) > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 flex items-center gap-3">
          <span className="text-orange-500 text-xl">⚠️</span>
          <div>
            <p className="font-semibold text-orange-800 text-sm">{data.open_deviations} Open Deviation{data.open_deviations > 1 ? 's' : ''}</p>
            <p className="text-orange-600 text-xs">Requires CAPA action before phase closure</p>
          </div>
        </div>
      )}
    </div>
  )
}
