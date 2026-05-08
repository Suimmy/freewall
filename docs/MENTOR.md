# Freewall — Mentor Consultation Doc

---

## 1. overview

**agi cognitive impact**
Hyper-personalized persuasion
Synthetic reality
Dopamine engineering
Echo chamber
Pure deskilling
Agency erosion
Parasocial AI bonding

**Freewall** = cognitive immune system for the post-AGI era. Multi-agent AI defense ที่ปกป้อง user จาก hyper-personalized AGI persuasion + synthetic content.

**Form factor**: Chrome extension MVP + web app (demo) · **Domain anchor**: health misinformation · **Market**: Thai-first, globally scalable

**Tagline**: *"In the post-AGI era, cognitive sovereignty is the new public health."*

---

## 2. Architecture (3-layer / 6-agent)

```
Layer 1 — Perception (cheap classifier, every viewport)
└── Content Classifier (gpt-5.5 reasoning=none) → category + confidence

Layer 2 — Reasoning (parallel dispatch, on-demand)
├── Coordinator (low) — decides which specialists fire
├── Persuasion (medium) — PersuSafety+Cialdini taxonomy, 21 tactics
├── Fact-Check (medium) — RAG against WHO/CDC corpus
├── Provenance (low) — domain reputation lookup + AI-detection
└── Counter-Perspective (high + WebSearchTool) — steelman alternative view

Layer 3 — Sovereignty (user-facing)
└── Weighted-sum Sovereignty Score (0-100, 3 bands: safe/caution/high_risk)
    + inline annotation + sidebar + "Daily Mirror" reflection
```

**Key design choice**: parallel dispatch in L2 (asyncio.TaskGroup) — sequential would be 4x latency, kills "live" demo feel.

**Stack**: OpenAI Agents SDK (Responses API under the hood) + Python 3.13/FastAPI + React/TS Chrome MV3 + Chroma RAG + scikit/ONNX. Single model `gpt-5.5` with reasoning tiering per agent (cost optimization).

**Path forward (locked decisions)**:
- Phase 3: BGE-M3 on-device embeddings (kills OpenAI embedding lock-in)
- Phase 2.17: ONNX in-browser AI detection (data doesn't leave device)
- Year 2: open-source LLM fallback (Llama 3.3 / Qwen-Thai / SeaLLM)

---

## 3. Agent details

| Agent | Layer | Role | Model | Reasoning | Tools | Input | Output | Cost/call |
|---|---|---|---|---|---|---|---|---|
| **Classifier** | L1 | Categorize content (news/ad/health_claim/social/meme/unknown) | gpt-5.5 | `none` | none | `text` | `{category, confidence}` | ~$0.001 |
| **Coordinator** | L2 | Decide which L2 specialists to dispatch | gpt-5.5 | `low` | none | `{content_id, category, confidence}` | `{dispatched: [...], skipped: [...]}` | ~$0.006 |
| **Persuasion** | L2 | Detect manipulation tactics from 21-tactic taxonomy (PersuSafety 15 + Cialdini 6 hybrid) | gpt-5.5 | `medium` | none | `{text, category}` | `{tactics_detected: [{tactic, evidence, confidence}], intended_action, hidden_agenda}` | ~$0.012 |
| **Fact-Check** | L2 | Extract claims (max 3), verify via RAG against WHO/CDC corpus, return verdict per claim | gpt-5.5 | `medium` | `rag_search(query, k)` | `{text, category, url}` | `{claims: [{claim, verdict, evidence_quote, sources: [{title, url, publisher}]}]}` | ~$0.064 |
| **Provenance** | L2 | Domain reputation lookup + ai-text/image detection passthrough | gpt-5.5 | `low` | `source_lookup(url_or_domain)` | `{text, url, has_image}` | `{source_reputation_category, synthetic_text_verdict, synthetic_image_verdict, ai_confidences}` | ~$0.011 |
| **Counter** | L2 | Live web search + steelman alternative view (only when score < 50) | gpt-5.5 | `high` | `WebSearchTool` (built-in) | `{text, category, prior_findings}` | `{alternative_view, sources, perspective_summary}` | ~$0.130 |

**Algorithms / approach**:
- **Persuasion**: rule-driven prompt (no few-shot, per overfit lock) — 21-tactic verbatim taxonomy + category-specific weighting + commercial-intent rules (Rule 1+2+3: price+product+CTA → financial_exploitation; +unsupported claim → deceptive_information; +regulated drug → misrepresentation_of_expertise)
- **Fact-Check**: dual-language rag_search (Thai query + English translation) — mitigates 10-20% cross-language gap of `text-embedding-3-small`. Header-based H2 chunking (not char-window) preserves semantic units.
- **Provenance**: 68-domain hardcoded reputation list (35 credible / 13 mixed / 20 unreliable) — no public API exists for free. AI-text/image detection deferred to ONNX Phase 2.17.
- **Sovereignty Score** (weighted-sum, interpretable): `100 × (0.30 × persuasion_safety + 0.30 × fact_check_score + 0.20 × source_trust + 0.10 × (1-image_AI) + 0.10 × (1-text_AI))`. Persuasion saturates at 5 tactics. Source unknown=0.2 (skeptical baseline).

**Eval numbers (current state)**:
- 61 unique smoke cases across 6 agents (8-case × 4-dim per Phase 2 testing standard: happy/adversarial/edge/honest-false-negative)
- 55 pytest pass + 2 skipped
- Persuasion adversarial prompt-injection resistance verified
- Fact-Check dual-language Thai→EN cross-search verified
- Latency ~10-15s end-to-end per post (parallel L2 dispatch)
- Cost ~$0.20/post real LLM, ~$0/post on cache replay
- **Pending**: PersuSafety formal eval (50-100 examples, mandatory pre-pitch per CLAUDE.md decision #11)

---

## 4. SOTA comparison — "Why not just ask GPT-9?"

**The honest answer**: GPT-9 alone CAN do most of this — but trades off in 5 dimensions where Freewall wins.

| Dimension | GPT-9 monolithic | Freewall multi-agent |
|---|---|---|
| **Latency** | 8-15s sequential reasoning | 10-15s with 4 parallel specialists (could be 3-5s with eager dispatch) |
| **Cost** | $0.30-0.50/post (high reasoning) | $0.20/post → $0.06 Year 1 → $0.0006 Year 3 (17 optimization techniques) |
| **Source citations** | Hallucinates URLs ~15-30% (2025 benchmarks) | RAG-grounded with verified WHO/CDC sources |
| **Calibration** | One-size-fits-all confidence | Per-agent confidence + interpretable weighted-sum (EU AI Act-aligned) |
| **User control** | Black-box answer | Per-tactic transparency, threshold tunable, override loggable |

**Plus** — capabilities GPT-9 monolithic CANNOT do:
- Counter-Perspective with **live web search** (steelman from current sources, not 2026-frozen knowledge)
- Provenance via **deterministic domain lookup** (not LLM-recall, no hallucination)
- **Cross-language Thai-EN dual-search RAG** (LLM monolithic conflates languages)
- **In-browser ONNX detection** (data sovereignty — content never leaves device)
- **Tier-aware routing** (free user = 2 agents, paid = 6) — economic feasibility for Thai market

### vs direct competitors (per `docs/freewall_sota.md`)

| Player | What they do | Gap we fill |
|---|---|---|
| **Anthropic Guardian** (rumored 2026) | General-purpose multi-agent safety | Domain-specific health + Thai-localized + sovereignty-framed |
| **GPTZero / Originality** | AI-text detection only | Full pipeline: detection + persuasion + fact-check + counter |
| **NewsGuard** | Domain reputation only | Adds persuasion + claims + counter perspective |
| **Aletheia** | Cybersec deepfake detection | Wellness/health framing + cognitive sovereignty thesis |
| **ED2D (AAAI 2026)** | Debate-mode belief revision (+23%) | Adopt as Year 1 stretch (Counter-Perspective debate mode) |

**Positioning**: "Personal Guardian Agent" (Gartner 2026 trend) for cognitive sovereignty under personalized AI persuasion — narrower than Anthropic Guardian, deeper than fact-checkers.

---

## 5. Open questions for mentor

> Listed in priority order. Mentor's hour is precious — if time-limited, focus on Q1-Q3.

**Q1 — Architecture: 6 agents or fewer?**
Coordinator + 4 specialists + Counter = 6. Could collapse Provenance + Fact-Check into 1 "Source-and-Claim" agent? Tradeoff: simpler vs. less interpretable per layer. We chose 6 for transparency (EU AI Act alignment) but want senior NLP eye on whether dispatch overhead justifies separation.

**Q2 — Persuasion taxonomy granularity (21 tactics)**
PersuSafety 15 + Cialdini 6 hybrid. Tested 9-case smoke shows good detection but unknown precision/recall vs PersuSafety formal eval. Concerns:
- Are 21 tactics the right cardinality? Year 2 plan = expand to ~50 (AI-era + culturally-Thai). Too granular too soon?
- Confidence calibration: agent emits 0.0-1.0 but never been calibrated against ground truth. Should we use Platt scaling / temperature scaling Year 1?

**Q3 — Cross-language RAG strategy**
Current: Fact-Check agent prompt instructs dual rag_search (Thai query + English translation), then merge. Mitigates ~10-20% cross-lingual embedding gap of `text-embedding-3-small`. Phase 3 plan: swap to BGE-M3 (multilingual, on-device).
- Is this prompt-level workaround acceptable? Or should we move to translation-augmented retrieval (TAR) at retrieval layer, not prompt layer?
- BGE-M3 + cross-encoder rerank — worth Phase 3 effort vs Year 2 polish?

**Q4 — Sovereignty Score: weighted-sum vs distillation**
Locked Phase 1: weighted-sum (interpretable, transparent, EU AI Act-aligned). Earlier plan was XGBoost distillation of gpt-5.5 (decision #6 → dropped #20). Question for mentor: was dropping XGBoost the right call? Tradeoff:
- Weighted-sum: interpretable + tunable + no training data needed BUT manually calibrated, may not generalize
- XGBoost distillation: better calibration BUT needs labeled corpus (~200 posts curation, dropped due to time)
- Year 2 revisit: active-learning loop from user-override patterns?

**Q5 — ถ้า GPT-9 เป็น AGI จริงในอนาคต Freewall ยังจำเป็นมั้ย? (ไม่แถ)**

**Honest TL;DR**: Pure-capability moat collapses. Structural moat may grow. Niche shrinks if users don't value sovereignty.

**Capability moats ที่หาย** (ยอมรับตรงๆ):
- Persuasion detection / fact-check / counter-perspective — GPT-9 ทำได้ใน 1 zero-shot prompt
- Multi-agent orchestration — กลายเป็น over-engineering ถ้า single-prompt AGI เก่งพอ
- 21-tactic taxonomy — AGI สังเคราะห์ taxonomy ที่ดีกว่าได้เอง
- Cross-language RAG, structured output, calibrated confidence — built-in capabilities

**Structural moats ที่ยังอยู่ (อาจแข็งแกร่งขึ้น)**:

1. **Conflict of interest** — GPT-9 ถูก train โดย OpenAI/Anthropic ที่มี engagement/safety incentives ของตัวเอง ≠ incentive ของ user. การ "ถาม AGI ของแพลตฟอร์มว่า platform กำลัง manipulate คุณมั้ย" = asking the fox to guard the henhouse. Freewall = independent third-party agent ที่ทำงานให้ user

2. **Trust mediation (cross-vendor adversarial alignment)** — industry trend "AI evaluating AI" (Constitutional AI, RLAIF) แต่ทั้งหมดเป็น *same-vendor self-evaluation*. Post-AGI ต้องมี separate entity ประเมิน AGI's output ด้วย independent incentive — Freewall = cross-vendor adversarial layer

3. **Data sovereignty** — Thai PDPA / EU AI Act high-risk จะ MANDATE local-first AI สำหรับ healthcare/finance/political decisions. AGI cloud-only ใช้ไม่ได้ในบาง vertical regardless of capability. Freewall มี on-device path (BGE-M3 + ONNX + Year 2 open-source LLM fallback)

4. **Interpretability requirement** — EU AI Act + Thai sectoral regs ต้องการ third-party auditable framework, ไม่ใช่ self-explanation จาก same model. Weighted-sum scoring + per-tactic transparency = compliance-by-design ที่ AGI black-box ทำไม่ได้

5. **Personalization asymmetry** — AGI's personalization คือ THREAT ไม่ใช่แค่ tool. AGI รู้ vulnerability ของ user ดีกว่าตัวเขาเอง (training data scale + behavior tracking). Freewall = user's personal proxy ที่ถือ context AGAINST AGI — asymmetric defense (one-vs-many) against asymmetric attack (many-vs-one)

**Pitch reframe (ไม่แถ)**:
> "We don't compete with AGI's *reasoning*. We compete with AGI's *trust position*. Post-AGI world ต้องการ agent ที่ทำงานให้ YOU, ไม่ใช่ทำงานให้ owner ของ AGI."

**Honest risks**:
- ถ้า users ไม่ value sovereignty (เคยชินกับ "trust the platform") → mass market shrinks. Niche = regulated industries + privacy-conscious + sovereign govts only.
- ถ้า Big Tech AGI ได้รับ regulatory mandate จากรัฐ ("safety AI must be operator-trusted") → squeezed
- ถ้า cross-vendor adversarial alignment กลายเป็น standard pattern → อาจมีคนอื่นทำได้เยอะ, ความ unique หาย

**Year 1 wedge implication**: Thai gov B2G + EU regulated sectors > mass consumer. Pricing structure (49-99 THB consumer + B2G primary) อยู่บนสมมติฐานนี้แล้ว.

**Question for mentor**:
- ใน 5 structural moats ข้างบน — defensible regardless of AGI capability มั้ย? มี blind spot ที่เราพลาด?
- "Cross-vendor adversarial alignment" เป็น defensible pattern หรือเป็น commodity ในอนาคต?
- ถ้า Thai gov mandate ใช้ Big Tech AGI ตามคำสั่งสหรัฐ/จีน — wedge สำหรับ sovereign AI shrink เร็วแค่ไหน?

**Q6 — Counter-Perspective evaluation**
Counter-Perspective uses WebSearchTool + reasoning=high (~$0.13/call, most expensive). Smoke shows agent finds Mayo/NIH/ACS/ADA/BMJ + Thai sources. But "quality of steelman" is subjective:
- How to evaluate? Human-in-loop review? Win-rate vs random search?
- ED2D paper shows debate mode = +23% belief revision. Adopt for high-risk content (score < 30) as Year 1 stretch?

**Q7 — Dataset strategy for Year 2 evaluation**
Currently 0 labeled training data (XGBoost dropped). PersuSafety has English subset for eval but no Thai. Options for Year 2:
- Crowdsource Thai labeling (cost / quality concerns)
- Active learning from user-override events (long ramp-up)
- Synthetic data via gpt-5.5 (rejected for circular dependence per JOURNAL)
- Adopt PUBHEALTH / CoAID public datasets (English only, distribution shift risk)

**Q8 — B2B compliance leg: Year 1 parallel หรือ Year 2-3 react-to-signal?**

**Honest concern**: post-AGI consumer leg has only ~30-50% survival probability (per Q5 honest analysis — users may simply trust Big Tech AGI). B2B AI compliance/audit (regulated industries forced by EU AI Act enforcement 2026 + Thai PDPA medical) has ~80%+ survival, with concrete enterprise buyers emerging now ($50k-500k contracts).

**The tradeoff**:
- **Year 1 parallel B2B motion** — start enterprise sales alongside consumer build. **Pros**: hedge AGI risk early; capture EU AI Act enforcement window before competitors; B2B contracts subsidize consumer freemium tier. **Cons**: dilutes 5-person team focus; hackathon team is consumer-shaped (UX/demo, not sales motion); SOC 2 + customer success + 6-9mo enterprise sales cycles incompatible with hackathon timeline
- **Year 2-3 react-to-signal** — build optionality only (multi-agent + RAG + taxonomy already reusable as audit framework). Pivot weight when AGI capability signals trigger (3/4 from Q5). **Pros**: stay focused now; lower execution risk; demo + grants = clean Year 1 narrative. **Cons**: may miss EU enforcement window if it bites earlier than expected; second-mover disadvantage if Anthropic/OpenAI partner-ecosystem captures audit niche first

**Question for mentor**:
- For 5-person team with $1-3M Year 1 grant trajectory + 70-80% consumer market survival NOW + 30-50% post-AGI — which is the right tradeoff?
- Are there models from companies who pivoted form factors mid-stream (e.g., PolyAI consumer→enterprise, Cohere LLM-API→B2B-RAG) that we should learn from?
- Is "build consumer leg + parallel B2B audit pilot from Year 1" achievable with our team size, or hubris?

---

## 6. What we want from mentor

**Primary**: 30-min review of architecture + 7 open questions → flag biggest risk we're underweighting

**Secondary**: connections to:
- Thai gov public-health stakeholders (DDC / สสส. / NBTC) for B2G Year 1
- Foundation grants ($1-3M target Year 1)
- PersuSafety researchers (Liu et al., COLM 2025) for taxonomy collaboration

**Not seeking**: code review, demo polish feedback (covered internally), or long-term roadmap (Year 3+ speculative)

---

## 7. Quick links / proof points

- Pitch demo: `[deploy URL — pending Phase 4]`
- Architecture spec: `docs/freewall_architecture.md`
- SOTA survey + competitor analysis: `docs/freewall_sota.md`
- Build journal (single-source-of-truth state): `JOURNAL.md`
- Real eval numbers: 61 smoke cases / 55 pytest / $2.33 spent of $100 budget
- Hackathon: OpenAI Codex × AIAT, 8-9 พ.ค. 2026, The Pine Resort
