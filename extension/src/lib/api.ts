/**
 * Backend HTTP + SSE client. No chrome.* dependency — usable from background worker,
 * content script, popup, or webapp fallback.
 *
 * Background service worker is the canonical caller (host-page CSP can block fetch from
 * content scripts on some sites). Popup may call directly for /daily-mirror.
 */

// TODO (Phase 4): read from chrome.storage / env so deployed backend URL is configurable.
const API_BASE = 'http://localhost:8000'

// TODO (Phase 1): replace `unknown` returns with generated types from shared/schemas after codegen.sh.

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status?: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!res.ok) {
    let code = 'unknown'
    let message = res.statusText
    try {
      const body = (await res.json()) as { error?: { code: string; message: string } }
      if (body.error) {
        code = body.error.code
        message = body.error.message
      }
    } catch {
      // body wasn't JSON — keep statusText
    }
    throw new ApiError(code, message, res.status)
  }
  return (await res.json()) as T
}

export const api = {
  /** POST /perceive — fire-and-forget. Returns 202 with content_id. */
  async perceive(payload: unknown): Promise<{ content_id: string }> {
    return request('/perceive', { method: 'POST', body: JSON.stringify(payload) })
  },

  /** POST /ask-why — request explanation for a cached ReasoningState. */
  async askWhy(content_id: string): Promise<unknown> {
    return request('/ask-why', { method: 'POST', body: JSON.stringify({ content_id }) })
  },

  /** POST /counter-perspective — lazy-trigger Counter-Perspective Agent. */
  async requestCounter(content_id: string): Promise<unknown> {
    return request('/counter-perspective', {
      method: 'POST',
      body: JSON.stringify({ content_id }),
    })
  },

  /** GET /daily-mirror — aggregated session metrics. Empty days return 200 with empty payload. */
  async getDailyMirror(): Promise<unknown> {
    return request('/daily-mirror', { method: 'GET' })
  },

  /**
   * GET /stream/{session_id} — SSE stream wrapped as AsyncIterable for ergonomic use:
   *
   *   for await (const event of api.streamReasoning(sessionId)) {
   *     if (event.type === 'agent_started') { ... }
   *     if (event.type === 'final') break  // closes the EventSource
   *   }
   *
   * TODO (Phase 1): surface connection state (open/reconnecting/closed) to caller.
   * TODO (Phase 1): typed events (ReasoningEvent discriminated union from shared/schemas).
   */
  streamReasoning(session_id: string): AsyncIterable<{ type: string; [key: string]: unknown }> {
    const url = `${API_BASE}/stream/${encodeURIComponent(session_id)}`
    const knownEventTypes = [
      'coordinator_dispatched',
      'agent_started',
      'agent_finished',
      'score_update',
      'final',
      'error',
    ]

    return {
      [Symbol.asyncIterator]() {
        const es = new EventSource(url)
        const queue: { type: string; [key: string]: unknown }[] = []
        let resolveNext: ((v: IteratorResult<{ type: string; [key: string]: unknown }>) => void) | null = null
        let closed = false

        const handleEvent = (type: string) => (e: MessageEvent<string>): void => {
          let data: Record<string, unknown>
          try {
            data = JSON.parse(e.data) as Record<string, unknown>
          } catch {
            data = { raw: e.data }
          }
          const event = { type, ...data }
          if (resolveNext) {
            const r = resolveNext
            resolveNext = null
            r({ value: event, done: false })
          } else {
            queue.push(event)
          }
        }

        for (const t of knownEventTypes) {
          es.addEventListener(t, handleEvent(t) as EventListener)
        }

        es.onerror = (): void => {
          // EventSource auto-reconnects on network blip. Log only — caller may inspect readyState.
          console.warn('[api.streamReasoning] EventSource error, readyState=', es.readyState)
        }

        const closeStream = (): void => {
          if (closed) return
          closed = true
          es.close()
          if (resolveNext) {
            const r = resolveNext
            resolveNext = null
            r({ value: undefined, done: true })
          }
        }

        return {
          async next(): Promise<IteratorResult<{ type: string; [key: string]: unknown }>> {
            const head = queue.shift()
            if (head !== undefined) return { value: head, done: false }
            if (closed) return { value: undefined, done: true }
            return new Promise((resolve) => {
              resolveNext = resolve
            })
          },
          async return(): Promise<IteratorResult<{ type: string; [key: string]: unknown }>> {
            closeStream()
            return { value: undefined, done: true }
          },
        }
      },
    }
  },
}
