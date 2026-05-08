# `shared/schemas/` — Single Source of Truth

> Cross-language data contracts for Freewall. Edit here once → regenerate TS types (extension) and Pydantic models (backend) from the same source.

> **⚠️ Status (2026-05-07)**: `codegen.sh` referenced below has **not been created yet** — deferred to Step 2/3 because `extension/src/types/` and `backend/app/schemas/` don't exist as targets yet. Schemas in this folder are stable; only the generation script is pending. See `JOURNAL.md` for the carried-forward TODO.

---

## Files

| File | Role | Consumed by |
|------|------|-------------|
| `perception.json` | L1 → L2 contract. Body of `POST /perceive` | extension (sender), backend Coordinator (receiver) |
| `reasoning.json` | L2 → L3 contract. Discriminated union of 6 SSE event types | backend orchestrator (sender), extension UI (receiver) |
| `agent_io.json` | Per-agent input contracts. Outputs $ref into `reasoning.json` | each agent in `backend/app/agents/` |
| `README.md` | This file | humans |

The verbatim enum values referenced by every schema live in `../ENUMS.md` — that file is the **human SSOT** for value lists; this folder is the **machine SSOT** for shapes.

---

## How the contract flows through the system

```
┌─────────────────────┐
│  shared/schemas/    │  ← edit JSON here, ONE place
│  *.json             │
└──────────┬──────────┘
           │
           │  bash codegen.sh
           │
   ┌───────┴────────┐
   ▼                ▼
┌─────────┐   ┌──────────────────┐
│ TS      │   │ Pydantic models  │
│ types   │   │                  │
│         │   │                  │
│ extension/  │ backend/app/      │
│ src/types/  │ schemas/          │
│ api.ts      │ *.py              │
└─────────┘   └──────────────────┘
```

After regen:
- Extension imports `Perception`, `ReasoningEvent`, etc. as TS types — autocomplete + compile-time errors on mismatched fields.
- Backend imports `PerceptionPayload`, `ReasoningEvent`, etc. as Pydantic models — runtime validation on request bodies + structured-output validation on agent responses.

---

## Editing workflow (the only safe protocol)

1. **Open the JSON file** for the contract you're changing.
2. **Add / rename / remove fields**. Update the `description` so consumers know what changed.
3. **If adding an enum value**: also update `../ENUMS.md` — that file is the place humans read.
4. **Run** `bash ../codegen.sh` to regenerate TS + Pydantic on both sides.
5. **Compile both sides**: `cd ../../extension && pnpm build`, `cd ../../backend && uv run mypy app`. Type errors point at every consumer that needs to be updated.
6. **Note the change** in `JOURNAL.md` — schema changes are decisions worth tracking, especially renames or removals.

### Anti-patterns

- ❌ Editing `extension/src/types/api.ts` directly. It's generated. Your change will be lost on next codegen.
- ❌ Editing `backend/app/schemas/*.py` directly. Same reason.
- ❌ Adding a field on one side only. The whole point of this folder is preventing drift.
- ❌ Skipping the compile step. Schema change without compiling = silent breakage at runtime.

---

## Cross-file `$ref` notes

`agent_io.json` references `reasoning.json` for finding types (e.g., `CounterPerspectiveAgentInput.prior_findings.persuasion` → `reasoning.json#/$defs/PersuasionFinding`).

Most JSON Schema codegen tools support cross-file `$ref` if the files are in the same directory and refs are relative paths (`./reasoning.json#/...`). If a tool struggles, alternatives:

1. Run codegen with all schema files passed at once (most tools merge `$defs` across files).
2. As last resort, inline the referenced shape — but then ENUMS.md and reasoning.json must stay in sync manually. Avoid.

---

## Versioning

Schemas are versioned with the project — no `v1`/`v2` field on the wire (yet). For the 18-hour build, breaking changes are coordinated via the JOURNAL entry + a Slack/chat ping. Post-MVP, consider adding a `schema_version` field to `perception.json` and `reasoning.json` headers if the API ever leaves the team.
