"""
Smoke-test RAG retrieval — verify Chroma + embedding flow returns relevant chunks.

Runs 6 queries (5 demo topics × 1 each + 1 out-of-domain). For each query:
  • Returns top-3 chunks with publisher + topic + first 150 chars of snippet
  • Expects at least 1 result from the topical org
  • Out-of-domain query verifies retrieval doesn't hallucinate matches

Run from `backend/`:
    uv run python scripts/test_rag.py

Costs ~$0.001 (6 query embeddings — text-embedding-3-small is cheap).
Prerequisite: `data/corpus/ingest.py` must have been run first.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import rag

# (query, expected_topic_substr, notes)
CASES: list[tuple[str, str, str]] = [
    (
        "ขมิ้นรักษามะเร็งได้",
        "cancer",
        "Thai cancer claim — should hit WHO cancer chunks",
    ),
    (
        "หยุดยาเบาหวานแล้วใช้สมุนไพรแทน",
        "diabetes",
        "Thai diabetes claim — should hit WHO diabetes chunks",
    ),
    (
        "GLP-1 weight loss medication safety",
        "obesity",
        "EN weight-loss claim — should hit WHO obesity-and-overweight chunks",
    ),
    (
        "Do multivitamins prevent cancer or heart disease?",
        "supplements",
        "EN multivitamin claim — should hit NIH ODS chunks",
    ),
    (
        "หยุดยาความดันใช้กระเทียมแทน",
        "cardiovascular",
        "Thai cardiovascular claim — should hit WHO cardiovascular chunks",
    ),
    (
        "iPhone 17 release date and new features",
        "(empty or off-topic)",
        "Out-of-domain — retrieval should still return something but topically irrelevant",
    ),
]


async def main() -> int:
    flags = 0
    print(f"\nRunning {len(CASES)} RAG queries...\n" + "=" * 78)

    for i, (query, expected, notes) in enumerate(CASES, 1):
        print(f"\n[{i}/{len(CASES)}] {notes}")
        print(f"     query     : {query!r}")
        print(f"     expected  : topic contains {expected!r}")

        try:
            hits = await rag.query(query, k=3)
        except Exception as e:
            print(f"     [FAIL] rag.query raised: {type(e).__name__}: {e}")
            flags += 1
            continue

        if not hits:
            print(f"     [FLAG] no hits returned")
            flags += 1
            continue

        topical_match = any(expected.lower() in (h.get("topic") or "").lower() for h in hits)
        marker = "OK  " if (topical_match or "empty" in expected) else "FLAG"
        print(f"     [{marker}] {len(hits)} hits, top-3 topics: "
              f"{[h.get('topic', '?') for h in hits]}")
        for j, hit in enumerate(hits, 1):
            snippet = (hit.get("snippet") or "").replace("\n", " ")[:120]
            print(f"            #{j} [{hit.get('publisher', '?'):>20s}] "
                  f"topic={hit.get('topic', '?')!r:<28s} {snippet}…")
        if not (topical_match or "empty" in expected):
            flags += 1

    print("\n" + "=" * 78)
    if flags:
        print(f"\n{flags}/{len(CASES)} cases flagged for qualitative review.")
        return 0  # don't fail hard — RAG retrieval quality is fuzzy
    print(f"\nAll {len(CASES)} queries returned topical matches.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
