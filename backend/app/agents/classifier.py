"""
L1 Content Classifier Agent.

Runs in L1 (perception layer) — output drives Coordinator dispatch + the
mock-pipeline topic-aware findings selection. Lightweight: no tools,
reasoning_effort=none. Input = plain text (per `prompts/classifier.md`).

I/O contracts: shared/schemas/agent_io.json → ClassifierInput / ClassifierOutput.
See `prompts/classifier.md` for instructions + few-shot examples.
"""

from __future__ import annotations

from pathlib import Path

from agents import Agent

from app.core.llm import make_model_settings
from app.schemas.agent_io import ClassifierOutput

_INSTRUCTIONS = (Path(__file__).parent / "prompts" / "classifier.md").read_text()


classifier_agent = Agent(
    name="classifier",
    instructions=_INSTRUCTIONS,
    model="gpt-5.5",
    model_settings=make_model_settings(reasoning_effort="none"),
    output_type=ClassifierOutput,
)
