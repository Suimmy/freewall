"""
POST /counter-perspective — lazy trigger Counter-Perspective Agent.

Use case: score was ≥ 50 → Counter did NOT auto-run during /perceive
→ user clicks "show counter perspective" → run Counter on demand.

Why lazy: Counter is the most expensive agent (effort=high + web search,
~$0.10/call). Auto-running for every post would burn budget; we run only
when user actually wants it.

If state already has a `counter` finding (auto-ran during /perceive because
score < 50), we just return it from cache — no second LLM call.

Wire shape: shared/schemas/reasoning.json#/$defs/CounterPerspectiveFinding
Stub: 404 if content not analyzed; otherwise canned response. Real impl
(Phase 1) dispatches Counter-Perspective Agent and updates cache.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core import cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/counter-perspective", tags=["counter"])


class CounterRequest(BaseModel):
    session_id: str
    content_id: str


# Inline minimal stub — replaced by codegen-generated CounterPerspectiveFinding
# from shared/schemas/reasoning.json after Step 3.
class _AlternativeSource(BaseModel):
    url: str
    title: str
    publisher: str | None = None
    credibility: str | None = None  # 'credible' | 'mixed' | 'unreliable' | 'unknown'


class CounterResponse(BaseModel):
    steelman: str
    alternative_sources: list[_AlternativeSource]


@router.post("", response_model=CounterResponse)
async def counter_perspective(request: CounterRequest) -> CounterResponse:
    """Run Counter-Perspective Agent on demand. Caches result on first run."""
    state = cache.get(request.content_id)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "content_not_found",
                    "message": (
                        f"No reasoning state for content_id={request.content_id}. "
                        "Re-trigger /perceive first."
                    ),
                }
            },
        )

    # Phase 1: if state already has a `counter` finding, return it directly
    # (avoids re-running the most expensive agent).
    if (existing := state.get("counter")) is not None:
        logger.info(
            "counter-perspective cache hit: session=%s content=%s",
            request.session_id, request.content_id,
        )
        return CounterResponse(**existing)

    logger.info(
        "counter-perspective dispatch: session=%s content=%s",
        request.session_id, request.content_id,
    )

    # TODO (Phase 1):
    # 1. budget.check_call(estimated_cost_usd=0.10) — Counter is expensive
    # 2. Build CounterPerspectiveAgentInput from `state` (text, category,
    #    persuasion + fact_check + provenance findings)
    # 3. Dispatch via Agents SDK:
    #      result = await Runner.run(counter_agent, input)
    #      finding: CounterPerspectiveFinding = result.final_output
    # 4. budget.record_usage(...)
    # 5. cache.set(content_id, {**state, "counter": finding.model_dump()})
    # 6. Emit "agent_finished" SSE event so any listeners on /stream see it
    # 7. Return finding

    return CounterResponse(
        steelman=(
            "Stub — real implementation runs Counter-Perspective Agent with "
            "web_search tool, then caches and returns the steelman."
        ),
        alternative_sources=[],
    )
