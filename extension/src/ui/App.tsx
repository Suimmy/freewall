import { Sidebar } from './components/Sidebar'

/**
 * Sidebar root — composes all overlay components.
 * Phase 1: state-driven conditional rendering from a zustand store fed by SSE events.
 *
 * Demo coverage components (per freewall_demo.md): Sidebar, Annotation, FactCheckCard,
 * ScoreBadge, DecisionPause, AskWhyModal, DailyMirror.
 */
export function App() {
  return (
    <div className="freewall-app">
      <Sidebar />
      {/* TODO (Phase 1): conditional render driven by store state:
            - Annotation       (post visible + has findings)
            - FactCheckCard    (Fact-Check Agent verdict)
            - DecisionPause    (user clicked Buy + score < 30)
            - AskWhyModal      ("Why?" clicked)
            - DailyMirror      (session end / popup view)
      */}
    </div>
  )
}
