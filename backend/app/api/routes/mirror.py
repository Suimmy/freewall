"""
GET /daily-mirror — end-of-day stats for the extension popup.

Aggregates today's perceptions, flagged counts, top tactics, score trend.
Pure aggregation — no LLM call, no per-content_id lookup. Returns 200 with
empty totals if no data for the requested day (NOT 404 — empty is valid).

Bonus: includes current budget state — UI can display remaining $/day to
demonstrate the system's cost awareness during demo.

Wire shape: docs/API_CONTRACTS.md §5
Stub: returns zeros + real budget state. Phase 1 adds metrics aggregation
from `services/orchestrator.py`'s in-memory store.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.core.budget import get_state as get_budget_state

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/daily-mirror", tags=["mirror"])


class DailyTotals(BaseModel):
    perceptions: int = 0
    flagged_caution: int = 0
    flagged_high_risk: int = 0
    fact_checks_run: int = 0
    counter_perspectives_shown: int = 0
    decision_pauses: int = 0


class TacticCount(BaseModel):
    tactic: str
    count: int


class ScoreTrendPoint(BaseModel):
    hour: str  # "HH:MM" UTC
    avg_score: float


class DailyMirrorResponse(BaseModel):
    date: str = Field(..., description="ISO date YYYY-MM-DD (UTC)")
    totals: DailyTotals
    top_tactics: list[TacticCount]
    score_trend: list[ScoreTrendPoint]
    budget: dict[str, Any] = Field(
        ..., description="Snapshot from core/budget.py — see budget.get_state()."
    )


@router.get("", response_model=DailyMirrorResponse)
async def daily_mirror(
    date: str | None = Query(
        default=None,
        description="ISO date YYYY-MM-DD. Defaults to today (UTC).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    ),
) -> DailyMirrorResponse:
    """Return aggregated metrics for one day. Empty totals if no activity."""
    target_date = date or datetime.now(timezone.utc).date().isoformat()
    logger.debug("daily-mirror requested for date=%s", target_date)

    # TODO (Phase 1): pull real numbers from a per-day metrics store updated
    # by orchestrator.run_pipeline() — `top_tactics` from PersuasionFinding
    # frequency, `score_trend` from ReasoningState scores per hour, etc.

    return DailyMirrorResponse(
        date=target_date,
        totals=DailyTotals(),
        top_tactics=[],
        score_trend=[],
        budget=get_budget_state(),
    )
