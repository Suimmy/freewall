/**
 * Agent activity panel — fixed top-right of the host page.
 * Phase 1: subscribe to SSE-driven store, animate agent_started → agent_finished, show score.
 */

const AGENTS = [
  'Content Classifier',
  'Coordinator',
  'Persuasion',
  'Fact-Check',
  'Provenance',
  'Counter-Perspective',
] as const

export function Sidebar() {
  return (
    <aside
      className="fixed top-4 right-4 w-80 max-h-[80vh] bg-freewall-panel
                 border border-freewall-border rounded-lg shadow-xl
                 pointer-events-auto overflow-y-auto font-sans"
    >
      <header className="px-4 py-3 border-b border-freewall-border">
        <h2 className="text-freewall-text font-semibold">Freewall</h2>
        <p className="text-xs text-freewall-muted mt-1">Cognitive immune system</p>
      </header>

      <ul className="p-3 space-y-2">
        {AGENTS.map((name) => (
          <li
            key={name}
            className="flex items-center justify-between text-sm text-freewall-text"
          >
            <span>{name}</span>
            {/* TODO (Phase 1): replace with animated status pill driven by SSE events */}
            <span className="text-freewall-muted text-xs">idle</span>
          </li>
        ))}
      </ul>
    </aside>
  )
}
