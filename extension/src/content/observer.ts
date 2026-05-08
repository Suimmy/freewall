/**
 * Viewport-triggered detection. IntersectionObserver fires when a content unit enters
 * the viewport; MutationObserver picks up lazy-loaded units (infinite scroll).
 *
 * Why viewport-gated: posts the user never sees aren't worth analysing — direct savings
 * on backend cost (CLAUDE.md decision #17, $80/day cap).
 */

import { messaging } from '@/lib/runtime'
import { debounce } from '@/lib/debounce'
import { pickPlugin, type SitePlugin } from './scraper'

// WeakSet — automatically cleans up entries when DOM nodes are garbage-collected
// (so we don't leak as users scroll through long feeds).
const seen = new WeakSet<HTMLElement>()

let io: IntersectionObserver | null = null
let mo: MutationObserver | null = null

export function startObserver(): void {
  const plugin = pickPlugin()
  if (!plugin) {
    console.warn('[content.observer] no scraper plugin matches', window.location.href)
    return
  }

  io = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const el = entry.target as HTMLElement
          if (!seen.has(el)) {
            seen.add(el)
            void handleVisible(el, plugin)
          }
        }
      }
    },
    // 0.5 = element half-visible. Lower = catches earlier but more false starts on fast scroll.
    { threshold: 0.5 },
  )

  // Initial scan
  for (const el of plugin.findContentUnits()) io.observe(el)

  // Re-scan on DOM mutations — debounced to absorb burst changes from React/Vue re-renders.
  mo = new MutationObserver(
    debounce(() => {
      if (!io) return
      for (const el of plugin.findContentUnits()) {
        if (!seen.has(el)) io.observe(el)
      }
    }, 150),
  )
  mo.observe(document.body, { childList: true, subtree: true })
}

async function handleVisible(el: HTMLElement, plugin: SitePlugin): Promise<void> {
  const content = plugin.extract(el)
  // TODO (Phase 1): annotate el with data-freewall-id={content_id} so the UI layer
  //                 can attach annotations back to the originating post element.
  try {
    await messaging.send({ type: 'perceive', payload: content })
  } catch (err) {
    console.error('[content.observer] perceive send failed', err)
  }
}
