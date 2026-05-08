"""
Custom exception types.

Each exception maps to a stable error `code` returned in API responses
(see docs/API_CONTRACTS.md). Use these instead of bare `Exception` /
`ValueError` so callers can branch on type and so the API handler can
return consistent `{ error: { code, message } }` shapes.
"""

from __future__ import annotations


class FreewallError(Exception):
    """Base for all Freewall errors. API exception handler catches this."""

    code: str = "freewall_error"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class LLMError(FreewallError):
    """OpenAI API failure — timeout, rate limit, invalid response shape."""

    code = "llm_error"


class AgentError(FreewallError):
    """Agent failed to produce valid structured output (after retries)."""

    code = "agent_error"


class RAGError(FreewallError):
    """Chroma retrieval / embedding failure."""

    code = "rag_error"


class ContentValidationError(FreewallError):
    """Incoming perception payload failed schema validation."""

    code = "invalid_perception"
