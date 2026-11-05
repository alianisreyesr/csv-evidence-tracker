import { describe, it, expect, beforeEach } from 'vitest'
import api from '../api/client'

// Run the request interceptors without touching the network.
async function runInterceptors(config) {
  let cfg = config
  for (const h of api.interceptors.request.handlers) {
    if (h) cfg = await h.fulfilled(cfg)
  }
  return cfg
}

describe('api client', () => {
  beforeEach(() => sessionStorage.clear())

  it('uses the /api base URL', () => {
    expect(api.defaults.baseURL).toBe('/api')
  })

  it('attaches the bearer token from sessionStorage', async () => {
    sessionStorage.setItem('csv_token', 'abc.def.ghi')
    const cfg = await runInterceptors({ headers: {} })
    expect(cfg.headers.Authorization).toBe('Bearer abc.def.ghi')
  })

  it('sends no Authorization header when logged out', async () => {
    const cfg = await runInterceptors({ headers: {} })
    expect(cfg.headers.Authorization).toBeUndefined()
  })
})
