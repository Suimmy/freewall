# Freewall — Technical Stack

## 1. Infrastructure

| Layer | Tool | Note |
|-------|------|------|
| Frontend | Chrome Extension Manifest V3 + vanilla JS หรือ React | มาตรฐาน |
| Overlay UI | Shadow DOM + Tailwind | มาตรฐาน |
| Backend | FastAPI (Python) | มาตรฐาน |
| Agent framework | **OpenAI Agents SDK** (released Mar 2025) | จำเป็น — เป็น hackathon ของ OpenAI |
| Vector DB | **Chroma** (embedded, free) หรือ Qdrant local | ใช้งานได้จริง |
| ML lib | scikit-learn + XGBoost | มาตรฐาน |
| In-browser ML | ONNX Runtime Web หรือ transformers.js | ใช้งานได้จริง |
| Codex | OpenAI Codex CLI | จำเป็น — ตาม theme hackathon |

---

## 2. LLMs (ของจริง, ใช้ผ่าน OpenAI API)

| Model | Use case | Note |
|-------|----------|------|
| **GPT-4o-mini** | Content classifier, fast persuasion analysis (high-frequency) | cheap, fast, structured output ดี |
| **GPT-4o** | Deep persuasion, Counter-Perspective, Fact-Check verdict | quality สูงกว่าสำหรับ judgment ละเอียด |
| **GPT-5 / o-series** | Coordinator/Synthesizer ถ้าต้องการ reasoning ลึก | เลือกตามที่ available + pricing ตอน hackathon |
| **text-embedding-3-small** | Embed health docs สำหรับ RAG | OpenAI native, cheap |

---

## 3. ML models off-the-shelf (มีจริง)

### AI-image detection

| Model (HuggingFace) | Note |
|---------------------|------|
| `Organika/sdxl-detector` | focused on SDXL-generated |
| `umm-maybe/AI-image-detector` | general AI image |
| `dima806/ai_vs_real_image_detection` | alternative |

**ข้อจำกัด**: accuracy 70-90% ขึ้นกับ generator (Flux, Midjourney v6 ตรวจยากขึ้น) → อย่า claim 99% ใน demo

### AI-text detection

| Model (HuggingFace) | Note |
|---------------------|------|
| `Hello-SimpleAI/chatgpt-detector-roberta` | RoBERTa, ChatGPT-era |
| `roberta-base-openai-detector` | OpenAI's old GPT-2 detector (dated) |

**ความจริง**: Modern LLM (GPT-4, Claude) detection **ไม่น่าเชื่อถือ** — OpenAI ปิด detector ตัวเองเพราะ accuracy ต่ำ ใช้เป็น **weak signal** ไม่ใช่ ground truth

### Sentence embeddings

| Model | Note |
|-------|------|
| `sentence-transformers/all-MiniLM-L6-v2` | lightweight, classic |
| `BAAI/bge-large-en-v1.5` | quality สูงกว่า, หนักกว่า |
| OpenAI `text-embedding-3-small` | API, ไม่ต้อง host เอง |

### C2PA reader

| Tool | Note |
|------|------|
| `c2pa-python` library | official Adobe/C2PA SDK |

**ข้อจำกัด**: C2PA adoption ต่ำมาก in the wild → ใช้เป็น bonus signal เมื่อมี

---

## 4. สิ่งที่ "ไม่มี" off-the-shelf — ต้อง build เอง

| Component | สถานะ | วิธี build |
|-----------|-------|-----------|
| Persuasion tactic classifier | ❌ ไม่มี pretrained | LLM + prompt + Pydantic structured output |
| Health claim verifier | ❌ ไม่มี API พร้อมใช้ | RAG: WHO/CDC fact sheets + LLM judge |
| Source reputation database | ⚠️ MBFC ไม่มี free API | hardcode list (~200 domains) จาก MBFC + Wikipedia perennial sources |
| Sovereignty Score model | ❌ ไม่มี pretrained | weighted sum (baseline) → XGBoost (stretch) |
| WHO/CDC API | ❌ ไม่มี API ทางการ | scrape + manual curation |

---

## 5. Strategy — default to pretrained API + specialist HF model (fine-tune only if needed)

| Task | คำแนะนำ | เหตุผล |
|------|---------|--------|
| Persuasion tactic | GPT-4o-mini + structured output, taxonomy = **PersuSafety 15 + Cialdini 6** | Fine-tune คุ้มเสี่ยง — marginal gain. PersuSafety taxonomy = SOTA (Liu et al., COLM 2025) |
| Fact-check (health) | GPT-4o + RAG | Knowledge มาจาก docs ไม่ใช่ weight |
| Content classifier | GPT-4o-mini | task ง่าย, structured output ทำได้เลย |
| Counter-perspective | GPT-4o | generation creative — LLM only |
| Coordinator/Synthesizer | GPT-4o + Agents SDK | orchestration + reasoning + debate trigger |
| **AI-image detection** | **MoA-style ensemble** ของ HF models (multiple detectors → combined probability) | DFBench MoA-DF (Jun 2025) พิสูจน์ว่า ensemble beats single LMM |
| **AI-text detection** | Specialist HF + LLM ensemble | weak signal — ขอแม่นยำพอ ไม่ใช่ perfect |
| Embeddings | text-embedding-3-small / all-MiniLM-L6-v2 | API หรือ local ก็ได้ |

### ทำไม default ไป OpenAI API (ไม่ใช่ Llama/Qwen) — แต่ open-source ใช้ได้ถ้าจำเป็น

Default reasoning:
- ต้อง host เอง → GPU/inference overhead ใน 18 ชม.
- Latency แย่กว่า OpenAI API
- Quality ตามหลัง GPT-4o ส่วนใหญ่
- เป็น hackathon ของ OpenAI → optics อ่อน

เปิดให้ใช้ open-source LLM ได้ถ้า: cost spike, OpenAI rate limit, หรือมี task ที่ open model ทำได้ดีกว่าจริง — คุยกับมนุษย์ก่อนเลือก

### ทำไม default ไม่ fine-tune — แต่ fine-tune ได้ถ้าจำเป็น

Default reasoning:
- Data labeling/synthesis: 2-3 ชม.
- Train + eval + deploy: 2-4 ชม.
- Risk: fail ได้หลายจุด
- Reward: marginal — GPT-4o-mini ทำได้แล้ว
- Total cost: ~6-8 ชม. = 1/3 ของเวลา สำหรับผลที่ไม่ make-or-break

เปิดให้ fine-tune ได้ถ้า: pretrained ไม่ผ่าน bar บน critical path (เช่น Persuasion Agent eval ต่ำกว่าที่ต้องการ defend ใน Q&A) — คุยกับมนุษย์ก่อนตัดสินใจลงทุนเวลา

---

## 6. งานที่ต้องทำจริงๆ ใน 18 ชม.

### ต้องทำแน่ๆ

1. **Sovereignty Score model**
   - Generate synthetic labels: GPT-4o ให้คะแนน 0-100 บน ~500 ตัวอย่าง
   - Train XGBoost บน features (persuasion, fact_check, synthetic_prob, source_rep, user_state) → label
   - 2-3 ชม. ของ 1 คน
   - **Fallback**: weighted sum hardcoded weights

2. **RAG corpus curation** (data work)
   - Manual collect ~30-50 WHO/CDC/Mayo fact sheets (vaccines, supplements, raw milk, diet fads, fad cures)
   - Embed ด้วย text-embedding-3-small
   - เก็บใน Chroma
   - 3-4 ชม. ของ 1 คน

3. **Demo content curation** (data work)
   - หา 5-7 real viral health misinfo posts จาก TikTok/IG ใน 30 วันก่อน
   - Screenshot + save HTML
   - Verify มี debunk source สำหรับแต่ละอัน
   - 2-3 ชม. ของ 1 คน

4. **Persuasion Agent eval** (Phase 4 polish)
   - Pull 50-100 examples จาก PersuSafety dataset (`PLUM-Lab/PersuSafety` บน GitHub)
   - Run Persuasion Agent on subset
   - Compute precision/recall + confusion matrix
   - แสดงเป็น 1 slide ใน pitch
   - 1-2 ชม. ของ 1 คน
   - **Why critical**: ป้องกันคำถาม "แม่นแค่ไหน?" จาก judges

### Optional stretch (Phase 4 polish ถ้าทันเวลา)

5. **Debate mode** (ED2D-inspired)
   - High-risk content (score < 30) → Persuasion vs Counter-Perspective debate 1 round
   - Render เป็น dialog ใน sidebar
   - 2-3 ชม. ของ Person B+C

### Default skip (เปิดใหม่ได้ถ้าจำเป็น)

- Fine-tune LLM (LoRA, full FT) — default skip, overkill สำหรับ baseline; reopen ถ้า pretrained ไม่ผ่าน eval bar
- Train AI-image detector ใหม่ — default skip, pretrained MoA ดีพอ; reopen ถ้า detector ensemble ไม่ครอบ threat ที่เจอ
- Distill GPT-4o → small model — default skip, ไม่คุ้มเสี่ยง; reopen ถ้า latency/cost เป็น blocker จริง

---

## 7. Plan B per component (graceful degradation)

> **📌 Single source of truth สำหรับ triage protocol** — `freewall_architecture.md` link มาที่นี่

### Persuasion tactic classifier

| Plan | สิ่งที่ทำ | เวลาเสีย |
|------|----------|----------|
| A | LLM + structured Pydantic output | baseline |
| B | LLM free-text → render bullet ใน UI | -10 min |
| C | Keyword/pattern matching 20 patterns | -1 hr |

### Health claim verifier

| Plan | สิ่งที่ทำ | เวลาเสีย |
|------|----------|----------|
| A | RAG: 30-50 WHO/CDC docs + LLM judge | baseline |
| B | LLM zero-shot + explicit "WHO/CDC consensus" prompt | -3 hr |
| C | Hardcoded verdict for 5-7 demo posts | -5 hr |

C ต้องบอก judges ตรงๆว่า "knowledge base limited to demo scope"

### Source reputation database

| Plan | สิ่งที่ทำ |
|------|----------|
| A | 200 domains (MBFC + Wikipedia perennial sources) |
| B | 30-50 domains (credible + unreliable + red flags) |
| C | "Unknown" สำหรับ unrecognized — rely on other signals |

### Sovereignty Score

| Plan | สิ่งที่ทำ | เวลาเสีย |
|------|----------|----------|
| A | XGBoost on 500 GPT-4o-labeled examples | baseline |
| B | Logistic regression on synthetic labels | -1 hr |
| C | Weighted sum (persuasion 0.3, fact 0.4, synthetic 0.2, source 0.1) | -3 hr |
| D | Average normalized signals | -3.5 hr |

### WHO/CDC corpus

| Plan | สิ่งที่ทำ | Coverage |
|------|----------|----------|
| A | 30-50 fact sheets (vaccines, supplements, raw milk, diet, cures, mental health, sexual health, child nutrition) | ~80% misinfo |
| B | 15 fact sheets — top 5 demo topics | 100% demo, ~50% real-world |
| C | 5-7 fact statements เขียนเอง (matches demo) | demo only |

---

## 8. Triage ถ้าเหลือ 4 ชม.

ลำดับ degradation:

1. Score: A → C (XGBoost → weighted sum) — save 3 hr
2. Health verifier: A → B (RAG → LLM zero-shot) — save 3 hr
3. Persuasion: A → A — **ห้ามลด** (hero feature)
4. Source rep: A → B (200 → 30) — save 1.5 hr
5. Counter-perspective: timeout 8s → fallback hardcoded message — save 1 hr

**Total save**: ~8.5 hr ถ้าจำเป็น

### ห้ามทิ้ง

- **6-agent orchestration** (Content Classifier + Coordinator + 4 L2 specialists ผ่าน Agents SDK) — ทิ้ง = ทิ้ง multi-agent narrative
- Persuasion Agent quality — judges ดู most critically
- Inline annotation UI — wow factor หลัก
- Real demo content — emotional weight

### Tactical

ก่อน hackathon **assign 1 คนคุม fallback chain** ชัดเจน — เมื่อทีมเริ่มลำบาก คนนี้ trigger downgrade plan ก่อนทุกคน panic

---

## สรุป 1 บรรทัด

Default: Pretrained LLM API + specialist HF model สำหรับ image/text detection — fine-tune เฉพาะเมื่อจำเป็น — งานจริง 80% คือ prompt engineering + data curation + agent orchestration + 1 XGBoost เล็ก
