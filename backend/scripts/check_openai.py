"""
Smoke-test OpenAI API key + gpt-5.5 access.

Run from `backend/`:
    uv run python scripts/check_openai.py

Exits 0 on full success, 1 on any failure. Key is read via the app's
pydantic-settings loader (same path FastAPI uses) — so this script
also validates that .env is being loaded correctly at import time.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Project is `package = false` (pyproject.toml) — not pip-installed, so `app`
# is not on sys.path by default. Add backend/ (parent of scripts/) to sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> int:
    # Step 1: settings load — fails here if .env missing or OPENAI_API_KEY absent
    try:
        from app.config import settings
    except Exception as e:
        print(f"[FAIL] settings load: {type(e).__name__}: {e}")
        print("        → check backend/.env exists + has OPENAI_API_KEY=sk-...")
        return 1

    key_preview = settings.openai_api_key[:7] + "..." + settings.openai_api_key[-4:]
    print(f"[OK]   .env loaded — key={key_preview}, model={settings.openai_model}")

    # Step 2: client init + cheap auth check via models.list (no token cost)
    from openai import APIError, AuthenticationError, OpenAI

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        first_model = client.models.list().data[0].id
    except AuthenticationError as e:
        print(f"[FAIL] auth rejected: {e}")
        print("        → key is invalid / revoked / not yet activated")
        return 1
    except APIError as e:
        print(f"[FAIL] OpenAI API error: {type(e).__name__}: {e}")
        return 1
    except Exception as e:
        print(f"[FAIL] network or other error: {type(e).__name__}: {e}")
        return 1

    print(f"[OK]   models.list() — first model: {first_model}")

    # Step 3: invoke configured model — validates access tier + that model exists
    try:
        r = client.responses.create(
            model=settings.openai_model,
            input="ping",
            max_output_tokens=20,
        )
    except APIError as e:
        print(f"[FAIL] {settings.openai_model} not accessible: {e}")
        print(f"        → either tier mismatch or model name wrong (config.py: openai_model)")
        return 1
    except Exception as e:
        print(f"[FAIL] {settings.openai_model} call failed: {type(e).__name__}: {e}")
        return 1

    print(f"[OK]   {settings.openai_model} responded: {r.output_text!r}")
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
