/**
 * Domain-level storage. Wraps lib/runtime.ts.storage (the chrome.* abstraction) with
 * typed helpers for sessions, preferences, and reasoning cache.
 *
 * If Phase 4 swaps RUNTIME_MODE to 'webapp', everything in this file keeps working
 * because we only touch the abstraction.
 */

import { storage } from '@/lib/runtime'

const SESSION_KEY = 'session_id'
const PREFS_KEY = 'preferences'
const REASONING_PREFIX = 'reasoning:'

// ─── Session ─────────────────────────────────────────────────────────────────────

/** Ensure a session_id exists. Idempotent — safe to call on every service-worker wake-up. */
export async function initSession(): Promise<string> {
  let id = await storage.get<string>(SESSION_KEY)
  if (!id) {
    id = crypto.randomUUID()
    await storage.set(SESSION_KEY, id)
  }
  return id
}

export async function getSessionId(): Promise<string> {
  return await initSession()
}

// ─── Reasoning cache ─────────────────────────────────────────────────────────────

/**
 * Cache reasoning data keyed by content_id.
 * TODO (Phase 1): merge incoming SSE events into a single ReasoningState object instead of
 *                 overwriting per event. Today this is sufficient to land the wiring.
 */
export async function cacheReasoning(content_id: string, event: unknown): Promise<void> {
  await storage.set(`${REASONING_PREFIX}${content_id}`, event)
}

export async function getReasoning(content_id: string): Promise<unknown> {
  return await storage.get(`${REASONING_PREFIX}${content_id}`)
}

// ─── Preferences ─────────────────────────────────────────────────────────────────

export interface Preferences {
  sensitivity: 'low' | 'medium' | 'high'
  blocked_sources: string[]
}

const DEFAULT_PREFS: Preferences = { sensitivity: 'medium', blocked_sources: [] }

export async function getPreferences(): Promise<Preferences> {
  return (await storage.get<Preferences>(PREFS_KEY)) ?? DEFAULT_PREFS
}

export async function setPreferences(prefs: Partial<Preferences>): Promise<void> {
  const current = await getPreferences()
  await storage.set(PREFS_KEY, { ...current, ...prefs })
}
