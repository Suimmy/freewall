"""
Per-session SSE event manager — connects orchestrator (producer) ↔ stream route (consumer).

Design decisions:
- **Idempotent get-or-create**: queue spawns on first `emit()` OR `subscribe()`, whichever
  comes first. Fixes race condition where background task emits before client subscribes.
- **Bounded queue (100)**: drops OLDEST on backpressure (slow subscriber).
- **5-min TTL after `final`**: cleanup task scheduled on emit of "final" event.
- **30 s subscribe timeout**: lets stream route detect client disconnect; outer route restarts.
- **Hackathon scope**: in-process state, single-subscriber-per-session. Process restart loses
  in-flight sessions (acceptable — frontend retries).

Phase 4 hardening could add: periodic orphan sweeper, multi-subscriber fan-out, persistent log.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_QUEUE_MAXSIZE = 100
_TTL_SECS_AFTER_FINAL = 300   # 5 min — Suim's spec
_SUBSCRIBE_TIMEOUT_SECS = 30  # how long to wait for next event before yielding heartbeat


@dataclass
class _Session:
    queue: asyncio.Queue[dict[str, Any]] = field(
        default_factory=lambda: asyncio.Queue(maxsize=_QUEUE_MAXSIZE)
    )
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    finalized_at: float | None = None
    cleanup_task: asyncio.Task[None] | None = None


_sessions: dict[str, _Session] = {}


def _get_or_create(session_id: str) -> _Session:
    """Idempotent — both emit() and subscribe() use this. Fixes race."""
    if session_id not in _sessions:
        _sessions[session_id] = _Session()
        logger.info("sse session created: %s", session_id)
    return _sessions[session_id]


def emit(session_id: str, event: dict[str, Any]) -> None:
    """
    Push one event to a session's queue. Creates session if not exists (vs old behavior).

    Caller responsibility: event shape matches `shared/schemas/reasoning.json` variants.
    """
    session = _get_or_create(session_id)
    session.last_activity = time.time()

    try:
        session.queue.put_nowait(event)
    except asyncio.QueueFull:
        # Backpressure — drop oldest, push new
        try:
            dropped = session.queue.get_nowait()
            logger.warning(
                "sse backpressure: dropped event type=%s for session=%s",
                dropped.get("type"), session_id,
            )
            session.queue.put_nowait(event)
        except asyncio.QueueEmpty:
            pass

    # On terminal event, schedule cleanup
    if event.get("type") == "final" and session.finalized_at is None:
        session.finalized_at = time.time()
        session.cleanup_task = asyncio.create_task(
            _cleanup_after_ttl(session_id, _TTL_SECS_AFTER_FINAL)
        )
        logger.info(
            "sse session finalized: %s — cleanup in %ds",
            session_id, _TTL_SECS_AFTER_FINAL,
        )


async def subscribe(session_id: str) -> AsyncIterator[dict[str, Any]]:
    """
    Async generator yielding events for a session. Used by routes/stream.py.

    Behavior:
    - Yields events as they arrive
    - On 30s idle, returns (route can reconnect)
    - Stops AFTER yielding the `final` event (client now has it)
    - Cleanup happens via emit("final")'s scheduled task, not here

    Usage:
        async for event in subscribe(session_id):
            yield {"event": event["type"], "data": json.dumps(event)}
    """
    session = _get_or_create(session_id)
    logger.info("sse subscriber attached: %s", session_id)
    try:
        while True:
            try:
                event = await asyncio.wait_for(
                    session.queue.get(), timeout=_SUBSCRIBE_TIMEOUT_SECS
                )
            except asyncio.TimeoutError:
                # Subscriber idle — let route close, client reconnects via EventSource
                logger.debug("sse subscribe idle timeout: %s", session_id)
                return

            session.last_activity = time.time()
            yield event

            if event.get("type") == "final":
                # Client received terminal event — clean exit
                return
    finally:
        logger.info("sse subscriber detached: %s", session_id)


async def _cleanup_after_ttl(session_id: str, delay_secs: int) -> None:
    """Wait then drop session. Called as background task by emit('final')."""
    try:
        await asyncio.sleep(delay_secs)
        if session_id in _sessions:
            del _sessions[session_id]
            logger.info("sse session cleaned up after TTL: %s", session_id)
    except asyncio.CancelledError:
        pass


def active_sessions() -> list[dict[str, Any]]:
    """For /health, admin, debug. Returns lightweight session metadata."""
    now = time.time()
    return [
        {
            "session_id": sid,
            "age_secs": round(now - s.created_at, 1),
            "last_activity_secs_ago": round(now - s.last_activity, 1),
            "finalized": s.finalized_at is not None,
            "queue_depth": s.queue.qsize(),
        }
        for sid, s in _sessions.items()
    ]
