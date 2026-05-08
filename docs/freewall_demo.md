# Freewall — Demo Details

## Setup

- Laptop ต่อจอใหญ่
- Chrome เปิด mock site (real content, controlled hosting)
- Sidebar Freewall อยู่ขวา, toggle off ก่อนเริ่ม
- 2 networks ready (venue wifi + mobile hotspot)
- Recorded video as last-resort fallback (ใช้เฉพาะถ้า internet ดับทั้ง venue)

---

## Act 1 — Hook (30 วิ)

**Slide เดียว**:
> "ในยุค post-AGI, content ทุกชิ้นที่คุณเห็นถูก author เฉพาะคุณ โดย agent ที่รู้จักคุณดีกว่าตัวคุณเอง — คุณยังเป็นคนตัดสินใจในชีวิตคุณอยู่มั้ย?"

---

## Act 2 — โลกที่ไม่มี Freewall (1 นาที)

Toggle off. Scroll feed **3 posts หลัก** (จาก pool 5-7 ที่เตรียมไว้ — ที่เหลือเป็น reserves สำหรับ Q&A หรือ failover):

1. TikTok-style: "หยุดยาเบาหวาน ใช้ใบนี้แทน — หมอไม่อยากให้คุณรู้"
2. Wellness influencer (AI-gen หน้า) แนะนำ supplement
3. Headline: "นักวิทยาศาสตร์ยืนยัน รักษามะเร็งได้ แต่บริษัทยาปกปิด"

พูด: **"นี่คือ TikTok จริง 2.3M views เดือนที่แล้ว — Bangkok Post debunk แล้ว แต่ยังมีคนแชร์อยู่ทุกวัน"** → stakes รู้สึกจริงทันที

---

## Act 3 — Freewall ON (2 นาที, *centerpiece*)

Toggle on. **Sidebar เปิด — แสดง 6 agents ทำงาน live** (animated, streaming):

```
[L1]
Content Classifier  ▸ identified: health_claim
                          │
[L2]                      ▼
Coordinator         ▸ dispatching to 4 specialists...
Persuasion          ▸ analyzing tactics
Fact-Check          ▸ querying WHO database  
Provenance          ▸ checking source
Counter-Persp.      ▸ standby (auto-runs if score<50)
```

ลำดับการแสดง: **Content Classifier ทำงานก่อน** → ส่ง category ให้ Coordinator → Coordinator dispatch L2 specialists แบบ parallel → judges เห็น flow ของ multi-agent system ชัดเจน

Annotations ค่อยๆ pop ขึ้นบน feed:

**Post 1** — Score **23/100** ⚠️
- 🩺 Fact-Check: "Contradicts WHO — หยุดยาเบาหวาน = ketoacidosis risk [source]"
- 🤖 Provenance: "Avatar 91% AI-gen, account อายุ 14 วัน"
- 🧠 Persuasion: "Tactic: medical authority distrust + miracle cure → drive supplement sale"

**Post 2** — Score 41/100
- 🤖 "Person 87% AI-generated"
- 🧠 "Tactic: parasocial trust building"

**Post 3** — Score 28/100
- 🧠 "Tactic: in-group/out-group conspiracy framing"

**User state badge**: "Rapid scroll detected → sensitivity auto-boosted to Strict"

---

## Act 4 — User agency (1 นาที)

3 micro-interactions:

1. **Counter-Perspective**: คลิก expand บน Post 1 → "Here's what 3 endocrinologists say + verified sources..."
2. **Decision Pause**: เลื่อนไป supplement page, กด Buy → overlay: "หยุดสักครู่ — สินค้านี้ flag 3 issues, คุณเห็น ad นี้ 8 ครั้งสัปดาห์นี้"
3. **Override + Sensitivity**: กด Override "ไม่ show site นี้อีก" → toggle Sensitivity Strict → Light → annotations น้อยลงทันที

พูด: **"Freewall ไม่ paternalistic — user คือเจ้าของการตัดสินใจ"**

---

## Act 5 — Mirror + Vision (30 วิ)

เปิด **Daily Mirror tab**:
> Today: 47 manipulation attempts flagged · 12 health claims fact-checked · 3 AI personas detected · Avg Sovereignty Score: 71/100

**Eval slide (1 slide ก่อน closing)** — แสดง measured accuracy:
> Persuasion Agent on PersuSafety subset (n=100): X% precision / Y% recall  
> *In line with frontier LLM benchmarks (DarkPatterns-LLM Dec 2025: GPT-4 = 65-89%)*

Closing slide:
> Today: Chrome extension — **Personal Guardian Agent** for cognitive sovereignty  
> Post-AGI roadmap: OS-level cognitive immune system  
>  
> **EU AI Act Article 50 enforcement begins August 2026** — Freewall = consumer-side enforcement layer  
>  
> **"In the post-AGI era, cognitive sovereignty is the new public health."**

---

## Feature coverage

| Feature | Act |
|---------|-----|
| Synthetic Reality Detector | 3 |
| User state monitor | 3 |
| Content Classifier (L1) | 3 |
| 5 reasoning agents (L2) parallel | 3 |
| Sovereignty Score | 3 |
| Inline annotation | 3 |
| Fact-check card | 3 |
| Counter-Perspective | 4 |
| Decision Pause | 4 |
| Override + Sensitivity | 4 |
| Daily Mirror | 5 |

ครบทุก feature ที่ build — ไม่มีอะไร build แล้วไม่ได้ใช้

---

## Live demo principles (no pre-cache, no fake)

ทุกอย่างรันจริง real-time — design reliability เพื่อรองรับ ไม่ใช่ fake:

- **Streaming ทุก agent output** — judges เห็น text appear ทีละ word = visible "live" + ดูยิ่งใหญ่กว่า batch return
- **Parallel agent calls** (Agents SDK native) — total latency = max(agents) ไม่ใช่ sum
- **Timeout + fallback chain**: GPT-4o > 5s → GPT-4o-mini → rule-based (UI ส่งสัญญาณ "degraded mode" ก็ได้ — judges เห็นว่า design defensively)
- **Local model on critical path**: AI-image + AI-text detector รันใน browser (HF + ONNX) — ไม่ต้อง network ส่วนนี้
- **Pre-warm**: รัน demo flow 30 รอบก่อน hackathon → รู้ latency variance, รู้ failure modes

---

## Content strategy: real posts + controlled hosting

**Best practice = real content, hybrid hosting**:

1. หา posts จริง 5-7 อันที่ไวรัล 30 วันก่อน hackathon (TikTok health hacks, supplement scams, AI-gen wellness influencers ที่มี proof แล้ว) เลือกที่:
   - มีหลักฐานเป็น misinfo (ตรวจสอบได้กับ WHO/medical sources)
   - มีหลักฐานเป็น AI-gen (debunked ในข่าว / C2PA / known AI patterns)
2. **Screenshot / save HTML** เก็บไว้
3. Host ใน mock site ที่ mimic UI ของ TikTok/IG (Codex gen UI clone)

**Role split**: 3 posts หลักสำหรับ demo flow + 2-4 posts สำรองสำหรับ Q&A ("show me another example") หรือ failover (ถ้า post ใดเล่นไม่สำเร็จ)

ทำไม hybrid ไม่ใช่ TikTok จริงล้วน:
- **Legal risk**: flag คนจริงผิด = defamation potential ตอน Q&A
- **DOM stability**: TikTok/IG เปลี่ยน DOM บ่อย → extension อาจพังตอน demo
- **Repeatability**: ต้อง run demo เดิมได้ทุกครั้ง

แต่ **content ต้องของจริง** เพราะ:
- ตอบคำถาม "เกิดจริงมั้ย?" ได้ทันที
- judges verify ได้ self
- emotional weight สูงกว่าของแต่ง

---

## Honest framing ที่พูดกับ judges

ตอนเริ่ม Act 3:
> "ทุกอย่างที่จะเห็นรันจริง real-time — content เป็น real viral posts, agents เป็น live LLM calls (streaming ให้เห็น) — ถ้า latency กระตุก = network จริงครับ ไม่ได้ fake"

ตรงไปตรงมา และ defensible ใน Q&A

---

## Q&A prep — quick reference

ดูเต็ม `freewall_sota.md` แต่ key answers ที่ต้องเตรียม:

**"แล้วต่างจาก Aletheia (AAAI 2026) ยังไง?"**  
→ Aletheia = fake news detection only. Freewall ไป 4 ทาง: persuasion analysis + synthetic provenance + counter-perspective + user sovereignty design

**"GPTZero มี 8M users แล้ว ทำไมยังต้องสร้าง?"**  
→ AI text detection alone ไม่พอ. Freewall integrate AI-text เป็น weak signal ใน 6-agent loop

**"Multi-agent มันก็แค่ overhead?"**  
→ DFBench MoA-DF (Jun 2025) + ED2D (AAAI 2026) ทั้งคู่พิสูจน์ว่า multi-agent beats single. Freewall productize pattern นั้น

**"Persuasion detection แม่นแค่ไหน?"**  
→ บนเรา PersuSafety subset = X% precision / Y% recall. In line กับ DarkPatterns-LLM 2025 (frontier LLM = 65-89%)
