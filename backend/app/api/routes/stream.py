"""
GET /stream/{session_id} — long-lived SSE channel.

Demo site (Vercel) opens this immediately after `POST /perceive-text` returns the
session_id. Backend pumps ReasoningEvent variants as the orchestrator emits them
through `services/sse.py`.

Why SSE (not WebSocket): one-way push is enough; runs on plain HTTP; native
EventSource API gives auto-reconnect for free.

Connection lifecycle:
  1. Client opens (EventSource) → register subscriber via sse.subscribe()
  2. Pump events: each event yielded as `{event: <type>, data: <json>}`
  3. Client closes (tab close / network drop) → generator's `finally` cleans up
  4. After "final" event yielded, generator exits cleanly (5-min TTL on session
     in services/sse.py handles late late reconnects via cached state — Phase 4)
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.services import sse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stream", tags=["stream"])


@router.get("/{session_id}")
async def stream(session_id: str, request: Request) -> EventSourceResponse:
    """
    Subscribe to reasoning events for one browser session.

    The async generator yields dicts in sse-starlette's expected shape:
      {"event": "<event_type>", "data": "<json string>"}
    sse-starlette formats them as `event: ...\\ndata: ...\\n\\n` per SSE spec.
    """

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        logger.info("stream opened: session=%s", session_id)
        try:
            async for event in sse.subscribe(session_id):
                # Detect client disconnect each loop iteration
                if await request.is_disconnected():
                    logger.info("stream client disconnected: session=%s", session_id)
                    return

                yield {
                    "event": event.get("type", "message"),
                    "data": json.dumps(event, ensure_ascii=False),
                }
        finally:
            logger.info("stream closed: session=%s", session_id)

    return EventSourceResponse(event_generator())
