/**
 * Typed message envelopes for content ↔ background ↔ popup communication.
 *
 * Discriminated unions on `type` give TypeScript narrowing inside handlers.
 * TODO (Phase 1): replace `unknown` payloads with generated types from shared/schemas
 *                 (PerceptionPayload, ReasoningEvent, CounterResponse, AskWhyResponse).
 */

export type ContentToBackgroundMessage =
  | { type: 'perceive'; payload: unknown }
  | { type: 'request_counter'; content_id: string }
  | { type: 'ask_why'; content_id: string }
  | { type: 'get_daily_mirror' }

export type BackgroundToContentMessage =
  | { type: 'reasoning_event'; content_id: string; event: unknown }
  | { type: 'counter_response'; content_id: string; data: unknown }
  | { type: 'ask_why_response'; content_id: string; data: unknown }
  | { type: 'error'; content_id?: string; error: { code: string; message: string } }

export type AnyMessage = ContentToBackgroundMessage | BackgroundToContentMessage

export function isContentToBackground(msg: AnyMessage): msg is ContentToBackgroundMessage {
  return (
    msg.type === 'perceive' ||
    msg.type === 'request_counter' ||
    msg.type === 'ask_why' ||
    msg.type === 'get_daily_mirror'
  )
}
