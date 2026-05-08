"""DEPRECATED 2026-05-07 (CLAUDE.md decision #20): no longer used.

XGBoost training was dropped after team voted out 200-post curation. Sovereignty Score
now computed via weighted-sum formula in `backend/app/services/scorer.py`.
File retained for traceability — do not run.

---

Original purpose:
Generate synthetic Sovereignty Score labels via gpt-5.5.

Reads viral health-misinfo posts (JSONL), calls gpt-5.5 with reasoning_effort=medium
to score each 0–100 + extract structured features, writes labelled JSONL.

Status: STUB — Phase 2 hackathon implementation. Argparse only for now.

Phase 2 implementation outline:
    1. Load posts JSONL (one post per line) — see data/source_posts/SPEC.md format
    2. Build a system prompt with the scoring rubric (persuasion tactics, claim
       verifiability, source signals, etc.). Static prefix → cache hit per CLAUDE.md
       decision #17.
    3. For each batch of N posts, call OpenAI with response_format=json_schema for
       structured output: {label_score: int, features: {...}, reasoning: str}
    4. Write labels JSONL (one line per post): {post_id, label_score, features, reasoning}
    5. Print summary: mean score, std, distribution by category_hint

Cost estimate (Phase 2):
    200 posts × ~$0.025/post = ~$5 (well within $80/day cap)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Input JSONL of raw posts")
    parser.add_argument("--output", type=Path, required=True, help="Output JSONL of labels")
    parser.add_argument("--model", default="gpt-5.5", help="OpenAI model name")
    parser.add_argument("--batch-size", type=int, default=10, help="Posts per API call")
    args = parser.parse_args()

    print(
        f"[generate_labels] STUB — would read {args.input} → write {args.output} "
        f"(model={args.model}, batch_size={args.batch_size})",
        file=sys.stderr,
    )
    print("[generate_labels] Phase 2 implementation pending.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    import sys
    print("ERROR: generate_labels.py is deprecated (CLAUDE.md decision #20).", file=sys.stderr)
    print("       XGBoost training scope dropped. See file docstring.", file=sys.stderr)
    sys.exit(1)
