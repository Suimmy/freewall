"""
Sovereignty Score computation — weighted-sum (per CLAUDE.md decision #20).

Was XGBoost+fallback (decision #6 original); pivoted 2026-05-07 to weighted-sum
primary after team voted out 200-post curation. Pitch reframe: "interpretable,
EU AI Act-aligned, transparent formula" instead of "distillation of gpt-5.5".

Score interpretation (per shared/ENUMS.md ScoreBand):
  70-100  safe
  30-69   caution
  0-29    high_risk

Phase 1: this module computes from agent findings (real or mock).
Phase 4: tune weights against demo content.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal

logger = logging.getLogger(__name__)

ScoreBand = Literal["safe", "caution", "high_risk"]


@dataclass
class ScoreResult:
    value: float            # 0-100
    band: ScoreBand
    confidence: float       # 0-1
    contributing_factors: list[dict[str, Any]]


# Weights — sum to 1.0. Tunable Phase 4 against demo content.
# Each component subtracts from a base of 100 proportional to its "danger signal".
WEIGHTS = {
    "persuasion": 0.30,         # detected unethical tactics
    "fact_check": 0.30,         # claims contradicted by RAG
    "provenance_source": 0.20,  # source reputation
    "provenance_image": 0.10,   # avatar AI-generation confidence
    "provenance_text": 0.10,    # text AI-generation confidence
}

# Source reputation category → trust score (0=most distrusted, 1=most trusted)
# unknown=0.2 (was 0.4, lowered 2026-05-08): no reputation signal = skeptical baseline,
# not nearly-neutral. Sanity: legit news pasted without URL still scores ≥70.
_SOURCE_TRUST = {
    "credible": 1.0,
    "mixed": 0.5,
    "unknown": 0.2,
    "unreliable": 0.0,
}

# Persuasion: a "saturating" curve — first few tactics matter most.
# 0 tactics → score 1.0 (no penalty); 5 tactics → score 0.0 (full penalty).
_PERSUASION_SATURATION = 5


def _band_for(value: float) -> ScoreBand:
    """Map score to band."""
    if value >= 70:
        return "safe"
    if value >= 30:
        return "caution"
    return "high_risk"


def _persuasion_score(findings: dict[str, Any]) -> tuple[float, str]:
    """0=many tactics (bad), 1=no tactics (good). Saturates at 5+ tactics."""
    persuasion = findings.get("persuasion") or {}
    tactics = persuasion.get("tactics") or []
    n = len(tactics)
    if n == 0:
        return 1.0, "no manipulation tactics detected"
    safety = max(0.0, 1.0 - n / _PERSUASION_SATURATION)
    return safety, f"{n} manipulation tactic(s) detected"


def _fact_check_score(findings: dict[str, Any]) -> tuple[float, str]:
    """0=contradicted, 1=supported, 0.5=unverifiable/no_claim."""
    fact = findings.get("fact_check") or {}
    claims = fact.get("claims") or []
    if not claims:
        return 0.5, "no claims to fact-check"

    contradicted = sum(1 for c in claims if c.get("verdict") == "contradicted")
    supported = sum(1 for c in claims if c.get("verdict") == "supported")
    total = len(claims)

    if contradicted > 0 and supported == 0:
        return 0.0, f"{contradicted}/{total} claim(s) contradicted by sources"
    if supported > 0 and contradicted == 0:
        return 1.0, f"{supported}/{total} claim(s) supported by sources"
    if contradicted > 0 and supported > 0:
        return 0.3, f"mixed: {contradicted} contradicted, {supported} supported"
    return 0.5, f"{total} claim(s) unverifiable"


def _provenance_source_score(findings: dict[str, Any]) -> tuple[float, str]:
    """Source reputation → trust 0..1."""
    prov = findings.get("provenance") or {}
    cat = prov.get("source_reputation_category") or "unknown"
    return _SOURCE_TRUST.get(cat, 0.4), f"source: {cat}"


def _provenance_image_score(findings: dict[str, Any]) -> tuple[float, str]:
    """1 - avatar AI confidence. Higher AI confidence = lower trust."""
    prov = findings.get("provenance") or {}
    ai_conf = prov.get("avatar_ai_confidence")
    if ai_conf is None:
        return 0.5, "no avatar signal"
    return max(0.0, 1.0 - ai_conf), f"avatar AI-confidence={ai_conf:.2f}"


def _provenance_text_score(findings: dict[str, Any]) -> tuple[float, str]:
    """1 - text AI confidence. Higher AI confidence = lower trust."""
    prov = findings.get("provenance") or {}
    ai_conf = prov.get("text_ai_confidence")
    if ai_conf is None:
        return 0.5, "no text-AI signal"
    return max(0.0, 1.0 - ai_conf), f"text AI-confidence={ai_conf:.2f}"


def compute_score(findings: dict[str, Any]) -> ScoreResult:
    """
    Compute Sovereignty Score 0-100 from agent findings via weighted sum.

    Each component returns a "trust score" 0..1 (1=trusted, 0=distrusted).
    Final value = 100 × sum(weight_i × trust_i).
    """
    logger.debug("scorer.compute_score: findings=%s", list(findings.keys()))

    components: list[tuple[str, float, float, str]] = [
        ("persuasion", WEIGHTS["persuasion"], *_persuasion_score(findings)),
        ("fact_check", WEIGHTS["fact_check"], *_fact_check_score(findings)),
        ("provenance_source", WEIGHTS["provenance_source"], *_provenance_source_score(findings)),
        ("provenance_image", WEIGHTS["provenance_image"], *_provenance_image_score(findings)),
        ("provenance_text", WEIGHTS["provenance_text"], *_provenance_text_score(findings)),
    ]

    weighted_total = sum(weight * trust for _, weight, trust, _ in components)
    value = round(100.0 * weighted_total, 1)
    band = _band_for(value)

    contributing_factors = [
        {
            "factor": name,
            "weight": weight,
            "trust": round(trust, 3),
            "contribution": round(100 * weight * trust, 1),
            "explanation": explain,
        }
        for name, weight, trust, explain in components
    ]

    confidence = _confidence(findings)

    return ScoreResult(
        value=value,
        band=band,
        confidence=confidence,
        contributing_factors=contributing_factors,
    )


def _confidence(findings: dict[str, Any]) -> float:
    """How many of the 3 agents we got results from. Range 0.33..1.0."""
    have = 0
    for key in ("persuasion", "fact_check", "provenance"):
        if findings.get(key):
            have += 1
    return round(have / 3.0, 2) if have > 0 else 0.0
