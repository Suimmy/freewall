"""
Unit tests for orchestrator helper functions.

Pure-function tests — no LLM calls. End-to-end orchestrator behavior is
covered by `tests/test_e2e.py::test_perceive_text_runs_full_mock_pipeline`.
"""

from __future__ import annotations

import pytest

from app.services.orchestrator import _verdict_to_ai_conf


class TestVerdictToAiConf:
    """
    Bridges Provenance agent's verdict-shape output → scorer-shape numeric.

    The mapping reflects honesty: 'uncertain' = 0.5 (no info), human/ai not
    pinned to extremes (we never claim 0.0 or 1.0 — calibrated humility).
    """

    def test_likely_human_maps_low(self) -> None:
        assert _verdict_to_ai_conf("likely_human") == 0.10

    def test_uncertain_maps_mid(self) -> None:
        assert _verdict_to_ai_conf("uncertain") == 0.50

    def test_likely_ai_maps_high(self) -> None:
        assert _verdict_to_ai_conf("likely_ai") == 0.85

    @pytest.mark.parametrize("garbage", ["", "garbage", "LIKELY_AI", "Uncertain", None])
    def test_unknown_verdict_defaults_to_mid(self, garbage: object) -> None:
        """
        Defensive: if agent returns unexpected enum/casing/None, we don't
        crash and don't silently bias toward 0 or 1 — return 0.50 (neutral).
        """
        # Agent.output_type=ProvenanceFinding enforces enum at Pydantic level,
        # but this tests the orchestrator's defensive fallback if that ever fails.
        assert _verdict_to_ai_conf(garbage) == 0.50  # type: ignore[arg-type]
