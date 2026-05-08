# Freewall — Pitch Deck Outline

> Async round-1 submission deck (PDF, judges read alone). 13 slides target.
> Team can work parallel — each slide marked with **owner** + **data dependency**.
>
> Style: 1 thesis per slide, dense readable, Q&A weapons at bottom.
> Tone: direct + honest + technically credible. NOT marketing fluff.

**Hackathon**: OpenAI Codex × AIAT, 2026-05-08 → 09 · The Pine Resort
**Round 1**: 2026-05-09 8am async PDF submission · Top 5 → 1pm stage pitch
**Format**: 16:9 · ~12-15 slides · self-readable PDF (no narration aid)

---

## Deck-level brief (read-once context for team)

**Problem**: post-AGI era, AGI-personalized persuasion + synthetic content erodes user cognitive sovereignty. Mass scale, asymmetric (AGI knows you, you don't know AGI's incentives).

**Solution**: Freewall = 3-layer / 6-agent multi-agent defense system. Browser-native (Mode 1 paste + Mode 2 feed scroll). 21-tactic persuasion taxonomy + RAG fact-check + counter-perspective with live web sources + interpretable Sovereignty Score. Single model gpt-5.5 with reasoning tiering.

**Wedge**: Thai health misinfo MVP. Year 1 expand ASEAN; Year 2-3 Sovereign AI fallback (BGE-M3 + open-source LLM); Year 1 B2G primary revenue.

**Defensibility post-AGI**: structural moats (conflict-of-interest, cross-vendor adversarial alignment, data sovereignty, interpretability, personalization asymmetry) — not capability competition.

**3 judging criteria added 2026-05-08**: Thai → globally scalable / tech war defensible / Thai-affordable. All 3 addressed via dedicated slides.

---

## Slide-by-slide outline

### Slide 1 — Cover

**Purpose**: brand + tagline + 3-second positioning

**Content**:
- Logo: 🛡️ Freewall (or designed icon)
- Tagline: *"Cognitive sovereignty is the new public health"*
- Subline: Multi-agent defense for the post-AGI era
- Team names + roles (5 people)
- Hackathon: OpenAI Codex × AIAT 2026

**Visual**: minimal, single-color background, 1 hero image (e.g., shield + brain glyph)
**Q&A weapon**: tagline = direct answer to "what's the elevator pitch"

---

### Slide 2 — Problem

(writing)
**Purpose**: ground judges in WHY this matters now (post-AGI urgency)

**Content** (3 layers of cognitive erosion):
1. **Hyper-personalized persuasion** — AGI knows your vulnerabilities better than you do (training data + behavior tracking)
2. **Synthetic reality** — AI-generated text/image/video at scale, indistinguishable from real
3. **Engagement business model + AGI = compounding harm** — platforms have no incentive to defend cognitive autonomy

**Real numbers** (use only verified):
- WHO 2024-2025 reports: health misinformation = global infodemic crisis
- Thai context: viral health misinfo on FB/LINE → measurable cancer treatment delay (Mahidol-Rama 2024 study)
- AGI personalization 2026 = Black Mirror in production (cite specific examples if found)

**Visual**: 3 panels (persuasion / synthetic / asymmetry)
**Q&A weapon**: "Why now?" answered immediately
**Data dependency**: Suim verifies Mahidol-Rama citation specifics

---

### Slide 3 — Solution at-a-glance

(architect view)
**Purpose**: 1-glance architecture comprehension. Can't get here without this slide working.

**Content**:
- 3-layer diagram top-to-bottom:
  - **L1 Perception** (cheap, every viewport): Classifier
  - **L2 Reasoning** (parallel dispatch, on-demand): Coordinator + Persuasion + Fact-Check + Provenance + Counter-Perspective
  - **L3 Sovereignty** (user-facing): Sovereignty Score (0-100) + inline annotation + sidebar + Daily Mirror
- Annotations:
  - "21-tactic taxonomy (PersuSafety + Cialdini hybrid)"
  - "RAG against WHO/CDC/Mahidol corpus"
  - "Live web search via OpenAI Responses API"
  - "Interpretable weighted-sum scoring (EU AI Act-aligned)"
- Single model: `gpt-5.5` with reasoning tiering (none/low/medium/high)

**Visual**: clean architecture diagram, color-coded by layer (blue / purple / amber)
**Q&A weapon**: "How does it work?" answered in 30s
**Data dependency**: pull from `docs/freewall_architecture.md`

---

### Slide 4 — Live demo (screenshot or QR)

(demo prep + screenshot capture)
**Purpose**: prove it's real, not slideware

**Content**:
- 3 screenshots side-by-side:
  - Mode 1 paste box (Suim's sibutramine or curcumin)
  - Mode 2 feed mock posts with inline annotations
  - Sidebar: per-agent timing badges + score banner + Counter-Perspective card
- 1 line: "Try it: [demo URL] — 6 agents analyze in ~10-15s (cached: ~1s)"
- QR code to demo URL
- Cost transparency: "$0.20/post real LLM, $0/replay (95% cache hit at scale)"

**Visual**: 3 screenshot grid, browser frame, real Thai content visible
**Q&A weapon**: "Does it actually work?" — visible proof
**Data dependency**: Phase 4 deployed URL + 1 cached real result + screenshot

---

### Slide 5 — Defensibility & Eval numbers

(data + numbers)
**Purpose**: technical credibility — we measured, we tested, we're honest

**Content**:
- **61 unique smoke cases** across 6 agents (8-case × 4 dimensions: happy / adversarial / edge / honest false-negative)
- **55 pytest pass + 2 skipped**
- **PersuSafety eval**: [pending Phase 4 — fill once run]
- **Per-agent latency** (post-optimization): Classifier 5s / Coordinator 4s / Persuasion 30s / Fact-Check 60-85s / Provenance 10s / Counter 120s
- **Cost economics**: $2.51 Phase 2 (97.5% headroom of $100 budget) → $0.20/post real → $0.06 Year 1 → $0.0006 Year 3
- Adversarial robustness verified:
  - Prompt injection in content text → Persuasion + Fact-Check both resist
  - Honest false-negative on grief / Fed news → no over-flagging
  - Cross-language Thai-EN dual rag_search → WHO English chunks reachable from Thai claims

**Visual**: numbers grid, sources cited (PersuSafety paper, WHO corpus, Mahidol)
**Q&A weapon**: "How do we know it's accurate?" — concrete numbers + adversarial tests
**Data dependency**: PersuSafety eval result (pending Phase 4)

---

### Slide 6 — Algorithm & Agent Improvement Roadmap

(architect)
**Purpose**: show post-MVP technical debt + plan honestly

**Content** (5 layers, each with 6-12mo improvement plan):

| Layer | Today | Year 1 plan | Year 2-3 |
|---|---|---|---|
| **Scoring** | Weighted-sum (interpretable) | Active learning from user overrides | XGBoost distillation revival + personalized vulnerability weighting |
| **Corpus** | 69 chunks header-based | 500+ chunks, EN/TH parity | Recursive H3 splitting + tiered metadata (peer-reviewed > authority) |
| **RAG** | text-embedding-3-small | BGE-M3 on-device + BM25 hybrid | Cross-encoder rerank (BGE/Cohere) + multi-hop reasoning |
| **Agents** | 21 tactics, rule-driven | PersuSafety eval + 21→50 tactics (AI-era + culturally Thai) | Agent self-correction ensemble + ED2D debate-mode |
| **Provenance** | 68 hardcoded domains | + author-level signals (verified ≠ trustworthy) | 5K+ via MBFC API + C2PA + reverse image search + fine-tuned Thai detectors 65→90% F1 |

**Pitch frame**: "Each layer maps to 1-3 papers' worth of headroom — focused 6-12mo execution plan, not wish list"

**Visual**: 5-row table, year columns, color-coded progress bars
**Q&A weapon**: "What's missing?" — we already named it ourselves
**Data dependency**: pull from JOURNAL Phase 4 detailed roadmap

---

### Slide 7 — Cost Trajectory: 333x in 3 Years

(data + economics)
**Purpose**: production economics judges WILL flag

**Content**:
- **4-tier cost trajectory**:
  - Today demo: $0.20/post (research mode)
  - Year 1: $0.06/post (cache + L1 filter + reasoning tier + BGE-M3 + tier-aware routing)
  - Year 2: $0.006/post (+ L1 distillation + open-source LLM fallback + federated cache)
  - Year 3: $0.0006/post (+ on-device + L2 distillation + edge inference)
- **17 cost optimization techniques** (8 existing ✅ + 9 new 🆕):
  - Year 1 (9): lazy cache 95%, L1 filter 70%, selective dispatch 20-40%, prompt caching 50-70%, reasoning tiering 40%, IntersectionObserver gate 60-80%, 🆕 BGE-M3 on-device, 🆕 speculative early termination 15-25%, 🆕 tier-aware routing 50-70% on free tier
  - Year 2 (6): L1 distillation 99%, in-browser ONNX 100% detection, 🆕 open-source LLM fallback 80%, 🆕 federated claim cache 30-50%, 🆕 SimHash dedup 20-40%, 🆕 streaming partial response
  - Year 3 (5): L2 distillation 95%, quantization INT8/INT4 50-75%, 🆕 edge inference WASM 80%, 🆕 IndexedDB browser cache 10-20%, 🆕 time-tier batch pricing 50% free

**Visual**: cost-per-post line chart $0.20→$0.0006 over 3 years + 17-technique table
**Q&A weapon**: "Why 95% cache hit possible?" → power-law social viral content / "Distillation feasible Year 2?" → industry-standard pattern (DistilBERT etc.)
**Data dependency**: Phase 4 actual cache hit rate from demo session

---

### Slide 8 — Unit Economics: Viable for Thailand

(commercial + Thai market)
**Purpose**: criterion 3 affordability — Thai-realistic pricing

**Content**:
- **Pricing matrix Thai market** (NOT $9.99 USD):
  - Free: 5 fresh posts/day (generous tier, unlimited cache hits)
  - Pro: **99 THB/mo** (10 fresh/day)
  - Family: 199 THB/mo (3 accounts)
  - B2G citizen-license: sponsored
- **Benchmark anchor**: Netflix Thai 99 THB / Spotify Thai 129 THB / YouTube Premium Thai 159 THB → Freewall Pro **same tier as standard Thai subs** (NOT $9.99 USD ≈ 360 THB which is 3-4x off)
- **Unit economics math**:
  | User behavior | Posts/mo | Year 1 cost | Year 2 cost | THB/mo viable |
  |---|---|---|---|---|
  | Light (10/day) | 300 | 648 THB | 65 THB | ❌ Y1 / ✅ Y2 |
  | Power (50/day) | 1,500 | 3,240 THB | 324 THB | ❌ both |
  | Average (5/day, 80% cache) | 30 fresh | 65 THB | 6.5 THB | ✅ both |
- **Year 1 revenue mix**: 50% foundation grants / **30% B2G Thai (Year 1 primary, NOT Year 2)** / 15% B2C Pro / 5% Enterprise
- **"Cognitive sovereignty as public health"** = policy hook for B2G subsidy from DDC + สสส. + NBTC

**Visual**: pricing matrix table + cost-vs-Thai-income breakeven chart
**Q&A weapon**: "Why 99 THB profitable Y1?" → cache + tier-aware routing + most users average not power / "B2G feasibility Y1?" → public-health budget exists, framing aligns NBTC/DDC/สสส.
**Data dependency**: validate Thai gov funding pool ($1-3M target) — Suim research

---

### Slide 9 — Thai-First, Globally Scalable

(writing)
**Purpose**: criterion 1 — counter "you're a local Thai project" objection

**Content**:
- **Universal vs Localized matrix**:
  | Universal (any market) | Localized per market |
  |---|---|
  | Multi-agent architecture | Source reputation list (68 → 5K per region) |
  | PersuSafety+Cialdini taxonomy | Demo content seeds |
  | RAG corpus structure | Embedding model (BGE-M3-thai vs multilingual) |
  | Weighted-sum scoring formula | Language-specific persuasion subtactics |
  | Sovereignty Score band logic | Cultural framing of authority/scarcity |
- **Market expansion timeline**: Thailand 2026 → ASEAN 2027 (Vietnam/Indonesia same WHO infodemic crisis) → Global 2028 (English-first markets)
- **Why Thailand first**:
  - Ground truth via WHO/DDC/Mahidol clearest
  - 80% Thai users: ZERO English-first defense tools available
  - Regulatory friendly to public-health framing
  - Funding pool exists (gov + foundations)

**Visual**: 2-column matrix + 3-step expansion timeline
**Q&A weapon**: "Why not start English market?" → less defensible wedge (Newsguard/GPTZero/Aletheia compete) / "Architecture lock-in to Thai?" → no, taxonomy is universal psychology, swap embeddings + corpus per market

---

### Slide 10 — Sovereign AI: Independence by Design

(architect)
**Purpose**: criterion 2 tech war — counter "you're an OpenAI wrapper" objection

**Content**:
- **3-tier autonomy spectrum**:
  1. **Today (cloud-only)**: gpt-5.5 + OpenAI embeddings + WebSearchTool — fast hackathon validation
  2. **Year 1 hybrid**: 🆕 BGE-M3 on-device embeddings (Phase 3 elevated) + 🆕 in-browser ONNX detection (Step 2.17) — kills OpenAI embedding bill + AI-detection cost + sovereignty story
  3. **Year 2 full open-source fallback**: Llama 3.3 / Qwen-Thai / SeaLLM — sensitive content premium tier stays cloud, routine analysis self-hosted
- **"Sovereign AI" framing**: Freewall is NOT downstream of US Big Tech — it's a defense LAYER user can swap LLM providers under. Aligns Thai gov "Sovereign AI" agenda (NBTC + DEPA priorities 2026)
- **Counter-narrative**: "Big Tech engagement business model conflicts with cognitive sovereignty — they CAN'T build this. We CAN run on their infra OR independently."
- **Production economics tie-in**: Year 2 LLM swap not just for sovereignty — also kills $80% cloud LLM cost on routine content

**Visual**: 3-tier ladder (cloud → hybrid → full sovereign) with cost reduction overlay
**Q&A weapon**: "What if OpenAI 10x prices?" → BGE-M3 already kills embeddings Y1; LLM fallback Y2 / "Air-gapped mode possible?" → Y2 yes / "Why won't Anthropic Guardian eat your lunch?" → general-purpose ≠ domain-specific health + Thai-localized + sovereignty-framed
**Data dependency**: BGE-M3 swap proof-of-concept (Phase 3 if elevated)

---

### Slide 11 — Roadmap & Rollout

(commercial)
**Purpose**: judges WILL ask "what's the plan beyond hackathon?"

**Content**:
- **Year 1 (B2C wedge + B2G primary)**:
  - Chrome extension free + Path C web app
  - Health misinfo anchor → 1 vertical of cognitive sovereignty
  - Foundation grants $1-3M (Hewlett, Knight, Mozilla, Open Society)
  - **B2G Thai Year 1 primary** — DDC + สสส. + NBTC public-health budget
  - PersuSafety eval published, blog announcement
- **Year 2 (vertical expansion + B2B)**:
  - Add finance/political/romance scams (cognitive sovereignty extends to financial)
  - B2B regulated industries pilot (compliance/audit framework)
  - BGE-M3 + open-source LLM live in production
  - 50-tactic taxonomy expansion + culturally-Thai subset
- **Year 3+ (platform partnerships)**:
  - OS-level integration tier (Apple, Google, Samsung)
  - Sovereign AI fallback default for sensitive content
  - 5K-domain reputation list via MBFC API
  - C2PA verification widely adopted in industry

**Visual**: 3-column timeline with milestones + revenue mix evolution
**Q&A weapon**: "Why won't Meta build this?" → engagement business model conflict / "Different from fact-checkers?" → full pipeline detection + persuasion + counter, not just claims
**Data dependency**: cite specific grant programs we're targeting

---

### Slide 12 — Commercialization & Moats

(commercial)
**Purpose**: revenue model + defensibility for skeptics

**Content**:
- **4 revenue streams**:
  1. B2C Freemium: Free + **Pro 99 THB/mo (Thai)** + Family 199 THB
  2. B2B Enterprise: $5-15/seat/mo for healthcare orgs / fact-checkers / Thai universities
  3. **B2G citizen-license** (Year 1 primary): per-citizen sponsored by Thai gov public-health budget
  4. Foundation grants Year 1: $1-3M target (Hewlett, Knight, etc.)
- **5 moats**:
  1. **Data** — tactic library compounds via user override patterns (active learning)
  2. **Trust** — privacy-first vs platform opacity (Big Tech can't claim independence)
  3. **Regulatory** — EU AI Act explainability + Thai sovereign AI alignment + per-tactic transparency
  4. **Speed** — sub-2s real-time on cache-hit (95% at scale)
  5. **Independence** — counters Meta/X engagement model (they won't build this)
- **Q&A weapons summary**:
  - "Why won't Anthropic Guardian threat?" → general-purpose ≠ domain-specific
  - "LLM cost?" → 17-technique trajectory $0.20 → $0.0006 over 3 years
  - "Why now?" → AGI personalization at scale 2026, regulatory window EU AI Act enforcement
  - "Extension or app?" → both planned, web app = Path C primary for hackathon (lower friction)

**Visual**: revenue waterfall + 5-moat shield diagram
**Q&A weapon**: condensed prepared answers for every objection

---

### Slide 13 — Vision: Cognitive Sovereignty Beyond Healthcare

(writing) + (taxonomy expansion)
**Purpose**: 5-year horizon — show this is bigger than current MVP

**Content**:
- **2-axis expansion table** (taxonomy depth × domain breadth):
  - **Year 1**: 21 tactics × Health misinfo
  - **Year 2**: + AI-era tactics × Wellness + Mental health + Financial sovereignty
  - **Year 3**: + Culturally-Thai tactics × Civic + Relational sovereignty
  - **Year 4+**: + Agentic-era tactics (compromised AI assistants) × Cognitive sovereignty in agentic web
- **Unifying thread**: in every domain, **agency erodes when mass-customized persuasion exploits THIS user's specific vulnerabilities**
- **Boundary clarity (what we DON'T do)**:
  - Pure cybersec (Aletheia / 1Password) ✗
  - Generic news bias (Newsguard / GPTZero) ✗
  - Productivity (ChatGPT / Claude) ✗
  - Only **"sovereignty under personalized AI persuasion"** ✓
- **Counter-narrative angle**: "Verified ≠ trustworthy — verified crypto scams, verified MLM, verified deepfake-political. Production-grade evaluation = behavioral data over time + bio-claim cross-reference, NOT blue-check trust."
- **Honest answer to "what about post-AGI?"** (from MENTOR.md Q5): pure capability moat collapses, structural moats (independence, sovereignty, interpretability, asymmetry) grow. We compete with AGI's **trust position**, not its **reasoning**.

**Visual**: 4×4 expansion grid + boundary diagram (what we are vs what we aren't)
**Q&A weapon**: "Why start health not finance/political?" → ground truth clearest via WHO/DDC, finance = legal liability, political = censorship risk → health = safest beachhead

---

### Slide 14 — Closing / CTA

(final)
**Purpose**: memorable last impression

**Content**:
- Tagline (large): *"In the post-AGI era, cognitive sovereignty is the new public health."*
- 3-line summary:
  - 🛡️ Multi-agent defense against AGI-personalized persuasion
  - 🇹🇭 Thai-first wedge, globally scalable architecture
  - 🤝 Sovereign AI by design — independent of Big Tech alignment
- Demo URL + QR code (large)
- Contact: team email / Twitter / GitHub
- "Try it live: [URL]"

**Visual**: tagline dominant, minimal else, single CTA
**Q&A weapon**: nothing — this is closure not Q&A

---

## Owner mapping summary (for parallel work)

| Slide |  | Data dependency |
|---||---|
| 1 Cover |  | logo + team |
| 2 Problem |  | Mahidol-Rama citation |
| 3 Solution |  | architecture doc |
| 4 Demo |  | Phase 4 deploy URL + screenshots |
| 5 Eval |  | PersuSafety eval (pending) |
| 6 Algorithm Roadmap |  | JOURNAL Phase 4 roadmap |
| 7 Cost Trajectory |  | 17 techniques table (in JOURNAL) |
| 8 Thai Pricing |  | gov funding research |
| 9 Thai-First Global |  | universal/local matrix |
| 10 Sovereign AI |  | BGE-M3 PoC if elevated |
| 11 Rollout |  | grant program research |
| 12 Commercialization |  | competitor pricing benchmark |
| 13 Vision |  | taxonomy expansion plan |
| 14 Closing |  | demo URL + final tagline |

---

## Pre-flight checklist (before round 1 submission)

- [ ] All 14 slides ≤ 12pt body text (judges read alone — must be readable)
- [ ] No emoji-overload (1-2 per slide max — readability over fun)
- [ ] Every number has a source cited at slide bottom
- [ ] Q&A weapons section on relevant slides (5, 7, 8, 10, 12, 13)
- [ ] PDF tested on different screen sizes (judges may use mobile)
- [ ] Demo URL works + cached posts ready (Phase 4.1 warm-cache routine done)
- [ ] Screenshots are CURRENT (not placeholder)
- [ ] Pricing in THB AND USD reference (judges may include international)
- [ ] No "TBD" / "coming soon" text — replace with "Year 1 plan" if needed

---

## What this deck is NOT

- ❌ Sales pitch fluff
- ❌ Animated transitions or stage-pitch theatrics (round 1 = static PDF)
- ❌ Tech-only deck (criterion 3 affordability + criterion 1 globally-scalable need business slides)
- ❌ Vague vision — every claim has a measured number or specific plan
- ❌ Defensive (don't apologize for limitations — frame as honest roadmap)

## What this deck IS

- ✅ Self-readable (judges WITHOUT narration must understand)
- ✅ Honest (real numbers, real limitations acknowledged)
- ✅ Defensible (Q&A weapons embedded throughout)
- ✅ Thai-first but globally credible
- ✅ Tech + business + vision balanced
