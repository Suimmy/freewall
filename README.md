# Freewall — Cognitive Defense System

> **Personal Guardian Agent for the post-AGI era.** Multi-agent AI defense against hyper-personalized persuasion + synthetic content. Hackathon project for OpenAI Codex × AIAT (May 8-9, 2026).

**Pitch**: *"In the post-AGI era, cognitive sovereignty is the new public health."*

---

## Quick links

- [`CLAUDE.md`](CLAUDE.md) — working agreement + 20 locked decisions (read first)
- [`JOURNAL.md`](JOURNAL.md) — build log + Active TODOs (read second)
- [`docs/freewall_demo.md`](docs/freewall_demo.md) — demo script (the north star)
- [`docs/CLIP_STORYBOARD.md`](docs/CLIP_STORYBOARD.md) — 5-min clip script (decision #19 deliverable)
- [`docs/freewall_sota.md`](docs/freewall_sota.md) — SOTA + Q&A prep + competitor analysis

---

## Repository layout

```
freewall_project/
├── CLAUDE.md                — Working agreement (read first)
├── JOURNAL.md               — Build log
├── README.md                — You are here
├── shared/                  — JSON schemas + ENUMS (TS + Python codegen)
│   ├── schemas/             — perception.json, reasoning.json, agent_io.json
│   ├── ENUMS.md             — ContentCategory / PersuasionTactic / etc.
│   └── codegen.sh           — emits to extension/src/types/ + backend/app/schemas/
├── backend/                 — FastAPI + 6 agents (Python 3.13 + uv)
│   ├── app/
│   │   ├── main.py          — FastAPI lifespan
│   │   ├── api/routes/      — /perceive, /perceive-text, /stream, /ask-why, ...
│   │   ├── agents/          — classifier, coordinator, persuasion, fact_check,
│   │   │                       provenance, counter (one file each)
│   │   │   ├── prompts/     — agent prompts as .md (load at startup)
│   │   │   └── tools/       — rag_search, source_lookup, web_search
│   │   ├── services/        — orchestrator, rag, scorer (weighted-sum), sse
│   │   └── core/            — llm, budget, cache, logging, exceptions
│   └── tests/               — pytest, 14 passing
├── demo/site/               — Vite + React + TS public demo (Vercel target)
├── extension/               — Chrome MV3 extension (Path B optional bonus)
├── ml/                      — ONNX export + PersuSafety eval (XGBoost dropped per #20)
├── data/                    — corpus (RAG), source_reputation (lookup),
│                              reasoning_cache (Phase 4 pre-cache)
├── docs/                    — architecture, demo, tech_stack, sota, clip_storyboard
└── infra/                   — railway.toml + vercel.json (deploy configs)
```

---

## Setup

### Prerequisites

- **Python 3.13** (managed by uv — `uv python install 3.13`)
- **Node.js 20+** + **pnpm 11+**
- **uv** for Python package management

### Backend

```bash
cd backend
uv sync
cp .env.example .env             # set OPENAI_API_KEY
uv run uvicorn app.main:app --reload   # http://localhost:8000
uv run pytest                          # 14 passing
```

### Demo site (Vite)

```bash
cd demo/site
pnpm install
cp .env.example .env.local       # VITE_BACKEND_URL=http://localhost:8000
pnpm dev                          # http://localhost:3000
pnpm build                        # outputs to dist/
```

### Extension (Chrome MV3, Path B optional)

```bash
cd extension
pnpm install
pnpm build                        # outputs to dist/
# In Chrome: chrome://extensions → Load unpacked → select extension/dist
```

### ML (ONNX export only — XGBoost dropped per decision #20)

```bash
cd ml
uv sync
# Phase 2: export HF AI detectors → extension/public/models/*.onnx
# Phase 4: PersuSafety eval mandatory
```

---

## Architecture (high-level)

```
Layer 1 — Perception (~80 ms)
  Content Classifier → category (health_claim, ad, social, news, meme, unknown)
                              │
                              ▼
Layer 2 — Reasoning (~3 s, parallel via asyncio.gather)
  Coordinator → dispatch decision
       │
       ├─ Persuasion        (LLM only, taxonomy in prompt)
       ├─ Fact-Check        (LLM + rag_search → Chroma)
       ├─ Provenance        (LLM + source_lookup + ONNX in browser)
       └─ Counter-Persp.    (LLM + WebSearchTool)
                              │
                              ▼
Layer 3 — Sovereignty
  scorer.py weighted-sum → 0-100 score → annotation overlay
```

Single LLM = `gpt-5.5` via OpenAI Agents SDK. Reasoning effort tier per agent: `none/low/medium/high`.

---

## Round 1 deliverables (8am 9 พ.ค. — async judging per decision #19)

| Deliverable | Where | Status |
|---|---|---|
| **A) Demo link** (Vercel + Railway) | `demo/site/` deployed | scaffold ready, deploy Phase 4 |
| **B) Slide deck** (10-12 slides PDF, self-readable) | not in repo | Phase 4 |
| **C) 5-min clip** (MP4 with bilingual captions) | `docs/CLIP_STORYBOARD.md` | scaffold script ready, record Phase 4 |

Round 2 (1pm 9 พ.ค., top 5 only) = stage pitch with same materials + Q&A.

---

## Locked decisions (don't re-debate)

See `CLAUDE.md` "Decisions already made" section. Highlights:

- 6 agents (not more, not less)
- gpt-5.5 single model, $100 budget, per-call $0.30 cap
- 5 demo topics: เบาหวาน / มะเร็ง / ลดน้ำหนัก / อาหารเสริม / ความดัน-หัวใจ
- Weighted-sum scoring (no XGBoost training, no team curation per #20)
- Async judging round 1 with Path C web-app mode mandatory
- Twitter-style UI theme

---

## License

Hackathon-private. Not for redistribution.
