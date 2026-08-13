import clsx from 'clsx'

const MAP = {
  PASS: 'badge-pass', FAIL: 'badge-fail', BLOCKED: 'badge-blocked',
  PENDING: 'badge-pending', pending: 'badge-pending',
  OPEN: 'badge-open', open: 'badge-open',
  CLOSED: 'badge-closed', closed: 'badge-closed', Resolved: 'badge-closed',
  CRITICAL: 'badge-critical', Critical: 'badge-critical',
  HIGH: 'badge-high', High: 'badge-high',
  MEDIUM: 'badge-medium', Medium: 'badge-medium',
  LOW: 'badge-low', Low: 'badge-low',
  Completed: 'badge-pass', 'In Progress': 'badge-blocked', Planned: 'badge-pending',
}

export default function StatusBadge({ value }) {
  const cls = MAP[value] ?? 'badge-pending'
  return <span className={cls}>{value}</span>
}
