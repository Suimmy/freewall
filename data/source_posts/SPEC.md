# ⚠️ DEPRECATED 2026-05-07 — kept for traceability

> Per CLAUDE.md decision #20 (post team-meeting 2026-05-07): team voted to skip 200-post curation. XGBoost training dropped → `backend/app/services/scorer.py` uses weighted-sum formula. **Do not implement this SPEC.** File retained (not deleted) for future reference if direction reverses.
>
> Active curation now: 20 prefilled example posts in `demo/site/examples.json` (Suim curates 8 พ.ค. morning).

---

# Source Posts — Curation SPEC (DEPRECATED)

> Team handbook for collecting **200 viral health-misinformation posts** to train the Sovereignty Score XGBoost model.
>
> **Cutoff**: 2026-05-08 17:00 (1 hour before hackathon kickoff). After this, data is locked.
>
> **Tool**: shared Google Sheets (one per project). See `sheets_setup.md` for setup instructions.

---

## Why we need this

The Sovereignty Score (0–100) is a regression model trained from scratch via XGBoost. The **teacher** (gpt-5.5 with `reasoning=medium`) reads each post, extracts ~17 features, and produces a label score. The **student** (XGBoost) learns to map features → score, deterministically + cheaply at serve time. This is **distillation**, not scratch labelling — XGBoost ≈ gpt-5.5's scoring function, just faster.

The team's job tonight is **collect representative content**. gpt-5.5 does the labelling Phase 2.

---

## Target & cutoffs

| Threshold | Count | Action |
|---|---|---|
| 🚨 Floor — escalate if below | 150 | Notify Suim by 16:00. Switch to Path 2 (add public datasets, accept language drift) or triage fallback (weighted-sum, no ML). |
| ✅ Target | 200 | Proceed with Path 1 (200 manual @ 80/20 Thai/English) |
| ✅ Bonus | 200–500 | Better — `generate_labels.py` will use all |
| 🛑 Cap | 500 | Random subsample if exceeded (label generation cost / time) |

**Cost reminder**: 500 posts × $0.025/post (gpt-5.5 reasoning=medium) ≈ $12.50 for label generation — fits in $80/day cap (decision #17).

---

## Distribution

### By language (target proportion)

- **80% Thai** (~160 posts)
- **20% English** (~40 posts)

This matches the demo content language proportion (Step 6) so XGBoost feature distribution at training time matches what it sees at serving time.

### By category (target counts)

Each category includes a mix of **clearly-misinformation**, **borderline/mixed**, and (for the control group) **clearly-legit** content. XGBoost needs the full 0–100 score range to learn properly.

| Category | Total | Misinfo | Borderline | Legit | Suggested collector |
|---|---|---|---|---|---|
| Anti-vaccine | 30 | 24 | 6 | 0 | Person B |
| Supplements / "miracle cures" | 40 | 32 | 8 | 0 | Person C |
| Cancer myth | 20 | 18 | 2 | 0 | Person D |
| Diet fads | 30 | 18 | 12 | 0 | Person E |
| COVID misinformation | 30 | 28 | 2 | 0 | Person E |
| Mental-health misinformation | 20 | 16 | 4 | 0 | Person D |
| **Legit health (control group)** | 30 | 0 | 0 | **30** | Suim |
| **Total** | **200** | **136 (68%)** | **34 (17%)** | **30 (15%)** | |

### Definitions

- **Misinfo** — clearly false/misleading viral claim (e.g., "vaccines cause autism", "5G spreads COVID", "turmeric cures cancer 100%")
- **Borderline / mixed** — partially-true, exaggerated, or subject to legitimate debate (e.g., "documented vaccine side effects in 0.001% cases", "intermittent fasting weight-loss claims", "some supplements have weak-evidence support")
- **Legit** — high-quality verified content from credible sources (WHO, CDC, Mayo Clinic, Reuters Science, กรมควบคุมโรค, สมาคมแพทย์ไทย, peer-reviewed journalism)

Why include borderline? Real Sovereignty Scores aren't bimodal (low or high) — most content sits in the middle. Borderline samples teach XGBoost the mid-range (40–60).

---

## Where to find content

### Misinfo + borderline (Thai)

- Facebook public groups/pages — anti-vax, alt-med, conspiracy theories. Search Thai: "วัคซีนทำให้ตาย", "หมอไม่บอก", "Big Pharma หลอก"
- Twitter Thai — same keywords, plus "ลดน้ำหนักด่วน", "ขมิ้นชันรักษามะเร็ง", "5G COVID"
- TikTok Thai — health influencers with questionable claims (videos, take description text)
- LINE OpenChat / Pantip — health threads with debunked claims

### Misinfo + borderline (English)

- r/conspiracy, r/AlternativeHealth (Reddit) — public, easy to scrape
- X English health influencers — search "miracle cure", "doctors hate this"
- Snopes / Reuters Fact Check archives — pre-labelled debunked claims (paraphrase the source claim, not the fact-check)

### Legit health (control group) — high-quality

- **Thai** (24): กรมควบคุมโรค Facebook posts, สมาคมแพทย์ไทย, หมอผู้เชี่ยวชาญ verified accounts (เช่น หมอเจี๊ยบ, หมอแล็บแพนด้า ที่อิง evidence)
- **English** (6): @WHO, @CDCgov, @MayoClinic Twitter; Reuters Science section; Bloomberg Health

**For legit posts: paste exact text from the credible source. We need clean-signal high-score examples to anchor XGBoost.**

---

## Per-post deliverable (one row in shared Sheets)

| Column | Field | Required | Example |
|---|---|---|---|
| A | `id` | auto | `post_042` (formula in Sheets) |
| B | `url` | ✅ | `https://facebook.com/.../posts/12345` |
| C | `platform` | ✅ | `facebook.com` |
| D | `author_real` | ✅ (Suim+collector see) | `@some_real_handle` |
| E | `author_anon` | auto | `anon_042` (formula in Sheets) |
| F | `captured_at` | ✅ | `2026-05-07` |
| G | `language` | ✅ | `th` |
| H | `text` | ✅ | (cleaned post body — no UI artifacts) |
| I | `image_urls` | ⛔ optional | `https://img.example.com/1.jpg` (comma-separated if multiple) |
| J | `category_hint` | ✅ | `anti_vaccine` |
| K | `collector` | ✅ | `B` |
| L | `notes` | ⛔ optional | "borderline — partly true side effect claim" |

### Cleaning rules for `text` field

1. **Remove platform UI artifacts** — `See less`, `Like Comment Share`, profile-link garbage like `toresnodp...`
2. **Remove the author name** from inside the text body (we anonymize via column E)
3. **Keep** punctuation, emojis, hashtags, URLs *inside* the post body
4. **Don't translate** — keep original language

### Anonymisation rules

- `author_real` (column D) — record actual handle for verification
- `author_anon` (column E) — auto-generated `anon_NNN` via Sheets formula
- A separate **mapping tab** (`_authors`) is editable by Suim only. Tab keeps `anon_NNN ↔ real handle` for audit.
- **Never commit** real handles to git. The Sheets export → JSONL pipeline drops column D before writing the local JSONL file.

---

## Ethics

- Use **content >= 1 month old** when possible (avoid real-time scraping)
- Never collect private/non-public posts
- Don't redistribute content publicly — internal training use only
- Demo content (`demo/` site) uses **paraphrased / re-curated** versions, not verbatim copies of the training pool

---

## Acceptance criteria — when can we stop?

- [ ] At least **150 rows** filled (floor) — soft target **200**
- [ ] Each category meets ±5 of its target count
- [ ] Language distribution within ±5% of 80/20 Thai/English target
- [ ] All `text` fields cleaned (manual eyeball spot-check 30 random rows)
- [ ] All rows have `category_hint` set
- [ ] Sheets export → CSV → `python data/tools/sheets_to_jsonl.py` succeeds (validates JSONL)
- [ ] `cat data/source_posts/posts_raw.jsonl | jq -c . > /dev/null` exits 0 (valid JSON per line)

---

## Workflow tonight (2026-05-07)

1. **Suim**: create the shared Google Sheets (see `sheets_setup.md` step-by-step), share link with team
2. **Each collector**: open Sheets, fill rows in claimed category until count met
3. **End-of-night**: anyone runs `python data/tools/sheets_to_jsonl.py` to export → validate
4. **Tomorrow morning**: continue if short of target. Hard cutoff **17:00**.
5. **Hackathon Phase 2**: Person E runs `ml/scripts/generate_labels.py`, then `train_scorer.py`, drops `scorer.pkl` into `backend/app/services/`.
