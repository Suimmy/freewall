"""
L2 Fact-Check Agent — RAG-grounded claim verification.

Tools: `rag_search` (Chroma over WHO/CDC/NIH/Mahidol corpus).
Reasoning effort: medium.

I/O contracts: shared/schemas/reasoning.json → FactCheckFinding (canonical).
Agent's output_type uses a *loose* version (`url: str` instead of `AnyUrl`)
because OpenAI structured-output validator rejects `"format": "uri"` in JSON
schema. The canonical FactCheckFinding stays in app.schemas.reasoning for
SSOT — orchestrator marshals agent output → canonical-shaped dict.

See `prompts/fact_check.md` for the claim-extraction + verdict workflow,
including the Thai-EN dual-search strategy for cross-language retrieval.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from agents import Agent
from pydantic import BaseModel

from app.agents.tools.rag_search import rag_search
from app.core.llm import make_model_settings


# Agent-side wire schema. Mirrors `app.schemas.reasoning.FactCheckFinding`
# 1:1 EXCEPT `url: str` (vs `AnyUrl` on the canonical) — necessary because
# OpenAI structured-output schema validator doesn't accept "format": "uri".
class _FCSource(BaseModel):
    title: str
    url: str
    publisher: str | None = None
    snippet: str | None = None


class _FCClaim(BaseModel):
    claim: str
    verdict: Literal["supported", "contradicted", "unverifiable", "not_a_claim"]
    explanation: str | None = None
    sources: list[_FCSource] | None = None


class _FCFinding(BaseModel):
    claims: list[_FCClaim]


_INSTRUCTIONS = (Path(__file__).parent / "prompts" / "fact_check.md").read_text()


fact_check_agent = Agent(
    name="fact_check",
    instructions=_INSTRUCTIONS,
    model="gpt-5.5",
    model_settings=make_model_settings(reasoning_effort="medium"),
    tools=[rag_search],
    output_type=_FCFinding,
)
