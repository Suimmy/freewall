"""DEPRECATED 2026-05-07 (CLAUDE.md decision #20): no longer used.

XGBoost training dropped — Sovereignty Score is now a weighted-sum formula in
`backend/app/services/scorer.py`. File retained for traceability — do not run.

---

Original purpose:
Train the Sovereignty Score XGBoost regressor.

Reads labelled JSONL produced by generate_labels.py, builds a feature matrix,
trains XGBoost regression, evaluates on a held-out split, writes scorer.pkl.

Status: STUB — Phase 2 hackathon implementation.

Phase 2 implementation outline:
    1. Load labels JSONL → pandas DataFrame
    2. Feature engineering (one-hot encode categoricals, leave NaN for XGBoost native handling):
       - persuasion: count + has_<top_tactic> indicators
       - factcheck: verdict one-hot, citation_count, confidence
       - provenance: synthetic_text/image scores, has_image
       - source_reputation: one-hot
       - category: one-hot top categories
       - user_state: scroll_velocity (gating)
    3. Train/test split (80/20, stratified by category if applicable)
    4. XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.1,
                    objective='reg:squarederror', missing=np.nan,
                    early_stopping_rounds=20)
    5. Eval: R², MAE, sanity-check known high/low risk posts
    6. Print feature importance (used for pitch defense)
    7. Pickle model → output path

Triage fallback (per CLAUDE.md): if XGBoost training fails or is unstable, swap to
hand-tuned weighted sum in backend/app/services/scorer.py — same input/output contract,
no model file needed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True, help="Input labels JSONL")
    parser.add_argument(
        "--output", type=Path, required=True, help="Output pickle path (e.g., backend/app/services/scorer.pkl)"
    )
    parser.add_argument("--test-split", type=float, default=0.2, help="Test set fraction")
    parser.add_argument("--random-seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    print(
        f"[train_scorer] STUB — would read {args.labels} → write {args.output} "
        f"(test_split={args.test_split}, seed={args.random_seed})",
        file=sys.stderr,
    )
    print("[train_scorer] Phase 2 implementation pending.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    import sys
    print("ERROR: train_scorer.py is deprecated (CLAUDE.md decision #20).", file=sys.stderr)
    print("       Sovereignty Score now in backend/app/services/scorer.py (weighted-sum).", file=sys.stderr)
    sys.exit(1)
