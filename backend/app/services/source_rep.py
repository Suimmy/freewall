"""
Domain reputation lookup.

Loads `data/source_reputation/{credible,mixed,unreliable}.json` once at
module import (cached). Lookup is O(1) per domain.

Used by:
  - tools/source_lookup.py (function_tool wrapper around `lookup()`)
  - services/orchestrator.py (pre-populates source.reputation in perception
    payloads if extension didn't)

⚠️ DATA REQUIRED — `data/source_reputation/{credible,mixed,unreliable}.json`
must be populated BEFORE this works. See JOURNAL.md Active TODOs Phase 2 —
"REPUTATION DATA". Claude can bootstrap from training knowledge + MBFC /
Wikipedia. Phase 4: add demo-specific mock-site domains.

Stub: returns 'unknown' for every domain — Phase 2 reads JSON files.
"""

from __future__ import annotations

import logging
from typing import Literal

logger = logging.getLogger(__name__)

Reputation = Literal["credible", "mixed", "unreliable", "unknown"]


def lookup(domain: str) -> Reputation:
    """
    Look up reputation for a domain (eTLD+1 normalized).

    Args:
        domain: hostname like 'example.com' (NOT 'www.example.com').

    Returns:
        'credible' | 'mixed' | 'unreliable' | 'unknown'
    """
    logger.debug("source_rep.lookup stub: domain=%s", domain)

    # TODO (Phase 2):
    # 1. On module import, load JSON files into module-global sets:
    #      _credible: set[str]
    #      _mixed: set[str]
    #      _unreliable: set[str]
    # 2. Normalize domain (lowercase, strip 'www.', take eTLD+1)
    # 3. Check membership in order: unreliable → mixed → credible → unknown
    # 4. Use `tldextract` if available, else simple split on dots

    return "unknown"


def normalize(domain: str) -> str:
    """Normalize a hostname to eTLD+1 (e.g., 'www.example.com' → 'example.com')."""
    # Stub — Phase 2: use tldextract for robust handling of co.uk, etc.
    d = domain.lower().strip()
    if d.startswith("www."):
        d = d[4:]
    return d
