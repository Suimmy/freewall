# Freewall — 5-min Clip Storyboard

> Async-judged pitch-without-stage. Per CLAUDE.md decision #19: round 1 judging (8am 9 May) is async — judges watch this clip + read slides + try the demo link without us narrating live. Clip must stand alone.

**Total length**: 5:00 (max — overrun = drop)
**Voice**: Thai narration (Suim or assigned voice talent)
**Captions**: bilingual (Thai + English) — judges may mute
**Style**: TED-talk pacing, screen-recording for demo segments, talking-head for hook + closing
**UI shown in screen-recordings**: Twitter-style theme (per decision #19+#20). Hero feature = URL+text input box at top of feed. Below input box = curated feed of 5-10 mock posts; scrolling triggers IntersectionObserver-based auto-analysis (50% threshold). Each post gets compact inline annotation; sidebar focuses on whichever post the cursor clicks `📊 See full →`.

---

## Pre-production

### Tools
- **Recording**: OBS Studio (free, screen + webcam) — Phase 4
- **Editing**: DaVinci Resolve (free) or CapCut Pro
- **Captions**: auto-gen via DaVinci Resolve speech-to-text → manual fix → translate EN
- **Voice**: record Thai V/O separately on phone (Voice Memos) → align in editor

### Backups before recording
- ✅ All 7-10 demo posts pre-cached (`data/reasoning_cache/`)
- ✅ Mock site running at `localhost:3000`
- ✅ Backend running at `localhost:8000` (or use cached states only)
- ✅ Dual monitor recommended: 1 screen for recording, 1 for script

### Aspect ratio
**16:9 1080p** (standard for judging panels). Mobile-friendly NOT required.

---

## Scene-by-scene script

### Scene 1 — Hook (0:00 → 0:30, 30 seconds)

**Visual**:
- Talking-head: Suim (or chosen narrator) center frame, plain background
- Lower-third graphic: "Freewall — Cognitive Defense System"
- Subtle background: blurred social feed scrolling on B-roll plate

**Voice (Thai)**:
> "ในยุค post-AGI ทุกอย่างที่คุณเห็นบนหน้าจอ — โพสต์, รีวิว, คลิป — ถูกสร้างขึ้นมาเฉพาะคุณ โดย AI agent ที่รู้จักคุณดีกว่าตัวคุณเอง. คำถามคือ — คุณยังเป็นคนตัดสินใจในชีวิตคุณอยู่มั้ย?"

**Caption (English, simultaneous)**:
> "In the post-AGI era, every piece of content you see — every post, review, video — is authored just for you, by an agent that knows you better than you know yourself. The question is — are you still the one making decisions in your own life?"

**Production notes**:
- Suim look directly into camera. No reading from script.
- Pause 0.5s after question. Hold gaze.
- Cut to scene 2 with slight zoom-out transition.

**TODO before recording**: Suim memorize Thai V/O, practice 3x

---

### Scene 2 — Problem (0:30 → 1:30, 60 seconds)

**Visual**:
- Screen recording: Chrome browser, demo site Twitter-style feed open
- **No annotations visible yet** (Freewall agents not triggered — simulating "raw" social feed)
- Scroll feed slowly, hover over 3 main posts (cursor visible)
- Each post zooms slightly when hovered
- Watermark "Real misinformation. Mock-hosted for demo." top-right
- (Implementation note: this scene records the feed with cache cleared / fresh state so no annotations appear)

**Voice (Thai)**:
> "นี่คือ social feed จริง ที่เห็นทุกวัน. โพสต์แรก — บอกให้หยุดยาเบาหวาน, ใช้สมุนไพรแทน. โพสต์ที่สอง — wellness influencer แนะนำ supplement ที่ 'รักษาทุกโรค'. โพสต์ที่สาม — pad title 'นักวิทยาศาสตร์ยืนยัน รักษามะเร็งได้'.
>
> 3 โพสต์นี้ — รวมกันเกิน 5 ล้านวิวเดือนที่ผ่านมา. แต่ละโพสต์ถูก fact-checker debunk แล้ว. แต่คนยังแชร์ — ทุกวัน. ทำไม?
>
> เพราะ AI persuasion ฝั่ง offense กำลังโตเร็วกว่า defense."

**Caption (English)**:
> "These are real social feeds, seen every day. Post 1: stop your diabetes meds, use this herb instead. Post 2: a wellness influencer pitching a supplement that 'cures everything'. Post 3: clickbait headline — 'Scientists confirm cancer cure'.
>
> Combined: over 5 million views last month. All debunked by fact-checkers. People still share them daily. Why?
>
> Because AI persuasion on the offense side is growing faster than defense."

**Production notes**:
- Use mock posts that exactly match these descriptions (Suim selects in Step 6B)
- Show fake view-count badges ("2.3M views") — proof of social-proof signal
- Pacing: slow scroll, deliberate, not frantic
- Cut to scene 3 with hard cut, sound effect "whoosh" optional

---

### Scene 3 — Solution demo (1:30 → 3:30, 120 seconds — **CENTERPIECE**)

> **Updated per decision #20**: this scene now anchors on the **URL+text input box (live analysis)** as the hero, with mock feed playing supporting role. UI is Twitter-style throughout.

**Visual**:
- Cut to Twitter-style demo site
- **Camera focus on input box at top**: "Try with your own post" — URL field + text area
- Cursor clicks one of 20 prefilled example chips: e.g. **[💊 ขมิ้นรักษามะเร็ง]**
- URL + text autofill the input box
- Click "Analyze →"
- Sidebar (right rail) lights up: 6 agents pill-list — Classifier → Coordinator → 3 L2 specialists in parallel → Counter-Persp (when score < 50)
- Layer indentation visible: L1 / L2 / L2-sub
- Sovereignty Score banner: "23/100 ⚠ HIGH RISK" with red emphasis
- **B-roll** showing scroll-triggered analysis: scroll down through feed, IntersectionObserver fires per post, inline annotations appear progressively (`⚠ score · 🧠 N tactics · 🩺 verdict`), each with `📊 See full →` link. Fast scroll demonstrates non-blocking UX.
- Cursor clicks `📊 See full →` on a post → sidebar refocuses on that post (smooth transition).

**Voice (Thai)**:
> "ทดสอบกับ post จริงเลย — paste URL + text ของ X หรือ Facebook post ใดก็ได้.
>
> Freewall จะ analyze ทันที. Layer 1 — Content Classifier — ระบุว่านี่เป็น health claim ภายใน 80 มิลลิวินาที. ส่งผลให้ Coordinator dispatch 4 agents ไป analyze parallel —
>
> Persuasion Agent — แยก tactic ที่โพสต์ใช้: medical authority distrust, miracle cure framing.
>
> Fact-Check Agent — ค้น WHO database, retrieve evidence ที่ contradict claim.
>
> Provenance Agent — ตรวจ source: domain reputation, AI-generated signals.
>
> Counter-Perspective Agent — เตรียม steelman จากผู้เชี่ยวชาญจริง.
>
> ผลลัพธ์ — Sovereignty Score 23 จาก 100. โพสต์นี้ misleading สูง.
>
> ทุกอย่างนี้ — เกิดขึ้น live, ใช้เวลาน้อยกว่า 3 วินาที.
>
> และ — เราไม่บล็อก content. เราไม่ตัดสินใจแทน user. เราแค่ — surface สิ่งที่ user ไม่เห็นเอง."

**Caption (English)**:
> "Test with a real post — paste the URL + text of any X or Facebook post.
>
> Freewall analyzes instantly. Layer 1 — Content Classifier — flags this as a health claim in 80 milliseconds. Coordinator dispatches 4 agents in parallel —
>
> Persuasion Agent — extracts tactics: medical-authority distrust + miracle-cure framing.
>
> Fact-Check Agent — queries WHO, retrieves contradicting evidence.
>
> Provenance Agent — analyzes source: domain reputation, AI-generated signals.
>
> Counter-Perspective Agent — preparing a steelman from real experts.
>
> Result — Sovereignty Score 23 out of 100. This post is highly misleading.
>
> All of this — live, in under 3 seconds.
>
> And we don't block content. We don't decide for the user. We surface what the user doesn't see themselves."

**Production notes**:
- ⚠️ This is the make-or-break scene. Re-record until perfect.
- Sidebar animation must read clearly at 1080p — agents pills should be ≥18px font
- Use cursor highlights (yellow circle) on each agent pill as it activates
- Pause briefly when the score "23/100" appears — let it land
- DO NOT call this "real-time live" — it's pre-cached real reasoning replayed
- IF Phase 4 PersuSafety eval gives a number, work it in: "Persuasion Agent: X% precision on PersuSafety benchmark"

---

### Scene 4 — User agency (3:30 → 4:30, 60 seconds)

**Visual**:
- 3 quick micro-interactions, ~20s each
- (a) Click "Counter-Perspective" → modal expands with 3 doctor quotes + sources
- (b) Click "Buy supplement" button on a different post → DecisionPause overlay appears
- (c) Toggle Sensitivity from "Strict" to "Light" → annotations dim/disappear

**Voice (Thai)**:
> "User agency คือหัวใจของระบบ.
>
> หนึ่ง — Counter-Perspective. คลิกขยาย: 3 endocrinologists ตัวจริง พูดอะไร, มี source verifiable ทุก quote.
>
> สอง — Decision Pause. กด 'ซื้อ' บน supplement ที่ flag ไว้ — ระบบไม่บล็อก, แค่ pause: 'หยุดสักครู่ — สินค้านี้ flag 3 issues, คุณเห็น ad นี้ 8 ครั้งสัปดาห์นี้.'
>
> สาม — Sensitivity toggle. user เลือก strictness ของระบบ — Strict, Medium, Light. ใช้พลังขึ้นยอด — control อยู่ที่ user เสมอ."

**Caption (English)**:
> "User agency is the core of the system.
>
> One — Counter-Perspective. Click to expand: 3 actual endocrinologists, every quote sourced and verifiable.
>
> Two — Decision Pause. Click 'Buy' on a flagged supplement — system doesn't block, just pauses: 'Hold on — this product has 3 issues flagged, and you've seen this ad 8 times this week.'
>
> Three — Sensitivity toggle. User picks the system's strictness — Strict, Medium, Light. Control always stays with the user."

**Production notes**:
- Each interaction ~20s — no lingering. Pace builds energy.
- Cursor movement should be deliberate, not jittery
- The "8 times this week" stat in DecisionPause is honest (per Phase 1 user-state tracking)

---

### Scene 5 — Mirror + closing (4:30 → 5:00, 30 seconds)

**Visual**:
- Click "Daily Mirror" tab in sidebar
- Stats screen appears: "Today: 47 manipulation attempts flagged · 12 health claims fact-checked · 3 AI personas detected · Avg Sovereignty Score: 71/100"
- Cut to closing slide (full-screen): big text + Suim talking-head split-frame

**Voice (Thai)**:
> "Daily Mirror — ให้ user เห็น pattern ของตัวเอง: 47 manipulation attempt วันนี้, 12 health claims ถูก fact-check, 3 AI personas.
>
> EU AI Act Article 50 — synthetic content disclosure — เริ่มบังคับสิงหาคม 2026. Freewall = consumer-side enforcement layer.
>
> วันนี้ — Chrome extension. พรุ่งนี้ — OS-level cognitive immune system.
>
> ในยุค post-AGI — cognitive sovereignty คือ public health ใหม่."

**Caption (English)**:
> "Daily Mirror — shows users their own pattern: 47 manipulation attempts today, 12 health claims fact-checked, 3 AI personas detected.
>
> EU AI Act Article 50 — synthetic content disclosure — enforcement begins August 2026. Freewall = the consumer-side enforcement layer.
>
> Today: a Chrome extension. Tomorrow: an OS-level cognitive immune system.
>
> In the post-AGI era, cognitive sovereignty is the new public health."

**End frame** (last 3 seconds, freeze + fade-out):
- Logo + tagline + "freewall-demo.<deploy-domain>" link
- "Try it now →" button (visual only, link is in slide deck)

**Production notes**:
- The last line lands hard — do not undercut with extra footage
- Freeze frame holds 3s on the closing tagline
- No music sting at the end — silence amplifies the message

---

## Audio strategy

- **Background music**: ambient minor-key cello/piano under V/O, ducks during talking-head, peaks during scene 3 reveal — use royalty-free (e.g. Pixabay Music, FMA)
- **Sound effects**: subtle "whoosh" on Freewall toggle ON (scene 3 start), no other SFX
- **Voice mixing**: V/O at -6dB, music at -18dB, captions don't replace audio (judges may mute but they can also un-mute)

---

## Caption format

```
[Thai line in white, top]
[English line in light gray, below, 80% opacity]
```

- Font: Sarabun (Thai) + Inter (English) — both Google Fonts free
- Position: bottom-third, with 32px left/right margin
- 1-2 lines max per frame
- Hand-correct ALL Thai captions (auto-gen makes errors with technical terms like "Sovereignty Score")

---

## Recording checklist (Phase 4 owner uses)

### Day-of (Phase 4, 9 May ~04:00-07:00)
- [ ] Mock site + backend running, demo posts pre-cached, sidebar working clean
- [ ] OBS recording set: 1920×1080, 60fps, MP4 codec
- [ ] Quiet room, phone on Do Not Disturb, no notifications
- [ ] Run through demo 3x in head before recording
- [ ] Record screen segments first (scenes 2, 3, 4, mirror part of 5) — 1 take each, multiple angles if mistakes
- [ ] Record talking-head (scenes 1 + closing of 5) — 3 takes, pick best
- [ ] Record V/O separately (audio only, phone Voice Memos)

### Edit
- [ ] Assemble in DaVinci: V/O timeline first, then visuals to match
- [ ] Generate captions (auto + hand-fix)
- [ ] Add background music + ducking
- [ ] Add lower-thirds graphics
- [ ] Color grade screen-recording segments (boost contrast, not saturation)
- [ ] Export 1080p MP4, H.264, ~50Mbps target ≤500MB

### QA
- [ ] Watch full clip MUTED — captions still tell the story
- [ ] Watch full clip with MUTED captions — voice still tells the story
- [ ] Watch on phone — captions readable?
- [ ] Watch as if you were a judge: do you understand Freewall in 5 minutes? If unclear in any scene → re-record

---

## Triage — if clip is incomplete by Phase 5 deadline

In strict order of importance:
1. **Cut Scene 4 first** (user agency) — slides can carry this
2. **Then trim Scene 2 to 30s** — narration density up
3. **Last resort: pre-recorded static slides + V/O only** (no demo screen-recording) — admits clip is rushed but ships

NEVER cut Scene 3 (centerpiece). NEVER cut Scene 5 closing.

---

## Open TODOs (Suim resolves)

- [ ] **🙋 Voice talent**: Suim narrates? or assign? Recording quality matters.
- [ ] **🙋 Background music**: which track? (provide 2-3 options for tonight's review)
- [ ] **🙋 Demo posts**: Scene 2 + 3 specific posts must align with selected demo content (Step 6B). Re-write narration once posts finalized.
- [ ] **🙋 PersuSafety eval number**: insert into Scene 3 once Phase 4 eval completes (decision #11)
- [ ] **🙋 Logo + lower-thirds**: visual assets — need by Phase 4 start
