import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

const actorHeaders = (actor) => ({ headers: { 'X-Actor': actor || 'portfolio.user' } })

export const fetchSummary       = () => api.get('/summary').then(r => r.data)
export const fetchPhases        = () => api.get('/phases').then(r => r.data)
export const fetchRequirements  = (params) => api.get('/requirements', { params }).then(r => r.data)
export const fetchTestCases     = (params) => api.get('/test-cases', { params }).then(r => r.data)
export const fetchExecutions    = (params) => api.get('/executions', { params }).then(r => r.data)
export const fetchDeviations    = (params) => api.get('/deviations', { params }).then(r => r.data)
export const fetchAuditLog      = (params) => api.get('/audit-log', { params }).then(r => r.data)
export const fetchRTM           = () => api.get('/rtm').then(r => r.data)

export const createDeviation = (body) => {
  const { actor, ...payload } = body
  return api.post('/deviations', payload, actorHeaders(actor)).then(r => r.data)
}

export const resolveDeviation = (id, body) => {
  const actor = body.actor || 'portfolio.user'
  return api.post(`/deviations/${id}/resolve`, body, actorHeaders(actor)).then(r => r.data)
}

export const createExecution = (body) => {
  const actor = body.executed_by || 'portfolio.user'
  return api.post('/executions', body, actorHeaders(actor)).then(r => r.data)
}

export default api
