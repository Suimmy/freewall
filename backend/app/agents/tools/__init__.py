"""
Function tools shared by agents.

Each tool is a function decorated with `@function_tool` (openai-agents SDK)
and registered in the relevant agent's `tools=[...]` list.

  - rag_search.py      — Chroma retrieval over WHO/CDC/Mayo corpus (Fact-Check)
  - web_search.py      — live web search for alternative sources (Counter)
  - source_lookup.py   — domain reputation lookup from data/source_reputation/

Tools should be small, deterministic, and schema-validated.
"""
