"""
L2 Counter-Perspective Agent — generates steelman + alternative sources.

Tools: `WebSearchTool()` from openai-agents SDK — built-in web search via the
Responses API (Phase 2 decision: chose option (a) over a custom Bing/Brave wrapper).
Reasoning effort: high — steelman synthesis is the deepest reasoning task in the system.

I/O contracts: shared/schemas/reasoning.json → CounterPerspectiveFinding (canonical).
Agent's output_type uses a *loose* version (`url: str` instead of `AnyUrl`)
because OpenAI structured-output validator rejects `"format": "uri"` — same
constraint we hit in Step 2.9 Fact-Check. Canonical stays in app.schemas.reasoning.

See `prompts/counter.md` for the steelman pattern + tone calibration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from agents import Agent, WebSearchTool
from pydantic import BaseModel

from app.core.llm import make_model_settings


# Agent-side wire schema — `url: str` to satisfy OpenAI structured-output schema validator.
class _CPSource(BaseModel):
    url: str
    title: str
    publisher: str | None = None
    credibility: Literal["credible", "mixed", "unreliable", "unknown"] | None = None


class _CPFinding(BaseModel):
    steelman: str
    alternative_sources: list[_CPSource] = []


_INSTRUCTIONS = (Path(__file__).parent / "prompts" / "counter.md").read_text()


counter_agent = Agent(
    name="counter",
    instructions=_INSTRUCTIONS,
    model="gpt-5.5",
    model_settings=make_model_settings(reasoning_effort="high"),
    tools=[WebSearchTool()],
    output_type=_CPFinding,
)
