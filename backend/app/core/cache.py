"""
Disk-backed cache for ReasoningState.

Used to:
  1. Pre-warm cache for demo content (Phase 4) — judges play demo without live LLM.
  2. Avoid re-analyzing identical content within a session.
  3. Provide fallback during BudgetExceededError — show cached state with a banner.

Storage: simple JSON files keyed by content_id. Production would swap for
Redis or sqlite. For hackathon scale (< 1000 entries) this is plenty.

Cache invalidation: not implemented (hackathon = static demo content). Manually
delete files in `settings.reasoning_cache_dir` to refresh.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


def _cache_path(content_id: str) -> Path:
    # Sanitize: content_id must be filesystem-safe (alphanumerics + - _ only).
    safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in content_id)
    return Path(settings.reasoning_cache_dir) / f"{safe_id}.json"


def get(content_id: str) -> dict[str, Any] | None:
    """Return cached ReasoningState dict, or None if not cached / unreadable."""
    p = _cache_path(content_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to read cache for content_id=%s: %s", content_id, e)
        return None


def set(content_id: str, state: dict[str, Any]) -> None:
    """Persist ReasoningState dict to disk. Overwrites existing entry."""
    p = _cache_path(content_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    logger.debug("Cached reasoning for content_id=%s", content_id)


def delete(content_id: str) -> bool:
    """Remove a cached entry. Returns True if it existed."""
    p = _cache_path(content_id)
    if p.exists():
        p.unlink()
        return True
    return False


def list_cached() -> list[str]:
    """List all cached content_ids (filenames without .json)."""
    cache_dir = Path(settings.reasoning_cache_dir)
    if not cache_dir.exists():
        return []
    return [p.stem for p in cache_dir.glob("*.json")]
