"""
L2 Provenance Agent — synthetic verdict + source verdict.

Tools: `source_lookup` — agent looks up domain reputation directly.
Reasoning effort: low (light reasoning, mostly signal mapping + lookup interpretation).

I/O contracts: input is text + url + synthetic_signals (Path C: signals usually empty
since no in-browser ML). Output: shared/schemas/reasoning.json → ProvenanceFinding.

See `prompts/provenance.md` for the verdict rubric + honesty constraint.
"""

from __future__ import annotations

from pathlib import Path

from agents import Agent

from app.agents.tools.source_lookup import source_lookup
from app.core.llm import make_model_settings
from app.schemas.reasoning import ProvenanceFinding

_INSTRUCTIONS = (Path(__file__).parent / "prompts" / "provenance.md").read_text()


provenance_agent = Agent(
    name="provenance",
    instructions=_INSTRUCTIONS,
    model="gpt-5.5",
    model_settings=make_model_settings(reasoning_effort="low"),
    tools=[source_lookup],
    output_type=ProvenanceFinding,
)
