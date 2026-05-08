# `data/corpus/` — health fact sheets for RAG

> Ground-truth source material for the **Fact-Check Agent** (Layer 2). Embedded into Chroma at hackathon kickoff, retrieved during agent dispatch when a health claim is detected.

---

## Layout

```
corpus/
├── en/              # English-language sources
│   ├── who/         # who.int fact sheets
│   ├── cdc/         # cdc.gov fact sheets
│   ├── nih/         # ods.od.nih.gov (NIH Office of Dietary Supplements)
│   └── mayo/        # mayoclinic.org articles
└── th/              # Thai-language sources
    ├── ddc/         # ddc.moph.go.th (กรมควบคุมโรค)
    ├── moph/        # moph.go.th (กระทรวงสาธารณสุข)
    └── mahidol/     # si.mahidol / rama.mahidol / chulalongkornhospital
```

**Topic scope** (locked 2026-05-07): corpus is focused on 5 demo-relevant topics — **เบาหวาน, มะเร็ง, ลดน้ำหนัก/GLP-1, อาหารเสริม/วิตามิน, ความดัน/โรคหัวใจ**. COVID and measles content was deliberately excluded after Suim's 2026-relevance review (low misinfo viral density). Adjacent supportive content (Long COVID, immunization general, hair-loss supplement debunk) retained.

**Why en/th split**: demo content is 80% Thai / 20% English (per CLAUDE.md decision + Step 4.5 SPEC). `text-embedding-3-small` is multilingual but cross-language retrieval has a ~10-20% performance gap. Tagging language in metadata lets the Fact-Check Agent prefer same-language matches when available, falling back to cross-language only when needed.

---

## File format

Each `.md` is one fact sheet. Structure:

```markdown
---
source_url: https://www.who.int/news-room/fact-sheets/detail/vaccines-and-immunization
source_org: WHO
lang: en
fetched_at: 2026-05-07
topic: vaccines
---

# <title>

<body — plain markdown, headings preserved>
```

Frontmatter is parsed by `ingest.py` and stored as Chroma metadata.

---

## Workflow

```
data/corpus/{en,th}/{source}/*.md
        │
        └─> data/corpus/ingest.py     (run once at hackathon kickoff)
              │  - parse frontmatter
              │  - chunk body (~500 chars, 50 overlap)
              │  - embed via OpenAI text-embedding-3-small
              │
              └─> chroma_db/freewall_corpus  (gitignored)
                    │
                    └─> backend/app/services/rag.py loads collection
                          │
                          └─> Fact-Check Agent retrieves top-k
```

Re-run `ingest.py` whenever new `.md` files are added.

---

## Ownership

| Phase | Owner | Action |
|-------|-------|--------|
| Pre-build (Step 5, 2026-05-07) | Claude | Bootstrap ~5-8 EN + ~3-5 TH seed fact sheets |
| Phase 1 (hackathon kickoff) | D (Fact-Check) | Implement `ingest.py` Chroma + embedding logic, run once |
| Phase 4 (polish) | Claude (Suim approves) | Add demo-specific fact sheets matching selected demo posts |

---

## Adding a new fact sheet

1. Pick a real authority source (WHO, CDC, Mayo, DDC, MOPH, Mahidol-affiliated hospital)
2. Save to the right language + source folder: `en/who/diabetes.md`, `th/ddc/dengue.md`, etc.
3. Fill frontmatter (`source_url`, `source_org`, `lang`, `fetched_at`, `topic`)
4. Re-run `ingest.py` to refresh Chroma

---

## What is NOT in scope here

- ❌ User-generated content / social posts (those live in `data/source_posts/`)
- ❌ Source reputation lists (those live in `data/source_reputation/`)
- ❌ Pre-cached agent reasoning output (lives in `data/reasoning_cache/`, Phase 4)

See `data/README.md` for the bigger picture.
