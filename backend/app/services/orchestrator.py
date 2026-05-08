"""
L2 pipeline orchestrator — the heart of Freewall's runtime.

Called from `routes/perceive.py` + `routes/perceive_text.py` as a background task.
For each PerceptionPayload:

  1. Classifier (L1) — emit category + detected topic
  2. Coordinator — emit dispatch decision
  3. L2 specialists in PARALLEL via `asyncio.gather` (Persuasion, Fact-Check, Provenance)
  4. Compute Sovereignty Score (`services/scorer.py` weighted-sum, decision #20)
  5. (If score < 50) Counter-Perspective Agent — second wave with topic-aware steelman
  6. Emit SSE events at each step (via `services/sse.py`)
  7. Save final ReasoningState to cache (via `core/cache.py`)

Mock vs live: controlled by `settings.use_mock_agents` (decision #18).
- True (pre-build / dev): per-topic canned findings, no LLM cost
- False (Phase 2 hackathon kickoff): real `Runner.run()` calls. See _run_live_pipeline TODO.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from agents import Runner

from app.agents.classifier import classifier_agent
from app.agents.coordinator import coordinator_agent
from app.agents.counter import counter_agent
from app.agents.fact_check import fact_check_agent
from app.agents.persuasion import persuasion_agent
from app.agents.provenance import provenance_agent
from app.config import settings
from app.core import budget, cache
from app.services import sse
from app.services.scorer import compute_score


def _format_coordinator_input(content_id: str, classifier_finding: dict[str, Any]) -> str:
    """Format text input for Coordinator agent. Matches `coordinator.md` Inputs section."""
    return (
        f"content_id: {content_id}\n"
        f"category: {classifier_finding['category']}\n"
        f"category_confidence: {classifier_finding['confidence']:.2f}"
    )


def _format_persuasion_input(text: str, category: str) -> str:
    """
    Format text input for Persuasion agent. Matches `persuasion.md` Inputs section.
    Category guides the agent toward likely tactics (e.g., ad → Cialdini scarcity).
    """
    return f"text: {text}\ncategory: {category}"


async def _run_persuasion_live(
    session_id: str, content_id: str, perception: dict[str, Any], category: str
) -> dict[str, Any]:
    """
    Run real Persuasion agent + bridge output to scorer-compatible shape.

    Bridge: agent outputs `tactics_detected` (per `PersuasionFinding`).
    Scorer reads `tactics`. We carry BOTH keys so UI gets the full structure
    while scorer's existing `_persuasion_score` doesn't need to change.
    """
    text = (perception.get("content") or {}).get("text") or ""
    pers_input = _format_persuasion_input(text, category)

    pers_result = await Runner.run(persuasion_agent, pers_input)
    _record_run_usage(pers_result)
    out = pers_result.final_output  # PersuasionFinding

    tactics_dump = [
        {
            "tactic": (
                t.tactic.value if hasattr(t.tactic, "value") else t.tactic
            ),
            "evidence": t.evidence,
            "confidence": t.confidence,
        }
        for t in out.tactics_detected
    ]

    return {
        # UI-shape (canonical from agent)
        "tactics_detected": tactics_dump,
        "intended_action": out.intended_action,
        "hidden_agenda": out.hidden_agenda,
        # Scorer-shape alias — _persuasion_score reads `tactics`
        "tactics": tactics_dump,
    }


def _format_counter_input(
    text: str, category: str, prior_findings: dict[str, Any]
) -> str:
    """
    Format text input for Counter-Perspective agent. Per `counter.md` Inputs section.

    prior_findings is JSON-serialized inline so the agent reads structured context
    (persuasion tactics, fact_check verdicts, provenance) when crafting the steelman.
    Long content texts are truncated to 1500 chars — the steelman engages the claim,
    not the entire post.
    """
    excerpt = text[:1500] + ("…" if len(text) > 1500 else "")
    # JSON dump prior_findings so agent can parse structure cleanly.
    prior_json = json.dumps(prior_findings, ensure_ascii=False, indent=2)
    return (
        f"text: {excerpt}\n"
        f"category: {category}\n"
        f"prior_findings:\n{prior_json}"
    )


async def _run_counter_live(
    session_id: str,
    content_id: str,
    perception: dict[str, Any],
    category: str,
    prior_findings: dict[str, Any],
) -> dict[str, Any]:
    """
    Run real Counter-Perspective agent. Fires lazily (orchestrator gates by score < 50).

    Output: agent's _CPFinding (loose `url: str`) → dict for SSE/cache.
    """
    text = (perception.get("content") or {}).get("text") or ""
    counter_input = _format_counter_input(text, category, prior_findings)

    counter_result = await Runner.run(counter_agent, counter_input)
    _record_run_usage(counter_result)
    out = counter_result.final_output  # _CPFinding

    sources_dump = []
    for s in (out.alternative_sources or []):
        sources_dump.append({
            "url": s.url,
            "title": s.title,
            "publisher": s.publisher,
            "credibility": (
                s.credibility.value if hasattr(s.credibility, "value") else s.credibility
            ),
        })
    return {
        "steelman": out.steelman,
        "alternative_sources": sources_dump,
        # Backward-compat alias for sidebar UI that reads `sources` key:
        "sources": sources_dump,
    }


def _format_fact_check_input(text: str, category: str, url: str) -> str:
    """
    Format text input for Fact-Check agent. Matches `fact_check.md` Inputs section.
    Agent uses category to weight medical-claim attention; uses url as topic hint.
    """
    return f"text: {text}\ncategory: {category}\nurl: {url}"


async def _run_fact_check_live(
    session_id: str, content_id: str, perception: dict[str, Any], category: str
) -> dict[str, Any]:
    """
    Run real Fact-Check agent.

    Schema match: agent's `FactCheckFinding.claims` already matches scorer's
    expected `findings["fact_check"]["claims"][i]["verdict"]` shape — minimal bridge.
    Sources are flattened to plain dicts (Pydantic models → dict for SSE/JSON).
    """
    text = (perception.get("content") or {}).get("text") or ""
    url = perception.get("url") or ""
    fc_input = _format_fact_check_input(text, category, url)

    fc_result = await Runner.run(fact_check_agent, fc_input)
    _record_run_usage(fc_result)
    out = fc_result.final_output  # _FCFinding (agent-side loose schema)

    claims_dump: list[dict[str, Any]] = []
    for c in out.claims:
        verdict = c.verdict.value if hasattr(c.verdict, "value") else c.verdict
        sources_dump = []
        for s in (c.sources or []):
            sources_dump.append({
                "title": s.title,
                "url": s.url,  # already str (agent-side _FCSource)
                "publisher": s.publisher,
                "snippet": s.snippet,
            })
        claims_dump.append({
            "claim": c.claim,
            "verdict": verdict,
            "explanation": c.explanation,
            "sources": sources_dump,
        })

    return {
        "claims": claims_dump,  # both UI + scorer read this key
    }


def _format_provenance_input(text: str, url: str) -> str:
    """
    Format text input for Provenance agent. Path C web-app has no L1 ML signals
    (no in-browser ONNX), so synthetic_signals is documented as missing.
    Agent should call source_lookup(url) tool to get domain reputation.
    """
    excerpt = text[:500] + ("…" if len(text) > 500 else "")
    return (
        f"text_excerpt: {excerpt}\n"
        f"url: {url}\n"
        f"synthetic_signals: (none — Path C web-app has no in-browser ML detection)"
    )


# Map agent's verdict-shape output → scorer-shape numeric confidences.
# Path C has no real ML signals; we use these midpoints to give the scorer
# something defensible to work with based on the agent's overall judgment.
_VERDICT_TO_AI_CONF: dict[str, float] = {
    "likely_human": 0.10,
    "uncertain": 0.50,
    "likely_ai": 0.85,
}


def _verdict_to_ai_conf(verdict: str) -> float:
    """Bridge agent's synthetic_verdict enum → numeric AI confidence for scorer."""
    return _VERDICT_TO_AI_CONF.get(verdict, 0.50)


async def _run_provenance_live(
    session_id: str, content_id: str, perception: dict[str, Any]
) -> dict[str, Any]:
    """
    Run real Provenance agent + bridge output to scorer-compatible shape.

    Returns a finding dict with BOTH:
      - Verdict-shape fields for UI (synthetic_verdict, source_verdict, reasoning)
      - Scorer-shape fields (source_reputation_category, avatar_ai_confidence,
        text_ai_confidence) — derived from the verdicts.
    """
    text = (perception.get("content") or {}).get("text") or ""
    url = perception.get("url") or ""
    prov_input = _format_provenance_input(text, url)

    prov_result = await Runner.run(provenance_agent, prov_input)
    _record_run_usage(prov_result)
    out = prov_result.final_output  # ProvenanceFinding

    synthetic_verdict = (
        out.synthetic_verdict.value if hasattr(out.synthetic_verdict, "value")
        else out.synthetic_verdict
    )
    source_verdict = (
        out.source_verdict.value if hasattr(out.source_verdict, "value")
        else out.source_verdict
    )
    ai_conf = _verdict_to_ai_conf(synthetic_verdict)

    # Step 2.17 Part A: when frontend provides AI-detection signals (Mode 2 cached
    # from offline ONNX run, or Mode 1 future live in-browser), use those instead
    # of the agent's verdict-derived placeholder. Falls back to ai_conf when None.
    sig = perception.get("synthetic_signals") or {}
    text_ai_conf = sig.get("text_ai_confidence") if sig.get("text_ai_confidence") is not None else ai_conf
    image_ai_conf = sig.get("avatar_ai_confidence") if sig.get("avatar_ai_confidence") is not None else ai_conf

    return {
        # UI-shape (verdict + reasoning)
        "synthetic_verdict": synthetic_verdict,
        "source_verdict": source_verdict,
        "reasoning": out.reasoning,
        # Scorer-shape (numeric signals — frontend-provided when available, else verdict-derived)
        "source_reputation_category": source_verdict,
        "avatar_ai_confidence": image_ai_conf,
        "text_ai_confidence": text_ai_conf,
    }

logger = logging.getLogger(__name__)


def _record_run_usage(result: Any) -> None:
    """
    Best-effort token-usage tracking from a `RunResult`.

    Agents SDK exposes the underlying Responses API responses via
    `result.raw_responses`. Each has `.usage`. Wrap in try/except since the
    SDK API surface may shift between versions — we don't want budget
    instrumentation to crash the pipeline.
    """
    try:
        for resp in getattr(result, "raw_responses", []) or []:
            usage = getattr(resp, "usage", None)
            if not usage:
                continue
            input_tokens = getattr(usage, "input_tokens", 0) or 0
            output_tokens = getattr(usage, "output_tokens", 0) or 0
            cached = 0
            details = getattr(usage, "input_tokens_details", None)
            if details is not None:
                cached = getattr(details, "cached_tokens", 0) or 0
            budget.record_usage(input_tokens, output_tokens, cached)
    except Exception as e:
        logger.warning("budget tracking skipped: %s", e)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Topic detection — covers 5 demo topics + fallback. Keywords case-insensitive.
# Order matters: more specific topics first (cardiovascular before diabetes since both share metformin etc.)
_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "weight_loss": [
        "ลดน้ำหนัก", "ลดความอ้วน", "ผอม", "ลดน้ำหน",
        "reduce", "sibutramine", "reductil", "ozempic", "wegovy", "semaglutide",
        "glp", "fat burner", "เผาผลาญ", "เหงื่อ",
    ],
    "supplements": [
        "คอลลาเจน", "collagen", "วิตามิน", "vitamin", "multivitamin",
        "อาหารเสริม", "supplement", "ปลูกผม", "ยาปลูก", "อย.",
    ],
    "cancer": [
        "มะเร็ง", "cancer", "ขมิ้น", "turmeric", "tumor", "เนื้องอก",
        "เคมีบำบัด", "chemo", "b17", "apricot",
    ],
    "cardiovascular": [
        "ความดัน", "hypertension", "blood pressure",
        "หัวใจ", "heart attack", "stroke", "หลอดเลือด",
        "statin", "cholesterol", "กระเทียม",
    ],
    "diabetes": [
        "เบาหวาน", "diabetes", "blood sugar", "น้ำตาลในเลือด",
        "insulin", "อินซูลิน", "metformin",
        "ใบกะเพรา", "มะระ", "อบเชย", "cinnamon",
    ],
}


def _detect_topic(text: str) -> str:
    """Return one of 5 demo topics + fallback. Simple substring match."""
    if not text:
        return "cancer"
    lower = text.lower()
    for topic, keywords in _TOPIC_KEYWORDS.items():
        if any(kw.lower() in lower for kw in keywords):
            return topic
    return "cancer"  # default — most viral, gives a confident demo


# Per-topic canned findings used when use_mock_agents=True.
# Each entry includes: persuasion tactics, fact_check claim, provenance signals,
# and (when triggered) a counter-perspective steelman.
_MOCK_FINDINGS: dict[str, dict[str, Any]] = {
    "cancer": {
        "persuasion": {
            "tactics": [
                {"tactic": "medical_authority_distrust", "confidence": 0.92,
                 "evidence": "หมอไม่อยากให้คุณรู้"},
                {"tactic": "miracle_cure_framing", "confidence": 0.88,
                 "evidence": "รักษาหายขาด 100%"},
                {"tactic": "false_dichotomy", "confidence": 0.74,
                 "evidence": "ไม่ต้องไปเคมี"},
            ],
        },
        "fact_check": {
            "claims": [{
                "claim": "ขมิ้นรักษามะเร็งได้",
                "verdict": "contradicted",
                "explanation": "WHO ระบุการรักษามะเร็งมาตรฐานคือ surgery + radiotherapy + "
                                "systemic therapy (chemo / hormonal / targeted). ไม่มีหลักฐาน "
                                "ขมิ้นรักษามะเร็งได้",
                "sources": [{
                    "title": "Cancer", "url": "https://www.who.int/news-room/fact-sheets/detail/cancer",
                    "publisher": "WHO",
                    "snippet": "Treatment typically involves surgery, radiotherapy, and/or systemic therapy.",
                }],
            }],
        },
        "provenance": {"source_reputation_category": "unreliable",
                        "avatar_ai_confidence": 0.91, "text_ai_confidence": 0.78},
        "counter": {
            "steelman": "Mahidol oncologists ระบุการรักษามะเร็งระยะแรกมีอัตรารักษาหายสูง — "
                        "การหยุดรักษาแผนปัจจุบัน ไป 'ทางเลือก' ไม่มีหลักฐาน เพิ่มอัตราตาย 2-5 เท่า",
            "sources": [
                {"publisher": "WHO", "url": "https://www.who.int/news-room/fact-sheets/detail/cancer"},
                {"publisher": "Mahidol Cancer Center", "url": "https://www.rama.mahidol.ac.th/cancer_center/"},
            ],
        },
    },

    "diabetes": {
        "persuasion": {
            "tactics": [
                {"tactic": "medical_authority_distrust", "confidence": 0.86,
                 "evidence": "หมอไม่บอก"},
                {"tactic": "miracle_cure_framing", "confidence": 0.82,
                 "evidence": "หายขาด"},
                {"tactic": "appeal_to_nature", "confidence": 0.78,
                 "evidence": "สมุนไพรธรรมชาติ"},
            ],
        },
        "fact_check": {
            "claims": [{
                "claim": "หยุดยาเบาหวานแล้วใช้สมุนไพรแทน",
                "verdict": "contradicted",
                "explanation": "WHO + ADA: 95% ของผู้ป่วย type 2 ต้องใช้ medication (metformin etc.) "
                                "การหยุดยา → ketoacidosis risk สูง. ไม่มี herb ใดทดแทน insulin/metformin",
                "sources": [{
                    "title": "Diabetes", "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes",
                    "publisher": "WHO",
                    "snippet": "Type 2 patients may require medications including Metformin, "
                                "Sulfonylureas, SGLT-2 inhibitors.",
                }],
            }],
        },
        "provenance": {"source_reputation_category": "unreliable",
                        "avatar_ai_confidence": 0.85, "text_ai_confidence": 0.72},
        "counter": {
            "steelman": "Endocrinologists Mahidol/Chula: เบาหวานเป็นโรคเรื้อรัง — การจัดการ "
                        "lifestyle + medication = หลักการที่พิสูจน์แล้ว 70+ ปี. หยุดยา = "
                        "เสี่ยง diabetic ketoacidosis (DKA) — ภาวะวิกฤตอาจเสียชีวิต",
            "sources": [
                {"publisher": "WHO Diabetes", "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes"},
                {"publisher": "Diabetes Association of Thailand", "url": "https://www.dmthai.org/"},
            ],
        },
    },

    "weight_loss": {
        "persuasion": {
            "tactics": [
                {"tactic": "miracle_cure_framing", "confidence": 0.90,
                 "evidence": "ลด 10 กิโลใน 2 สัปดาห์"},
                {"tactic": "social_proof", "confidence": 0.78,
                 "evidence": "หลายคน review แล้ว"},
                {"tactic": "false_authority", "confidence": 0.75,
                 "evidence": "หมอแนะนำ / ดารากิน"},
            ],
        },
        "fact_check": {
            "claims": [{
                "claim": "ยาลดน้ำหนัก Reduce-15 / Sibutramine ปลอดภัยในการใช้ระยะยาว",
                "verdict": "contradicted",
                "explanation": "Sibutramine ถูก FDA สหรัฐและ EMA ยุโรปถอนทะเบียน 2010 "
                                "เพราะเพิ่มความเสี่ยง cardiovascular events (heart attack/stroke) "
                                "16% ในผู้ป่วย high-risk. WHO obesity guideline 2025 แนะนำ GLP-1 "
                                "ภายใต้การดูแลแพทย์เท่านั้น",
                "sources": [{
                    "title": "Obesity and overweight",
                    "url": "https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight",
                    "publisher": "WHO",
                    "snippet": "WHO published guidelines on glucagon-like peptide-1 (GLP-1) therapies "
                                "for adult obesity treatment, supporting safe, equitable and appropriate "
                                "inclusion of pharmacological therapy within comprehensive chronic care.",
                }],
            }],
        },
        "provenance": {"source_reputation_category": "unreliable",
                        "avatar_ai_confidence": 0.83, "text_ai_confidence": 0.81},
        "counter": {
            "steelman": "Endocrinologists: ลดน้ำหนักยั่งยืน = lifestyle modification + medication "
                        "(GLP-1 ภายใต้แพทย์ดูแล) — ไม่ใช่ Sibutramine ที่ถอนทะเบียนทั่วโลก. "
                        "Weight loss > 0.5-1 kg/week มักเป็น muscle/water ไม่ใช่ fat loss จริง",
            "sources": [
                {"publisher": "WHO Obesity",
                 "url": "https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight"},
                {"publisher": "Mahidol-Rama Sport Medicine",
                 "url": "https://www.rama.mahidol.ac.th/atrama/issue050/believe-it-or-not"},
            ],
        },
    },

    "supplements": {
        "persuasion": {
            "tactics": [
                {"tactic": "appeal_to_nature", "confidence": 0.84,
                 "evidence": "ธรรมชาติ ไม่มีผลข้างเคียง"},
                {"tactic": "miracle_cure_framing", "confidence": 0.80,
                 "evidence": "รักษาทุกโรค"},
                {"tactic": "social_proof", "confidence": 0.72,
                 "evidence": "ป้าเพื่อนกินแล้วหาย"},
            ],
        },
        "fact_check": {
            "claims": [{
                "claim": "อาหารเสริม / multivitamin ช่วยป้องกันมะเร็ง + โรคหัวใจ",
                "verdict": "contradicted",
                "explanation": "NIH Office of Dietary Supplements: 'most studies in men and women "
                                "comparing MVMs to a placebo have found that MVMs do not reduce the risk "
                                "of CVD.' การกินอาหารเสริมไม่ใช่ทดแทนอาหารดี + ออกกำลังกาย",
                "sources": [{
                    "title": "Multivitamin/mineral Supplements",
                    "url": "https://ods.od.nih.gov/factsheets/MVMS-Consumer/",
                    "publisher": "NIH ODS",
                    "snippet": "MVMs cannot take the place of eating a variety of foods that are "
                                "important to a healthy diet.",
                }],
            }],
        },
        "provenance": {"source_reputation_category": "unreliable",
                        "avatar_ai_confidence": 0.88, "text_ai_confidence": 0.74},
        "counter": {
            "steelman": "Mahidol nutrition: คนที่กิน balanced diet ไม่ขาดสารอาหาร — supplement "
                        "ใช้เฉพาะกรณี deficiency จริง (folic acid ในหญิงตั้งครรภ์, B12 ใน vegan, "
                        "vitamin D ใน elderly). 'รักษาทุกโรค' = red flag ทั้งหมด",
            "sources": [
                {"publisher": "NIH ODS", "url": "https://ods.od.nih.gov/factsheets/MVMS-Consumer/"},
                {"publisher": "Mahidol-Rama Dermatology",
                 "url": "https://www.rama.mahidol.ac.th/atrama/issue039/believe-it-or-not"},
            ],
        },
    },

    "cardiovascular": {
        "persuasion": {
            "tactics": [
                {"tactic": "medical_authority_distrust", "confidence": 0.88,
                 "evidence": "หมอไม่อยากให้รู้"},
                {"tactic": "appeal_to_nature", "confidence": 0.82,
                 "evidence": "กระเทียมแทนยา"},
                {"tactic": "false_dichotomy", "confidence": 0.76,
                 "evidence": "ยา vs ธรรมชาติ"},
            ],
        },
        "fact_check": {
            "claims": [{
                "claim": "หยุดยาความดัน / statin ใช้สมุนไพรแทน",
                "verdict": "contradicted",
                "explanation": "WHO: CVD เป็นสาเหตุการตายอันดับ 1 ของโลก (~32% ของการตายทั้งหมด). "
                                "Essential medications (ACE inhibitors, beta-blockers, statins) "
                                "ลดความเสี่ยง heart attack/stroke 25-50%. ไม่มี herb ที่ทดแทน",
                "sources": [{
                    "title": "Cardiovascular diseases",
                    "url": "https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)",
                    "publisher": "WHO",
                    "snippet": "Essential medications: Aspirin, Beta-blockers, Calcium channel blockers, "
                                "Angiotensin-converting enzyme inhibitors, Diuretics, Statins.",
                }],
            }],
        },
        "provenance": {"source_reputation_category": "unreliable",
                        "avatar_ai_confidence": 0.79, "text_ai_confidence": 0.69},
        "counter": {
            "steelman": "Cardiologists: ความดัน + cholesterol เป็น silent killers — ไม่มีอาการจน "
                        "เกิด heart attack/stroke. Statin + ACE inhibitor ลดอัตราตายสูงมาก ตาม "
                        "evidence-based clinical trials > 30 ปี. Garlic ผงผสมอาหารดีต่อ flavor "
                        "แต่ไม่ใช่ replacement",
            "sources": [
                {"publisher": "WHO CVD",
                 "url": "https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)"},
                {"publisher": "Heart Association of Thailand", "url": "http://www.thaiheart.org/"},
            ],
        },
    },
}


async def replay_cached(
    session_id: str, content_id: str, state: dict[str, Any]
) -> None:
    """
    Replay cached `state` as SSE events for instant UX on cache hit (decision #4).

    Re-emits the same event sequence a fresh run would, with small delays so the
    UI's agent pills animate (≈1-2s total replay vs ≈10-15s for a real run).
    No LLM calls — cost is $0.
    """
    logger.info("CACHE HIT: replaying state for content_id=%s", content_id)

    # ---- L1 Classifier ----
    sse.emit(session_id, {
        "type": "agent_started", "session_id": session_id, "content_id": content_id,
        "agent": "classifier", "timestamp": _now_iso(),
    })
    await asyncio.sleep(0.08)
    sse.emit(session_id, {
        "type": "agent_finished", "session_id": session_id, "content_id": content_id,
        "agent": "classifier", "finding": state.get("classifier", {}),
        "timestamp": _now_iso(),
    })

    # ---- L2 Coordinator ----
    sse.emit(session_id, {
        "type": "agent_started", "session_id": session_id, "content_id": content_id,
        "agent": "coordinator", "timestamp": _now_iso(),
    })
    await asyncio.sleep(0.12)
    dispatched = state.get("dispatched_agents", [])
    skipped = state.get("skipped_agents", [])
    # Counter is in dispatched_agents but NOT a workers-dispatch event — emit only the 3 specialists.
    workers_dispatched = [a for a in dispatched if a != "counter"]
    sse.emit(session_id, {
        "type": "coordinator_dispatched",
        "session_id": session_id, "content_id": content_id,
        "timestamp": _now_iso(),
        "dispatched_agents": workers_dispatched, "skipped_agents": skipped,
    })
    sse.emit(session_id, {
        "type": "agent_finished", "session_id": session_id, "content_id": content_id,
        "agent": "coordinator", "finding": state.get("coordinator", {}),
        "timestamp": _now_iso(),
    })

    # ---- L2 specialists (all started together — match live parallel UX) ----
    for agent in workers_dispatched:
        sse.emit(session_id, {
            "type": "agent_started", "session_id": session_id, "content_id": content_id,
            "agent": agent, "timestamp": _now_iso(),
        })
    # Stagger finished events lightly so pills resolve at different times
    for i, agent in enumerate(workers_dispatched):
        await asyncio.sleep(0.15 + i * 0.05)
        sse.emit(session_id, {
            "type": "agent_finished", "session_id": session_id, "content_id": content_id,
            "agent": agent, "finding": state.get(agent, {}),
            "timestamp": _now_iso(),
        })

    # ---- Score ----
    sse.emit(session_id, {
        "type": "score_update", "session_id": session_id, "content_id": content_id,
        "score": state.get("score", {}), "timestamp": _now_iso(),
    })

    # ---- Counter (if present in cached state) ----
    if "counter" in state:
        sse.emit(session_id, {
            "type": "agent_started", "session_id": session_id, "content_id": content_id,
            "agent": "counter", "timestamp": _now_iso(),
        })
        await asyncio.sleep(0.25)
        sse.emit(session_id, {
            "type": "agent_finished", "session_id": session_id, "content_id": content_id,
            "agent": "counter", "finding": state["counter"],
            "timestamp": _now_iso(),
        })

    # ---- Final ----
    sse.emit(session_id, {
        "type": "final", "session_id": session_id, "content_id": content_id,
        "state": state, "timestamp": _now_iso(),
    })

    logger.info("replay END: session=%s content=%s", session_id, content_id)


async def run_pipeline(perception: dict[str, Any]) -> None:
    """
    Run the full L2 pipeline for one perception payload.

    Routes mock vs live based on `settings.use_mock_agents`.
    Note: cache hit/miss branching happens in the route handler
    (`api/routes/perceive_text.py`) — this function always runs the full pipeline.

    `_skip_cache_write` (set by route handler when force_fresh=true) is honored
    at the end of each pipeline branch — Mode 1 paste box never writes cache.
    """
    session_id = perception["session_id"]
    content_id = perception["content_id"]
    text = (perception.get("content") or {}).get("text") or ""
    skip_cache_write = bool(perception.get("_skip_cache_write"))

    logger.info(
        "pipeline START: session=%s content=%s mock=%s text_len=%d skip_cache=%s",
        session_id, content_id, settings.use_mock_agents, len(text), skip_cache_write,
    )

    if settings.use_mock_agents:
        await _run_mock_pipeline(session_id, content_id, text, skip_cache_write)
    else:
        await _run_live_pipeline(session_id, content_id, perception, skip_cache_write)


async def _run_mock_pipeline(
    session_id: str, content_id: str, text: str, skip_cache_write: bool = False,
) -> None:
    """Mock pipeline — emits all 6 agent events with topic-aware findings."""
    topic = _detect_topic(text)
    findings_pack = _MOCK_FINDINGS[topic]
    logger.info("mock pipeline: topic=%s session=%s", topic, session_id)

    # ---- L1 Classifier ----
    classifier_finding: dict[str, Any] = {
        "category": "health_claim", "confidence": 0.92, "topic": topic,
    }
    sse.emit(session_id, {
        "type": "agent_started", "session_id": session_id, "content_id": content_id,
        "agent": "classifier", "timestamp": _now_iso(),
    })
    await asyncio.sleep(0.08)  # ~80 ms — Layer 1 fast classification
    sse.emit(session_id, {
        "type": "agent_finished", "session_id": session_id, "content_id": content_id,
        "agent": "classifier", "finding": classifier_finding,
        "timestamp": _now_iso(),
    })

    # ---- L2 Coordinator ----
    dispatched = ["persuasion", "fact_check", "provenance"]
    coordinator_finding: dict[str, Any] = {
        "dispatched": dispatched,
        "reason": f"category=health_claim, topic={topic}",
    }
    sse.emit(session_id, {
        "type": "agent_started", "session_id": session_id, "content_id": content_id,
        "agent": "coordinator", "timestamp": _now_iso(),
    })
    await asyncio.sleep(0.15)
    sse.emit(session_id, {
        "type": "coordinator_dispatched",  # legacy event for backward compat
        "session_id": session_id, "content_id": content_id,
        "timestamp": _now_iso(),
        "dispatched_agents": dispatched, "skipped_agents": [],
    })
    sse.emit(session_id, {
        "type": "agent_finished", "session_id": session_id, "content_id": content_id,
        "agent": "coordinator", "finding": coordinator_finding,
        "timestamp": _now_iso(),
    })

    # ---- L2 specialists in parallel ----
    for agent in dispatched:
        sse.emit(session_id, {
            "type": "agent_started", "session_id": session_id, "content_id": content_id,
            "agent": agent, "timestamp": _now_iso(),
        })

    async def _run(name: str, delay_ms: int) -> tuple[str, dict[str, Any]]:
        await asyncio.sleep(delay_ms / 1000.0)
        # Emit agent_finished as soon as THIS specialist completes (mirror live
        # pipeline behavior — no batched emission after gather).
        finding = findings_pack[name]
        sse.emit(session_id, {
            "type": "agent_finished", "session_id": session_id, "content_id": content_id,
            "agent": name, "finding": finding, "timestamp": _now_iso(),
        })
        return name, finding

    # Stagger so the UI sees agents finish at different times
    results = await asyncio.gather(
        _run("persuasion", 800),
        _run("fact_check", 1200),
        _run("provenance", 600),
    )
    findings: dict[str, Any] = {name: finding for name, finding in results}

    # ---- Score (weighted-sum) ----
    score = compute_score(findings)
    sse.emit(session_id, {
        "type": "score_update", "session_id": session_id, "content_id": content_id,
        "score": score.__dict__, "timestamp": _now_iso(),
    })

    # ---- Counter-Perspective if score < 50 ----
    if score.value < 50:
        sse.emit(session_id, {
            "type": "agent_started", "session_id": session_id, "content_id": content_id,
            "agent": "counter", "timestamp": _now_iso(),
        })
        await asyncio.sleep(0.8)  # high-effort steelman
        counter_finding = findings_pack["counter"]
        findings["counter"] = counter_finding
        sse.emit(session_id, {
            "type": "agent_finished", "session_id": session_id, "content_id": content_id,
            "agent": "counter", "finding": counter_finding, "timestamp": _now_iso(),
        })
        dispatched.append("counter")

    # ---- Final state + cache ----
    state = {
        "score": score.__dict__,
        "topic": topic,
        "classifier": classifier_finding,
        "coordinator": coordinator_finding,
        "dispatched_agents": dispatched,
        "skipped_agents": [],
        **findings,
    }
    if not skip_cache_write:
        cache.set(content_id, state)
    sse.emit(session_id, {
        "type": "final", "session_id": session_id, "content_id": content_id,
        "state": state, "timestamp": _now_iso(),
    })

    logger.info(
        "pipeline END (mock): session=%s topic=%s score=%s counter=%s",
        session_id, topic, score.value, "counter" in findings,
    )


async def _run_live_pipeline(
    session_id: str, content_id: str, perception: dict[str, Any],
    skip_cache_write: bool = False,
) -> None:
    """
    Live pipeline — all 6 agents wired with real `Runner.run` calls (Steps 2.3-2.11).

    Sequence:
      1. L1 Classifier            → category + confidence
      2. L2 Coordinator           → dispatch decision (workers + skipped)
      3. L2 specialists (parallel) → Persuasion + Fact-Check + Provenance
      4. Sovereignty Score        → weighted-sum from agent outputs
      5. L2 Counter (lazy)        → only when score < 50
      6. Cache + emit final state

    `_MOCK_FINDINGS` + `_detect_topic` are only used by `_run_mock_pipeline`
    (when `USE_MOCK_AGENTS=true`); the live path computes `topic` for UI
    metadata only — it does NOT depend on mock findings.
    """
    text = (perception.get("content") or {}).get("text") or ""
    topic = _detect_topic(text)  # UI hint only — flags one of 5 demo topics
    logger.info("live pipeline START: topic=%s session=%s", topic, session_id)

    # ---- L1 Classifier (REAL) ----
    sse.emit(session_id, {
        "type": "agent_started", "session_id": session_id, "content_id": content_id,
        "agent": "classifier", "timestamp": _now_iso(),
    })
    try:
        classifier_result = await Runner.run(classifier_agent, text)
    except Exception as e:
        logger.exception("classifier Runner.run failed")
        sse.emit(session_id, {
            "type": "error", "session_id": session_id, "content_id": content_id,
            "error": f"classifier failed: {type(e).__name__}: {e}",
            "timestamp": _now_iso(),
        })
        return
    _record_run_usage(classifier_result)
    classifier_output = classifier_result.final_output  # ClassifierOutput
    classifier_finding: dict[str, Any] = {
        "category": classifier_output.category.value
        if hasattr(classifier_output.category, "value") else classifier_output.category,
        "confidence": classifier_output.confidence,
        "topic": topic,  # UI metadata — one of 5 demo topics or fallback
    }
    sse.emit(session_id, {
        "type": "agent_finished", "session_id": session_id, "content_id": content_id,
        "agent": "classifier", "finding": classifier_finding,
        "timestamp": _now_iso(),
    })

    # ---- L2 Coordinator (REAL) ----
    sse.emit(session_id, {
        "type": "agent_started", "session_id": session_id, "content_id": content_id,
        "agent": "coordinator", "timestamp": _now_iso(),
    })
    coord_input = _format_coordinator_input(content_id, classifier_finding)
    try:
        coord_result = await Runner.run(coordinator_agent, coord_input)
    except Exception as e:
        logger.exception("coordinator Runner.run failed")
        sse.emit(session_id, {
            "type": "error", "session_id": session_id, "content_id": content_id,
            "error": f"coordinator failed: {type(e).__name__}: {e}",
            "timestamp": _now_iso(),
        })
        return
    _record_run_usage(coord_result)
    coord_output = coord_result.final_output  # CoordinatorOutput
    # Convert StrEnum values to plain strings for SSE/JSON serialization
    dispatched: list[str] = [
        a.value if hasattr(a, "value") else a for a in coord_output.dispatched_agents
    ]
    skipped: list[dict[str, str]] = [
        {
            "agent": s.agent.value if hasattr(s.agent, "value") else s.agent,
            "reason": s.reason,
        }
        for s in coord_output.skipped_agents
    ]
    coordinator_finding: dict[str, Any] = {
        "dispatched": dispatched,
        "skipped": skipped,
        "reason": f"category={classifier_finding['category']}, "
                  f"confidence={classifier_finding['confidence']:.2f}",
    }
    sse.emit(session_id, {
        "type": "coordinator_dispatched",
        "session_id": session_id, "content_id": content_id,
        "timestamp": _now_iso(),
        "dispatched_agents": dispatched, "skipped_agents": skipped,
    })
    sse.emit(session_id, {
        "type": "agent_finished", "session_id": session_id, "content_id": content_id,
        "agent": "coordinator", "finding": coordinator_finding,
        "timestamp": _now_iso(),
    })

    # ---- L2 specialists (parallel, all LIVE) ----
    # Iterate real `dispatched` from Coordinator. Skipped agents are not run.
    for agent in dispatched:
        sse.emit(session_id, {
            "type": "agent_started", "session_id": session_id, "content_id": content_id,
            "agent": agent, "timestamp": _now_iso(),
        })

    category = classifier_finding["category"]

    async def _run(name: str) -> tuple[str, dict[str, Any]]:
        """
        Dispatch one specialist by name. Each branch wraps Runner.run in
        try/except so a single agent's failure produces a benign finding
        (scorer gets neutral contribution) rather than aborting the pipeline.
        """
        if name == "persuasion":
            try:
                finding = await _run_persuasion_live(
                    session_id, content_id, perception, category
                )
                return name, finding
            except Exception as e:
                logger.exception("persuasion Runner.run failed")
                return name, {
                    "tactics_detected": [],
                    "tactics": [],
                    "intended_action": "(unknown — persuasion agent error)",
                    "hidden_agenda": None,
                    "_error": f"{type(e).__name__}: {e}",
                }
        if name == "fact_check":
            try:
                finding = await _run_fact_check_live(
                    session_id, content_id, perception, category
                )
                return name, finding
            except Exception as e:
                logger.exception("fact_check Runner.run failed")
                return name, {
                    "claims": [],
                    "_error": f"{type(e).__name__}: {e}",
                }
        if name == "provenance":
            try:
                finding = await _run_provenance_live(session_id, content_id, perception)
                return name, finding
            except Exception as e:
                logger.exception("provenance Runner.run failed")
                return name, {
                    "synthetic_verdict": "uncertain",
                    "source_verdict": "unknown",
                    "reasoning": f"Provenance agent error: {type(e).__name__}",
                    "source_reputation_category": "unknown",
                    "avatar_ai_confidence": 0.5,
                    "text_ai_confidence": 0.5,
                }
        # Coordinator should never dispatch an unknown specialist (DispatchableAgent
        # enum constrains this), but defend the orchestrator if it ever does.
        logger.error("unknown specialist dispatched: %s", name)
        return name, {"_error": f"unknown specialist: {name}"}

    async def _run_and_emit(name: str) -> tuple[str, dict[str, Any]]:
        # Emit agent_finished as soon as THIS specialist completes — not batched
        # after asyncio.gather() returns. Without this wrapper, all 3 finished
        # events fire at once when the slowest specialist completes, hiding the
        # real per-agent timing in the UI.
        result_name, finding = await _run(name)
        sse.emit(session_id, {
            "type": "agent_finished", "session_id": session_id, "content_id": content_id,
            "agent": result_name, "finding": finding, "timestamp": _now_iso(),
        })
        return result_name, finding

    results = await asyncio.gather(*(_run_and_emit(name) for name in dispatched))
    findings: dict[str, Any] = {name: finding for name, finding in results}

    # ---- Score (weighted-sum) ----
    score = compute_score(findings)
    sse.emit(session_id, {
        "type": "score_update", "session_id": session_id, "content_id": content_id,
        "score": score.__dict__, "timestamp": _now_iso(),
    })

    # ---- Counter-Perspective if score < 50 (LIVE — Step 2.11 wired) ----
    if score.value < 50:
        sse.emit(session_id, {
            "type": "agent_started", "session_id": session_id, "content_id": content_id,
            "agent": "counter", "timestamp": _now_iso(),
        })
        try:
            counter_finding = await _run_counter_live(
                session_id, content_id, perception, category, findings,
            )
        except Exception as e:
            logger.exception("counter Runner.run failed")
            counter_finding = {
                "steelman": (
                    "Counter-Perspective is temporarily unavailable. "
                    "Consult mainstream medical authorities (WHO/CDC/Mayo Clinic) "
                    "before acting on this content's claims."
                ),
                "alternative_sources": [],
                "sources": [],
                "_error": f"{type(e).__name__}: {e}",
            }
        findings["counter"] = counter_finding
        sse.emit(session_id, {
            "type": "agent_finished", "session_id": session_id, "content_id": content_id,
            "agent": "counter", "finding": counter_finding, "timestamp": _now_iso(),
        })
        dispatched.append("counter")

    # ---- Final state + cache ----
    state = {
        "score": score.__dict__,
        "topic": topic,
        "classifier": classifier_finding,
        "coordinator": coordinator_finding,
        "dispatched_agents": dispatched,
        "skipped_agents": skipped,
        **findings,
    }
    if not skip_cache_write:
        cache.set(content_id, state)
    else:
        logger.info("force_fresh=true: skipping cache.set for content=%s", content_id)
    sse.emit(session_id, {
        "type": "final", "session_id": session_id, "content_id": content_id,
        "state": state, "timestamp": _now_iso(),
    })

    logger.info(
        "live pipeline END: session=%s topic=%s category=%s confidence=%.2f "
        "dispatched=%s skipped=%d score=%s counter=%s",
        session_id, topic, classifier_finding["category"], classifier_finding["confidence"],
        dispatched, len(skipped), score.value, "counter" in findings,
    )
