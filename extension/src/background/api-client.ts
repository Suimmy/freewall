/**
 * Background message hub. Translates content/popup messages into backend calls,
 * relays SSE events back to content scripts. Single source of session state.
 */

import { messaging } from '@/lib/runtime'
import { api, ApiError } from '@/lib/api'
import type { ContentToBackgroundMessage } from '@/lib/events'
import { cacheReasoning } from './storage'

export function startApiClient(): void {
  messaging.on<ContentToBackgroundMessage, unknown>(async (msg) => {
    try {
      switch (msg.type) {
        case 'perceive': {
          const result = await api.perceive(msg.payload)
          // Spawn SSE listener in background — fire-and-forget so the response returns immediately.
          // TODO (Phase 1): use real session_id (not content_id) per shared/schemas reasoning stream contract.
          void listenToReasoning(result.content_id)
          return result
        }
        case 'request_counter':
          return await api.requestCounter(msg.content_id)
        case 'ask_why':
          return await api.askWhy(msg.content_id)
        case 'get_daily_mirror':
          return await api.getDailyMirror()
        default: {
          // Exhaustiveness check — TS narrows to never if all cases handled.
          const _exhaustive: never = msg
          return { error: { code: 'unknown_message_type', message: String(_exhaustive) } }
        }
      }
    } catch (err) {
      if (err instanceof ApiError) {
        return { error: { code: err.code, message: err.message, status: err.status } }
      }
      console.error('[api-client] unexpected error', err)
      return { error: { code: 'internal', message: String(err) } }
    }
  })
}

async function listenToReasoning(content_id: string): Promise<void> {
  // TODO (Phase 1): forward events to the originating tab via chrome.tabs.sendMessage(tabId, ...)
  //                 instead of just caching. Track tabId from sender in messaging.on handler.
  // TODO (Phase 1): merge events into a single ReasoningState object (storage.ts.cacheReasoning today
  //                 overwrites per event).
  try {
    for await (const event of api.streamReasoning(content_id)) {
      await cacheReasoning(content_id, event)
      if (event.type === 'final' || event.type === 'error') break
    }
  } catch (err) {
    console.error('[api-client.listenToReasoning] stream error', err)
  }
}
