/**
 * Light-touch decoupling layer over chrome.* APIs.
 *
 * Single swap point: change `RUNTIME_MODE` to flip between Chrome extension and standalone
 * web-app. Phase 4 will exercise this if Codex computer use can't load unpacked extensions.
 *
 * UI components MUST go through this module — never import chrome.* directly.
 */

export const RUNTIME_MODE: 'chrome' | 'webapp' = 'chrome'

// Detect chrome runtime presence at load time. `chrome.runtime.id` is only set when running
// inside an extension context — guards against accidental webapp execution in chrome mode.
const isChrome =
  RUNTIME_MODE === 'chrome' &&
  typeof chrome !== 'undefined' &&
  !!chrome.runtime?.id

// ─── Storage ────────────────────────────────────────────────────────────────────

export const storage = {
  async get<T = unknown>(key: string): Promise<T | undefined> {
    if (isChrome) {
      const result = await chrome.storage.local.get(key)
      return result[key] as T | undefined
    }
    const raw = window.localStorage.getItem(key)
    return raw === null ? undefined : (JSON.parse(raw) as T)
  },

  async set(key: string, value: unknown): Promise<void> {
    if (isChrome) {
      await chrome.storage.local.set({ [key]: value })
      return
    }
    window.localStorage.setItem(key, JSON.stringify(value))
  },

  async remove(key: string): Promise<void> {
    if (isChrome) {
      await chrome.storage.local.remove(key)
      return
    }
    window.localStorage.removeItem(key)
  },

  watch<T = unknown>(key: string, callback: (value: T | undefined) => void): () => void {
    if (isChrome) {
      const listener = (
        changes: { [k: string]: chrome.storage.StorageChange },
        area: chrome.storage.AreaName,
      ): void => {
        if (area !== 'local') return
        const change = changes[key]
        if (change !== undefined) callback(change.newValue as T | undefined)
      }
      chrome.storage.onChanged.addListener(listener)
      return () => chrome.storage.onChanged.removeListener(listener)
    }
    // TODO (Phase 4): webapp mode receives storage events from same-origin tabs only.
    // For cross-tab webapp sync we'll need BroadcastChannel + custom event bus.
    const handler = (e: StorageEvent): void => {
      if (e.key !== key) return
      callback(e.newValue === null ? undefined : (JSON.parse(e.newValue) as T))
    }
    window.addEventListener('storage', handler)
    return () => window.removeEventListener('storage', handler)
  },
}

// ─── Messaging (content ↔ background ↔ popup) ────────────────────────────────────

export const messaging = {
  async send<TReq = unknown, TRes = unknown>(message: TReq): Promise<TRes> {
    if (isChrome) {
      return (await chrome.runtime.sendMessage(message)) as TRes
    }
    // TODO (Phase 4): webapp mode — use BroadcastChannel('freewall-bus') or in-page event bus.
    throw new Error('[runtime.messaging.send] not implemented for webapp mode')
  },

  on<TReq = unknown, TRes = unknown>(
    handler: (msg: TReq) => Promise<TRes>,
  ): () => void {
    if (isChrome) {
      const listener = (
        msg: TReq,
        _sender: chrome.runtime.MessageSender,
        sendResponse: (response: TRes) => void,
      ): boolean => {
        handler(msg)
          .then(sendResponse)
          .catch((err) => {
            console.error('[runtime.messaging.on] handler error', err)
          })
        // Returning true keeps the message channel open for the async sendResponse — required
        // by chrome.runtime.onMessage when the handler is async.
        return true
      }
      chrome.runtime.onMessage.addListener(listener)
      return () => chrome.runtime.onMessage.removeListener(listener)
    }
    // TODO (Phase 4): webapp messaging
    return () => {}
  },
}

// ─── Tab info (popup → current page URL) ─────────────────────────────────────────

export const tabs = {
  async getCurrentUrl(): Promise<string | null> {
    if (isChrome) {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
      return tab?.url ?? null
    }
    return window.location.href
  },
}
