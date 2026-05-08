# `data/source_reputation/` — domain credibility lists

> Hardcoded reputation database for the **Provenance Agent** (Layer 2). No external API exists for free reputation lookup, so we maintain our own curated list (per CLAUDE.md decision #8).

---

## Files

| File | Description |
|------|-------------|
| `credible.json` | Authoritative health, news, scientific institutions |
| `mixed.json` | Generally reliable but with editorial bias / occasional errors |
| `unreliable.json` | Known misinformation, clickbait, conspiracy, pseudoscience |

A domain appearing in **none** of the 3 files is treated as `unknown` by `tools/source_lookup.py`.

---

## Schema

```json
{
  "schema_version": "1.0",
  "category": "credible | mixed | unreliable",
  "last_updated": "YYYY-MM-DD",
  "notes": "free-text scope note",
  "domains": [
    {
      "domain": "who.int",
      "name": "World Health Organization",
      "type": "international_authority",
      "lang": ["en", "multilingual"],
      "notes": "UN agency for international public health"
    }
  ]
}
```

### `type` enum

| Value | Examples |
|-------|----------|
| `international_authority` | WHO, UNICEF |
| `govt_health` | CDC (US), DDC (TH), NHS (UK), MOPH (TH) |
| `medical_school` | mayoclinic.org, hopkinsmedicine.org, si.mahidol.ac.th |
| `medical_journal` | nejm.org, thelancet.com, nature.com |
| `reputable_news` | reuters.com, bbc.com, apnews.com |
| `mixed_news` | popular outlets with editorial bias |
| `clickbait` | low-quality content farms |
| `known_misinfo` | repeatedly sanctioned for false health claims |
| `conspiracy` | structurally promotes conspiracy narratives |
| `pseudoscience` | "alternative medicine" with unfounded claims |

### `lang` field

ISO codes or `"multilingual"`. Useful for the Provenance Agent to tell user: "this Thai source is `mixed_news` (not Thai-credible)."

---

## Lookup contract

Used by `backend/app/agents/tools/source_lookup.py`:

```python
def lookup(url_or_domain: str) -> SourceReputation:
    # 1. Normalize: extract eTLD+1 (e.g., "https://m.who.int/foo" -> "who.int")
    # 2. Search credible.json -> mixed.json -> unreliable.json
    # 3. Return {category, name, type, lang, notes} or {"category": "unknown"}
```

**Always normalize to eTLD+1** — sub-domains like `m.cnn.com` should match `cnn.com`, except where the sub-domain has independent reputation (e.g., a university's anti-vax sub-site — flag in `notes`).

---

## Maintenance

| Phase | Owner | Action |
|-------|-------|--------|
| Pre-build (Step 5, 2026-05-07) | Claude | Bootstrap ~50-100 well-known domains from training knowledge |
| Phase 1 (hackathon) | C (Provenance) | Implement `tools/source_lookup.py` to load these JSONs |
| Phase 4 (polish) | E (ML/Demo) + Claude | Add demo-specific mock-site domains for the demo content |

### Adding a domain

1. Pick the right file based on category
2. Add entry following the schema (no trailing comma — pure JSON, not JSONC)
3. Bump `last_updated`
4. **Don't duplicate across files** — a domain belongs in exactly one category

### Removing / re-categorizing

If a source's reputation changes (e.g., a once-credible journal retracts → becomes mixed), move the entry — don't dual-list. `last_updated` should reflect the change.

---

## Pitch defensibility note

Our pitch slide should acknowledge the limitation: "static curated list, ~50-100 domains. In production, would integrate MBFC API + Wikipedia source-reliability + ad fontes media." This is honest framing per CLAUDE.md anti-pattern #7 (don't oversell limitations).
