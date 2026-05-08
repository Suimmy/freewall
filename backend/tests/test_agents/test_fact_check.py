"""
Fact-Check Agent — output schema sanity.

Same pattern as test_persuasion: schema-only tests run without LLM, guard
against verdict hallucination + missing-source mistakes for supported/
contradicted verdicts. Real-LLM + Chroma tests are skipped by default.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.agents.fact_check import fact_check_agent
from app.schemas.reasoning import FactCheckFinding


def test_fact_check_agent_loads_with_tools() -> None:
    """Agent imports cleanly + has rag_search tool wired."""
    assert fact_check_agent.name == "fact_check"
    assert fact_check_agent.model == "gpt-5.5"
    assert fact_check_agent.tools is not None
    assert len(fact_check_agent.tools) == 1   # rag_search


def test_finding_accepts_contradicted_with_sources() -> None:
    """Realistic contradicted claim with supporting source."""
    payload = {
        "claims": [
            {
                "claim": "Cinnamon cures diabetes",
                "verdict": "contradicted",
                "explanation": "Major medical authorities state cinnamon does not cure diabetes.",
                "sources": [
                    {
                        "title": "WHO diabetes fact sheet",
                        "url": "https://who.int/diabetes",
                        "publisher": "WHO",
                        "snippet": "Diabetes management requires...",
                    }
                ],
            }
        ]
    }
    finding = FactCheckFinding(**payload)
    assert finding.claims[0].verdict == "contradicted"
    assert finding.claims[0].sources[0].publisher == "WHO"


def test_finding_accepts_not_a_claim_with_no_sources() -> None:
    """Pure-opinion content → 'not_a_claim' verdict with empty sources is valid."""
    payload = {
        "claims": [
            {
                "claim": "I love mornings",
                "verdict": "not_a_claim",
                "explanation": "Pure opinion, no factual content to verify.",
                "sources": [],
            }
        ]
    }
    finding = FactCheckFinding(**payload)
    assert finding.claims[0].verdict == "not_a_claim"
    assert finding.claims[0].sources == []


def test_finding_rejects_unknown_verdict() -> None:
    """Hallucinated verdict name → ValidationError. High-blast-radius."""
    payload = {
        "claims": [
            {"claim": "x", "verdict": "totally_made_up", "explanation": "...", "sources": []}
        ]
    }
    with pytest.raises(ValidationError):
        FactCheckFinding(**payload)


def test_finding_accepts_empty_claims_list() -> None:
    """Valid edge case — agent failed to extract claims (rare but possible)."""
    finding = FactCheckFinding(claims=[])
    assert finding.claims == []


@pytest.mark.skip(
    reason="Costs LLM tokens + needs Chroma corpus ingested (Step 2.8). "
    "Run on demand via `scripts/test_live_fact_check.py` after 2.8 lands."
)
def test_fact_check_contradicts_known_misinfo() -> None:
    """Real-LLM + Chroma: cinnamon claim should be contradicted with WHO source.
    Skipped by default — costs tokens AND requires corpus ingested.
    """
    pass
