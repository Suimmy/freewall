"""
Multi-agent layer.

Six agents (CLAUDE.md decision #5):

  L1 (perception):
    - classifier.py        — Content Classifier Agent

  L2 (reasoning):
    - coordinator.py       — dispatches L2 workers + computes Sovereignty Score
    - persuasion.py        — detects PersuSafety + Cialdini tactics
    - fact_check.py        — RAG-grounded claim verification
    - provenance.py        — synthetic + source verdict over L1 signals
    - counter.py           — Counter-Perspective steelman + alternative sources

Each module exports a single `Agent` instance (openai-agents SDK).
Tools shared across agents live in `tools/`. Markdown prompts loaded at
startup live in `prompts/`.

Pattern (every agent file):

    from agents import Agent
    from app.core.llm import make_model_settings
    from app.schemas.agent_io import <AgentName>Input  # codegen output
    from app.schemas.reasoning import <AgentName>Finding  # codegen output

    instructions = (Path(__file__).parent / "prompts" / "<name>.md").read_text()

    <name>_agent = Agent(
        name="<name>",
        instructions=instructions,
        model="gpt-5.5",
        model_settings=make_model_settings(reasoning_effort="<tier>"),
        tools=[...],
        output_type=<AgentName>Finding,
    )
"""
