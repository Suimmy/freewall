"""
Centralized settings loader.

All env vars are read here ONCE at import time. Other modules
do `from app.config import settings` instead of calling `os.getenv()` —
keeps config in one place + gives type-safe access via Pydantic.

If a required env var is missing, the app fails fast at startup
(rather than blowing up on the first request).

Model strategy (post gpt-5.5 — see CLAUDE.md decision #17):
- ONE model: gpt-5.5
- reasoning_effort tunes cost/quality per agent
- Verbosity tunes output length
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ReasoningEffort = Literal["none", "minimal", "low", "medium", "high", "xhigh"]
Verbosity = Literal["low", "medium", "high"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",            # read from backend/.env when uvicorn runs in backend/
        env_file_encoding="utf-8",
        case_sensitive=False,        # OPENAI_API_KEY == openai_api_key
    )

    # --- OpenAI ---
    openai_api_key: str = Field(..., description="Required. Get at platform.openai.com.")
    openai_model: str = "gpt-5.5"
    openai_max_output_tokens: int = 2000   # API-level ceiling, hard-stops runaway output

    # --- Reasoning effort per use case (defaults from Q2/Q3 discussion) ---
    # Override in .env if a particular agent is too slow / wrong tier in practice.
    reasoning_effort_classifier: ReasoningEffort = "none"      # L1 — fast classification
    reasoning_effort_routing: ReasoningEffort = "low"          # Coordinator — light routing
    reasoning_effort_default: ReasoningEffort = "medium"       # Persuasion, Fact-Check
    reasoning_effort_provenance: ReasoningEffort = "low"       # short reasoning over signals
    reasoning_effort_counter: ReasoningEffort = "high"         # steelman needs depth

    # --- Verbosity defaults ---
    verbosity_default: Verbosity = "low"

    # --- Budget guard ---
    per_call_max_usd: float = 0.30
    per_day_max_usd: float = 80.00
    cost_warning_threshold_pct: float = 0.80

    # --- Vector DB ---
    chroma_dir: str = "./data/chroma_index"

    # --- Reasoning state cache ---
    reasoning_cache_dir: str = "./data/reasoning_cache"

    # --- Server ---
    log_level: str = "INFO"
    env: str = "dev"      # "dev" or "prod"
    port: int = 8000

    # --- CORS ---
    # Comma-separated list of exact origins. For Vercel preview branches use the regex below.
    # Override via env: CORS_ALLOWED_ORIGINS=http://localhost:3000,https://freewall-demo.vercel.app
    cors_allowed_origins: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"           # Vite alt port
        "https://freewall-demo.vercel.app"  # production — update after first Vercel deploy
    )
    # Regex covers Vercel preview branches + Chrome extension (use one regex param)
    cors_origin_regex: str = (
        r"https://freewall-demo-.*\.vercel\.app|chrome-extension://.*"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    # --- Mock/live agent toggle (CLAUDE.md decision #18) ---
    # True during pre-build / local dev → orchestrator returns canned findings, no LLM cost.
    # Flip to False at hackathon Phase 2 kickoff to wire real Runner.run() calls.
    use_mock_agents: bool = True


# Singleton — instantiated once at import. Missing env vars raise here, not later.
settings = Settings()  # type: ignore[call-arg]
