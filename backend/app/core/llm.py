"""
OpenAI client + Agents SDK helpers.

Most LLM calls go through the openai-agents SDK (`Agent` + `Runner`). This
module exposes:

- `get_client()` — shared singleton AsyncOpenAI for cases that bypass the
  Agents SDK (e.g., embeddings for Chroma, direct Responses API call).
- `make_model_settings(...)` — typed builder for the `ModelSettings` instance
  every Freewall agent passes to `Agent(...)`. Pulls `max_tokens` from config
  by default so output cap stays in `.env`.

NOTE: We use a single model (`gpt-5.5`) and tune reasoning per agent — see
config.py for per-use-case defaults.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from agents import ModelSettings, set_default_openai_key
from openai import AsyncOpenAI
from openai.types.shared import Reasoning

from app.config import settings

ReasoningEffort = Literal["none", "minimal", "low", "medium", "high", "xhigh"]
Verbosity = Literal["low", "medium", "high"]


# Push our pydantic-settings-loaded key into the Agents SDK at import time.
# Agents SDK normally reads OPENAI_API_KEY from os.environ — but our config.py
# uses pydantic-settings which intentionally does NOT pollute os.environ
# (security: key never enters process-wide env table). This bridges the gap.
set_default_openai_key(settings.openai_api_key)


@lru_cache(maxsize=1)
def get_client() -> AsyncOpenAI:
    """Cached singleton AsyncOpenAI client. Reused across all callers."""
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        max_retries=3,   # SDK retries on 429 / 5xx with exponential backoff
    )


def make_model_settings(
    *,
    reasoning_effort: ReasoningEffort,
    verbosity: Verbosity = "low",
    max_tokens: int | None = None,
) -> ModelSettings:
    """
    Build a ``ModelSettings`` for a Freewall agent.

    Usage in an Agent definition:
        from agents import Agent
        from app.core.llm import make_model_settings

        my_agent = Agent(
            model="gpt-5.5",
            model_settings=make_model_settings(reasoning_effort="medium"),
            ...
        )

    Args:
        reasoning_effort: gpt-5.5 reasoning tier — none / low / medium / high / xhigh.
        verbosity: output length tier (default "low" — keeps token cost down).
        max_tokens: hard ceiling. Defaults to ``settings.openai_max_output_tokens``.
    """
    return ModelSettings(
        reasoning=Reasoning(effort=reasoning_effort),
        verbosity=verbosity,
        max_tokens=max_tokens if max_tokens is not None else settings.openai_max_output_tokens,
    )
