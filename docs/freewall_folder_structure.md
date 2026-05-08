# Freewall — Folder & File Structure (Production-grade, Modular)

## Top-level structure

```
freewall/
├── extension/          # Chrome extension (Frontend - Person A)
├── backend/            # FastAPI + Agents SDK (Person B + C + D)
├── ml/                 # XGBoost training + ONNX export (Person E)
├── data/               # Curated corpus, source rep list (Person D + E)
├── demo/               # Demo content + mock site (Person E)
├── shared/             # JSON schemas - single source of truth
├── infra/              # docker-compose, scripts
├── docs/               # Architecture, runbook
└── README.md
```

แต่ละ top-level folder = ขอบเขตชัดเจนให้คนหนึ่งคนเป็นเจ้าของ → ลด merge conflict

---

## `extension/` — Chrome extension (Person A — Frontend)

```
extension/
├── manifest.json
├── package.json
├── tsconfig.json
├── vite.config.ts                 # Vite + @crxjs/vite-plugin
├── src/
│   ├── content/                   # รันบนหน้าเว็บ
│   │   ├── scraper.ts             # DOM extraction
│   │   ├── observer.ts            # IntersectionObserver + MutationObserver
│   │   ├── user-state.ts          # Scroll velocity, dwell time
│   │   ├── injector.ts            # Inject Shadow DOM root
│   │   └── index.ts               # Content script entry
│   ├── background/                # Service worker
│   │   ├── api-client.ts          # Backend POST + SSE listener
│   │   ├── ml-runner.ts           # ONNX runtime in browser
│   │   ├── storage.ts             # chrome.storage wrapper
│   │   └── index.ts
│   ├── ui/                        # React in Shadow DOM
│   │   ├── components/
│   │   │   ├── Annotation.tsx
│   │   │   ├── FactCheckCard.tsx
│   │   │   ├── ScoreBadge.tsx
│   │   │   ├── Sidebar.tsx        # Agent log animation
│   │   │   ├── DecisionPause.tsx
│   │   │   ├── DailyMirror.tsx
│   │   │   └── AskWhyModal.tsx
│   │   ├── hooks/
│   │   ├── styles/
│   │   └── App.tsx
│   ├── popup/                     # Extension popup (Settings)
│   │   ├── SensitivityToggle.tsx
│   │   ├── Overrides.tsx
│   │   └── index.tsx
│   ├── types/
│   │   └── api.ts                 # Generated from shared/schemas/
│   └── lib/
│       ├── debounce.ts
│       └── events.ts
└── public/
    ├── icons/
    └── models/                    # ONNX models (committed or fetched)
        ├── ai-image-detector.onnx
        └── ai-text-detector.onnx
```

**Why this layout**: content/background/ui แยก = Manifest V3 best practice + แต่ละไฟล์ < 200 บรรทัด → debug ง่าย

---

## `backend/` — FastAPI + Agents (Persons B, C, D)

```
backend/
├── pyproject.toml                 # uv หรือ poetry
├── Dockerfile
├── app/
│   ├── main.py                    # FastAPI entry + CORS + lifespan
│   ├── config.py                  # Pydantic Settings (env vars)
│   ├── api/
│   │   ├── deps.py                # Common dependencies
│   │   └── routes/
│   │       ├── perceive.py        # POST /perceive (L1 ingest)
│   │       ├── stream.py          # GET /stream/{session_id} (SSE)
│   │       ├── ask_why.py         # POST /ask-why
│   │       ├── counter.py         # POST /counter-perspective (lazy)
│   │       └── mirror.py          # GET /daily-mirror
│   ├── agents/                    # ⭐ แต่ละ agent = ไฟล์เดียว
│   │   ├── coordinator.py         # Person B
│   │   ├── persuasion.py          # Person C
│   │   ├── fact_check.py          # Person D
│   │   ├── provenance.py          # Person C
│   │   ├── counter.py             # Person C
│   │   ├── classifier.py          # Person B
│   │   ├── tools/                 # Agent tools (function calling)
│   │   │   ├── rag_search.py
│   │   │   ├── web_search.py
│   │   │   └── source_lookup.py
│   │   └── prompts/               # Markdown prompts (iterate without code change)
│   │       ├── persuasion.md
│   │       ├── fact_check.md
│   │       ├── provenance.md
│   │       ├── counter.md
│   │       └── classifier.md
│   ├── schemas/                   # Pydantic models
│   │   ├── perception.py          # L1 output
│   │   ├── reasoning.py           # L2 output
│   │   ├── agents.py              # Per-agent I/O
│   │   └── score.py               # Sovereignty Score
│   ├── services/                  # Business logic
│   │   ├── orchestrator.py        # Coordinator dispatch + parallel exec
│   │   ├── rag.py                 # Chroma client + retrieval
│   │   ├── source_rep.py          # Domain reputation lookup
│   │   ├── scorer.py              # XGBoost loader + predict
│   │   └── sse.py                 # SSE event manager
│   └── core/
│       ├── llm.py                 # OpenAI client + retry/fallback
│       ├── logging.py
│       └── exceptions.py
└── tests/
    ├── test_agents/
    │   ├── test_persuasion.py
    │   └── test_fact_check.py
    └── test_e2e.py
```

**Key pattern**: prompts เป็น `.md` files แยกจาก code → Person C iterate prompt ไม่ต้อง git pull / restart server (load on startup or hot reload)

**Per-agent file = ≤ 100 lines** (definition + tools + glue) → 4 คนเขียน 4 agents พร้อมกันโดยไม่ conflict

---

## `ml/` — Training + Model export (Person E)

```
ml/
├── requirements.txt
├── notebooks/                     # Exploration + training
│   ├── 01_label_generation.ipynb  # GPT-4o → synthetic labels
│   ├── 02_train_xgboost.ipynb     # Train scorer
│   └── 03_eval.ipynb              # Precision/recall on holdout
├── scripts/                       # Productionizable CLI
│   ├── generate_labels.py
│   ├── train_scorer.py
│   └── export_onnx.py             # HF model → ONNX for browser
├── eval/                          # ⭐ SOTA-aligned evaluation
│   ├── persusafety_subset.jsonl   # 50-100 examples from PLUM-Lab/PersuSafety
│   ├── run_persuasion_eval.py     # Run Persuasion Agent on subset
│   ├── compute_metrics.py         # Precision/recall/F1
│   └── results/
│       └── eval_v1_results.json   # Used in pitch slide
├── data/                          # Outputs (gitignored)
│   ├── synthetic_labels.jsonl
│   └── features.parquet
├── models/                        # Trained models (versioned)
│   ├── sovereignty_scorer_v1.pkl
│   └── MODEL_CARD.md              # What it does, accuracy, limitations
└── README.md                      # Reproducibility steps
```

**Why split notebooks vs scripts**: notebook = explore, script = canonical training run → reproducibility

**Why `eval/` folder**: SOTA in this field (DarkPatterns-LLM, PersuSafety, Persuaficial) all publish measured accuracy. Pitch slide ที่แสดง "we measured precision X% / recall Y% on PersuSafety" = defensibility ใน Q&A

---

## `data/` — Corpus + lookup tables (Persons D + E)

```
data/
├── source_reputation/
│   ├── credible.json              # ~100 known credible domains
│   ├── unreliable.json            # ~100 known low-quality
│   ├── ambiguous.json             # mixed
│   └── build_list.py              # Compile from MBFC + Wikipedia
├── corpus/
│   ├── who/                       # Markdown fact sheets
│   │   ├── vaccines.md
│   │   ├── diabetes.md
│   │   └── ...
│   ├── cdc/
│   ├── mayo/
│   ├── chroma_index/              # Built index (gitignored)
│   ├── ingest.py                  # Embed + index → Chroma
│   └── INDEX.md                   # List of topics covered
└── README.md
```

**Why markdown**: easy diff, easy edit, easy embed (chunk by header)

---

## `demo/` — Curated content + mock site (Person E)

```
demo/
├── content/
│   ├── posts.json                 # Index: which posts demo which feature
│   ├── post-001/
│   │   ├── source.html            # Saved post HTML
│   │   ├── screenshot.png
│   │   ├── debunk.md              # Source disproving the post
│   │   └── meta.json              # ai_gen_evidence, viral_metrics
│   └── post-002/...
├── mock-site/                     # Hosts curated content
│   ├── index.html
│   ├── feed.tsx                   # TikTok/IG-like UI
│   ├── posts-loader.ts
│   └── styles/
└── rehearsal/
    ├── script.md                  # Demo script
    └── timing.md                  # Per-act timing target
```

---

## `shared/` — Single source of truth (everyone reads, nobody owns alone)

```
shared/
├── schemas/                       # JSON Schema (language-agnostic)
│   ├── perception.json            # L1 → L2 contract
│   ├── reasoning.json             # L2 → L3 contract
│   ├── agent_io.json              # Per-agent I/O
│   └── README.md
├── codegen.sh                     # Generate TS types + Pydantic from JSON Schema
└── ENUMS.md                       # Shared enums (tactic types, categories, etc.)
```

**ที่นี่คือ single source of truth** — เปลี่ยนตรงนี้ที่เดียว → run `codegen.sh` → generate ทั้ง TS types (ไป extension/) และ Pydantic models (ไป backend/) → guarantee schema sync

ป้องกัน drift: คนหนึ่งเปลี่ยน schema ฝั่งเดียวแล้วลืม sync อีกฝั่ง

---

## `infra/` — DevOps

```
infra/
├── docker-compose.yml             # Backend + Chroma
├── .env.example
└── scripts/
    ├── dev.sh                     # Start backend + watch extension
    ├── build.sh                   # Production builds
    └── seed.sh                    # Build Chroma index from corpus
```

---

## `docs/` — Brief but essential

```
docs/
├── ARCHITECTURE.md                # 3-layer overview
├── AGENT_DESIGN.md                # 6 agents + dispatch logic
├── API_CONTRACTS.md               # Endpoints + schemas
├── RUNBOOK.md                     # Demo day operations + fallback
└── ASSIGNMENTS.md                 # Who owns what
```

---

## Ownership matrix

| Person | Primary folders | Secondary |
|--------|----------------|-----------|
| A — Frontend | `extension/` | shared/schemas (read) |
| B — Backend/Orchestrator | `backend/app/api/`, `backend/app/agents/coordinator.py`, `backend/app/agents/classifier.py`, `backend/app/services/orchestrator.py`, `infra/` | shared/schemas (write) |
| C — Agents (Persuasion, Counter, Provenance) | `backend/app/agents/persuasion.py`, `counter.py`, `provenance.py`, `prompts/` | tests |
| D — Fact-Check + RAG + Data | `backend/app/agents/fact_check.py`, `backend/app/services/rag.py`, `data/corpus/` | data/source_reputation |
| E — ML + Demo | `ml/`, `demo/`, `data/source_reputation/`, ONNX models in `extension/public/models/` | helps integration |

**Total agents**: 6 (Coordinator + Content Classifier in B's column = 2; Persuasion + Counter + Provenance in C's column = 3; Fact-Check in D's column = 1)

---

## Production-grade principles ที่ใช้ตรงนี้

1. **Single source of truth** for schemas (`shared/`) → no drift
2. **Prompts as data** (markdown files) → iterate without code change
3. **One file per agent** → no merge conflict
4. **Services layer separated from API layer** → testable
5. **Notebooks for exploration, scripts for canonical runs** → reproducibility
6. **Demo content versioned with metadata** → defensible in Q&A
7. **Model card** for trained model → explain limitations
8. **`docs/` ที่ essential เท่านั้น** → ไม่ over-document แต่มี runbook สำหรับ demo day
