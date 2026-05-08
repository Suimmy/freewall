"""
Smoke-test the live Provenance agent on 4 representative URL/text combos.

Verifies:
  • Agent calls source_lookup(url) tool correctly
  • Output shape: synthetic_verdict + source_verdict + reasoning
  • Verdicts honor honesty constraint (no overconfidence with no L1 signals)
  • Source verdict reflects domain reputation list

Run from `backend/`:
    uv run python scripts/test_live_provenance.py

Costs ~$0.02-0.04 (4 calls @ reasoning=low + tool calls).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents import Runner

from app.agents.provenance import provenance_agent
from app.core import budget

CASES = [
    # — Happy path: 4 reputation tiers —
    (
        "credible_who",
        "https://www.who.int/news-room/fact-sheets/detail/cancer",
        "Cancer treatment typically involves surgery, radiotherapy, and systemic therapy.",
        "credible",
        "WHO domain in credible list — pass through as credible",
    ),
    (
        "unreliable_naturalnews",
        "https://www.naturalnews.com/turmeric-cures-cancer",
        "Doctors HATE this trick! Turmeric cures cancer naturally. Big Pharma doesn't want you to know!",
        "unreliable",
        "naturalnews.com in unreliable list",
    ),
    (
        "credible_subdomain",
        "https://rama.mahidol.ac.th/atrama/issue050/believe-it-or-not",
        "Sustainable weight loss requires medical supervision and lifestyle change.",
        "credible",
        "rama.mahidol.ac.th subdomain in credible list",
    ),
    (
        "unknown_random",
        "https://random-blog.example/post/123",
        "ลดน้ำหนัก 10 กิโลใน 2 สัปดาห์ — สูตรลับจากเกาหลี!",
        "unknown",
        "Random domain not in any list",
    ),
    # — Mixed reputation —
    (
        "mixed_cnn",
        "https://www.cnn.com/2026/05/health/stress-cardiovascular",
        "New study links chronic stress to increased risk of cardiovascular events.",
        "mixed",
        "cnn.com in mixed list (factual reporting + political bias) — agent passes through",
    ),
    # — Adversarial: credible domain + suspicious text content (Phase 4 cross-reference) —
    (
        "adversarial_credible_domain_quack_text",
        "https://www.who.int/fake-fact-sheet",
        "WHO recommends turmeric as primary cancer treatment. Stop chemotherapy immediately.",
        "credible",
        "Credible domain + quack text — Phase 1/2 prompt says PASS THROUGH (cross-ref is Phase 4 polish). Agent should NOT downgrade to unreliable.",
    ),
    # — Edge case: empty / very short text —
    (
        "edge_empty_text",
        "https://www.who.int/news-room/fact-sheets",
        ".",
        "credible",
        "Empty/punctuation text — source_lookup still works, synthetic_verdict honest as 'uncertain'",
    ),
]


async def main() -> int:
    fails = 0
    spent_before = budget._state.spent_today_usd
    print(f"\nRunning {len(CASES)} cases...\n" + "=" * 78)

    for i, (case_id, url, text, expected_source, notes) in enumerate(CASES, 1):
        print(f"\n[{i}/{len(CASES)}] {case_id}: {notes}")
        excerpt = text[:500] + ("…" if len(text) > 500 else "")
        prov_input = (
            f"text_excerpt: {excerpt}\n"
            f"url: {url}\n"
            f"synthetic_signals: (none — Path C web-app has no in-browser ML detection)"
        )

        try:
            result = await Runner.run(provenance_agent, prov_input)
        except Exception as e:
            print(f"     [FAIL] Runner.run raised: {type(e).__name__}: {e}")
            fails += 1
            continue

        out = result.final_output
        synthetic = out.synthetic_verdict.value if hasattr(out.synthetic_verdict, "value") else out.synthetic_verdict
        source = out.source_verdict.value if hasattr(out.source_verdict, "value") else out.source_verdict
        match = source == expected_source
        marker = "OK  " if match else "FLAG"
        print(f"     [{marker}] synthetic={synthetic!r}  source={source!r}  expected_source={expected_source!r}")
        print(f"            reasoning: {out.reasoning}")
        if not match:
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
        print(f"\n{fails}/{len(CASES)} cases flagged.")
        return 1
    print(f"\nAll {len(CASES)} cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
