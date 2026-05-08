/**
 * Blocked-sources list editor.
 * Phase 1: add input field + remove buttons; persist via background/storage.setPreferences.
 */

interface Props {
  value: string[]
  onChange: (next: string[]) => void
}

export function Overrides({ value }: Props) {
  // onChange will be wired up Phase 1 once add/remove UI exists.
  return (
    <div>
      <div style={{ fontSize: 12, marginBottom: 4, color: '#374151' }}>
        Blocked sources ({value.length})
      </div>
      <div style={{ fontSize: 11, color: '#6b7280' }}>
        {value.length === 0 ? 'None' : value.join(', ')}
      </div>
      {/* TODO (Phase 1): add input + remove buttons; call onChange */}
    </div>
  )
}
