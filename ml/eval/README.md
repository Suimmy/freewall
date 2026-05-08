# `ml/eval/` — PersuSafety Persuasion Agent Evaluation

> **Phase 4 mandatory** per CLAUDE.md decision #11. Result number goes into the pitch deck as a defensibility metric.

---

## Why this matters

Liu et al. (PersuSafety, COLM 2025, arXiv:2504.10430) is the SOTA benchmark for evaluating LLM-based persuasion detection. Running our `persuasion` agent on a subset of their dataset gives us:

1. A measured precision / recall / F1 number — beats hand-wavy "feels accurate"
2. Direct comparison to published baselines (Liu et al. report numbers we can match against)
3. Q&A defense: "We evaluated on PersuSafety and scored X% F1 across the 21 tactics."

---

## Methodology

1. **Subset selection**: 50–100 examples drawn from `PLUM-Lab/PersuSafety` on HuggingFace Datasets
2. **Stratified by tactic**: cover all 21 PersuasionTactic enum values (CLAUDE.md decision #9)
3. **Run the agent**: backend `/perceive` endpoint with each example's text → collect detected tactics
4. **Compare**: detected tactics ∩ ground-truth tactics → P/R/F1 per tactic + macro-average
5. **Output**: `eval/results.json` with metrics + qualitative error categories

---

## Files in this folder

| File | Purpose |
|---|---|
| `README.md` | This file |
| `persusafety_subset.jsonl` | 50–100 examples (currently empty — populated Phase 4) |
| `run_persuasion_eval.py` | Eval script (currently stub) |

---

## Run

Backend must be running locally first:
```bash
cd ../backend && uv run uvicorn app.main:app --reload &
```

Then run eval:
```bash
cd ml
uv run python eval/run_persuasion_eval.py \
  --subset eval/persusafety_subset.jsonl \
  --backend-url http://localhost:8000 \
  --output eval/results.json
```

Inspect `results.json` → paste headline number into pitch deck.

---

## Acceptance criteria for "done"

- [ ] `persusafety_subset.jsonl` has 50–100 examples (stratified across 21 tactics)
- [ ] `run_persuasion_eval.py` runs end-to-end and writes `results.json`
- [ ] Macro-F1 reported in `results.json`
- [ ] Top-3 confused tactics surfaced in qualitative analysis
- [ ] Pitch slide shows the number with proper disclosure (sample size, methodology)
