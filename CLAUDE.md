# CLAUDE.md — Freewall

> Cognitive immune system for the post-AGI era. Hackathon project for OpenAI Codex × AIAT (May 8-9, 2026).

This file is the working agreement between human team and Claude Code. Read it first every session.

---

## Project context

**Freewall** is a multi-agent AI defense system that protects users from hyper-personalized AGI persuasion + synthetic content. Form factor: Chrome extension (MVP), with health misinformation as the demo domain anchor.

**Pitch**: "In the post-AGI era, cognitive sovereignty is the new public health."

**Hackathon**: 18 hours of live build (May 8 evening → May 9 morning), 5-person team, demo Saturday afternoon at The Pine Resort.

---

## Source of truth documents

These 6 files are the design spec — Claude Code should defer to them, not re-debate decisions:

| File | What it covers |
|------|----------------|
| `docs/cognitive_impact_taxonomy.md` | Threat taxonomy + why we picked this scope |
| `docs/freewall_architecture.md` | 3-layer + 6-agent design |
| `docs/freewall_demo.md` | Demo script (the build's north star) |
| `docs/freewall_tech_stack.md` | Tech choices + plan B + triage |
| `docs/freewall_folder_structure.md` | File layout + ownership |
| `docs/freewall_sota.md` | ⭐ SOTA survey + Q&A prep + competitor analysis |

If a prompt seems to conflict with these, ask the human — don't assume the docs are wrong.

---

## Hard constraints (non-negotiable)

### Architecture
- **3 layers**: Perception (L1) → Reasoning (L2) → Sovereignty (L3)
- **6 agents** total: Content Classifier (L1) + Coordinator + Persuasion + Fact-Check + Provenance + Counter-Perspective (L2)
- **Multi-agent via OpenAI Agents SDK** by default (LangGraph/CrewAI allowed if a real need surfaces — discuss first)
- **Parallel dispatch** in L2 (not sequential) — that's the latency win

### Stack (locked)
- **Frontend**: Chrome Extension Manifest V3 + React + TypeScript + Tailwind + Shadow DOM
- **Build tool**: Vite + `@crxjs/vite-plugin`
- **Backend**: Python 3.13 + FastAPI + uv (package manager)
- **LLM**: OpenAI API only — **`gpt-5.5`** (single model). Tune cost/quality per agent via `model_settings.reasoning.effort`: `none` (L1 classifier) / `low` (Coordinator routing, Provenance) / `medium` (Persuasion, Fact-Check) / `high` (Counter-Perspective steelman). Use `text.verbosity = "low"` to cap output length. Agents SDK uses Responses API under the hood — get prompt caching + native tools + structured output for free.
- **Vector DB**: Chroma (embedded, local)
- **ML**: scikit-learn + XGBoost
- **In-browser ML**: ONNX Runtime Web

### Stack (default preferences, not banned)
Default to OpenAI Agents SDK + OpenAI API + HF pretrained detectors for speed and optics. But if a task genuinely needs them, the following are allowed — discuss tradeoff with human before adopting:
- LangGraph / CrewAI (if orchestration needs outgrow Agents SDK)
- Open-source LLMs — Llama, Qwen, etc. (if cost, latency, or capability requires it)
- Fine-tuning (if a pretrained model can't hit the bar on a critical path)
- Custom-trained detectors (if HF pretrained doesn't cover the threat)

---

## Decisions already made — DO NOT re-litigate

These were debated and locked. Do not re-open without explicit human request:

1. **Chrome extension as MVP form factor** (mobile/OS roadmap, not now)
2. **Health misinformation as demo domain** (not generic, not finance, not politics)
3. **Real viral posts in mock-hosted site** (not live TikTok scraping, not fully synthetic)
4. **No fake demo content; lazy content-level caching** — never fabricate agent output. Cache pattern (revised 2026-05-07 evening per team meeting + Suim preference for "real API > pre-cache" authenticity): backend `cache.get/set` keyed by `content_id` (sha256 of post text). First request for a given content = REAL agents (~$0.20). Subsequent requests for same content = replay from cache (~$0). For round 1 async judging (#19), demo team warms cache by visiting deployed URL once after Phase 4 deploy → all 10 fixed feed posts cached → judges see "real LLM analysis" replay at zero LLM cost. Live paste box = always real LLM (cache by hash). Replaces earlier "git-committed pre-cache" approach (rejected for being less authentic in pitch story).
5. **6 agents, not more, not less** — locked
6. **Weighted-sum for Sovereignty Score** (XGBoost dropped 2026-05-07 — see #20). Pitch framing: "interpretable, EU AI Act-aligned, transparent formula". XGBoost training scripts marked deprecated (`ml/scripts/{generate_labels,train_scorer}.py`).
7. **RAG with WHO/CDC fact sheets** for Fact-Check agent
8. **Source reputation = hardcoded list** (no API exists for free)
9. **Persuasion taxonomy = PersuSafety 15 + Cialdini 6 hybrid** (SOTA per Liu et al., COLM 2025) — not Cialdini-only
10. **Synthetic Reality Detector = MoA-style ensemble** (multiple HF models combined) — per DFBench MoA-DF (Jun 2025)
11. **Persuasion Agent eval on PersuSafety subset is mandatory** (Phase 4) — for measured accuracy in pitch
12. **Debate mode for high-risk content** (score < 30) is Phase 4 stretch — ED2D-inspired (AAAI 2026)
13. **Product positioning = "Personal Guardian Agent"** (Gartner 2026 trend alignment)
14. **Docs scope**: keep current 6 source-of-truth docs in `docs/` as-is. **Skip** `docs/AGENT_DESIGN.md` (overlaps `freewall_architecture.md` — Layer 2 already lists 6 agents + tools + dispatch). **Create in Step 1** `docs/API_CONTRACTS.md` (human-readable cheatsheet paired with `shared/schemas/`). **Defer to Phase 4-5** `docs/RUNBOOK.md` (demo-day operations) + `docs/ASSIGNMENTS.md` (derived from existing ownership tables) + `docs/CLIP_STORYBOARD.md` (5-min clip script + recording cues, per #19).
15. **Perception scope = viewport-triggered content units** (NOT full-page scrape). Extension's `scraper.ts` defines per-site what a "content unit" is: 1 post on social feeds, 1 article on news sites, 1 AI message on chat sites. **MVP scope = feed-style mock site only** (per decision #3) — article / AI chat / generic web = post-MVP. Schema field `content_id` (not `post_id`) reflects this generality.
16. **Dev env + deployment**: dev uses **uv venv only** — no conda, no Docker for dev (adds overhead without benefit). All Python deps live in `backend/.venv/` (gitignored), never global. **Demo must be a public link** (judges + Codex computer use will access it) — backend deploy target (Railway / Fly.io / Render / Cloud Run, Docker if required by platform) deferred to Phase 4. Extension distribution (Chrome Web Store unlisted vs unpacked ZIP + instructions vs web-app fallback) also Phase 4.
17. **Model + cost strategy** (after gpt-5.5 confirmation, decided 2026-05-07; revised twice 2026-05-07 per #20 + #4 lazy cache): single model `gpt-5.5` via openai-agents SDK (which uses Responses API under the hood). Reasoning tier per agent: `none/low/medium/high`. **Budget**: $100 OpenAI credit (50 + 50 top-up); enforce `per_call_max=$0.30`, `per_day_max=$80`, hard-fail with HTTP 503 + UI banner if exceeded. **Lazy cache** (per #4 + #19): backend caches by content_id; first request = real LLM, subsequent = cache replay. Demo team warms 10 fixed feed posts after deploy (~$2). Caching discipline: **static prefix first, dynamic content last** in every prompt (maximizes prompt-cache hit). **Estimated round-1 cost**: $15-30 over 14h (50 judges × scroll + paste, mostly cache hits). Pitch slide must include "Production economics" section.
18. **Smart pre-build approach + sequential Phase 2** (decided 2026-05-07; revised same day evening): pre-build window does **scaffolding (Step 1-8) + Phase 1 mock-LLM wiring + E2E spine**. Real LLM calls + RAG ingest + agent prompts iteration all wait for May 8 evening kickoff. Pattern: orchestrator splits `_run_mock_pipeline` (USE_MOCK_AGENTS=true) and `_run_live_pipeline` (false). Demo paste box + Twitter UI feed E2E spine works end-to-end with mock data. **Phase 2 is SEQUENTIAL** (revised 2026-05-07 evening): single dev (Suim + Claude) goes step-by-step, not parallel — original 5-owner plan dropped. Time budget OK: 14h hackathon window, ~10-12h Phase 2 budget leaves 2-4h for Phase 3-6. Hackathon rules verified to allow scaffolding/boilerplate prep.
19. **Async judging round 1 structure** (decided 2026-05-07; revised twice 2026-05-07 evening): Round 1 (8am 9 May) = async submission only — team submits 3 deliverables and **goes to sleep, no narration, no Q&A**. Top 5 of 50 advance to round 2 stage pitch (1pm 9 May).
    - **(A) Demo link** — public URL hosting the mock site. **Path C web-app mode = ONLY path** (extension Path B dropped 2026-05-07 evening per team decision: judges won't install extensions, security/friction concern). **UI theme = Twitter-style** (familiar to judges, low onboarding friction). **Layout** (single page): top = input box for paste URL+text + 20 prefilled example chips; below = curated feed 5-10 mock posts; right rail = sidebar with 6 agents + score banner.
    - **Interaction modes**:
      (i) Paste URL+text → manual `Analyze →` → sidebar shows full analysis;
      (ii) Scroll feed → IntersectionObserver triggers analysis when post enters viewport at 50% threshold (one-time per post). Each post gets compact inline annotation when complete; sidebar = "focused" mode (default = paste box; click `📊 See full →` on any post → sidebar refocuses on that post). No race conditions — sidebar never auto-updates on scroll.
    - **Lazy content-level cache** (replaces git pre-cache): backend `/perceive-text` checks `cache.get(content_id)` first. Hit = replay events from cache via SSE. Miss = run real agents (~$0.20) + cache result. **Demo team visits URL after deploy to warm all 10 fixed posts before AIAT submit** (~$2 one-time). Subsequent judges hit cache = $0. Live paste box = always real LLM (cache by text-hash). Total cost estimate: ~$15-30 over 14h judging window (lots of headroom in $100 budget). Authenticity: real agents on first call, deterministic cache replay otherwise.
    - **Scroll trigger semantics**: 50% viewport intersection ratio = TIMING decision only. POST payload always sends FULL post text (from frontend state, not DOM scrape). Viewport % does not affect analysis content.
    - Self-explanatory experience required: onboarding tour overlay + inline tooltips on every domain term + agent expand cards with description + findings. Backend deploy must include auto-restart (no human to recover during async window).
    - **(B) Slide deck** (~10-12 slides, self-readable PDF) — judges read alone. Must include: cover, problem, solution architecture, demo screenshots (fallback if link broken), eval numbers (#11 PersuSafety result), interpretable-formula framing (#20), "Production economics" slide (#17), roadmap, "How to try" link, team, closing tagline.
    - **(C) 5-min recorded clip** (MP4) — pre-recorded pitch-without-stage. Thai voice-over + bilingual captions (Thai + English). Structure: hook (0:30) → problem (1:00) → solution demo screen-recording (2:00) → user agency micro-interactions (1:00) → closing (0:30). Production effort ~6-8h, dedicated owner needed Phase 4-5. See `docs/CLIP_STORYBOARD.md`.
20. **Weighted-sum scoring + no team curation** (decided 2026-05-07, post-meeting): Team voted to skip 200-post curation effort. Drop XGBoost training entirely. Replace with **weighted-sum formula** in `backend/app/services/scorer.py` combining agent outputs (persuasion tactic count, fact-check verdict distribution, source reputation, AI-detection confidences). Manually tuned on demo content. Pitch reframe: from "distillation of gpt-5.5" → **"interpretable transparent scoring, EU AI Act-aligned"**. Ramifications:
    - ❌ Drop: `data/source_posts/*` (SPEC, sheets_setup, example.jsonl), `data/tools/sheets_to_jsonl.py`, `ml/scripts/{generate_labels,train_scorer}.py`, XGBoost dependency. Marked deprecated, not deleted (recoverable if direction reverses).
    - ✅ Keep: `data/corpus/` (Fact-Check RAG), `data/source_reputation/` (Provenance lookup), `ml/scripts/export_onnx.py` (HF AI detectors per #10), `ml/eval/` (PersuSafety mandatory per #11).
    - ✅ Add: input box (URL + text paste) with **20 prefilled examples** (5 topics × 4, 70/20/10 misinfo/borderline/legit split, 80/20 Thai/EN); Twitter-style UI theme.
    - Phase 2 weighted-sum formula example: `score = 100 × (0.30 × (1 - tactic_count/10) + 0.30 × fact_check_score + 0.20 × source_rep_score + 0.10 × (1 - synthetic_image_conf) + 0.10 × (1 - synthetic_text_conf))` — weights tunable Phase 4.
    - Cost win: ~$25 saved from no training → reallocated to live LLM headroom (#17).

---

## Coding conventions

### Python (backend)
- **Python 3.13**, type hints everywhere, `from __future__ import annotations`
- **Pydantic v2** for all schemas — no plain dicts crossing module boundaries
- **uv** for dependencies (`uv add`, `uv sync`)
- **ruff** for lint+format (single tool, no black/isort)
- **Async by default** for I/O — agents, LLM calls, RAG retrieval
- One agent = one file (≤ 100 lines including tools and glue)
- Prompts in `app/agents/prompts/*.md` — load at startup, NOT inline in Python

### TypeScript (extension)
- **Strict mode** (`strict: true`)
- React functional components + hooks only
- Shadow DOM for all overlay UI (don't pollute host page CSS)
- Generated types from `shared/schemas/` — never hand-write API types

### Comments — WHY, not WHAT
```python
# ❌ Don't:
# Loop through agents
for agent in agents:

# ✅ Do:
# Parallel dispatch matters here — sequential would be 4x latency
# and break demo's "live" feel
async with asyncio.TaskGroup() as tg:
    for agent in agents:
```

If the WHAT is non-obvious, the variable/function name is wrong — rename instead of commenting.

### Commits
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- One concern per commit
- Commit message body explains WHY when non-trivial

### Tests
- Don't aim for coverage — aim for **risk reduction**
- Test the Coordinator dispatch logic (high blast radius)
- Test agent output schema parsing (LLM output is unreliable)
- Skip UI snapshot tests (waste time, brittle)

---

## File-level ownership (avoid conflicts)

| Person | Files they own |
|--------|---------------|
| A (Frontend) | `extension/**` |
| B (Backend) | `backend/app/api/**`, `backend/app/agents/coordinator.py`, `backend/app/agents/classifier.py`, `backend/app/services/orchestrator.py` |
| C (Agents) | `backend/app/agents/persuasion.py`, `counter.py`, `provenance.py`, `prompts/persuasion.md`, `counter.md`, `provenance.md` |
| D (Fact-Check) | `backend/app/agents/fact_check.py`, `backend/app/services/rag.py`, `data/corpus/**`, `prompts/fact_check.md` |
| E (ML/Demo) | `ml/**`, `demo/**`, `data/source_reputation/**` |

**Shared (everyone reads, B writes, others propose via PR)**: `shared/schemas/**`

If editing a file outside your column, ask first or open a PR.

---

## Working principles

### When in doubt, prefer:

1. **Working over elegant** — hackathon ships in 18 hours. Premature abstractions kill.
2. **Fallback over fragile** — every external dep needs a plan B (see `freewall_tech_stack.md` §7)
3. **Visible over hidden** — agent activity should be observable in the demo sidebar
4. **Real over fake** — no pre-cached demo content; engineer reliability instead
5. **Honest over impressive** — if a model is unreliable (e.g., AI-text detection), say so in the UI

### Decision protocol when stuck

If Claude Code is unsure between approach A vs B, follow this tree:

1. Does either violate a "Hard Constraint" or "Decisions already made"? → Pick the other.
2. Is one demoably visible in `freewall_demo.md`? → Pick that.
3. Does one have a documented fallback in tech stack? → Pick that (lower risk).
4. Still tied? → Ask the human. Don't guess.

### When to ask vs proceed

**Proceed without asking** if:
- The task is in the source-of-truth docs
- It's writing boilerplate code or scaffolding
- It's data curation following a clear pattern

**Ask first** if:
- Adding a new dependency
- Changing a schema in `shared/`
- Spending > 30 minutes on something not in scope
- A tradeoff has product implications (latency vs accuracy, etc.)

---

## Anti-patterns (DO NOT DO)

1. ❌ Don't add agents beyond the 6 specified
2. ❌ Don't call GPT-4o on every viewport — that's L1's job (cheap classifiers)
3. ❌ Don't make the user state monitor primary detection — it's a gating signal only
4. ❌ Don't put prompts inline in Python — `prompts/*.md` only
5. ❌ Don't import from one agent into another — agents talk via Coordinator
6. ❌ Don't use `localStorage` for cross-domain data — use `chrome.storage`
7. ❌ Don't claim 99% accuracy in demo for AI detection — be honest about model limitations
8. ❌ Don't generate fake demo content — use real viral posts only
9. ❌ Don't add features not in `freewall_demo.md` — every Act 3 second is precious
10. ❌ Don't refactor "for cleanliness" during build phase — only during polish phase

---

## Status tracking

### `JOURNAL.md` (root of repo)

Update after each significant work block. Format:

```markdown
## 2026-05-08 14:30 — [Person/Initials]

**What**: <1 sentence>
**Why** (if non-obvious): <1 sentence>
**Decisions**: <bullets if any>
**Blocking**: <none / what>
**Next**: <what's next>
```

Don't over-journal. One entry per ~2 hours of work or per significant decision.

### Phase tracking

Current build phase is in `JOURNAL.md` header. Phases (from `freewall_folder_structure.md` workflow):

- Phase 0 — Foundation lock (hour 0-1)
- Phase 1 — Mock E2E spine (hour 1-3)
- Phase 2 — Parallel build (hour 3-10)
- Phase 3 — Integration (hour 10-13)
- Phase 4 — Polish + content (hour 13-16)
- Phase 5 — Rehearsal (hour 16-17)
- Phase 6 — Buffer (hour 17-18)

**During Phase 4 onwards, no new features** — only polish + bug fix + demo prep.

---

## Demo-driven priorities

The demo script in `freewall_demo.md` is the **acceptance test**. If a feature isn't in the demo, deprioritize it.

Demo coverage requirements (everything that must work end-to-end):
- 6 agents visible in sidebar
- Inline annotations on 3 main posts
- Fact-check card with WHO source
- Counter-Perspective on click
- Decision Pause on Buy button
- Override + Sensitivity toggle
- Daily Mirror at end

Anything outside this = nice-to-have. Cut without ceremony if behind schedule.

---

## Triage (when behind schedule)

Single source of truth: `freewall_tech_stack.md` §8.

Quick reference: degrade in this order
1. Score: XGBoost → weighted sum
2. Health verifier: RAG → LLM zero-shot
3. Source rep: 200 → 30 domains
4. Counter-Perspective: live → hardcoded fallback message
5. **Never** cut: Persuasion agent quality, multi-agent orchestration, real demo content, annotation UI

---

## Quick start for new Claude Code session

When opening a new session, Claude should:

1. Read this CLAUDE.md (you're doing it now ✓)
2. Read `JOURNAL.md` to understand where the team is
3. Check `git status` and `git log -5` for recent changes
4. Confirm current phase before suggesting work
5. Ask the human "what's the focus right now?" if not obvious

Don't read all 6 source-of-truth docs unless the task requires it — they total ~3500 lines. Reference them on demand.

**Read `freewall_sota.md` BEFORE Q&A prep** — it has citations to use and direct competitor analysis (Aletheia, GPTZero, ED2D, etc.)

---

## Closing

This is a high-velocity, high-stakes 18-hour build. Optimize for **shipping a defendable demo**, not perfection. Every line of code should serve either:
- The demo (`freewall_demo.md`)
- The defensibility in Q&A (e.g., real content, model cards)
- The team velocity (clean structure, good tests on critical paths)

If unsure whether something serves these — it probably doesn't. Cut it.

**Vision**: cognitive sovereignty as new public health. **Execution**: 18 hours, 5 people, 1 working demo.

Let's build.
