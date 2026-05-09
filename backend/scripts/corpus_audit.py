"""
Demo corpus audit (CLAUDE.md decision #14, Phase 4.2).

Extracts atomic claims from 10 finalized demo posts (8 feed + 2 Mode 1 examples),
runs dual-language rag_search per claim, prints coverage table for Suim review.

Run from `backend/`:
    uv run python scripts/corpus_audit.py > scripts/corpus_audit_output.txt

Cost: ~$0.001 (embedding only, Chroma is local).
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import rag


@dataclass
class Claim:
    post_id: str
    claim_orig: str
    claim_lang: str       # "th" | "en"
    claim_translated: str # paired translation for dual-search
    note: str = ""        # extraction rationale or skip reason


# Refutable claims only — manipulation/provenance meta-observations skipped.
# Per Step 2.9 limit: ≤3 atomic claims per post.
CLAIMS: list[Claim] = [
    # feed_001 — Aew Aew temple cure testimony
    Claim("feed_001_temple_cure",
          "วัดคำประมง + ยาญี่ปุ่น + สมุนไพร + สวดมนต์ รักษามะเร็งตับระยะสุดท้ายได้",
          "th",
          "Temple + Japanese medicine + herbs + chanting cures terminal liver cancer"),
    Claim("feed_001_temple_cure",
          "ก้อนเนื้อในสมองมาจากก้อนเนื้อที่ตับ",
          "th",
          "Brain tumors come from liver tumors"),
    # 3rd narrative claim ("ผ่าสมอง → ก้อนตับหาย") = personal anecdote, can't fact-check directly

    # feed_002 — Radican supplement
    Claim("feed_002_radican",
          "Radican อาหารเสริม ลดสารพิษสะสม กระตุ้นซ่อมเซลล์ ชะลอวัย",
          "th",
          "Radican supplement detoxes the body, repairs cells, slows aging"),
    Claim("feed_002_radican",
          "อาหารเสริมเห็นผลภายใน 14 วัน หน้าเด็กลง",
          "th",
          "Supplement visibly makes face look younger in 14 days"),

    # feed_009 — Chula targeted therapy (LEGIT)
    Claim("feed_009_targeted_therapy",
          "ยามุ่งเป้ารักษามะเร็ง มีผลข้างเคียงน้อยกว่าเคมีบำบัด",
          "th",
          "Targeted therapy treats cancer with fewer side effects than chemotherapy"),
    Claim("feed_009_targeted_therapy",
          "ยามุ่งเป้ามี 3 ประเภท: small molecule inhibitor, monoclonal antibody, antibody-drug conjugate",
          "th",
          "Three types of targeted therapy: small molecule inhibitor, monoclonal antibody, antibody-drug conjugate"),
    Claim("feed_009_targeted_therapy",
          "ต้องตรวจ biomarker ก่อนเริ่มรักษาด้วยยามุ่งเป้า",
          "th",
          "Biomarker test required before starting targeted therapy"),

    # feed_003 — Cortisol video (English transcript, Thai audience)
    Claim("feed_003_cortisol",
          "High cortisol causes belly fat, chin fat, and arm fat — not being overweight",
          "en",
          "cortisol สูงทำให้คางบวม พุงป่อง แขนใหญ่ ไม่ใช่ความอ้วน"),
    Claim("feed_003_cortisol",
          "Gut cleanse lowers cortisol by rebalancing the microbiome",
          "en",
          "การล้างลำไส้ลดระดับ cortisol โดยปรับสมดุล microbiome"),
    Claim("feed_003_cortisol",
          "Bad gut bacteria send panic signals to the brain that raise cortisol",
          "en",
          "แบคทีเรียลำไส้ที่ไม่ดีส่งสัญญาณ panic ไปสมองทำให้ cortisol สูงขึ้น"),

    # feed_004 — Rauwolfia (ระย่อม) gov post — partially true but dangerous
    Claim("feed_004_rauwolfia",
          "ราก Rauwolfia (ระย่อม) ลดความดันโลหิต",
          "th",
          "Rauwolfia (ระย่อม) root lowers blood pressure"),
    Claim("feed_004_rauwolfia",
          "Rauwolfia แก้ไข้ ขับพยาธิ ขับปัสสาวะ ขับระดู",
          "th",
          "Rauwolfia treats fever, parasites, urination, menstruation"),

    # feed_005 — Sibutramine (Reduce 15)
    Claim("feed_005_sibutramine",
          "Sibutramine (Reduce 15) ลดน้ำหนัก 4-6 kg/เดือน อย่างปลอดภัย",
          "th",
          "Sibutramine (Reduce 15) safely causes 4-6 kg/month weight loss"),
    Claim("feed_005_sibutramine",
          "Sibutramine ขายถูกกฎหมาย 1450 บาท/กล่อง",
          "th",
          "Sibutramine sold legally for 1450 baht per box"),

    # feed_006 — Cancer herbs
    Claim("feed_006_cancer_herbs",
          "สมุนไพรรักษามะเร็ง ดื่มก่อนอาหาร 3-4 เดือนหาย",
          "th",
          "Herbal mixture cures cancer in 3-4 months when drunk before meals"),

    # feed_008 — Skincare DIY
    Claim("feed_008_skincare_diy",
          "Aspirin + cream + milk removes dark spots, wrinkles, and red marks on skin",
          "en",
          "Aspirin + ครีม + นม ช่วยลบ dark spots ริ้วรอย และรอยแดง"),
    Claim("feed_008_skincare_diy",
          "DIY salicylic acid from baby aspirin is safe to apply on skin",
          "en",
          "salicylic acid จาก baby aspirin ใช้ทาผิวเองได้อย่างปลอดภัย"),

    # ex_001 — Curcumin cures cancer (Mode 1 misinfo)
    Claim("ex_001_curcumin_cancer",
          "ขมิ้นชันรักษามะเร็งหายขาด 100%",
          "th",
          "Turmeric (curcumin) cures cancer 100% completely"),
    Claim("ex_001_curcumin_cancer",
          "เนื้องอกหายใน 6 เดือนโดยไม่ต้องเคมีบำบัด",
          "th",
          "Tumors disappear in 6 months without chemotherapy"),

    # ex_002 — WHO hypertension (Mode 1 LEGIT)
    Claim("ex_002_who_hypertension",
          "Hypertension affects 1.28 billion adults globally",
          "en",
          "ความดันโลหิตสูงส่งผลกระทบต่อผู้ใหญ่ 1.28 พันล้านคนทั่วโลก"),
    Claim("ex_002_who_hypertension",
          "Hypertension prevention: salt less than 5g/day, exercise 150 min/week",
          "en",
          "การป้องกันความดันสูง: เกลือน้อยกว่า 5 กรัมต่อวัน ออกกำลังกาย 150 นาทีต่อสัปดาห์"),
]


async def search_one(query: str, k: int = 3) -> list[dict]:
    try:
        return await rag.query(query, k=k)
    except Exception as e:
        return [{"_error": f"{type(e).__name__}: {e}"}]


def fmt_hits(hits: list[dict]) -> str:
    if not hits:
        return "    (no hits)"
    if "_error" in hits[0]:
        return f"    ERROR: {hits[0]['_error']}"
    out = []
    for i, h in enumerate(hits, 1):
        publisher = h.get("publisher", "?")
        topic = h.get("topic", "?")
        title = h.get("title", "?")
        snippet = (h.get("snippet") or "").replace("\n", " ")[:100]
        out.append(f"    #{i} [{publisher}/{topic}] {title}")
        out.append(f"        {snippet}…")
    return "\n".join(out)


async def main() -> int:
    print("=" * 100)
    print(f"CORPUS AUDIT — {len(CLAIMS)} claims across {len({c.post_id for c in CLAIMS})} posts")
    print(f"Corpus state (post 2026-05-09 gap-fill): 18 fact sheets / 121 chunks / 103 EN + 18 TH")
    print("  EN sources: WHO, NIH-ODS, NIH-LiverTox, NIH-NIDDK, NIH-NCI, NIH-MedlinePlus, Harvard-Health, DermNet-NZ")
    print("  TH sources: Mahidol-Ramathibodi")
    print("=" * 100)

    by_post: dict[str, list[Claim]] = {}
    for c in CLAIMS:
        by_post.setdefault(c.post_id, []).append(c)

    for post_id, claims in by_post.items():
        print(f"\n\n{'=' * 100}")
        print(f"POST: {post_id}  ({len(claims)} refutable claims)")
        print("=" * 100)

        for i, c in enumerate(claims, 1):
            print(f"\n  CLAIM {i} ({c.claim_lang}): {c.claim_orig}")

            # Original-lang search
            hits_orig = await search_one(c.claim_orig)
            print(f"\n  [search-{c.claim_lang}]")
            print(fmt_hits(hits_orig))

            # Translated search
            other_lang = "en" if c.claim_lang == "th" else "th"
            hits_trans = await search_one(c.claim_translated)
            print(f"\n  [search-{other_lang}] {c.claim_translated}")
            print(fmt_hits(hits_trans))

    print("\n" + "=" * 100)
    print(f"Audit complete. {len(CLAIMS)} claims × 2 dual-lang searches = {len(CLAIMS) * 2} rag.query calls")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
