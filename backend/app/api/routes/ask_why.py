"""
POST /ask-why — explain a flagging decision in natural language.

User clicked an annotation → this endpoint reads the cached ReasoningState
for that content_id and asks the LLM to explain in plain language.
Does NOT re-run agents.

Why this design:
- Low latency (< 1s) — user expects instant explanation on click
- Low cost (~$0.005/call) — single summarization, not full pipeline
- Consistency — explanation grounded in the same state that drove the annotation

Wire shape: docs/API_CONTRACTS.md §3
Stub: returns 404 if not cached; otherwise returns canned text + the cached
contributing_factors. Real impl (Phase 1) calls LLM to summarize.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from agents import Runner
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.agents.ask_why import ask_why_agent
from app.core import cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ask-why", tags=["ask-why"])


class AskWhyRequest(BaseModel):
    session_id: str
    content_id: str


class AskWhyResponse(BaseModel):
    explanation: str
    contributing_factors: list[dict[str, Any]]


@router.post("", response_model=AskWhyResponse)
async def ask_why(request: AskWhyRequest) -> AskWhyResponse:
    """Explain a flagging decision in natural language. Reads cached state only."""
    state = cache.get(request.content_id)
    if state is None:
        # 404: probably evicted from cache, or extension lost track. UI should
        # gracefully show "explanation unavailable" and re-trigger /perceive.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "content_not_found",
                    "message": (
                        f"No reasoning state cached for content_id={request.content_id}. "
                        "Re-trigger /perceive to regenerate."
                    ),
                }
            },
        )

    logger.info(
        "ask-why hit cache: session=%s content=%s",
        request.session_id, request.content_id,
    )

    factors = state.get("score", {}).get("contributing_factors", [])

    # Compact state for the LLM — strip large/redundant fields, keep what
    # the prompt needs to ground the explanation.
    state_for_llm: dict[str, Any] = {
        "score": state.get("score"),
        "topic": state.get("topic"),
        "classifier": state.get("classifier"),
        "persuasion": state.get("persuasion"),
        "fact_check": state.get("fact_check"),
        "provenance": state.get("provenance"),
        "counter": state.get("counter"),
    }
    payload = json.dumps(state_for_llm, ensure_ascii=False, default=str)

    try:
        result = await Runner.run(ask_why_agent, payload)
        explanation = (result.final_output or "").strip()
    except Exception as e:
        logger.exception("ask-why LLM call failed: %s", e)
        # Graceful fallback — surface a neutral explanation built from factors.
        score = state.get("score", {})
        explanation = (
            f"Score {score.get('value')} ({score.get('band')}). "
            "Detailed explanation temporarily unavailable — see the per-agent "
            "findings in the sidebar for the full breakdown."
        )

    return AskWhyResponse(
        explanation=explanation,
        contributing_factors=factors,
    )
