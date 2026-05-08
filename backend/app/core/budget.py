"""
Cost circuit breaker for OpenAI API spend.

Two layers of defense:

  1. `check_call(estimated_cost_usd)` — pre-call estimate. Reject if a single
     call would cost more than `per_call_max_usd`, OR if it would push daily
     spend over `per_day_max_usd`. Use this in agent input_guardrails.
  2. `record_usage(input_tokens, output_tokens, ...)` — post-call. Updates the
     running daily total from actual response.usage. Logs a warning when
     threshold reached.

Pricing locked to gpt-5.5 (as of 2026-05-07):
  $5.00/M input · $30.00/M output · $0.50/M cached input.

State is in-process only — daily total resets when the backend restarts or
when the date rolls over (UTC midnight). For multi-process deploy, swap
`_state` for Redis.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.core.exceptions import FreewallError

logger = logging.getLogger(__name__)


class BudgetExceededError(FreewallError):
    """Raised when an LLM call would exceed budget caps. Maps to HTTP 503."""

    code = "budget_exceeded"


# gpt-5.5 pricing per 1,000,000 tokens (verify against current pricing if changed)
INPUT_USD_PER_M = 5.00
OUTPUT_USD_PER_M = 30.00
CACHED_INPUT_USD_PER_M = 0.50


def _utc_today() -> date:
    return datetime.now(timezone.utc).date()


@dataclass
class _BudgetState:
    today_utc: date = field(default_factory=_utc_today)
    spent_today_usd: float = 0.0

    def check_day_rollover(self) -> None:
        today = _utc_today()
        if self.today_utc != today:
            logger.info(
                "Daily budget rollover: $%.2f spent on %s — resetting",
                self.spent_today_usd, self.today_utc,
            )
            self.today_utc = today
            self.spent_today_usd = 0.0


_state = _BudgetState()


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
) -> float:
    """Estimate USD cost from token counts. Output includes reasoning tokens."""
    fresh_input = max(0, input_tokens - cached_input_tokens)
    return (
        fresh_input * INPUT_USD_PER_M / 1_000_000
        + cached_input_tokens * CACHED_INPUT_USD_PER_M / 1_000_000
        + output_tokens * OUTPUT_USD_PER_M / 1_000_000
    )


def check_call(estimated_cost_usd: float) -> None:
    """
    Call BEFORE making an LLM request. Raises BudgetExceededError if over caps.

    Estimating cost before the call requires a token count — for prompts you
    can use `tiktoken` or just multiply char count by ~0.25. For now, agents
    can call this with a rough estimate; record_usage() corrects later.
    """
    from app.config import settings

    _state.check_day_rollover()

    if estimated_cost_usd > settings.per_call_max_usd:
        raise BudgetExceededError(
            f"Estimated call cost ${estimated_cost_usd:.4f} exceeds per-call limit "
            f"${settings.per_call_max_usd:.2f}",
        )
    projected = _state.spent_today_usd + estimated_cost_usd
    if projected > settings.per_day_max_usd:
        raise BudgetExceededError(
            f"Daily budget would exceed ${settings.per_day_max_usd:.2f} "
            f"(currently ${_state.spent_today_usd:.4f}, this call ${estimated_cost_usd:.4f})",
        )


def record_usage(
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
) -> float:
    """
    Call AFTER each LLM response. Records actual cost from response.usage.
    Returns the cost charged (USD).
    """
    from app.config import settings

    cost = estimate_cost(input_tokens, output_tokens, cached_input_tokens)
    _state.check_day_rollover()
    _state.spent_today_usd += cost

    pct = _state.spent_today_usd / settings.per_day_max_usd
    if pct >= settings.cost_warning_threshold_pct:
        logger.warning(
            "Daily budget at %.0f%%: $%.2f spent / $%.2f cap",
            pct * 100, _state.spent_today_usd, settings.per_day_max_usd,
        )
    return cost


def get_state() -> dict[str, float | str]:
    """Snapshot for /health, admin endpoint, or budget banner in UI."""
    from app.config import settings

    _state.check_day_rollover()
    return {
        "today_utc": _state.today_utc.isoformat(),
        "spent_today_usd": round(_state.spent_today_usd, 4),
        "daily_cap_usd": settings.per_day_max_usd,
        "remaining_usd": round(
            max(0.0, settings.per_day_max_usd - _state.spent_today_usd), 4,
        ),
    }
