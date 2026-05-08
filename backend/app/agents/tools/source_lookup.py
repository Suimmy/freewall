"""
Source reputation lookup tool — used by Provenance Agent.

Checks a domain against our hardcoded reputation lists in
`data/source_reputation/{credible,mixed,unreliable}.json` (68 domains total).
Returns matched verdict + publisher name + publisher type, or 'unknown' if not found.

Architecture:
- `lookup_domain(url_or_domain)` — pure-sync, directly callable from tests + orchestrator.
- `source_lookup` (@function_tool) — Agents SDK wrapper, used by Provenance agent.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from agents import function_tool

logger = logging.getLogger(__name__)

# Reputation tables location (env override → backend-anchored fallback).
# source_lookup.py is at backend/app/agents/tools/source_lookup.py →
# parents[3] = backend root. Bundled in backend/data/source_reputation/ for
# self-contained deploy. SOURCE_REP_DIR env var lets ops override.
import os as _os

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_REP_DIR_ENV = _os.environ.get("SOURCE_REP_DIR")
_REP_DIR = (
    Path(_REP_DIR_ENV).resolve()
    if _REP_DIR_ENV
    else _BACKEND_ROOT / "data" / "source_reputation"
)


@lru_cache(maxsize=1)
def _load_lookup_table() -> dict[str, dict[str, str]]:
    """
    Load + flatten 3 reputation JSONs into single dict[domain, entry] for O(1) lookup.

    Cached: loaded once per process, never reloaded.
    """
    table: dict[str, dict[str, str]] = {}
    for category_file in ("credible.json", "mixed.json", "unreliable.json"):
        path = _REP_DIR / category_file
        if not path.exists():
            logger.warning("reputation file missing: %s", path)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        category = data["category"]  # "credible" / "mixed" / "unreliable"
        for entry in data.get("domains", []):
            domain = entry["domain"].lower().strip()
            if domain in table:
                logger.warning(
                    "duplicate domain %r — %s overrides %s",
                    domain, category, table[domain]["reputation"],
                )
            table[domain] = {
                "reputation": category,
                "name": entry.get("name", ""),
                "type": entry.get("type", ""),
            }
    logger.info("source_lookup table loaded: %d domains", len(table))
    return table


def _normalize_domain(url_or_domain: str) -> str:
    """
    Strip protocol, path, query, fragment, port, and 'www.' prefix.
    Lowercase. Does NOT do eTLD+1 reduction (we keep subdomains for finer matching).

    Examples:
        'https://www.who.int/news/...'  → 'who.int'
        'WWW.CDC.gov:443'               → 'cdc.gov'
        'rama.mahidol.ac.th'            → 'rama.mahidol.ac.th'  (no parent reduction)
    """
    s = url_or_domain.strip().lower()
    if "://" in s:
        s = s.split("://", 1)[1]
    for sep in ("/", "?", "#"):
        if sep in s:
            s = s.split(sep, 1)[0]
    # Strip port (after path stripping)
    if ":" in s:
        s = s.split(":", 1)[0]
    if s.startswith("www."):
        s = s[4:]
    return s


def lookup_domain(url_or_domain: str) -> dict[str, Any]:
    """
    Look up reputation for a URL or domain. Pure-sync; safe to call from anywhere.

    Returns dict with: domain (normalized), reputation, name, type, found.
    Not-found case returns reputation='unknown', name=None, type=None, found=False.
    """
    normalized = _normalize_domain(url_or_domain)
    table = _load_lookup_table()
    entry = table.get(normalized)
    if entry:
        return {
            "domain": normalized,
            "reputation": entry["reputation"],
            "name": entry["name"],
            "type": entry["type"],
            "found": True,
        }
    return {
        "domain": normalized,
        "reputation": "unknown",
        "name": None,
        "type": None,
        "found": False,
    }


@function_tool
async def source_lookup(domain: str) -> dict[str, Any]:
    """
    Look up reputation for a domain.

    Args:
        domain: URL or hostname. Will be normalized (strip protocol, path, www).
                Subdomains are kept for exact match — pass 'rama.mahidol.ac.th'
                if that's the actual subdomain you want to check.

    Returns:
        - domain: normalized hostname (e.g., 'who.int')
        - reputation: 'credible' | 'mixed' | 'unreliable' | 'unknown'
        - name: publisher name (e.g., 'World Health Organization'), or None
        - type: publisher type (e.g., 'international_authority'), or None
        - found: True if domain matched our list, False otherwise
    """
    return lookup_domain(domain)
