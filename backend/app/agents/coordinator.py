"""
L2 Coordinator Agent — routes L2 dispatch.

Decides which worker agents (`persuasion`, `fact_check`, `provenance`) to
dispatch for a given perception, based on `category` + `category_confidence`.
Does NOT compute the Sovereignty Score (that's done in
`services/orchestrator.py` after workers return).

Counter-Perspective is NOT dispatched here — orchestrator runs Counter as a
SECOND wave only when initial score < 50 (lazy / cost-aware).

I/O contracts: shared/schemas/agent_io.json → CoordinatorInput / CoordinatorOutput.
See `prompts/coordinator.md` for routing rules.
"""

from __future__ import annotations

from pathlib import Path

from agents import Agent

from app.core.llm import make_model_settings
from app.schemas.agent_io import CoordinatorOutput

_INSTRUCTIONS = (Path(__file__).parent / "prompts" / "coordinator.md").read_text()


coordinator_agent = Agent(
    name="coordinator",
    instructions=_INSTRUCTIONS,
    model="gpt-5.5",
    model_settings=make_model_settings(reasoning_effort="low"),
    output_type=CoordinatorOutput,
)
