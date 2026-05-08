# Freewall — SOTA Survey & Competitive Position

> Reference document สำหรับ Q&A ที่ judges อาจถามเรื่อง related work, novelty, และ accuracy

## ภาพรวมของ field ในปี 2025-2026

Field ของ cognitive defense / anti-manipulation AI กำลัง **hot มาก** — งานวิจัยกระจายในหลายสาย แต่ยังไม่มี product ที่รวม comprehensive defense layer ออกมา

**Policy tailwind 2026**:
- **EU AI Act Article 50** เริ่มบังคับ Aug 2026 → ต้อง machine-readable disclosure ของ AI-generated content
- **California SB 942** มีผลแล้วตั้งแต่ Jan 2026
- **Gartner** ระบุ "guardian agents" เป็น 1 ใน 5 trends ของ agentic AI ปี 2026

**Infrastructure**:
- **C2PA** มี 6,000+ members แล้ว (Adobe, Microsoft, BBC, Google, Meta, OpenAI, TikTok, Sony, Canon, Leica)
- Hardware adoption real (Pixel 10, Sony PXW-Z300, Galaxy S25)
- ⚠️ **Most platforms ยัง strip metadata** ตอน upload/transcoding

---

## 1. Direct competitors — Browser extensions ที่ทำคล้าย

| Product | Year | Focus | Approach | Verdict |
|---------|------|-------|----------|---------|
| **Aletheia** (research) | Feb 2026 | Fake news detection | LLM + RAG + Discussion Hub + Stay Informed | ⭐ ใกล้สุด, มี user study 250 คน, AAAI |
| **Facticity AI** | live | Auto fact-check claims | LLM + curated sources, True/False/Unverifiable | ✅ shipping, similar to Fact-Check Agent |
| **GPTZero** | live | AI text detection | Proprietary, claims 99% accuracy, 8M users | ✅ category leader for AI text |
| **Sourcer AI** | live | Article reputability/bias | ML, $5/month | competitor for Provenance |
| **Trusted Times** | live | Fake news classification | ML + bias indicators | similar pattern |
| **UnCovered** | live | Fact-checking with rebuttal | Perplexity Sonar API | open-source GitHub |
| **Genaios** | live | AI content verification | Detection + multilingual | EU-focused, SemEval winner |
| **TrustNet** (MIT) | 2024 | Decentralized fact-check | Crowd + algorithm | research only |

---

## 2. Academic SOTA — งานวิจัยที่ overlap

### Persuasion / Manipulation detection

| Paper | Year | Contribution | Relevant to |
|-------|------|--------------|-------------|
| **PersuSafety** (arXiv 2504.10430) | Apr 2025 | First framework for LLM persuasion safety, **15 unethical strategies** | ⭐ Persuasion Agent taxonomy + eval dataset |
| **Persuaficial** (arXiv 2601.04925) | Jan 2026 | Benchmark for AI-persuasion detection, 4 LLMs zero-shot | Validates LLM zero-shot persuasion detection (beats BERT supervised in cross-domain) |
| **Persuasion with LLMs survey** (arXiv 2411.06837) | Nov 2024 | Comprehensive survey of LLM persuasion | Background context |
| **DarkPatterns-LLM** (arXiv 2512.22470) | Dec 2025 | First multi-layer benchmark for AI manipulation. **GPT-4 only 65-89% accurate** | Honest accuracy reference |
| **DarkBench** | 2024-2025 | Dark patterns in conversational AI benchmark | UI dark pattern reference |

### Multi-agent for defense / misinformation

| Paper | Year | Contribution | Relevant to |
|-------|------|--------------|-------------|
| **ED2D** (arXiv 2511.07267, AAAI 2026) | Nov 2025 | **Evidence-based Multi-Agent Debate** for misinformation + persuade users to correct beliefs | ⭐ ใกล้ Freewall มาก — multi-agent + RAG + counter-perspective |
| **T²Agent** (arXiv 2505.19768) | May 2025 | Multi-agent + MCTS for multimodal misinformation | Multi-agent precedent |
| **FactAgent** | 2024 | Single agent fact-checking via subtasks | Fact-Check pattern |
| **MoA-DF in DFBench** (arXiv 2506.03007) | Jun 2025 | **Mixture of Agents** for deepfake detection — beats single LMM | ⭐ Validates multi-agent for synthetic detection |
| **Agentic Superego** (arXiv 2506.13774) | Jun 2025 | Personalized constitutional oversight, Creed.Space prototype | Validates "AI guardian" concept |

### Cognitive sovereignty / dark patterns / autonomy

| Paper | Year | Contribution | Relevant to |
|-------|------|--------------|-------------|
| **Cognitive Sovereignty** (Ethics & Info Tech, Springer) | Nov 2025 | Constitutional framework for cognitive sovereignty | ⭐ Cite ในบทนำ — academic legitimacy ของ term |
| **GreaseDroid** (Oxford) | 2021 | Community-driven dark pattern removal in mobile | Form factor reference |
| **AppRay**, dark pattern mobile detection | 2024-2025 | UI manipulation detection at scale | Dark pattern detection precedent |

---

## 3. Component-level SOTA

### AI-text detection

- **GPTZero** ใหญ่ที่สุด, อ้าง 99% accuracy แต่ academic consensus คือ modern LLM detection **unreliable**
- OpenAI ปิด text classifier ของตัวเอง (2023) เพราะ accuracy ต่ำ
- Persuaficial (Jan 2026): zero-shot LLM detection ใช้ได้, ดีกว่า BERT supervised ใน cross-domain
- **Implication for Freewall**: ใช้เป็น weak signal, อย่า claim high confidence

### AI-image detection

- **DFBench** (Jun 2025): MoA-DF (multi-agent) achieves SOTA, beats single multimodal LMM
- **AIGIBench** (May 2025): comprehensive benchmark — detection NOT solved, especially for Flux, Midjourney v6
- Best practice 2025: multimodal ensembles + provenance signals
- **Implication for Freewall**: ensemble multiple HF detectors = MoA-style

### Provenance (C2PA)

- 6,000+ members in 2026
- Hardware adoption real (Pixel 10, Sony, Canon, Leica, Fujifilm, Samsung S25)
- LinkedIn + TikTok preserve credentials
- ⚠️ **Most platforms ยัง strip metadata** during upload/transcoding
- Durable Content Credentials (watermark + fingerprint) = emerging answer
- **Implication for Freewall**: ใช้เป็น bonus signal เมื่อมี — primary detection ยังต้องอาศัย ML

### Persuasion taxonomy (foundation)

- **Cialdini's 6 principles** (1984/2001): reciprocity, commitment, social proof, authority, liking, scarcity
- **Da San Martino et al. (2019)**: 18 persuasive techniques, SemEval datasets
- **PersuSafety** (2025): 15 unethical strategies extending Cialdini
- **Implication for Freewall**: ใช้ PersuSafety 15 + Cialdini 6 hybrid taxonomy

---

## 4. Where Freewall sits — honest assessment

### ที่ Freewall **novel** (defendable)

| มิติ | ทำไม novel |
|-----|------------|
| **Integration** | Aletheia ทำ fact-check, GPTZero ทำ AI-detection, Sourcer ทำ source rep — **ไม่มีตัวไหนรวมทุกอย่าง + persuasion + counter-perspective ใน extension เดียว** |
| **Multi-agent productized** | MoA-DF (academic, deepfake only) + ED2D (academic, AAAI 2026) ใช้ multi-agent — แต่**ยังไม่มี productized consumer extension** ที่ใช้ multi-agent defense |
| **Cognitive Sovereignty framing** | เป็น academic concept (Springer 2025) — **ยังไม่มี consumer product** ใดอ้างกรอบนี้เป็น brand |
| **User agency design** (Override + Sensitivity) | tools ส่วนใหญ่ paternalistic หรือ binary — Freewall เน้น user control |
| **Health domain RAG anchor** | tools อื่น generic — Freewall โฟกัสเรื่อง wellness ตรงตาม Wellness Thailand strategy |
| **Debate mode** (high-risk content) | ED2D-inspired — Persuasion vs Counter-Perspective challenge each other |

### ที่ Freewall **NOT novel** (ต้อง honest)

| Component | ของที่มีอยู่แล้ว |
|-----------|-----------------|
| LLM + RAG fact-checking | Aletheia (Feb 2026), Facticity AI |
| AI text detection | GPTZero (8M users, market leader) |
| AI image detection | DFBench MoA-DF, many HF models |
| Source reputation | Sourcer AI, Trusted Times, NewsGuard |
| Browser extension form factor | standard |
| Cialdini-based persuasion taxonomy | 30+ years old foundation |
| Multi-agent for misinformation | ED2D, T²Agent, MoA-DF (academic) |

---

## 5. Q&A prep — anticipated judge questions

### "แล้วต่างจาก Aletheia (AAAI 2026) ยังไง?"

**ตอบ**: Aletheia = fake news detection only ผ่าน LLM+RAG. Freewall extends 4 ทาง:
1. **Persuasion tactic analysis** — Aletheia ไม่มี
2. **Synthetic content provenance** — Aletheia ไม่ตรวจ AI-gen
3. **Counter-Perspective Agent** — Aletheia มี Discussion Hub แต่ไม่มี automated counter-argument
4. **User sovereignty design** (Override + Sensitivity) — Aletheia paternalistic กว่า

### "GPTZero claim 99% accuracy แล้ว ทำไมยังต้องสร้าง?"

**ตอบ**: AI text detection alone ไม่พอ — modern LLM (GPT-5, Claude) detection ใน wild ยัง unreliable (research consensus 2025). Freewall integrate AI-text เป็น **weak signal** ใน 1 ของ 6 agents — combine กับ persuasion + claim verification + provenance ใน loop เดียว. GPTZero ไม่ทำส่วนหลัง

### "Multi-agent มันก็แค่ overhead?"

**ตอบ**: 
- DFBench MoA-DF (Jun 2025) พิสูจน์ว่า multi-agent **beats single model** ใน deepfake detection
- ED2D (AAAI 2026) พิสูจน์ว่า multi-agent debate ดีกว่า single agent ใน misinformation correction
- Freewall replicate pattern นี้ใน production extension — academic precedent ชัดเจน

### "Persuasion detection แม่นแค่ไหน?"

**ตอบ (with eval data)**: เราวัดบน PersuSafety subset 50-100 examples ได้ X% precision / Y% recall — in line กับ DarkPatterns-LLM (Dec 2025) ที่ benchmark GPT-4 ได้ 65-89%. Freewall ใช้ multi-agent + structured output เพื่อลด variance

### "C2PA adoption ต่ำมาก ใช่มั้ย?"

**ตอบ**: ถูกต้อง — 6000+ members แต่ social platforms ยัง strip metadata. Freewall design ตรงนี้ — Provenance Agent ใช้ C2PA เมื่อมี, fall back ไป HF ensemble + source reputation เมื่อไม่มี. EU AI Act Article 50 เริ่ม Aug 2026 จะเร่ง adoption — Freewall เตรียม ready

### "Why now? ทำไมต้องตอนนี้?"

**ตอบ**: 3 ปัจจัย convergence:
1. **Policy**: EU AI Act Aug 2026, California SB 942 Jan 2026 — regulation มาแล้ว
2. **Threat**: Cognitive Sovereignty (Yuste, Springer 2025) ยกเป็น constitutional issue
3. **Capability**: Frontier LLMs + Agents SDK ทำให้ multi-agent defense possible เป็นครั้งแรก

---

## 6. Citations to use ใน application + pitch

ลำดับความสำคัญ (sorted by impact):

1. **Cognitive Sovereignty** — Yuste et al., Ethics and Information Technology, Springer (Nov 2025)
2. **PersuSafety** — Liu et al., COLM 2025 (arXiv 2504.10430) — taxonomy + dataset
3. **DFBench MoA-DF** — Wang et al., (arXiv 2506.03007, Jun 2025) — multi-agent for synthetic detection
4. **ED2D** — AAAI 2026 (arXiv 2511.07267) — multi-agent debate for misinformation
5. **DarkPatterns-LLM** — (arXiv 2512.22470, Dec 2025) — accuracy bounds reference
6. **EU AI Act Article 50** — enforcement Aug 2026
7. **Gartner Guardian Agents trend** — 2026 agentic AI report

---

## 7. Honest disclaimers สำหรับ Q&A

ใช้เมื่อ judges ถาม technical accuracy:

- "AI text detection ใน wild ยังไม่น่าเชื่อถือ — เราเลย ensemble กับ persuasion + provenance"
- "C2PA adoption กำลังโต แต่ social media platforms ส่วนใหญ่ยัง strip metadata — เรารับ reality นี้"
- "Persuasion detection accuracy ของ frontier model ยังแค่ ~80% (DarkPatterns-LLM 2025) — เราใช้ multi-agent + measured eval เพื่อลด variance"
- "AI-image detection ยังไม่ solved — Flux, Midjourney v6 ตรวจยากขึ้น (AIGIBench 2025) — ensemble ช่วยได้แต่ไม่ perfect"

---

## Verdict 1 บรรทัด

**Freewall ไม่ใช่ ML invention ใหม่ — เป็น product synthesis ที่ตรง SOTA frontier ของ field ที่กำลัง hot โดยรวม technique ที่ proven ใน research แต่ยังไม่ productized — defensible ใน Q&A ถ้า team อ่าน 5-7 papers ที่ list ไว้ก่อน hackathon**
