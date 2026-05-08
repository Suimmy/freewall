"""Run the Persuasion Agent against a PersuSafety subset and report P/R/F1.

Status: STUB — Phase 4 hackathon implementation. Decision #11 marks this MANDATORY —
the resulting number goes into the pitch deck as a defensibility metric.

Phase 4 implementation outline:
    1. Load eval/persusafety_subset.jsonl (50–100 examples). Each line:
         {"id": str, "text": str, "ground_truth_tactics": [PersuasionTactic, ...]}
    2. For each row, POST to backend /perceive (must be running on --backend-url):
         { session_id, content_id, url, captured_at, content: { text, ... }, ... }
    3. Subscribe to SSE stream on /stream/{session_id}, collect PersuasionFinding event
    4. Compare detected tactics vs ground_truth_tactics:
         - per-tactic P/R/F1
         - macro-F1 across all 21 tactics
         - Top-3 confusion pairs (tactic A predicted, tactic B was truth)
    5. Write results.json:
         {"sample_size": int, "macro_f1": float, "per_tactic": {...}, "errors": [...]}
    6. Print headline number for pitch deck.

Suggested first row to iterate against (when subset exists):
    {"id": "p001", "text": "Doctors hate this one trick…",
     "ground_truth_tactics": ["scarcity", "authority_appeal"]}
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subset", type=Path, required=True, help="Input JSONL of eval examples")
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Backend base URL (must be running)",
    )
    parser.add_argument("--output", type=Path, required=True, help="Output results.json")
    args = parser.parse_args()

    print(
        f"[run_persuasion_eval] STUB — would read {args.subset}, hit {args.backend_url}, "
        f"write {args.output}",
        file=sys.stderr,
    )
    print("[run_persuasion_eval] Phase 4 implementation pending.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
