"""
Shared pytest fixtures + env setup.

CRITICAL: env setup happens at module level (top of file) — runs BEFORE
test modules are imported (and therefore before `from app.config import
settings` is evaluated, which requires OPENAI_API_KEY).

Tests must NOT make real OpenAI calls; the dummy key here just lets the
app import cleanly. Real-API integration tests should set
OPENAI_API_KEY in the env BEFORE pytest runs and use `@pytest.mark.integration`
(skipped by default).
"""

from __future__ import annotations

import os

# Set BEFORE any test modules import app.* — pydantic-settings reads at import time.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-stub-not-real-do-not-call-api")

import uuid

import pytest


@pytest.fixture
def fresh_session_id() -> str:
    """Unique session_id per test."""
    return str(uuid.uuid4())


@pytest.fixture
def fresh_content_id() -> str:
    """Unique content_id per test."""
    return f"test_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_perception_payload(fresh_session_id: str, fresh_content_id: str) -> dict:
    """Minimal valid PerceptionPayload-shaped dict for stub-level tests."""
    return {
        "session_id": fresh_session_id,
        "content_id": fresh_content_id,
        "url": "https://example.com/test",
        "captured_at": "2026-05-09T14:23:11.482Z",
        "content": {"text": "test content", "category": "social"},
        "source": {"domain": "example.com", "reputation": "unknown"},
    }
