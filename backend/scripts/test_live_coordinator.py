"""
Smoke-test the live Coordinator agent on representative dispatch scenarios.

Verifies:
  • Routing table — health_claim/news/social/ad/unknown all dispatch all 3
  • Meme rule — fact_check skipped on category='meme'
  • Confidence override — confidence < 0.5 triggers dispatch-all regardless of category

Run from `backend/`:
    uv run python scripts/test_live_coordinator.py

Costs ~$0.02 total (4 calls @ reasoning=low on gpt-5.5).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents import Runner

from app.agents.coordinator import coordinator_agent
from app.core import budget

# (case_id, classifier_finding, expected_dispatched_set, expected_skipped_count, notes)
CASES = [
    # — Happy path: dispatch table all 6 categories —
    (
        "health_claim_high_conf",
        {"content_id": "case01", "category": "health_claim", "confidence": 0.98},
        {"persuasion", "fact_check", "provenance"}, 0,
        "Health claim, high confidence — dispatch all 3",
    ),
    (
        "news_high_conf",
        {"content_id": "case02", "category": "news", "confidence": 0.95},
        {"persuasion", "fact_check", "provenance"}, 0,
        "News, high confidence — dispatch all 3",
    ),
    (
        "ad_high_conf",
        {"content_id": "case05", "category": "ad", "confidence": 0.92},
        {"persuasion", "fact_check", "provenance"}, 0,
        "Ad — dispatch all 3 (prompt's table: ad row dispatches all)",
    ),
    (
        "social_high_conf",
        {"content_id": "case06", "category": "social", "confidence": 0.85},
        {"persuasion", "fact_check", "provenance"}, 0,
        "Social — dispatch all 3 (prompt's table)",
    ),
    # — Skip rule: meme → skip fact_check —
    (
        "meme_high_conf",
        {"content_id": "case03", "category": "meme", "confidence": 0.92},
        {"persuasion", "provenance"}, 1,
        "Meme — skip fact_check (no factual claim)",
    ),
    # — Override rule: confidence < 0.5 dispatches all regardless of category —
    (
        "unknown_low_conf",
        {"content_id": "case04", "category": "unknown", "confidence": 0.30},
        {"persuasion", "fact_check", "provenance"}, 0,
        "Low confidence override → dispatch all (defensive)",
    ),
    # — Boundary: meme + confidence < 0.5 → override should fire (no skip) —
    (
        "meme_below_threshold",
        {"content_id": "case07", "category": "meme", "confidence": 0.49},
        {"persuasion", "fact_check", "provenance"}, 0,
        "Meme @ 0.49 — override < 0.5 fires, dispatch all even for meme (DON'T skip fact_check)",
    ),
]


def _format_input(finding: dict) -> str:
    return (
        f"content_id: {finding['content_id']}\n"
        f"category: {finding['category']}\n"
        f"category_confidence: {finding['confidence']:.2f}"
    )


async def main() -> int:
    fails = 0
    spent_before = budget._state.spent_today_usd
    print(f"\nRunning {len(CASES)} cases...\n" + "=" * 78)

    for i, (case_id, finding, expected_dispatched, expected_skipped_count, notes) in enumerate(
        CASES, 1
    ):
        print(f"\n[{i}/{len(CASES)}] {case_id}: {notes}")
        print(f"     input            : {finding}")
        coord_input = _format_input(finding)

        try:
            result = await Runner.run(coordinator_agent, coord_input)
        except Exception as e:
            print(f"     [FAIL] Runner.run raised: {type(e).__name__}: {e}")
            fails += 1
            continue

        out = result.final_output
        dispatched = {
            a.value if hasattr(a, "value") else str(a) for a in out.dispatched_agents
        }
        skipped = [
            (s.agent.value if hasattr(s.agent, "value") else str(s.agent), s.reason)
            for s in out.skipped_agents
        ]
        dispatched_match = dispatched == expected_dispatched
        skipped_count_match = len(skipped) == expected_skipped_count
        ok = dispatched_match and skipped_count_match
        marker = "OK  " if ok else "FAIL"
        print(f"     [{marker}] dispatched: {sorted(dispatched)}  expected: {sorted(expected_dispatched)}")
        print(f"            skipped   : {skipped}  (expected count: {expected_skipped_count})")
        if not ok:
            fails += 1

        # Cost tracking
        for resp in getattr(result, "raw_responses", []) or []:
            usage = getattr(resp, "usage", None)
            if not usage:
                continue
            cached = 0
            details = getattr(usage, "input_tokens_details", None)
            if details is not None:
                cached = getattr(details, "cached_tokens", 0) or 0
            budget.record_usage(
                getattr(usage, "input_tokens", 0) or 0,
                getattr(usage, "output_tokens", 0) or 0,
                cached,
            )

    spent_after = budget._state.spent_today_usd
    print("\n" + "=" * 78)
    print(f"\nTotal cost this run: ${spent_after - spent_before:.4f} ({len(CASES)} calls)")
    if fails:
        print(f"\n{fails}/{len(CASES)} cases failed.")
        return 1
    print(f"\nAll {len(CASES)} cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
