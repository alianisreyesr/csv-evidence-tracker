/**
 * RoleBadge.jsx
 * -------------
 * Visual pill component that displays the current user's role.
 * Color-coded to match the role hierarchy:
 *   Analyst      → blue
 *   QA Reviewer  → purple
 *   Admin        → amber
 */
export default function RoleBadge({ role }) {
  const styles = {
    'Analyst':     'bg-blue-100   text-blue-800   border-blue-200',
    'QA Reviewer': 'bg-purple-100 text-purple-800 border-purple-200',
    'Admin':       'bg-amber-100  text-amber-800  border-amber-200',
  }
  const cls = styles[role] || 'bg-gray-100 text-gray-700 border-gray-200'

  return (
    <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full border ${cls}`}>
      {role}
    </span>
  )
}
