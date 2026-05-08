# `data/` — local data assets

> Most contents are gitignored for privacy. **Specs + example fixtures are the committed surface.**

---

## Subfolders

| Folder | Purpose | Status |
|---|---|---|
| `source_posts/` | Raw curated viral posts (target 200) for ML training | spec ready, posts pending team curation tonight |
| `tools/` | Helpers (Sheets → JSONL converter, etc.) | scaffolded Step 4.5 |
| `corpus/` | WHO/CDC/Mayo fact sheets for RAG (Fact-Check Agent) | scaffold Step 5 / Phase 4 |
| `source_reputation/` | Domain credibility lists (credible/mixed/unreliable JSON) | scaffold Step 5 / Phase 4 |
| `labels/` | Output of `ml/scripts/generate_labels.py` (gpt-5.5 synthetic labels) | populated Phase 2 hackathon |
| `reasoning_cache/` | Pre-cached agent results for demo posts (decision #17) | populated Phase 4 |

---

## Privacy

Real curated content (`source_posts/`, `corpus/` if it ever holds full WHO fact-sheets verbatim) stays **local — gitignored**.

What IS committed:
- Specs (`SPEC.md`, `sheets_setup.md`)
- Example fixtures (`example.jsonl` — 3-5 fake posts for testing)
- Reputation lists (small JSON, no PII)

---

## Data flow (overview)

```
data/source_posts/posts_raw.jsonl
  │
  └─> ml/scripts/generate_labels.py (gpt-5.5)
        │
        └─> data/labels/labels.jsonl
              │
              └─> ml/scripts/train_scorer.py (XGBoost)
                    │
                    └─> backend/app/services/scorer.pkl
```

```
data/corpus/{who,cdc,mayo}/*.md
  │
  └─> backend/app/services/rag.py (ingest → Chroma)
        │
        └─> Fact-Check Agent retrieval
```

```
data/source_reputation/{credible,mixed,unreliable}.json
  │
  └─> backend/app/services/source_rep.py (lookup)
        │
        └─> Provenance Agent input feature
```

See `JOURNAL.md` for project status.
