"""
Persuasion Agent — output schema sanity.

Schema tests run without LLM (cheap, fast, always-on) and guard against
LLM hallucinating tactic names outside the 21-value enum. Real-LLM tests
are skipped by default (need API key + cost budget).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.agents.persuasion import persuasion_agent
from app.schemas.reasoning import PersuasionFinding


def test_persuasion_agent_loads_with_correct_shape() -> None:
    """Agent instance imports cleanly with expected metadata."""
    assert persuasion_agent.name == "persuasion"
    assert persuasion_agent.model == "gpt-5.5"
    assert persuasion_agent.model_settings is not None
    assert persuasion_agent.model_settings.reasoning is not None
    assert persuasion_agent.model_settings.reasoning.effort == "medium"


def test_finding_accepts_valid_tactic() -> None:
    """A known-good payload parses cleanly."""
    payload = {
        "tactics_detected": [
            {
                "tactic": "fear_mongering",
                "evidence": "Big Pharma doesn't want you to know",
                "confidence": 0.85,
            }
        ],
        "intended_action": "buy supplement",
        "hidden_agenda": "affiliate revenue",
    }
    finding = PersuasionFinding(**payload)
    assert len(finding.tactics_detected) == 1
    assert finding.tactics_detected[0].tactic == "fear_mongering"


def test_finding_rejects_unknown_tactic() -> None:
    """Hallucinated tactic name → schema validation error.

    This is THE high-blast-radius test: LLMs occasionally invent enum values.
    Schema rejection catches them before they reach the UI as gibberish.
    """
    payload = {
        "tactics_detected": [
            {"tactic": "made_up_tactic_xyz", "evidence": "x", "confidence": 0.5},
        ],
        "intended_action": "test",
    }
    with pytest.raises(ValidationError):
        PersuasionFinding(**payload)


def test_finding_rejects_confidence_out_of_range() -> None:
    """confidence must be 0-1; LLMs sometimes return raw percentages."""
    payload = {
        "tactics_detected": [
            {"tactic": "fear_mongering", "evidence": "x", "confidence": 85.0},
        ],
        "intended_action": "test",
    }
    with pytest.raises(ValidationError):
        PersuasionFinding(**payload)


def test_finding_accepts_empty_tactics_list() -> None:
    """Valid for benign content — no tactics found is a real outcome."""
    finding = PersuasionFinding(
        tactics_detected=[],
        intended_action="general informational reading",
        hidden_agenda=None,
    )
    assert finding.tactics_detected == []


@pytest.mark.skip(
    reason="Costs LLM tokens; run on demand via `scripts/test_live_persuasion.py` instead. "
    "Pytest stays free + deterministic via mock pipeline."
)
def test_persuasion_detects_fear_mongering_in_classic_misinfo() -> None:
    """Real-LLM: 'doctors hate this trick' should detect fear_mongering OR
    misrepresentation_of_expertise. Skipped by default — costs tokens.
    """
    pass
