// Content script entry — boots all subsystems in dependency order.
// injector first (Shadow DOM root must exist before UI mount), then observer + user-state.

import { injectShadowRoot } from './injector'
import { startObserver } from './observer'
import { startUserState } from './user-state'

console.log('[Freewall content] injected on', window.location.href)

injectShadowRoot()
startObserver()
startUserState()

// TODO (Phase 1): mount React App into Shadow DOM root, e.g.
//   const shadow = injectShadowRoot()
//   mountSidebar(shadow)
// TODO (Phase 1): listen for BackgroundToContentMessage events (reasoning_event, counter_response)
//                 via messaging.on(); dispatch into UI state store.
