/**
 * Sensitivity tier picker — low / medium / high.
 * Maps to Preferences.sensitivity used by background/storage and Coordinator dispatch
 * thresholds (Phase 1).
 *
 * Inline styles intentionally — Tailwind config sets `important: ':host'` which scopes
 * utility classes to Shadow DOM only. Phase 4 may consolidate popup styles via a
 * separate sheet.
 */

type Sensitivity = 'low' | 'medium' | 'high'

interface Props {
  value: Sensitivity
  onChange: (next: Sensitivity) => void
}

const OPTIONS: Sensitivity[] = ['low', 'medium', 'high']

export function SensitivityToggle({ value, onChange }: Props) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 12, marginBottom: 4, color: '#374151' }}>Sensitivity</div>
      <div style={{ display: 'flex', gap: 4 }}>
        {OPTIONS.map((opt) => (
          <button
            key={opt}
            type="button"
            onClick={() => onChange(opt)}
            style={{
              padding: '4px 10px',
              fontSize: 12,
              background: value === opt ? '#2563eb' : '#e5e7eb',
              color: value === opt ? 'white' : '#374151',
              border: 'none',
              borderRadius: 4,
              cursor: 'pointer',
              textTransform: 'capitalize',
            }}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}
