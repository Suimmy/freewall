// Backend API client for the demo site.
// Phase 1 wired (E2E spine, 2026-05-07): real fetch to /perceive-text + EventSource to /stream.
// Backend pipeline runs in mock mode (USE_MOCK_AGENTS=true) until hackathon Phase 2.

import type { AnalysisResult, ReasoningEvent } from "@/types";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export interface AnalyzeTextInput {
  url: string;
  text: string;
  // Mode 1 paste box passes force_fresh=true to bypass cache (every paste = real LLM).
  // Mode 2 feed scroll leaves it undefined/false to use the warmed cache.
  force_fresh?: boolean;
  // Step 2.17 Part A — Mode 2 sends pre-cached AI-detection signals from offline
  // ONNX run (precompute_feed_signals.py). Mode 1 omits these until Phase 4
  // stretch wires live in-browser ONNX (Part B).
  text_ai_confidence?: number;
  image_ai_confidence?: number;
}

export interface AnalyzeTextResult {
  status: "queued" | "cached";
  session_id: string;
  content_id: string;
}

/**
 * POST /perceive-text — submit user-pasted post for analysis.
 * Returns session_id immediately (background pipeline kicks off on backend).
 * Caller should then open EventSource via openReasoningStream(session_id).
 */
export async function analyzeText(input: AnalyzeTextInput): Promise<AnalyzeTextResult> {
  const res = await fetch(`${BACKEND_URL}/perceive-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Backend ${res.status}: ${detail.slice(0, 200)}`);
  }

  return res.json() as Promise<AnalyzeTextResult>;
}

/**
 * Subscribe to streaming reasoning events for a session.
 * Returns a cleanup fn — call it on unmount or when starting a new session.
 *
 * Event flow (mock mode):
 *   coordinator_dispatched → agent_started × 3 (parallel) → agent_finished × 3
 *   → score_update → final
 *
 * The browser's EventSource auto-reconnects on transient network drops.
 * We close it explicitly after `final` or on caller's cleanup signal.
 */
export function openReasoningStream(
  sessionId: string,
  onEvent: (event: ReasoningEvent) => void,
  onComplete: (result: AnalysisResult) => void,
  onError: (err: Error) => void
): () => void {
  const url = `${BACKEND_URL}/stream/${sessionId}`;
  const eventSource = new EventSource(url);

  // Backend emits each event with `event:` line set to the type, so we listen
  // to specific named events (not the generic `message`).
  const listenerTypes = [
    "coordinator_dispatched",
    "agent_started",
    "agent_finished",
    "score_update",
    "final",
    "error",
  ] as const;

  const handlers = listenerTypes.map((type) => {
    const handler = (msg: MessageEvent<string>) => {
      try {
        const parsed = JSON.parse(msg.data) as ReasoningEvent;
        onEvent(parsed);

        if (parsed.type === "final") {
          // Extract full state — backend emits {type: "final", state: {...}}
          const state = (parsed as unknown as { state?: Record<string, unknown> }).state ?? {};
          const score = state.score as
            | { value: number; band: AnalysisResult["band"] }
            | undefined;

          if (score) {
            const result: AnalysisResult = {
              content_id: parsed.content_id,
              topic: state.topic as string | undefined,
              score: score.value,
              band: score.band,
              // Each agent finding is optional — propagate whatever backend included
              classifier: state.classifier as AnalysisResult["classifier"],
              coordinator: state.coordinator as AnalysisResult["coordinator"],
              persuasion: state.persuasion as AnalysisResult["persuasion"],
              fact_check: state.fact_check as AnalysisResult["fact_check"],
              provenance: state.provenance as AnalysisResult["provenance"],
              counter: state.counter as AnalysisResult["counter"],
            };
            onComplete(result);
          }
          eventSource.close();
        }

        if (parsed.type === "error") {
          const errMsg =
            (parsed.payload as { error?: string } | undefined)?.error ??
            (parsed as unknown as { error?: string }).error ??
            "Unknown error from backend";
          onError(new Error(errMsg));
          eventSource.close();
        }
      } catch (err) {
        console.error(`[Freewall SSE] parse error for ${type}:`, err, msg.data);
      }
    };
    eventSource.addEventListener(type, handler as EventListener);
    return { type, handler };
  });

  // Connection-level error (network, CORS, server down)
  const onConnError = () => {
    if (eventSource.readyState === EventSource.CLOSED) {
      onError(new Error("EventSource closed unexpectedly"));
    }
    // Otherwise it's auto-reconnecting — let it retry
  };
  eventSource.addEventListener("error", onConnError);

  // Cleanup
  return () => {
    handlers.forEach(({ type, handler }) =>
      eventSource.removeEventListener(type, handler as EventListener)
    );
    eventSource.removeEventListener("error", onConnError);
    eventSource.close();
  };
}

export interface AskWhyResponse {
  explanation: string;
  contributing_factors: Array<Record<string, unknown>>;
}

/**
 * POST /ask-why — request plain-language explanation of a cached score.
 * Reads cached state on the backend, calls gpt-5.5 to summarize. ~2-3s, ~$0.005/call.
 */
export async function askWhy(
  sessionId: string,
  contentId: string
): Promise<AskWhyResponse> {
  const res = await fetch(`${BACKEND_URL}/ask-why`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, content_id: contentId }),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Backend ${res.status}: ${detail.slice(0, 200)}`);
  }

  return res.json() as Promise<AskWhyResponse>;
}

export const __backendUrl = BACKEND_URL;
