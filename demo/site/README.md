# `demo/site/` — Freewall Demo Web App

> Standalone Vite + React + TypeScript + Tailwind app. Deployed to **Vercel** (decision #19 + Suim's pick), talks to FastAPI backend on **Railway**.

This is the **public-facing demo** for round 1 async judging (8am 9 พ.ค.). Judges click a public link, see Twitter-style feed + URL+text input box, paste content → see live agent analysis.

---

## Quick start

```bash
cd demo/site
pnpm install
cp .env.example .env.local        # edit if backend not on localhost:8000
pnpm dev                          # http://localhost:3000
```

Build:

```bash
pnpm build                        # outputs to dist/
pnpm preview                      # serve the build
```

Type-check:

```bash
pnpm typecheck
```

---

## Architecture

```
demo/site/
├── package.json
├── vite.config.ts                 # alias @ → src
├── tsconfig.{app,node}.json       # strict + project refs (Vite template)
├── tailwind.config.js             # Twitter-inspired palette + risk colors
├── postcss.config.js
├── .env.example                   # local: VITE_BACKEND_URL=http://localhost:8000
├── .env.production                # prod: Railway URL (Phase 4 final)
├── index.html
├── public/
│   ├── examples.json              # 🙋 Suim curates 20 examples (8 พ.ค. morning)
│   └── favicon.svg
└── src/
    ├── main.tsx                   # React 18 createRoot
    ├── App.tsx                    # main page layout
    ├── styles.css                 # Tailwind base + component utilities
    ├── components/
    │   ├── InputBox.tsx           # URL + text input + Analyze button + chips
    │   ├── Feed.tsx               # warmup mock posts list
    │   ├── PostCard.tsx           # single Twitter-style post card
    │   └── Sidebar.tsx            # 6 agents pill-list + result panel
    ├── lib/
    │   ├── api.ts                 # POST /perceive-text + SSE stream (stubbed Phase 1)
    │   └── examples.ts            # loadExamples() from public/examples.json
    └── types/
        └── index.ts               # ExamplePost, MockPost, AnalysisResult, etc.
```

---

## Deploy (Phase 4)

Per CLAUDE.md decision #19 + Suim's "Vercel + Railway split" choice:

1. Push to GitHub
2. **Vercel**: Import the repo, set:
   - **Root Directory**: `demo/site`
   - **Framework**: Vite
   - **Build Command**: `pnpm build`
   - **Output Directory**: `dist`
   - **Env var**: `VITE_BACKEND_URL=https://freewall-api.up.railway.app` (set after Railway deploys)
3. Vercel auto-deploys on push to main → public URL like `https://freewall-demo.vercel.app`

---

## Phase 1 / 2 wiring TODOs

Each TODO maps to a `// TODO (Phase 1)` or `// TODO (Phase 2)` in code.

**Backend integration**:
- `lib/api.ts` — replace stubbed `analyzeText()` with real `POST /perceive-text`
- `lib/api.ts` — replace stubbed `openReasoningStream()` with real `EventSource`
- Auto-generated types: when `shared/codegen.sh` is updated to emit into `demo/site/src/types/api.ts`, replace local types

**UI**:
- `App.tsx` — feed posts placeholder → 3-5 real mock posts (Step 6B Suim curates)
- `App.tsx` — pre-cache reasoning state → load from `data/reasoning_cache/` (Phase 4)
- `Sidebar.tsx` — animate agent pills (in/out, "agent_started" pulses)
- `PostCard.tsx` — annotation overlay positioning (currently inline below text)

**Polish (Phase 4 per #19)**:
- Onboarding tour overlay
- Inline tooltips on domain terms ("Sovereignty Score?", "Persuasion?")
- Loading skeleton instead of just text "Analyzing..."

---

## What this is NOT

- ❌ Not the Chrome extension — that lives in `extension/` (Path B optional bonus)
- ❌ Not the backend — that lives in `backend/` (FastAPI on Railway)
- ❌ Not the data layer — corpus + reputation in `data/`

This is the **face the judges see**. Keep it clean, fast, and honest.
