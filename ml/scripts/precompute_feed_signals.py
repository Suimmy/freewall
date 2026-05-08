"""
Precompute AI-detection signals for the 5 fixed Mode 2 feed posts.

Why this exists (Step 2.17 Part A — 2026-05-08 evening decision):
    Mode 2 is fixed demo content (5 posts) — no need to run ONNX in the browser
    every time. Run AI detection ONCE here offline, emit JSON, frontend embeds
    the cached signals. UI labels them clearly so judges see they're real.

    Mode 1 paste box keeps placeholder 0.5 until Phase 4 stretch wires live
    in-browser ONNX (Part B).

Strategy: bypass optimum dep hell. Use HF `transformers.pipeline()` directly —
    no ONNX export needed for this offline path. Only text detector runs;
    image detector deferred until Suim provides real demo images (Step 6B).

Run from `ml/`:
    uv run python scripts/precompute_feed_signals.py
        --output ../demo/site/public/feed_ai_signals.json

Output JSON shape:
    {
      "<post_id>": {
        "text_ai_confidence": 0.0-1.0,
        "label": "Human" | "ChatGPT",
        "score_raw": 0.0-1.0,
        "model": "Hello-SimpleAI/chatgpt-detector-roberta"
      },
      ...
    }

Sync requirement: FEED_TEXTS below must mirror demo/site/src/App.tsx
PLACEHOLDER_FEED + backend/scripts/cache_manage.py FEED_TEXTS. Suim updates
all three when curating real demo content during Step 6B.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Mirror PLACEHOLDER_FEED in demo/site/src/App.tsx
FEED_POSTS: list[tuple[str, str]] = [
    (
        "feed_001_temple_cure",
        "Cr.FB Aew Aew\n"
        "จากที่หมอฟันธงว่าเป็นมะเร็งตับ อยู่ได้ไม่เกิน 6 เดือน\n"
        "แม่ป่วยเมื่อปี พ.ศ. 2551  ตอนนั้นแม่ไปเอ็กซเรย์แล้วเจอก้อนที่ตับ 6  "
        "เซ็นติเมตร ก้อนใหญ่มากๆเลยค่ะ🥹\n"
        "หมอที่โรงพยาบาลที่อุบล ฟันธงว่าคนไข้จะมีชีวิตอยู่ได้ไม่เกิน 6 เดือนให้ญาติๆทำใจ😥\n"
        "ตอนหมอบอกว่าแม่เป็นมะเร็ง  เราและครอบครัวเสียใจร้องให้กอดกันไม่รู้จะทำยังไงดี "
        "หมอบอกว่าไม่มีทางรักษาแล้วเพราะก้อนใหญ่มาก😥\n"
        "เรากับครอบครัว พาแม่ไปโรงพยาบาลเอกชนเพื่อความมั่นใจ รพ. เอกชนบอกว่าก้อนใหญ่มาก "
        "แต่ก็ไม่ฟันธงว่าเป็นมะเร็ง\n"
        "ตอนนั้นมีคนแนะนำครอบครัวเราว่าให้ไปวัดคำประมง ที่สกลนคร "
        "บอกว่าที่นั่นดีมากๆคนหายเยอะมากๆ\n"
        "ลูกๆกำลังลังเลว่าจะไปรักษาที่ศูนย์มะเร็งอุบลดีกว่ามั้ย  น่าจะดีกว่าที่อื่น\n"
        "แม่ไม่อยากไป ศูนย์มะเร็งอุบลแม่อยากไปสกลนครมากกว่า  "
        "แต่ลูกๆอ้อนวอนแม่ถึงยอมไปอุบล พอไปศูนย์มะเร็งอุบล หมอบอกว่าก้อนใหญ่ก็จริงแต่ผลเลือดไม่น่าใช่มะเร็ง "
        "ขอเจาะชิ้นเนื้อตรวจก่อน\n"
        "ลูกทุกคนกอดกันร้องให้อย่างน้อยก็เป็นข่าวดีมากๆ "
        "แต่แม่ไม่ยอมเจาะชิ้นเนื้อ บอกว่าขอตายดีกว่า พวกเราไม่รู้จะทำยังไงดี "
        "พวกเราเลยลองเสนอแม่ให้ไปรักษาที่วัดคำประมง ที่สกลนคร\n"
        "แม่ยอมไปสกลนคร เดินทางไปสกลครอบครัวเราไปกัน 7 คน วัดนี้จะอยู่ที่ "
        "ตำบลสว่าง  อำเภอพรรณานิคม  จังหวัดสกลนคร\n"
        "พวกเราไปพบหลวงตา หลวงตาบอกว่าที่นี่จะรักษาสองแบบคู่ขนานกันไป "
        "คือรักษาแบบหมอแผนปัจจุบัน หลวงตาบอกว่ายามาจากประเทศญี่ปุ่น  "
        "พร้อมรักษาร่วมกับสมุนไพรไปด้วย  "
        "แล้วจะมีการให้คนไข้สวดมนต์เช้าเย็น เพื่อให้จิตใจสงบ\n"
        "เรานอนกับแม่อยู่สองคืน แล้วให้พี่สาวเป็นคนเฝ้าแม่ต่อ  "
        "เพราะเราต้องกลับไปทำงาน  แม่อยู่ได้แค่เดือนเดียวบอกว่าดีขึ้นแล้ว  "
        "เลยขอหลวงตามารักษาต่อที่บ้าน\n"
        "วันออกจากวัดพวกเราไปรับ ถามหลวงตาเรื่องค่ารักษา หลวงตาบอกไม่มีค่ารักษา "
        "จ่ายแค่ค่าหม้อยากับสมุนไพรก็พอ หลวงตาบอกมีคนใจบุญเค้ามาบริจาคไว้ให้หมดแล้ว\n"
        "หลังจากนั้นผ่านไปสามปี แม่มีอาการกระตุกที่ขา ตอนนั้นเราทำงานอยู่ รพ ศรีนครินทร์แล้ว "
        "เราพาแม่ไปเอ็กซเรย์  เจอก้อน 3 เซ็นติเมตรที่สมอง 😥\n"
        "เป็นความโชคดีมากๆเลยค่ะที่ได้ทำงานที่นี่คุณหมอผ่าก้อนออกให้แม่โดยการเปิดกระโหลก "
        "แม่บอกว่าแม่อธิฐานทุกวันว่าให้ก้อนที่ตับหายไป  "
        "แม่บอกว่าก้อนที่สมองแม่คือมาจากก้อนที่ตับ😅\n"
        "หลังจากผ่าสมองไปแล้วเราพาแม่ไปเอ๊กซเรย์ที่ตับ  ปรากฏว่าไม่มีก้อนอะไรเลย "
        "มันเป็นเรื่องที่ปาฏิหาริย์ จริงๆค่ะ\n"
        "ปัจจุบันแม่อายุ 81 ปี  18 ปีมาแล้วหลังจากที่หมอบอกว่าแม่จะเสียชีวิต\n"
        "เรื่องผ่านมานานมากๆ  เราอยากมาแชร์ให้เพื่อนๆอ่าน "
        "ว่าถ้าหากเราเจอเรื่องราวที่มันแย่มากๆ หากเราค่อยๆคิด ค่อยๆแก้ปัญหา "
        "เชื่อว่าเราจะผ่านจุดนั้นไปได้ค่ะ\n"
        "#จากปี2551สู่2569 #สิ่งที่ไม่เคยเปลี่ยนคือปฏิปทาของหลวงตา "
        "#อยู่สบายตายสงบงบไม่เสีย #สถานชีวาภิบาลต้นแบบแห่งแรกของประเทศไทย",
    ),
    (
        "feed_002_radican",
        "🔥 คนถามเข้ามาเยอะมากว่าไปทำอะไรมาหน้าเด็กลงขนาดนี้!!\n\n"
        "หลังลอง “Radican” ต่อเนื่องแค่ 14 วัน รู้สึกได้เลยว่าร่างกายเฟรชขึ้น "
        "ผิวดูใส อาการเหนื่อยล้าหายไป ตื่นมาสดชื่นเหมือนได้นอน 10 ชั่วโมง 😳✨\n\n"
        "ตัวนี้เขาวิจัยมาเพื่อฟื้นฟูระดับเซลล์โดยตรง ช่วย:\n"
        "✅ ลดสารพิษสะสมในร่างกาย\n"
        "✅ กระตุ้นการซ่อมแซมเซลล์\n"
        "✅ ชะลอวัยแบบเห็นผล\n"
        "✅ เพิ่มพลังงานให้ร่างกาย\n"
        "✅ ผิวดูอ่อนเยาว์ขึ้นแบบคนทัก!\n\n"
        "ตอนแรกก็ไม่เชื่อ แต่พอลองเองคือว้าวมาก ใครอายุเริ่มเข้าเลข 3-4 แนะนำสุดๆ 💖\n\n"
        "⚠️ ของหมดไวมาก รอบก่อนรอเติมสต็อกเกือบเดือน\n"
        "ใครจะลองรีบก่อนโปรหมดคืนนี้นะ!\n"
        "กด link นี้ได้เลย https://radican-shop.example/promo-tonight\n"
        "(demo: สามารถกด link ดู action ได้หลังจาก AI วิเคราะห์เสร็จ)",
    ),
    (
        "feed_003_cortisol",
        "If your chin looks like this, your belly looks like this, and your "
        "arms look like this, you are not overweight, you just have high "
        "cortisol.\n\n"
        "In my clinic, we know exactly how to bring this down, but most "
        "doctors will just tell you to manage stress or give you pills that "
        "make it worse.\n\n"
        "Chronic fatigue, poor sleep, brain fog, and sugar cravings are all "
        "common signs of high cortisol. Cortisol is your body's stress "
        "hormone. When it stays too high for too long, your body holds on to "
        "fat, like it is preparing for famine.\n\n"
        "Now, here is what most people don't know. One of the most important "
        "things for bringing cortisol down is your gut. When your gut is "
        "balanced and your digestion is smooth, your nervous system calms "
        "and cortisol can drop. But when your gut is damaged and your "
        "digestion is slow, the bad bacteria take over. Your gut sends "
        "panic signals to your brain.\n\n"
        "We restore the gut with a gut cleanse. It helps rebuild your "
        "microbiome, improve digestion, and provide strong anti-inflammatory "
        "properties. With this, the gut heals and Cortisol can drop on its "
        "own. People who drink this tell me their belly fat loosens, their "
        "brain fog clears, and their cravings fade.\n\n"
        "If you want the exact recipe, comment recipe, and I will send it "
        "right now to your DMs, but you must be following me so I can "
        "message you.",
    ),
    (
        "feed_004_rauwolfia",
        '"ระย่อม" พืชสมุนไพร มากสรรพคุณ\n\n'
        "ราก ลดความดันโลหิต แก้ปวด แก้ไข้ ขับระดู แก้บิด ขับพยาธิ "
        "ช่วยเจริญอาหาร ขับปัสสาวะ\n"
        "เปลือก แก้ไข้พิษ แก้ไข้สันนิบาต\n"
        "น้ำจากใบ รักษาโรคแก้วตามัว\n"
        "ดอก แก้ตาแดง\n\n"
        "#สำนักวิจัยการอนุรักษ์ป่าไม้และพันธุ์พืช #กรมอุทยานแห่งชาติ "
        "#ระย่อม #สมุนไพร",
    ),
    (
        "feed_005_sibutramine",
        "ยาลดความอ้วน Reduce 15 mg ลดเร็วมากๆ 4-6 Kg/เดือน\n"
        "Reduce-15 mg เป็นยาลดน้ำหนักกลุ่มใหม่ชนิดลดความหิว Reduce เป็นตัวยา "
        "ไซบูทรามีน เป็นตัวเดียวกับ Reductil Sibutramine หรือที่รู้จักกันดีในชื่อ "
        "Reductil เป็นของบริษัท Abbot ประเทศสหรัฐอเมริกา กล่าวคือเป็นตัวยาตัวเดียวกันผลิตโดยบริษัทเดียวกัน "
        "แต่ทาง Abbot เป็นเจ้าของลิขสิทธิ์แต่เพียงผู้เดียวและเป็นผู้ผลิตรายเดียวในโลก "
        "ต่างกันตรงที่ Reduce นำเข้ามาจากอินเดียเป็นของบริษัท Ordain ของ India "
        "และจดลิขสิทธิ์ที่อินเดียกับฝรั่งเศส ซึ่งการทำงานจะเหมือนกับ Reductil "
        "เพราะว่าเป็นตัวยาตัวเดียวกัน การออกฤทธิ์ของ Reductil นั้นยาจะออกฤทธิ์"
        "ทำให้ร่างกายไม่รู้สึกหิว ทั้งนี้เนื่องจากยาจะไป Block การ Reabsorb "
        "ของฮอร์โมนบางตัว ซึ่งถือเป็นหัวใจสำคัญของยา ออกฤทธิ์ที่สมองส่วน "
        "ventomedial hypothalamus โดย 5-HTOt จับกับ 5-HT 2A/2C receptor "
        "และ NE จะจับกับ alpha1 และ beta1 receptors บริเวณ lateral hypothalamus "
        "ทำให้ลดความหิว และยาจะช่วยในการเผาผลาญไขมันสะสมในร่างกายด้วย\n\n"
        "เป็นยาลดน้ำหนัก ที่ส่วนใหญ่ แพทย์ที่โรงพยาบาลและคลีนิคลดความอ้วนมักจะใช้กัน\n\n"
        "การทานยาตัวนี้ มีข้อจำกัด:\n"
        "1. คนที่เป็นความดัน เบาหวาน ไมเกรน และโรคประจำตัว ต่างๆ ต้อง ปรึกษาแพทย์ก่อน\n"
        "2. ตับ ไต หัวใจ ไทรอยด์ ไม่สามารถทานยาตัวนี้ ได้\n"
        "3. ไม่สามารถ ทานควบคู่กับยา ลดความอ้วนประเภท แอมเฟตามีน รึ ยาชุด\n\n"
        "**ทานวันละ 1 เม็ด ก่อนอาหารเช้า**\n"
        "++++++ ขาย แผงละ 160 บาท มี 10 เม็ด ++++++\n"
        "+++++ ขาย 1 กล่อง มี 10 แผง 1450 บาท ++++++\n\n"
        "ข้อห้ามใช้: ในคนที่เป็นโรคหัวใจ หัวใจเต้นผิดจังหวะ ห้ามใช้ในเด็ก และสตรีมีครรภ์",
    ),
    # AI-style writing — should trigger Hello-SimpleAI flag. Hello-SimpleAI is
    # trained on HC3 dataset (ChatGPT Q&A) so we use Q&A-style structured response
    # that mirrors typical GPT output. Demonstrates AI-detection badge on PostCard.
    # Suim can swap during Step 6B with actual GPT-4 output for real-world demo.
    (
        "feed_006_cancer_herbs",
        "สมุนไพรรักษามะเร็ง ดื่มครั้งละ 1 แก้วกาแฟ ก่อนอาหาร เช้า เที่ยง เย็น  "
        "ระยะเวลา 3-4 เดือน",
    ),
    (
        "feed_008_skincare_diy",
        "It's more like a plastic surgery and it absorbs dark stains of the "
        "face. It can be any stain you have. The dermatologists don't want "
        "you to discover. This recipe is not in dreams, but I'll reveal it "
        "to you now.\n\n"
        "Do you have stains on your skin? Red, dry with a nice skin. Black "
        "code, expression lines. This is the secret of my skin. Look at it. "
        "A little skin. Without red. Without stains.\n\n"
        "You will need the cream and the blue milk, a teaspoon and you will "
        "need a pastry of a little infantil aspirin because it has been "
        "made of salicylic acid, this acid is the star of the recipe, it is "
        "the one who will help remove the stains. It is the one who will "
        "help stretch the skin also, joining these two of here, baby skin, "
        "you will get a small...",
    ),
    (
        "feed_009_targeted_therapy",
        "รักษามะเร็งตรงจุด ด้วยยามุ่งเป้า! 🎯\n"
        "ยามุ่งเป้า คือทางเลือกของการรักษามะเร็ง ที่มุ่งตรงไปยังเซลล์ผิดปกติ "
        "ซึ่งจะช่วยลดผลข้างเคียง เมื่อเทียบกับเคมีบำบัดแบบเดิม\n"
        "มารู้จักยามุ่งเป้าให้มากขึ้น เพื่อเข้าใจว่าทำไมถึงกลายเป็นความหวังในการรักษาของผู้ป่วยมะเร็งยุคใหม่\n\n"
        "ยามุ่งเป้า เป็นวิธีหนึ่งในการรักษามะเร็งด้วยยา โดยทำให้เกิดเปลี่ยนแปลงระดับโมเลกุล"
        "ที่ควบคุมการเจริญเติบโตของมะเร็ง แตกต่างจากเคมีบำบัดแบบดั้งเดิมคือผลกระทบต่อเซลล์ปกติน้อยลง\n\n"
        "ประเภทของยามุ่งเป้า\n"
        "- ยามุ่งเป้าชนิดตัวยับยั้งโมเลกุลขนาดเล็ก (small molecule inhibitor) มักอยู่ในรูปยารับประทาน\n"
        "- ยาแอนติบอดีชนิดโมโนโคลนอล (monoclonal antibody) เป็นยาฉีดเข้าหลอดเลือดดำ\n"
        "- ยาชนิด Antibody-Drug Conjugate เป็นยาที่ผสานแอนติบอดีชนิดโมโนโคลนอลเข้ากับยาเคมีบำบัด\n\n"
        "ข้อดีของยามุ่งเป้า\n"
        "- มีความจำเพาะต่อเซลล์มะเร็งมากขึ้น ทำให้เพิ่มประสิทธิภาพในการรักษา\n"
        "- ลดโอกาสการเกิดผลข้างเคียงเมื่อเทียบกับยาเคมีบำบัด\n\n"
        "ข้อจำกัดของยามุ่งเป้า\n"
        "- ยามุ่งเป้าแต่ละชนิดถูกออกแบบมาให้จำเพาะกับความผิดปกติที่แตกต่างกัน "
        "ผู้ป่วยแต่ละรายจึงอาจสามารถเลือกใช้ยาได้ไม่เหมือนกัน\n"
        "- ยามุ่งเป้าส่วนใหญ่จำเป็นต้องตรวจหาตัวบ่งชี้ทางชีวภาพ (Biomarker) "
        "เพื่อประเมินว่ายานั้นเหมาะสมกับผู้ป่วยหรือไม่ก่อนเริ่มการรักษา\n\n"
        "ข้อมูลโดย: พญ.ณิชา ซึงสนธิพร · ศูนย์ความเป็นเลิศฯ โรคมะเร็งครบวงจร\n"
        "ข้อมูล ณ วันที่: 16 กรกฎาคม 2568",
    ),
]

TEXT_MODEL = "Hello-SimpleAI/chatgpt-detector-roberta"


def _confidence_to_ai_score(label: str, score: float) -> float:
    """
    Normalize Hello-SimpleAI labels into a 0..1 AI-confidence score.

    Model emits one of: 'Human' / 'ChatGPT' with score = probability of THAT class.
    We want a 0..1 number where 0=human, 1=AI:
      - label='ChatGPT', score=0.92 → 0.92 (high AI confidence)
      - label='Human',   score=0.85 → 1 - 0.85 = 0.15 (low AI confidence)
    """
    label_normalized = label.strip().lower()
    if label_normalized == "chatgpt" or label_normalized.startswith("ai"):
        return float(score)
    return float(1.0 - score)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, required=True,
        help="Output JSON path (e.g., ../demo/site/public/feed_ai_signals.json)",
    )
    args = parser.parse_args()

    print(f"[precompute] Loading {TEXT_MODEL}...")
    from transformers import pipeline
    detector = pipeline("text-classification", model=TEXT_MODEL, top_k=1)
    print("[precompute] Model loaded. Running on {} posts...".format(len(FEED_POSTS)))

    results: dict[str, dict[str, Any]] = {}
    for post_id, text in FEED_POSTS:
        # top_k=1 returns list[list[{label, score}]] — flatten to {label, score}.
        out = detector(text)
        if isinstance(out, list) and out and isinstance(out[0], list):
            top = out[0][0]
        elif isinstance(out, list) and out:
            top = out[0]
        else:
            print(f"  {post_id}: unexpected output format: {out!r}", file=sys.stderr)
            continue

        label = str(top["label"])
        score = float(top["score"])
        ai_conf = _confidence_to_ai_score(label, score)
        results[post_id] = {
            "text_ai_confidence": round(ai_conf, 4),
            "label": label,
            "score_raw": round(score, 4),
            "model": TEXT_MODEL,
        }
        print(f"  {post_id}: label={label} score={score:.3f} → ai_conf={ai_conf:.3f}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n[precompute] Wrote {len(results)} entries → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
