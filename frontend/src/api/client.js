import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

// Every protected endpoint requires `Authorization: Bearer <jwt>` (see
// app/dependencies.py). Attach it here from the same sessionStorage key
// AuthContext writes to, so every call through this client is authenticated
// — previously this file never sent the token at all, so every "protected"
// screen 401'd against the real API.
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('csv_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const fetchSummary       = () => api.get('/summary').then(r => r.data)
export const fetchPhases        = () => api.get('/phases').then(r => r.data)
export const fetchRequirements  = (params) => api.get('/requirements', { params }).then(r => r.data)
export const fetchTestCases     = (params) => api.get('/test-cases', { params }).then(r => r.data)
export const fetchExecutions    = (params) => api.get('/executions', { params }).then(r => r.data)
export const fetchDeviations    = (params) => api.get('/deviations', { params }).then(r => r.data)
export const fetchAuditLog      = (params) => api.get('/audit-log', { params }).then(r => r.data)
export const fetchRTM           = () => api.get('/rtm').then(r => r.data)

// The audit-log actor is now derived server-side from the verified JWT, not
// a client-supplied X-Actor header (see app/audit_middleware.py and
// app/routers/executions.py), so these calls no longer send one.
export const createDeviation = (body) => api.post('/deviations', body).then(r => r.data)

export const resolveDeviation = (id, body) => api.patch(`/deviations/${id}/resolve`, body).then(r => r.data)

export const createExecution = (body) => api.post('/executions', body).then(r => r.data)

export default api
