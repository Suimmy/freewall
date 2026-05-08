import { createRoot } from 'react-dom/client'
import { App } from './App'
import './styles/index.css'

// Vite dev entry — renders the sidebar standalone in a browser tab via index.html.
// Phase 1 will add a separate `mountSidebar(shadow: ShadowRoot)` export for the
// content-script Shadow DOM target.

const root = document.getElementById('root')
if (root) {
  createRoot(root).render(<App />)
}
