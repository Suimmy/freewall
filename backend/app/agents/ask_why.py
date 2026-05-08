"""
Ask Why agent — one-shot summarizer for the L3 explainability modal.

Reads cached ReasoningState (no agent re-runs) and produces 3-5 plain
sentences explaining the Sovereignty Score in the user's language.
Reasoning=low + verbosity=low → fast (~2-3s) and cheap (~$0.005/call).
Plain text output — no Pydantic structured type needed.
"""

from __future__ import annotations

from pathlib import Path

from agents import Agent

from app.core.llm import make_model_settings

_INSTRUCTIONS = (Path(__file__).parent / "prompts" / "ask_why.md").read_text()


ask_why_agent = Agent(
    name="ask_why",
    instructions=_INSTRUCTIONS,
    model="gpt-5.5",
    model_settings=make_model_settings(reasoning_effort="low", verbosity="low"),
)
