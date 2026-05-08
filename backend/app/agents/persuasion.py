"""
L2 Persuasion Agent — detects PersuSafety + Cialdini tactics.

Reasoning effort: medium (analytical detection work).
I/O contracts: shared/schemas/reasoning.json → PersuasionFinding
              (input is text + category — see `_format_persuasion_input` in orchestrator).

See `prompts/persuasion.md` for the 21-tactic taxonomy + few-shot examples.
The taxonomy is large enough to be a stable cache prefix — most of the
prompt is shared across calls, so prompt caching cuts input cost ~80%.
"""

from __future__ import annotations

from pathlib import Path

from agents import Agent

from app.core.llm import make_model_settings
from app.schemas.reasoning import PersuasionFinding

_INSTRUCTIONS = (Path(__file__).parent / "prompts" / "persuasion.md").read_text()


persuasion_agent = Agent(
    name="persuasion",
    instructions=_INSTRUCTIONS,
    model="gpt-5.5",
    model_settings=make_model_settings(reasoning_effort="medium"),
    output_type=PersuasionFinding,
)
