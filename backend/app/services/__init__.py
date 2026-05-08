"""
Service layer — business logic + integrations.

  - orchestrator.py    runs the full L2 pipeline for one perception
  - rag.py             Chroma client lifecycle + retrieval helpers
  - source_rep.py      domain reputation lookup (loads data/source_reputation/)
  - scorer.py          Sovereignty Score: XGBoost / weighted-sum fallback
  - sse.py             per-session asyncio.Queue event manager

Routes call services. Services may call agents (`Runner.run`), `core/llm.py`,
and each other. Tools (in `agents/tools/`) usually delegate the real work
back to a service of the same name.
"""
