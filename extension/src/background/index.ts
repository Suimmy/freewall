// Service worker entry — wires all background subsystems on boot.
// MV3 service workers are event-driven and not persistent; long-lived state lives in
// chrome.storage (via background/storage.ts), never module scope.

import { startApiClient } from './api-client'
import { initSession } from './storage'

console.log('[Freewall background] service worker booted')

chrome.runtime.onInstalled.addListener((details) => {
  console.log('[Freewall background] onInstalled', details.reason)
})

// Fire-and-forget: ensure session_id exists, register message handlers.
// Both are idempotent — safe across service worker wake-ups.
void initSession()
startApiClient()
