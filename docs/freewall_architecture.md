# Freewall — 3-Layer Architecture (Hackathon MVP++)

## Layer 1 — Perception

**คำถามที่ตอบ**: "บนจออะไร + ใครทำ + user อยู่ในสภาพไหน?"

| ส่วน | ทำอะไร |
|------|--------|
| DOM scraper | อ่าน content ที่ผู้ใช้กำลังเห็น |
| **Synthetic Reality Detector** | ตรวจ AI-gen ทั้ง text (perplexity-based) + image (HF pretrained) + C2PA metadata → ออกมาเป็น "synthetic probability" |
| **Content Classifier Agent** ⭐ | news / ad / health claim / social / meme → GPT-4o-mini → เป็น **agent ตัวที่ 6** ที่ทำงานก่อน L2 (กรองให้ Coordinator ตัดสินใจว่าจะ dispatch agent ตัวไหนบ้าง) |
| Source reputation | domain นี้น่าเชื่อแค่ไหน — hardcoded list 200 domains |
| **User state monitor** | scroll velocity, dwell time, click rhythm — **เป็น context** ให้ Layer 2 ตัดสินใจว่าจะแทรกแซงแรงแค่ไหน (ถ้า user scroll เร็วผิดปกติ = อยู่ใน hijacked mode → threshold ต่ำลง) |

ที่ behavior signal ต้องอยู่ที่นี่: ไม่ได้ใช้เป็น primary detection แต่ใช้เป็น **gating signal** — ตัดสินใจว่า annotation ที่ออกมาจะ aggressive แค่ไหน ใช้ค้านความรู้สึก "Screen Time clone" เพราะเอา behavior + content combine กัน

---

## Layer 2 — Reasoning ⭐ (hero layer)

**คำถามที่ตอบ**: "content นี้อันตรายแค่ไหน + ทำไม + ทางเลือกของผู้ใช้คืออะไร?"

**Total 6 agents** (1 ใน L1 + 5 ใน L2) ใช้ OpenAI Agents SDK:

```
[L1]  Content Classifier Agent
              │ category
              ▼
[L2]  Coordinator Agent
      (dispatch + synthesize)
              │
       parallel dispatch
       ┌──────┬─────┬──────┐
       ▼      ▼     ▼      ▼
  Persuasion Fact- Prove- Counter-
    Agent   Check  nance Perspective
```

| Agent | หน้าที่ | Tool |
|-------|---------|------|
| **Coordinator** | รับ input จาก L1, ตัดสินใจว่าจะเรียก agent ไหนบ้าง (เช่น meme ไม่ต้องเรียก Fact-Check), parallel dispatch, แล้วรวม output → **Cognitive Sovereignty Score** ผ่าน XGBoost. ถ้า initial score < 30 → trigger **Debate mode** (Persuasion vs Counter-Perspective) — inspired by ED2D (AAAI 2026) | orchestration logic + ML scorer |
| **Persuasion** | Detect tactic + intended action + hidden agenda — ใช้ taxonomy hybrid: **PersuSafety 15 unethical strategies** (Liu et al., COLM 2025) + **Cialdini's 6 principles** | LLM + structured output |
| **Fact-Check** | health claim verification | LLM + RAG (WHO/CDC) |
| **Provenance** | source trust + รวม synthetic signal จาก L1 (MoA-style ensemble per DFBench MoA-DF) | LLM + reasoning over L1 metadata |
| **Counter-Perspective** | สร้าง steelman ของมุมตรงข้าม + แหล่งข้อมูลที่น่าเชื่อถือกว่า | LLM + web search tool |

Counter-Perspective รันอัตโนมัติเฉพาะเมื่อ score < 50 (ประหยัด token, แต่พร้อมแสดงทันทีเมื่อ user expand)

**Debate mode (Phase 4 stretch)**: ถ้า initial score < 30 → Coordinator trigger 1 round ของ debate ระหว่าง Persuasion Agent vs Counter-Perspective Agent → render เป็น dialog ใน sidebar — inspired by ED2D (AAAI 2026) ที่พิสูจน์ว่า multi-agent debate ดีกว่า aggregation alone

---

## Layer 3 — Sovereignty

**คำถามที่ตอบ**: "user จะทำอะไรกับ insight นี้ได้บ้าง?"

User actions ที่ทำได้:

| Action | คำอธิบาย |
|--------|----------|
| Inline annotation | highlight + tooltip บอก tactic |
| Fact-check card | claim + verdict + source |
| Counter-perspective | กด expand → เห็นมุมตรงข้าม |
| Decision Pause | Buy/Share/Sign up โดน hold ชั่วคราวถ้า score ต่ำ |
| **Override / dismiss** | กดผ่านได้ทันที (หนึ่งคลิก) — สำคัญ เพื่อไม่ให้รู้สึก paternalistic |
| **Sensitivity mode** | toggle Light / Standard / Strict — user เลือกระดับความ aggressive ของระบบเอง |
| **Daily Mirror** | end-of-day dashboard: today blocked X manipulations, fact-checked Y claims, sovereignty score trend |
| **Ask why** | คลิกที่ annotation → "ทำไมถึง flag?" → LLM อธิบายเหตุผลละเอียด |

Override + Sensitivity คือสิ่งที่บอก judges ว่า **เราเคารพ user agency** — ไม่ใช่ระบบ paternalistic — ตรงกับ theme "Cognitive Sovereignty"

---

## Over-engineered มั้ย? — ตอบจริงใจ

**ไม่ over-engineer แต่อยู่ที่ขอบ** — สำหรับทีม 5 คนใน 18 ชม. ทำได้ ถ้า:

- 1 คน (A): extension + DOM + UI overlay
- 1 คน (B): backend + Coordinator + Content Classifier Agent + Agents SDK setup
- 1 คน (C): Persuasion + Counter-Perspective + Provenance Agent + prompt eng
- 1 คน (D): Fact-Check Agent + RAG + vector DB + corpus curation
- 1 คน (E): ML scorer + Synthetic Detector + demo content + mock site

### Triage protocol

ดูรายละเอียด graceful degradation + plan B per component + 4-hour triage rule ที่ **`freewall_tech_stack.md`** (single source of truth)

---

ภาพรวมตอนนี้ **ครบและ defendable** — ไม่ minimum, ไม่ overstuffed
