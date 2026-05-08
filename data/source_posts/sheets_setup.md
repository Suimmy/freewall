# ⚠️ DEPRECATED 2026-05-07 — kept for traceability

> Per CLAUDE.md decision #20 (post team-meeting): team voted to skip 200-post curation. **Do not create this Sheet.** File retained for traceability only.
>
> Active curation: 20 prefilled example posts in `demo/site/examples.json` (Suim curates directly, no Sheets workflow needed).

---

# Google Sheets Setup — Step-by-step (DEPRECATED)

> Suim creates this once tonight. ~10 minutes.
>
> Output: shared Sheet that team uses concurrently to collect 200 posts. End-of-session export → CSV → `python data/tools/sheets_to_jsonl.py` produces `posts_raw.jsonl`.

---

## Step 1 — Create the Sheet

1. Go to https://sheets.google.com → **+ Blank**
2. Rename file: **"Freewall Source Posts (Tier 1)"**
3. Rename Tab 1 from "Sheet1" to **`posts`**
4. Add Tab 2 (➕ icon at bottom-left) named **`_authors`**

---

## Step 2 — Set up the `posts` tab columns

In the **`posts`** tab, paste this header into row 1 (cells A1 through L1):

| A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `id` | `url` | `platform` | `author_real` | `author_anon` | `captured_at` | `language` | `text` | `image_urls` | `category_hint` | `collector` | `notes` |

### Add formulas to A2 and E2 (autofill)

In **A2**: paste this formula then drag down to row 501 (so up to 500 posts auto-id):

```
=IF(B2="", "", CONCAT("post_", TEXT(ROW()-1, "000")))
```

In **E2**: paste this formula then drag down to row 501:

```
=IF(D2="", "", CONCAT("anon_", TEXT(ROW()-1, "000")))
```

This means: as soon as someone fills column B (url), `id` auto-generates. As soon as they fill column D (author_real), `author_anon` auto-generates.

---

## Step 3 — Add data validation (dropdowns)

This catches typos and forces consistent values.

### Column C — `platform` dropdown

1. Select cells **C2:C501**
2. Menu: **Data → Data validation → + Add rule**
3. **Criteria**: "Dropdown" → enter values (one per line):
   ```
   facebook.com
   x.com
   reddit.com
   tiktok.com
   instagram.com
   line
   web
   ```
4. Save

### Column G — `language` dropdown

1. Select **G2:G501**
2. Same flow — values:
   ```
   th
   en
   ```

### Column J — `category_hint` dropdown

1. Select **J2:J501**
2. Values:
   ```
   anti_vaccine
   supplement
   cancer_myth
   diet_fad
   covid_misinfo
   mental_health_misinfo
   legit_health
   ```

### Column K — `collector` dropdown

1. Select **K2:K501**
2. Values:
   ```
   B
   C
   D
   E
   Suim
   ```

### Column F — `captured_at` date validation (optional but recommended)

1. Select **F2:F501**
2. Data validation → **Criteria: Is valid date**

---

## Step 4 — Conditional formatting (warnings)

These highlight rows that need attention.

### Highlight rows with empty `text` (column H)

1. Select **A2:L501**
2. Menu: **Format → Conditional formatting → + Add rule**
3. **Criteria**: Custom formula:
   ```
   =AND($B2<>"", LEN($H2)<50)
   ```
   (means: row has a URL but text is shorter than 50 chars)
4. Format style: light red background
5. Done

### Highlight duplicate URLs

1. Select **B2:B501**
2. Conditional formatting → Custom formula:
   ```
   =COUNTIF($B$2:$B$501, B2) > 1
   ```
3. Format style: light yellow background
4. Done

---

## Step 5 — Set up the `_authors` tab (mapping table — Suim only)

In the **`_authors`** tab, paste header into row 1:

| A | B |
|---|---|
| `author_anon` | `author_real_handle` |

This is the audit trail. Suim copies `author_anon` and `author_real` columns from the `posts` tab into here for safekeeping. **This tab is not exported to JSONL** — it stays in the Sheet only.

---

## Step 6 — Permissions

1. Top-right **Share** button
2. Add team emails (B, C, D, E) as **Editor**
3. Important: **uncheck** "Notify people" if you don't want spam
4. **Set protection on the `_authors` tab**: Tab right-click → "Protect sheet" → "Set permissions" → "Restrict who can edit this range" → "Only you" → Done

---

## Step 7 — Test before sharing

Add 1 example row in `posts` (same as `data/source_posts/example.jsonl` post_001):

| Column | Value |
|---|---|
| B (url) | `https://example.com/fake/post/1` |
| C (platform) | `facebook.com` |
| D (author_real) | `@example_user` |
| F (captured_at) | `2026-05-07` |
| G (language) | `th` |
| H (text) | `ข่าวด่วน! หมอไม่อยากให้คุณรู้ว่า ขมิ้นชันรักษามะเร็งได้ 100% รีบสั่งยาเสริมอาหาร $99 ก่อนถูกห้ามขายตลอดกาล!` |
| J (category_hint) | `supplement` |
| K (collector) | `Suim` |
| L (notes) | `setup test row — delete after team starts` |

Verify:
- Column A auto-fills `post_001`
- Column E auto-fills `anon_001`
- Dropdowns work in C, G, J, K
- Save the Sheet (auto-saves)

Once verified, **delete this test row** so team starts at empty rows.

---

## Step 8 — Share the link in team chat

Share message template:

```
🎯 Freewall data collection — Tonight target: 200 posts

🔗 Sheets URL: [paste link here]
📋 Spec: data/source_posts/SPEC.md (read this first)
⏰ Cutoff: 2026-05-08 17:00 (Friday afternoon, 1h before hackathon)

Your category assignments:
  Person B: anti_vaccine 30 + COVID? — Thai-focus
  Person C: supplements 40 — Thai-focus
  Person D: cancer myth 20 + mental health 20 — Thai-focus
  Person E: diet fads 30 + COVID misinfo 30 — mixed
  Suim:    legit_health 30 (control group)

Distribution per category: ~80% misinfo + ~15-20% borderline/mixed
(or for legit_health: 100% high-quality verified content from WHO/CDC/Mayo/กรมควบคุมโรค/etc.)
```

---

## Step 9 — End-of-session export

When team finishes (target 200 collected):

1. **Suim**: in Sheets — **File → Download → Comma-separated values (.csv)**
2. Save as `data/source_posts/posts_raw.csv` (gitignored already)
3. From repo root:
   ```bash
   cd data/tools
   python sheets_to_jsonl.py
   ```
4. Output: `data/source_posts/posts_raw.jsonl` (also gitignored)
5. Validate:
   ```bash
   cat ../source_posts/posts_raw.jsonl | jq -c . > /dev/null && echo "✓ valid JSONL"
   wc -l ../source_posts/posts_raw.jsonl
   ```
6. Phase 2 hackathon: Person E uses `posts_raw.jsonl` as input to `ml/scripts/generate_labels.py`.

---

## Troubleshooting

- **Sheets formula not auto-filling**: drag the formula cell's bottom-right blue dot down to row 501 manually
- **Dropdown shows "Invalid"**: re-check spelling matches the validation list exactly (case-sensitive)
- **Duplicate URL not highlighting**: confirm conditional formatting range is `$B$2:$B$501` (with dollar signs)
- **Can't share with team**: check Google Workspace policies (some orgs block external sharing)
