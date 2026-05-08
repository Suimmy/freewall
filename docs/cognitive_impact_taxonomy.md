# Taxonomy — Negative Cognitive Impacts from AGI

## ปัญหาของ list เดิม

List ที่ทีมร่างไว้ตอนแรก:
- dopamine addict
- deskilling
- brainrot
- medical misinformation
- reality blur
- echo chamber
- aggressive personalization

**ปัญหา 2 ข้อ**:

1. **Overlap หนัก** — dopamine addict, brainrot, aggressive personalization จริงๆ คืออันเดียวกันในมุมต่างกัน:
   - personalization = สาเหตุ
   - dopamine = กลไก
   - brainrot = ผลลัพธ์
   ไม่ใช่ parallel categories

2. **Pre-AGI bias** — list ปัจจุบันเอนไปทางปัญหา social media ปัจจุบัน ไม่ใช่ post-AGI โดยแท้

---

## Taxonomy ใหม่ — 3 axes (clean, ไม่ overlap)

### Input-side threats (AGI ทำอะไรกับเรา)

| Threat | คำอธิบาย |
|--------|----------|
| **Hyper-personalized persuasion** | AGI รู้จิตวิทยาเราดีกว่าตัวเอง → craft persuasion เฉพาะคนเดียว |
| **Synthetic reality / reality blur** | content สังเคราะห์เนียนกว่าของจริง |
| **Echo chamber filtering** | feed filter จนเห็นด้านเดียว |
| **Dopamine engineering** | personalized engagement weaponization |
| **Mental privacy intrusion** | AGI รู้ thoughts/mood/weakness ตลอดเวลา |

### Output-side threats (เราสูญเสียอะไร)

| Threat | คำอธิบาย |
|--------|----------|
| **Deskilling** | ทักษะฝ่อเพราะ AI ทำให้หมด |
| **Memory atrophy** | AGI จำให้ → เราไม่จำเอง |
| **Agency erosion** | autopilot life — AGI ตัดสินใจแทนเรา |
| **Attention fragmentation** | สมาธิจดจ่อหายไป |
| **Identity erosion** | AI เขียนแทน, voice clone → "ตัวเอง" คืออะไร |

### Relational threats (ความสัมพันธ์เปลี่ยน)

| Threat | คำอธิบาย |
|--------|----------|
| **Parasocial AI bonding** | dependency บน AI companion → loneliness paradox |
| **Human disconnection** | คุยกับ AI มาก คุยคนน้อยลง |
| **Meaning crisis** | depression จาก obsolescence (AGI ทำดีกว่าทุกอย่าง) |
| **Trust collapse** | เมื่อทุกอย่าง fake ได้ → default = ไม่เชื่ออะไร |

### หมายเหตุ

**Medical misinformation** ไม่ใช่ category แยก — เป็น **domain instance** ของ "Synthetic reality + Hyper-personalized persuasion" ใน health domain

**Brainrot / dopamine / personalization** ตอนนี้ collapse เป็น dimension เดียวคือ "Dopamine engineering" (ใน Input-side)

---

## Tier ranking สำหรับ hackathon focus

เกณฑ์ 4 อย่าง:
1. Post-AGI uniqueness (ปัจจุบันป้องกันไม่ได้ ต้องรอ AGI)
2. Demoable ใน 18 ชม.
3. LLM-native (บังคับใช้ AI)
4. Judge resonance (Sandy + DPM + Gabriel)

### Tier S — เลือกเป็น primary

- **Hyper-personalized persuasion** ← เลือกแล้ว
  - LLM-vs-LLM defense (poetic, fit OpenAI)
  - Demo ชัด
  - ไม่มีในตลาด
  - "AI ปัจจุบันยังไม่ฉลาดพอจะ defend → ต้องรอ AGI-level" → ตอบ post-AGI โดยตัวมันเอง

- **Synthetic reality / reality blur** ← เลือกเป็น supporting
  - Concrete, viscerally post-AGI
  - Demo ง่าย
  - High stakes

### Tier A — strong but secondary

- **Agency erosion** — สำคัญมาก แต่ demo ยาก (long-term effect)
- **Parasocial AI bonding** — emotionally resonant แต่ scope กว้าง

### Tier B — อย่าเลือกเป็นหลัก

- **Dopamine engineering** — pre-AGI (TikTok ทำได้แล้ว), Opal/Screen Time มีแล้ว
- **Echo chamber** — pre-AGI (Facebook ก่อตั้งปัญหานี้)
- **Pure deskilling** — important แต่ demo ยาก

---

## Strategic decision สำหรับ Freewall

**Threat ที่ focus**:
- Primary: Hyper-personalized persuasion
- Secondary: Synthetic reality

**Domain anchor** (สำหรับ wellness theme alignment):
- Health misinformation (เป็น domain ที่ demo Persuasion + Synthetic ได้พร้อมกัน + ตรง Wellness Thailand strategy)

**Roadmap mention** (ในแผนอนาคต ไม่ build ใน hackathon):
- Echo chamber diversifier
- Anti-deskilling friction
- Long-term agency mirror

**Pitch framing**:
> "Algorithmic Reality" — โลกที่ content รอบตัวคุณถูก author เฉพาะคุณคนเดียว โดย agent ที่รู้จักคุณดีกว่าคุณรู้จักตัวเอง เพื่อบังคับให้คุณตัดสินใจตามที่มันต้องการ

**Product positioning**:
> Freewall = **Personal Guardian Agent** — cognitive immune system  
> (aligned กับ Gartner "Guardian Agents" trend ปี 2026)

**Tagline**:
> "In the post-AGI era, cognitive sovereignty is the new public health."

---

## Academic + policy backing

**Cognitive Sovereignty as constitutional concept**:
- Yuste et al., *Ethics and Information Technology*, Springer (Nov 2025) — proposes constitutional framework for cognitive sovereignty as response to predictive digital platforms eroding volition
- Freewall = **first consumer product** ที่ implement กรอบนี้

**Policy timing 2026** (regulation tailwind):
- **EU AI Act Article 50** — enforcement Aug 2026 → mandates machine-readable disclosure of AI-generated content
- **California SB 942** — มีผลแล้วตั้งแต่ Jan 2026
- Freewall = **consumer-side enforcement layer** สำหรับ era ที่ regulation ตามไม่ทัน

