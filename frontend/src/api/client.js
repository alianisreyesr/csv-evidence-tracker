import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

export const fetchSummary       = () => api.get('/summary').then(r => r.data)
export const fetchPhases        = () => api.get('/phases').then(r => r.data)
export const fetchRequirements  = (params) => api.get('/requirements', { params }).then(r => r.data)
export const fetchTestCases     = (params) => api.get('/test-cases', { params }).then(r => r.data)
export const fetchExecutions    = (params) => api.get('/executions', { params }).then(r => r.data)
export const fetchDeviations    = (params) => api.get('/deviations', { params }).then(r => r.data)
export const fetchAuditLog      = (params) => api.get('/audit', { params }).then(r => r.data)
export const fetchRTM           = () => api.get('/rtm').then(r => r.data)

export const createDeviation = (body) => api.post('/deviations', body).then(r => r.data)
export const resolveDeviation = (id, body) => api.put(`/deviations/${id}/resolve`, body).then(r => r.data)
export const createExecution = (body) => api.post('/executions', body).then(r => r.data)

export default api
