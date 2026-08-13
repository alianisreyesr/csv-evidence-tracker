import { useQuery } from '@tanstack/react-query'
import { fetchSummary } from '../api/client'
import StatCard from '../components/StatCard'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'

const PIE_COLORS = ['#2E7D32', '#DC2626', '#F59E0B', '#6B7280']

export default function Dashboard() {
  const { data, isLoading } = useQuery({ queryKey: ['summary'], queryFn: fetchSummary })

  if (isLoading) return <div className="text-gray-400 text-sm">Loading dashboard…</div>

  const execData = [
    { name: 'PASS',    value: data?.executions?.pass    ?? 0 },
    { name: 'FAIL',    value: data?.executions?.fail    ?? 0 },
    { name: 'BLOCKED', value: data?.executions?.blocked ?? 0 },
    { name: 'PENDING', value: data?.executions?.pending ?? 0 },
  ]

  const phaseData = (data?.phases ?? []).map(p => ({
    name: p.phase_name,
    requirements: p.total_requirements ?? 0,
    test_cases: p.total_test_cases ?? 0,
  }))

  const passRate = data?.executions?.total
    ? Math.round((data.executions.pass / data.executions.total) * 100)
    : 0

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Validation Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">GxP · Computer System Validation · ALCOA+</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Phases" value={data?.total_phases ?? 0} />
        <StatCard label="Requirements" value={data?.total_requirements ?? 0} />
        <StatCard label="Test Cases" value={data?.total_test_cases ?? 0} />
        <StatCard
          label="Pass Rate"
          value={`${passRate}%`}
          sub={`${data?.executions?.pass ?? 0} / ${data?.executions?.total ?? 0} executed`}
          color={passRate >= 80 ? 'text-green-700' : 'text-red-600'}
        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Execution pie */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-600 mb-4">Execution Results</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={execData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                {execData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
              </Pie>
              <Legend />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Phase bar */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-600 mb-4">Requirements & Tests by Phase</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={phaseData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="requirements" fill="#003366" radius={[4,4,0,0]} />
              <Bar dataKey="test_cases"   fill="#007A7A" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Open deviations warning */}
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
