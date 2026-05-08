# Freewall — API Contracts

> Human-readable cheatsheet for the 5 backend endpoints. Machine-readable shapes live in `shared/schemas/` — this doc is for grokking the API at a glance, not for code generation.

**Base URL** (dev): `http://localhost:8000`
**Auth**: none (local hackathon — extension talks to localhost backend)
**CORS**: backend allows `chrome-extension://*` origins (configured in `backend/app/main.py`)
**Content-Type**: `application/json` for requests/responses; `text/event-stream` for SSE

---

## Endpoint summary

| # | Method | Path | Purpose | Request schema | Response schema |
|---|--------|------|---------|----------------|-----------------|
| 1 | `POST` | `/perceive` | Ingest one content unit from L1 | `perception.json` (PerceptionPayload) | 202 Accepted |
| 2 | `GET` | `/stream/{session_id}` | Subscribe to L2 reasoning events | — | SSE of `reasoning.json` events |
| 3 | `POST` | `/ask-why` | Explain why a content was flagged | `{ session_id, content_id }` | `{ explanation: string }` |
| 4 | `POST` | `/counter-perspective` | Lazy trigger Counter-Perspective Agent | `{ session_id, content_id }` | `CounterPerspectiveFinding` |
| 5 | `GET` | `/daily-mirror` | End-of-day stats for the popup | query `?date=YYYY-MM-DD` (optional) | `DailyMirrorPayload` (defined below) |

---

## 1. `POST /perceive`

**Purpose**: Extension content script sends one content unit (post, article, AI message, etc.) when it enters the viewport.

**Request body**: matches `shared/schemas/perception.json#PerceptionPayload`

**Response**:
- `202 Accepted` — payload queued for async processing. Body is empty or `{ "status": "queued", "content_id": "..." }`.
- `400 Bad Request` — schema validation failed. Body: `{ "error": { "code": "invalid_perception", "message": "..." } }`.
- `429 Too Many Requests` — extension is sending too fast (rate limit, e.g., > 20 req/sec per session).

**When called**: every time `IntersectionObserver` in `extension/src/content/observer.ts` fires for a new content unit.

**Why fire-and-forget (202 not 200)**: Coordinator + agents take 2-10 seconds. Extension cannot block on this — it fires, then listens on `/stream/{session_id}` for results. Backend uses async tasks (FastAPI `BackgroundTasks` or asyncio queue).

---

## 2. `GET /stream/{session_id}`

**Purpose**: Long-lived SSE connection. Backend pushes reasoning events as agents complete.

**Path param**: `session_id` (UUID v4) — the same session_id used in `/perceive` payloads.

**Response**: `Content-Type: text/event-stream`. Each event matches one of the variants in `shared/schemas/reasoning.json` (CoordinatorDispatchedEvent, AgentStartedEvent, AgentFinishedEvent, ScoreUpdateEvent, FinalEvent, ErrorEvent).

**Example stream**:
```
data: {"type":"coordinator_dispatched","session_id":"...","content_id":"post_3f8a","timestamp":"...","dispatched_agents":["persuasion","fact_check","provenance"]}

data: {"type":"agent_started","agent":"persuasion","session_id":"...","content_id":"post_3f8a","timestamp":"..."}

data: {"type":"agent_finished","agent":"persuasion","finding":{"tactics_detected":[...],"intended_action":"..."},"session_id":"...","content_id":"post_3f8a","timestamp":"..."}

data: {"type":"score_update","score":{"value":18,"band":"high_risk","confidence":0.82},"session_id":"...","content_id":"post_3f8a","timestamp":"..."}

data: {"type":"final","state":{...full ReasoningState...},"session_id":"...","content_id":"post_3f8a","timestamp":"..."}
```

**Multiplexing**: One stream carries events for ALL content_ids in that session. UI dispatches by `content_id` to the right DOM annotation.

**Reconnect**: If extension drops the connection, it reconnects with the same `session_id`. Backend replays the most recent `final` event for each in-flight content_id (if cached) so UI catches up without missing state.

**When called**: extension background script opens this connection on extension boot (after first `/perceive`) and keeps it alive for the tab's lifetime.

---

## 3. `POST /ask-why`

**Purpose**: User clicks an annotation → modal opens → "Why was this flagged?" → LLM explains in natural language using the existing reasoning state (no re-analysis needed).

**Request body**:
```json
{
  "session_id": "uuid",
  "content_id": "post_3f8a"
}
```

**Response**:
```json
{
  "explanation": "This post uses the fear_mongering tactic ('Doctors HATE this trick') combined with misrepresentation_of_expertise (claiming hidden knowledge). The factual claim about cinnamon curing diabetes is contradicted by WHO. Source domain has unreliable reputation.",
  "contributing_factors": [
    { "factor": "Fear-mongering tactic detected", "weight": -0.4 },
    { "factor": "Health claim contradicted by WHO", "weight": -0.3 },
    { "factor": "Source rated unreliable", "weight": -0.2 }
  ]
}
```

**Errors**:
- `404 Not Found` — content_id has no reasoning state in cache (probably evicted; UI should re-trigger via /perceive).
- `500 Internal Server Error` — LLM call failed; UI shows "explanation unavailable, see findings below" + falls back to listing raw findings.

**Backend implementation note**: this endpoint reads cached `ReasoningState` (from /stream session) and asks LLM to summarize in plain language. **Does NOT re-run agents.**

---

## 4. `POST /counter-perspective`

**Purpose**: Lazy trigger for Counter-Perspective Agent. Use case: score was ≥ 50 → Counter did NOT auto-run → user clicked "show counter perspective" → backend runs Counter on demand.

**Request body**:
```json
{
  "session_id": "uuid",
  "content_id": "post_3f8a"
}
```

**Response**: matches `shared/schemas/reasoning.json#/$defs/CounterPerspectiveFinding`
```json
{
  "steelman": "Even if cinnamon supplements...",
  "alternative_sources": [
    { "url": "https://...", "title": "Mayo Clinic — Diabetes self-care", "publisher": "Mayo Clinic", "credibility": "credible" }
  ]
}
```

**Errors**:
- `404 Not Found` — content_id unknown.
- `503 Service Unavailable` — web search tool unavailable; backend should return a fallback steelman generated without live sources.

**Latency expectation**: 4-8 seconds (LLM + web search). UI shows skeleton/spinner.

---

## 5. `GET /daily-mirror`

**Purpose**: Aggregate stats for end-of-day "Daily Mirror" dashboard in the extension popup.

**Query params**:
- `date` (optional, format `YYYY-MM-DD`, default = today): which day to summarize.

**Response** (`DailyMirrorPayload` — not in `shared/schemas/` for v0; will codify if it stabilizes):
```json
{
  "date": "2026-05-09",
  "totals": {
    "perceptions": 412,
    "flagged_caution": 38,
    "flagged_high_risk": 9,
    "fact_checks_run": 51,
    "counter_perspectives_shown": 7,
    "decision_pauses": 2
  },
  "top_tactics": [
    { "tactic": "fear_mongering", "count": 14 },
    { "tactic": "false_scarcity", "count": 9 },
    { "tactic": "misrepresentation_of_expertise", "count": 6 }
  ],
  "score_trend": [
    { "hour": "09:00", "avg_score": 78 },
    { "hour": "10:00", "avg_score": 71 }
  ],
  "budget": {
    "today_utc": "2026-05-09",
    "spent_today_usd": 12.34,
    "daily_cap_usd": 80.00,
    "remaining_usd": 67.66
  }
}
```

The `budget` field surfaces the LLM-spend state from `core/budget.py:get_state()`. UI shows remaining $/day in popup as a "self-aware cost" demo signal. See CLAUDE.md decision #17.

**Errors**:
- `200 OK` with empty totals if user had zero perceptions on that date (don't 404 — empty is a valid state).

**When called**: user opens extension popup OR clicks "Today's Mirror" link in sidebar.

---

## Cross-reference

- Wire shapes: `shared/schemas/perception.json`, `shared/schemas/reasoning.json`, `shared/schemas/agent_io.json`
- Enum values: `shared/ENUMS.md`
- Backend route handlers: `backend/app/api/routes/{perceive,stream,ask_why,counter,mirror}.py` (Step 2)
- Extension API client: `extension/src/background/api-client.ts` (Step 3)

---

## Conventions used here

- **Path naming**: kebab-case (`/ask-why`, `/counter-perspective`, `/daily-mirror`).
- **JSON keys**: snake_case (matches Python idiom; codegen handles TS conversion automatically).
- **IDs**: `session_id` is UUID v4; `content_id` is opaque string (hash recommended).
- **Timestamps**: ISO 8601 with timezone (`2026-05-09T14:23:11.482Z`).
- **Status codes**: 2xx happy path, 400 invalid input, 404 not in cache, 429 rate-limited, 5xx backend issue. Bodies always JSON `{ error: { code, message } }` for non-2xx.
