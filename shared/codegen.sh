#!/usr/bin/env bash
# Codegen: shared/schemas/*.json → extension/src/types/*.ts + backend/app/schemas/*.py
#
# TS side:  one file per schema (perception.ts, reasoning.ts, agent_io.ts)
#           plus api.ts barrel that re-exports from each. agent_io is namespaced
#           to avoid name collisions with reasoning's inlined finding types.
# Python:   one Pydantic v2 module per schema. ruff format on output.
#
# Tools (deterministic, idempotent):
#   - json-schema-to-typescript (npm) via `pnpm dlx`
#   - datamodel-code-generator (pip)  via `uv run` (added to backend dev deps)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ─── TypeScript ──────────────────────────────────────────────────────────────────

echo "==> codegen: TypeScript types"
TS_DIR="$REPO_ROOT/extension/src/types"
mkdir -p "$TS_DIR"

# cd into shared/schemas so json-schema-to-typescript resolves `./other.json` $refs.
cd "$REPO_ROOT/shared/schemas"
for schema in *.json; do
  name=$(basename "$schema" .json)
  out="$TS_DIR/${name}.ts"
  {
    echo "// AUTO-GENERATED from shared/schemas/${schema}. Regenerate via: bash shared/codegen.sh"
    echo
    # --unreachableDefinitions emits types from $defs even when root doesn't $ref them.
    # Required for agent_io.json (root is just a title; all types live in $defs).
    pnpm dlx json-schema-to-typescript "$schema" --no-bannerComment --unreachableDefinitions
  } > "$out"
  echo "    wrote $out"
done

# Barrel — re-export everything. agent_io is namespaced because it inlines reasoning's
# finding types via $ref, which would collide with reasoning.ts's exports of the same.
cat > "$TS_DIR/api.ts" <<'EOF'
// AUTO-GENERATED — barrel for shared schemas. Regenerate via: bash shared/codegen.sh
//
// Use:
//   import type { PerceptionPayload, ReasoningEvent } from '@/types/api'
//   import type { agentIo } from '@/types/api'
//   const out: agentIo.CoordinatorOutput = ...

export type * from './perception'
export type * from './reasoning'
export type * as agentIo from './agent_io'
EOF
echo "    wrote $TS_DIR/api.ts"

# ─── Pydantic v2 ─────────────────────────────────────────────────────────────────

echo "==> codegen: Pydantic v2 models"
cd "$REPO_ROOT/backend"
for schema in perception reasoning agent_io; do
  uv run datamodel-codegen \
    --input "../shared/schemas/${schema}.json" \
    --input-file-type jsonschema \
    --output "app/schemas/${schema}.py" \
    --output-model-type pydantic_v2.BaseModel \
    --target-python-version 3.13 \
    --use-standard-collections \
    --use-union-operator \
    --use-double-quotes
  echo "    wrote backend/app/schemas/${schema}.py"
done

echo "==> codegen: ruff format on generated Pydantic"
uv run ruff format app/schemas/ --quiet

cd "$REPO_ROOT"
echo "==> codegen: done"
