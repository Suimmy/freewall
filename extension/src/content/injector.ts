/**
 * Inject a Shadow DOM root for the Freewall sidebar UI.
 *
 * Why Shadow DOM: isolates our CSS from the host page (and vice-versa) so neither side
 * can break the other. Required for a robust overlay across arbitrary sites.
 *
 * If Phase 4 swaps to webapp mode (no extension), replace this with a function that mounts
 * into a `<div id="freewall-portal">` already present in the host site — single-file change.
 */

const HOST_ID = 'freewall-root'

export function injectShadowRoot(): ShadowRoot {
  const existing = document.getElementById(HOST_ID)
  if (existing && existing.shadowRoot) return existing.shadowRoot

  const host = document.createElement('div')
  host.id = HOST_ID
  // `all: initial` neutralises inherited styles from the host page.
  // `pointer-events: none` keeps clicks falling through where our UI isn't drawn —
  // children re-enable pointer events as needed.
  host.style.cssText =
    'all: initial; position: fixed; top: 0; right: 0; bottom: 0; ' +
    'width: 0; height: 0; z-index: 2147483647; pointer-events: none;'

  // Attach to documentElement (not body) so SPAs that swap <body> don't drop us.
  document.documentElement.appendChild(host)

  const shadow = host.attachShadow({ mode: 'open' })

  // TODO (Phase 1): inject compiled Tailwind CSS into the shadow root, e.g.
  //   import tailwindCss from '@/ui/styles/index.css?inline'
  //   const style = document.createElement('style')
  //   style.textContent = tailwindCss
  //   shadow.appendChild(style)
  // TODO (Phase 1): observe documentElement for shadow-root removal (some sites nuke unknown
  //                 children) and re-inject if it disappears.

  return shadow
}
