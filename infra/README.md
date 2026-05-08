# `infra/` — Deploy configs

> **Decision #19 + Suim's pick (2026-05-07)**: Vercel (frontend) + Railway (backend) split.
>
> This folder holds the deploy-platform-specific configs. Code-level config (env files, build commands) lives next to each app.

---

## Architecture

```
┌─────────────────────────────┐         ┌────────────────────────────────┐
│ Vercel (frontend, edge CDN) │         │ Railway (backend, app server)  │
│                             │ fetch + │                                │
│  https://freewall-demo.     │ ◄─SSE──►│  https://freewall-api.         │
│       vercel.app            │         │       up.railway.app           │
│                             │         │                                │
│  Deploys from:              │         │  Deploys from:                 │
│  /demo/site                 │         │  /backend                      │
└─────────────────────────────┘         └────────────────────────────────┘
```

---

## Files

| File | Platform | Used at |
|---|---|---|
| `railway.toml` | Railway | Repo root or `/backend` deploy |
| `vercel.json` | Vercel | Imported via Vercel UI when connecting repo |
| `Procfile.example` | Railway | Optional fallback if Railway can't auto-detect |

---

## Deploy steps (Phase 4 — ~04:00 of 9 พ.ค.)

### Backend (Railway)

1. Connect GitHub repo to Railway: <https://railway.app/new>
2. **Root directory**: `/backend`
3. Railway auto-detects Python via `pyproject.toml` (uv supported in build)
4. Set env vars:
   - `OPENAI_API_KEY=<the $100 credit key>`
   - `FRONTEND_URL=https://freewall-demo.vercel.app` (after Vercel deploys)
   - `USE_MOCK_AGENTS=false` (decision #18 — flip to live LLM)
5. Note the auto-generated public URL (e.g., `freewall-api.up.railway.app`)
6. Add `/health` route monitoring → Railway auto-restart on failure

### Frontend (Vercel)

1. Connect same GitHub repo to Vercel: <https://vercel.com/new>
2. Configure:
   - **Root directory**: `demo/site`
   - **Framework**: Vite (auto-detected)
   - **Build command**: `pnpm build`
   - **Output directory**: `dist`
3. Set env var:
   - `VITE_BACKEND_URL=https://freewall-api.up.railway.app` (paste Railway URL)
4. Deploy → public URL like `https://freewall-demo.vercel.app`
5. Note the URL → paste into Railway's `FRONTEND_URL` env var → redeploy backend

### Verify

```bash
# Backend health
curl https://freewall-api.up.railway.app/health
# Expect: {"status": "ok"}

# Frontend
open https://freewall-demo.vercel.app
# Expect: Twitter-style UI loads, examples chips visible

# End-to-end (paste URL+text in input box → click Analyze)
# Expect: 6 agents activate in sidebar, score appears <5s
```

---

## Cost notes (per CLAUDE.md decision #17)

- **Railway**: $5/month free credit. Estimate: ~8 hours of active runtime per month. **Watch credit on 9 พ.ค. 06:00** — if < $1 remaining, top up $5.
- **Vercel**: Hobby tier free, unlimited bandwidth (within fair use). No credit concern.

---

## Status

- [x] Pre-build scaffold (Step 7 — 2026-05-07)
- [ ] Phase 4: actual deploy (Backend B owns deploy, ~30-45 min total)
- [ ] Phase 5: smoke-test from external network (Suim's phone, mobile data)
