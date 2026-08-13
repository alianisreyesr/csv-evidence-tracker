import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import RTM from './pages/RTM'
import TestQueue from './pages/TestQueue'
import Deviations from './pages/Deviations'
import AuditLog from './pages/AuditLog'
import Phases from './pages/Phases'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/rtm" element={<RTM />} />
        <Route path="/test-queue" element={<TestQueue />} />
        <Route path="/deviations" element={<Deviations />} />
        <Route path="/audit" element={<AuditLog />} />
        <Route path="/phases" element={<Phases />} />
      </Routes>
    </Layout>
  )
}
