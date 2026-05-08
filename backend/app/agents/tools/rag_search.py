"""
RAG search tool — used by Fact-Check Agent.

Retrieves the top-k most relevant chunks from the WHO/CDC/NIH/Mahidol corpus
indexed in Chroma. Wraps `app.services.rag.query()` with the @function_tool
decorator so the Agents SDK can route LLM tool calls here.
"""

from __future__ import annotations

import logging
from typing import Any

from agents import function_tool

from app.services import rag

logger = logging.getLogger(__name__)


@function_tool
async def rag_search(query: str, k: int = 5) -> list[dict[str, Any]]:
    """
    Retrieve the top-k most relevant chunks from the health corpus matching `query`.

    Args:
        query: natural-language question or claim to search for. Multilingual
               (Thai + English) supported via text-embedding-3-small.
        k: number of results to return (1-10).

    Returns:
        List of {title, url, publisher, snippet, lang, topic} dicts ordered by
        cosine similarity. Empty list if collection is empty.
    """
    logger.info("rag_search: query=%r k=%d", query[:80], k)
    return await rag.query(query, k=k)
