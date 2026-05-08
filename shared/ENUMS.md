# Freewall — Shared Enums

> Single source of truth for all enum values. JSON Schemas in `schemas/` reference these by string value.
>
> **Versioning**: this file is v0. Changes require coordination — every enum is consumed by both extension (TS) and backend (Python).

---

## `ContentCategory` — output of Content Classifier (L1)

Used by Coordinator to decide which L2 agents to dispatch (e.g., `meme` skips Fact-Check).

| Value | Meaning | Triggers which L2 agents |
|-------|---------|--------------------------|
| `news` | News article / journalism | Fact-Check, Persuasion, Provenance |
| `ad` | Advertisement / sponsored | Persuasion, Provenance |
| `health_claim` | Medical / wellness claim | Fact-Check, Persuasion, Provenance |
| `social` | Personal post / opinion | Persuasion, Provenance |
| `meme` | Image macro / joke | Provenance only |
| `unknown` | Classifier uncertain | All agents (safe default) |

---

## `PersuasionTactic` — output of Persuasion Agent

Hybrid taxonomy per CLAUDE.md decision #9: **PersuSafety 15** (unethical) + **Cialdini 6** (foundational).

### Cialdini 6 (foundational — neutral persuasion)

Verbatim from Cialdini, *Influence: Science and Practice* (chapter titles, classic 6 — not the 7-principle edition that adds Unity). Order matches book.

| # | Value | Verbatim chapter title | Description |
|---|-------|------------------------|-------------|
| 1 | `reciprocation` | Reciprocation | Free gift creates obligation to return |
| 2 | `commitment_consistency` | Commitment and Consistency | Small yes leads to big yes |
| 3 | `social_proof` | Social Proof | Others are doing it |
| 4 | `liking` | Liking | Familiarity / similarity / attractiveness |
| 5 | `authority` | Authority | Expert / credential / symbol of authority |
| 6 | `scarcity` | Scarcity | Limited time / quantity drives desire |

> Note: literature also commonly uses "Reciprocity" for #1 — same concept, but `reciprocation` matches the book chapter verbatim.

### PersuSafety 15 (unethical) — verbatim from Liu et al., "LLM Can be a Dangerous Persuader" (arXiv 2504.10430, COLM 2025), Table 4

| # | Value | Verbatim label | Short description |
|---|-------|----------------|-------------------|
| 1 | `manipulative_emotional_appeals` | Manipulative Emotional Appeals | Exploiting feelings to bypass reason |
| 2 | `false_scarcity` | False Scarcity | Manufactured limited availability |
| 3 | `deceptive_information` | Deceptive Information | Lies, fabrications, distortions |
| 4 | `bait_and_switch` | Bait and Switch | Promised X, deliver Y |
| 5 | `exploitative_cult_tactics` | Exploitative Cult Tactics | Group-pressure / love-bombing patterns |
| 6 | `guilt_tripping` | Guilt Tripping | Inducing guilt to influence |
| 7 | `fear_mongering` | Fear-mongering | Amplifying threat to drive action |
| 8 | `pressure_and_coercion` | Pressure and Coercion | Forcing compliance |
| 9 | `exploiting_vulnerable_individuals` | Exploiting Vulnerable Individuals | Targeting elderly, ill, grieving, etc. |
| 10 | `creating_dependency` | Creating Dependency | Locking user into reliance |
| 11 | `misrepresentation_of_expertise` | Misrepresentation of Expertise | Fake credentials / authority claim |
| 12 | `social_isolation` | Social Isolation | Cutting target off from outside views |
| 13 | `overwhelming_information` | Overwhelming Information | Drowning the user in data to disable judgment |
| 14 | `playing_on_identity` | Playing on Identity | "People like you do/believe X" |
| 15 | `financial_exploitation` | Financial Exploitation | Extracting money via manipulation |

**Verified**: 2026-05-06, fetched from arXiv HTML v1. Names must match this list verbatim for PersuSafety benchmark eval (Phase 4) to be valid.

### PersuSafety 6 topics (informational, not an enum value)

The paper also defines 6 domains where these strategies are studied. Not encoded as an enum (we use `ContentCategory` instead), but useful context for prompt engineering:

> Interpersonal Relationship · Marketing · Professional Career · Financial · Digital Privacy/Security · Health

Our demo anchor (**Health**) aligns directly with one of the 6 — a defensibility point for Q&A.

---

## `SourceReputation` — output of source rep lookup (L1)

From hardcoded list in `data/source_reputation/` (~200 domains).

| Value | Meaning |
|-------|---------|
| `credible` | Established journalism / institutional (WHO, CDC, Reuters) |
| `mixed` | Some bias / opinion mixed with fact |
| `unreliable` | Known misinfo / low editorial standards |
| `unknown` | Domain not in our list |

---

## `SyntheticVerdict` — output of Provenance Agent (L2)

Aggregates `synthetic_signals` from L1 (ai_text_prob, ai_image_prob, c2pa_present) into a single verdict.

| Value | Trigger |
|-------|---------|
| `likely_human` | All AI-gen probabilities < 0.3, OR C2PA verified human capture |
| `uncertain` | Probabilities 0.3-0.7, OR conflicting signals |
| `likely_ai` | Any modality with prob ≥ 0.7 |

> **Honesty note** (CLAUDE.md anti-pattern #7): never claim 99% accuracy in demo. UI must show this verdict with confidence range.

---

## `FactCheckVerdict` — output of Fact-Check Agent (L2)

| Value | Meaning |
|-------|---------|
| `supported` | RAG retrieval finds matching authoritative source (WHO/CDC/Mayo) |
| `contradicted` | RAG retrieval finds source contradicting the claim |
| `unverifiable` | No relevant source found, OR claim too vague to verify |
| `not_a_claim` | Content has no factual claim to verify (e.g., pure opinion) |

---

## `ScoreBand` — derived from Sovereignty Score (0-100)

Set by Coordinator. Drives UI severity + Counter-Perspective auto-run.

| Value | Range | UI behavior | Counter-Perspective |
|-------|-------|-------------|---------------------|
| `safe` | 70-100 | Subtle / no annotation | Lazy (on user click) |
| `caution` | 30-69 | Warning annotation | Auto-run (per architecture.md) |
| `high_risk` | 0-29 | Alert annotation + Decision Pause eligible | Auto-run + **debate mode** (Phase 4 stretch) |

---

## `SensitivityMode` — user setting (L3)

User chooses how aggressive the system is. Stored in `chrome.storage`.

| Value | Threshold shift | Default annotations |
|-------|-----------------|---------------------|
| `light` | +20 to score before banding | Only `high_risk` shown |
| `standard` | No shift | `caution` + `high_risk` shown |
| `strict` | -20 to score before banding | All bands shown |

> **Why this enum exists**: CLAUDE.md decision #L3 — "Override + Sensitivity" is anti-paternalism. User agency is part of the pitch.

---

## `AnnotationSeverity` — UI annotation level

| Value | Visual | When |
|-------|--------|------|
| `info` | Blue dot, no auto-popup | `safe` band, but tactic detected |
| `warning` | Yellow underline | `caution` band |
| `alert` | Red highlight + sidebar pulse | `high_risk` band |

---

## Extension protocol

When adding a new value to any enum:

1. Add it here with description
2. Update `schemas/*.json` if the enum is referenced
3. Re-run `codegen.sh` to regenerate TS types + Pydantic models
4. Note the change in `JOURNAL.md` (schema changes are decisions worth tracking)

When **removing** or **renaming** a value: never silently — coordinate with all consumers (extension + backend + ml/eval).
