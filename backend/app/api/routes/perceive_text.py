"""
POST /perceive-text — judge-pasted content endpoint (decision #19 + #20).

Demo site (Vercel) sends {url, text} from the input box. Backend:
  1. Validates inputs
  2. Generates session_id + content_id (hash of text)
  3. Builds a PerceptionPayload-shaped dict
  4. Schedules orchestrator.run_pipeline() as background task
  5. Returns 202 with {session_id, content_id, status}

Frontend then opens GET /stream/{session_id} to receive SSE events.

Wire shape: extends shared/schemas/perception.json minimally — we synthesize
the PerceptionPayload from {url, text} since judges don't send full extension
metadata (no scraper, no synthetic_signals, no user_state).
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

from app.core import cache
from app.services import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/perceive-text", tags=["perceive"])

# Constraints
_TEXT_MIN = 10           # too-short → not a real post
_TEXT_MAX = 4000         # ~1k tokens — covers the longest realistic FB post
_URL_MAX = 500


class PerceiveTextRequest(BaseModel):
    url: str = Field(..., max_length=_URL_MAX, description="Source URL of the post")
    text: str = Field(..., min_length=_TEXT_MIN, max_length=_TEXT_MAX,
                      description="Visible text of the post")
    # Mode 1 paste box sets force_fresh=True so every paste runs real LLM (per Suim
    # 2026-05-08 evening: "Mode 1 ทุกครั้ง real, ช้าหน่อย OK"). Mode 2 feed scroll
    # leaves it false to use the warmed cache for instant replay.
    force_fresh: bool = Field(default=False,
                              description="If true, bypass cache (no read, no write)")
    # AI-detection signals (Step 2.17 Part A — 2026-05-08 evening). Mode 2 sends
    # pre-cached signals from offline ONNX run (Hello-SimpleAI text detector).
    # Mode 1 leaves these None until Phase 4 stretch wires live in-browser ONNX.
    # If provided, Provenance Agent uses these values; if None, falls back to 0.5.
    text_ai_confidence: float | None = Field(default=None, ge=0.0, le=1.0,
                                              description="0..1 AI-generated probability for text")
    image_ai_confidence: float | None = Field(default=None, ge=0.0, le=1.0,
                                               description="0..1 AI-generated probability for image")


class PerceiveTextResponse(BaseModel):
    status: str = Field(default="queued", description="'queued' | 'cached'")
    session_id: str
    content_id: str


def _make_content_id(text: str) -> str:
    """Stable hash of normalized text — enables cache hits across paste retries."""
    norm = " ".join(text.split())  # collapse whitespace
    digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()
    return f"text_{digest[:16]}"


def _parse_domain(url: str) -> str | None:
    """Best-effort domain extraction. None if unparseable."""
    try:
        parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
        return parsed.netloc or None
    except Exception:
        return None


def _build_perception(req: PerceiveTextRequest, session_id: str, content_id: str) -> dict[str, Any]:
    """Synthesize a PerceptionPayload-ish dict for the orchestrator."""
    # Pass through AI-detection signals if frontend provided them (Mode 2 cached
    # signals from precompute_feed_signals.py, or Mode 1 live in Phase 4).
    synthetic_signals = None
    if req.text_ai_confidence is not None or req.image_ai_confidence is not None:
        synthetic_signals = {
            "text_ai_confidence": req.text_ai_confidence,
            "avatar_ai_confidence": req.image_ai_confidence,
        }
    return {
        "session_id": session_id,
        "content_id": content_id,
        "url": req.url,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "content": {
            "text": req.text,
            "category": None,           # L1 Classifier will set this
            "lang": None,
            "image_urls": [],
        },
        "source": {
            "domain": _parse_domain(req.url),
            "platform": None,            # demo site doesn't know — orchestrator infers
        },
        "synthetic_signals": synthetic_signals,
        "user_state": None,
    }


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=PerceiveTextResponse)
async def perceive_text(
    body: PerceiveTextRequest,
    background_tasks: BackgroundTasks,
) -> PerceiveTextResponse:
    """
    Accept user-pasted post → kick off pipeline → return session/content IDs.

    Frontend then opens EventSource `/stream/{session_id}` to receive events.
    """
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is empty after trim")

    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    content_id = _make_content_id(text)

    perception = _build_perception(body, session_id, content_id)

    # Lazy cache check (CLAUDE.md decision #4): same content_id served previously
    # → replay cached SSE events instead of running real LLM agents (~$0.10-0.25 saved).
    # Mode 1 paste box passes force_fresh=true to bypass cache entirely (read + write).
    if not body.force_fresh:
        cached_state = cache.get(content_id)
        if cached_state is not None:
            logger.info(
                "perceive-text CACHE HIT: session=%s content=%s text_len=%d",
                session_id, content_id, len(text),
            )
            background_tasks.add_task(
                orchestrator.replay_cached, session_id, content_id, cached_state,
            )
            return PerceiveTextResponse(
                status="cached",
                session_id=session_id,
                content_id=content_id,
            )

    logger.info(
        "perceive-text %s: session=%s content=%s url=%s text_len=%d",
        "FORCE FRESH (no cache)" if body.force_fresh else "CACHE MISS",
        session_id, content_id, body.url, len(text),
    )

    # Schedule mock-or-live pipeline (per CLAUDE.md decision #18 USE_MOCK_AGENTS).
    # NOTE: force_fresh only controls cache.get bypass above (forces a real LLM
    # run). We still write the result to cache so downstream operations like
    # /ask-why can read it. Otherwise Mode 1 paste → score visible but Ask Why
    # fails with content_not_found 404.
    perception["_skip_cache_write"] = False
    background_tasks.add_task(orchestrator.run_pipeline, perception)

    return PerceiveTextResponse(
        status="queued",
        session_id=session_id,
        content_id=content_id,
    )
