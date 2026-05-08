# `backend/app/schemas/` — auto-generated Pydantic models

> **DO NOT EDIT FILES HERE BY HAND.** They are output of `codegen.sh`. Manual edits will be overwritten on the next codegen run.

---

## What lives here (after codegen runs)

| File | Generated from | Used by |
|------|----------------|---------|
| `perception.py` | `shared/schemas/perception.json` | `app/api/routes/perceive.py`, `app/services/orchestrator.py` |
| `reasoning.py` | `shared/schemas/reasoning.json` | SSE event emitters, `services/sse.py`, agent wrappers |
| `agent_io.py` | `shared/schemas/agent_io.json` | Each agent in `app/agents/*.py` for input validation |

Plus the underlying enums (referenced via `Literal[...]` in generated models — see `shared/ENUMS.md` for the verbatim values).

---

## Current status

**Codegen has not run yet** — this folder contains only `__init__.py` and this README. See `JOURNAL.md` Active TODOs for when codegen will fire (trigger: end of Step 3 — once `extension/src/types/` also exists as a target).

In the meantime, routes use **inline minimal stubs** (e.g., `_PerceptionStub` in `routes/perceive.py`). After codegen runs, those inline stubs get replaced with one-line imports:

```python
# Before (now):
class _PerceptionStub(BaseModel):
    session_id: str
    content_id: str
    ...

# After codegen:
from app.schemas.perception import PerceptionPayload
```

---

## How to (re)generate (after `codegen.sh` exists)

From the repo root:

```bash
bash shared/codegen.sh
```

This reads `shared/schemas/*.json` and writes Pydantic v2 models into this folder. Re-run any time a JSON schema changes.

---

## Why we don't write Pydantic models by hand

- Three sources of truth (TS types, Pydantic, JSON Schema) drift in days
- Codegen guarantees parity — same field names, same enum values, same nullability
- Reviewers can trust that schema changes propagate consistently
