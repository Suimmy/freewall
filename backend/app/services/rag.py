"""
Chroma vector DB lifecycle + retrieval helpers.

Persistent local DB at `<repo>/data/corpus/chroma_db/`. Embedded mode — runs
in-process, no separate server. Reused by `tools/rag_search.py` (Fact-Check
agent's RAG tool) and by `data/corpus/ingest.py` (one-time ingestion).

Architecture:
- `init_client()` — idempotent connect to PersistentClient + get_or_create_collection.
  Called from main.py lifespan for warm-start; auto-called by query() if needed.
- `query(text, k)` — embed via OpenAI + Chroma similarity search + format results.
- `get_collection()` — direct collection accessor (used by ingest.py).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import chromadb

from app.core.llm import get_client

logger = logging.getLogger(__name__)


# Chroma DB location resolution (env override → backend-anchored fallback).
# rag.py is at backend/app/services/rag.py → parents[2] = backend root.
# In dev + Railway deploy, backend/data/corpus/chroma_db is bundled with the
# app (committed to git). CHROMA_DIR env var lets ops override (e.g., for a
# mounted volume on Railway pro tier).
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_CHROMA_DIR_ENV = os.environ.get("CHROMA_DIR")
_CHROMA_DIR = (
    Path(_CHROMA_DIR_ENV).resolve()
    if _CHROMA_DIR_ENV
    else _BACKEND_ROOT / "data" / "corpus" / "chroma_db"
)
_COLLECTION_NAME = "freewall_corpus"
_EMBED_MODEL = "text-embedding-3-small"

# Module-global Chroma client — set by init_client() on first use.
_client: Any | None = None
_collection: Any | None = None


def init_client() -> None:
    """
    Initialize Chroma client + collection. Idempotent — safe to call repeatedly.

    Called from `main.py` lifespan for warm-start, but `query()` also auto-calls
    this so individual scripts/tests don't need explicit setup.
    """
    global _client, _collection
    if _collection is not None:
        return
    _CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    _client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
    _collection = _client.get_or_create_collection(_COLLECTION_NAME)
    logger.info(
        "rag client initialized: path=%s collection=%s count=%d",
        _CHROMA_DIR, _COLLECTION_NAME, _collection.count(),
    )


def get_collection() -> Any:
    """
    Return the loaded collection, initializing if needed.

    Used by ingest.py to upsert chunks; also by query() internally.
    """
    if _collection is None:
        init_client()
    return _collection


async def _embed(text: str) -> list[float]:
    """Embed a single string via OpenAI text-embedding-3-small."""
    client = get_client()
    response = await client.embeddings.create(
        model=_EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


async def query(text: str, k: int = 5) -> list[dict[str, Any]]:
    """
    Retrieve top-k chunks matching `text`. Used by tools/rag_search.

    Args:
        text: query string (claim or question to verify).
        k: number of results to return.

    Returns:
        List of {title, url, publisher, snippet, lang, topic} dicts ordered by
        similarity (most relevant first). Empty list if collection is empty.
    """
    coll = get_collection()
    if coll.count() == 0:
        logger.warning("rag.query: collection is empty — run data/corpus/ingest.py")
        return []

    embedding = await _embed(text)
    results = coll.query(
        query_embeddings=[embedding],
        n_results=min(k, coll.count()),
    )

    # Chroma returns parallel lists per query (we sent 1 query, so use [0]).
    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]

    hits: list[dict[str, Any]] = []
    for doc, meta in zip(docs, metas):
        m = meta or {}
        section = m.get("section", "")
        topic = m.get("topic", "")
        # Compose human-readable title from publisher / topic / section for citation.
        title = f"{topic}: {section}" if section else topic or "(no topic)"
        hits.append({
            "title": title,
            "url": m.get("source_url", ""),
            "publisher": m.get("source_org", ""),
            "snippet": doc,
            "lang": m.get("lang", ""),
            "topic": topic,
            "section": section,
        })
    return hits
