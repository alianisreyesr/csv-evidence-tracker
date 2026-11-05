import { describe, it, expect } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import StatusBadge from '../components/StatusBadge'
import RoleBadge from '../components/RoleBadge'

describe('StatusBadge', () => {
  it('maps known values to their badge class', () => {
    expect(renderToStaticMarkup(<StatusBadge value="PASS" />)).toContain('badge-pass')
    expect(renderToStaticMarkup(<StatusBadge value="Resolved" />)).toContain('badge-closed')
  })

  it('falls back to the pending style for unknown values', () => {
    const html = renderToStaticMarkup(<StatusBadge value="WEIRD" />)
    expect(html).toContain('badge-pending')
    expect(html).toContain('WEIRD')
  })
})

describe('RoleBadge', () => {
  it('renders role-specific colours', () => {
    expect(renderToStaticMarkup(<RoleBadge role="Admin" />)).toContain('amber')
    expect(renderToStaticMarkup(<RoleBadge role="QA Reviewer" />)).toContain('purple')
  })

  it('uses a neutral style for unknown roles', () => {
    expect(renderToStaticMarkup(<RoleBadge role="Guest" />)).toContain('gray')
  })
})
