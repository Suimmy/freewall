# `ml/` — ONNX Model Export + PersuSafety Eval

> ⚠️ **Scope reduced 2026-05-07 per CLAUDE.md decision #20**: XGBoost training dropped (no team curation, weighted-sum scoring instead). Only ONNX export + eval remain.
>
> Owner: Person E (per CLAUDE.md ownership table). Run Phase 2-4 hackathon.

This package handles offline ML work: exporting pretrained HF detectors to ONNX (for in-browser inference) + running mandatory PersuSafety eval. **Backend serves the ONNX models, this package builds them.**

---

## What lives here (2 components after #20 pivot)

| Component | Type | Strategy | Phase |
|---|---|---|---|
| **Synthetic Reality Detectors** (text + image) | Binary classifier | No training — HF pretrained → ONNX export | Phase 2 |
| **PersuSafety eval** | Eval-only (no train) | Run Persuasion Agent on subset, measure P/R/F1 | Phase 4 (mandatory per decision #11) |

**Content Classifier (L1)** is NOT here — it's a `gpt-5.5 reasoning=none` LLM call inside `backend/app/agents/classifier.py` (decision #17).

**Sovereignty Score** is NOT here either — moved to `backend/app/services/scorer.py` as a weighted-sum formula (decision #20). No training, no ML model file.

---

## Run commands

Setup (once):
```bash
cd ml
uv sync                      # install deps into ml/.venv (separate from backend/)
```

### Component 1 — ONNX export (Phase 2)

```bash
# AI text detector — Hello-SimpleAI/chatgpt-detector-roberta (~100 MB → ~30 MB int8)
uv run python scripts/export_onnx.py \
  --hf-model Hello-SimpleAI/chatgpt-detector-roberta \
  --task text-classification \
  --output ../extension/public/models/ai-text-detector.onnx \
  --quantize int8

# AI image detector — umm-maybe/AI-image-detector (~100 MB → ~30 MB int8)
uv run python scripts/export_onnx.py \
  --hf-model umm-maybe/AI-image-detector \
  --task image-classification \
  --output ../extension/public/models/ai-image-detector.onnx \
  --quantize int8
```

### Component 2 — PersuSafety eval (Phase 4 mandatory)

```bash
# Backend must be running on localhost:8000 first
uv run python eval/run_persuasion_eval.py \
  --subset eval/persusafety_subset.jsonl \
  --backend-url http://localhost:8000 \
  --output eval/results.json
```

---

## Deprecated (per #20) — DO NOT run

- `scripts/generate_labels.py` — was for gpt-5.5 batch labelling 200 posts → no longer needed
- `scripts/train_scorer.py` — was for XGBoost training → replaced by `backend/app/services/scorer.py` weighted-sum

These files retain DEPRECATED headers + `sys.exit(1)` to prevent accidental runs. Marked deprecated, not deleted (per Suim — recoverable if direction reverses).

---

## Why a separate `uv` project from `backend/`?

- Deploy bundle: backend doesn't need `transformers` + `optimum` (~400 MB) at runtime — backend only loads the exported ONNX file
- Cold start: ml imports take 10–15 s (transformers); backend boots in 2–3 s
- Lifecycle: ml = export once, backend = serve forever
- Decision #16 (uv only, no conda, no Docker for dev)

---

## Status

- [x] Pre-build scaffold: pyproject + README + script stubs (Step 4 — 2026-05-07)
- [x] Scope reduction per #20 (2026-05-07): XGBoost training out, weighted-sum in `backend/`
- [ ] `uv sync` first time (verifies deps resolve) — pending Suim run
- [ ] Phase 2: run ONNX export → drop into `extension/public/models/`
- [ ] Phase 4: run PersuSafety eval, paste numbers into pitch deck

See `JOURNAL.md` Active TODOs (Phase 2 + Phase 4 sections).

---

## File layout

```
ml/
├── pyproject.toml
├── README.md           ← you are here
├── .gitignore
├── scripts/
│   ├── generate_labels.py    # ⚠️ DEPRECATED per #20 (kept for traceability)
│   ├── train_scorer.py       # ⚠️ DEPRECATED per #20 (kept for traceability)
│   └── export_onnx.py        # ✅ ACTIVE — HF model → ONNX
└── eval/
    ├── README.md
    ├── persusafety_subset.jsonl   # 50-100 examples (Phase 4 populate)
    └── run_persuasion_eval.py     # ✅ ACTIVE — Phase 4 mandatory eval
```
