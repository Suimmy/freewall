import { createRoot } from 'react-dom/client'
import { useEffect, useState } from 'react'
import { storage } from '@/lib/runtime'
import type { Preferences } from '@/background/storage'
import { SensitivityToggle } from './SensitivityToggle'
import { Overrides } from './Overrides'

const PREFS_KEY = 'preferences'
const DEFAULT_PREFS: Preferences = { sensitivity: 'medium', blocked_sources: [] }

function PopupApp() {
  const [prefs, setPrefs] = useState<Preferences>(DEFAULT_PREFS)

  useEffect(() => {
    void storage.get<Preferences>(PREFS_KEY).then((p) => {
      if (p) setPrefs(p)
    })
  }, [])

  const update = (patch: Partial<Preferences>): void => {
    const next: Preferences = { ...prefs, ...patch }
    setPrefs(next)
    void storage.set(PREFS_KEY, next)
  }

  return (
    <div style={{ padding: 16, fontFamily: 'system-ui, sans-serif' }}>
      <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: '#111827' }}>
        Freewall
      </h2>
      <SensitivityToggle
        value={prefs.sensitivity}
        onChange={(s) => update({ sensitivity: s })}
      />
      <Overrides
        value={prefs.blocked_sources}
        onChange={(b) => update({ blocked_sources: b })}
      />
    </div>
  )
}

const root = document.getElementById('popup-root')
if (root) {
  createRoot(root).render(<PopupApp />)
}
