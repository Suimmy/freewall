import { useCallback, useEffect, useRef, useState } from "react";
import type {
  AnalysisResult,
  ExamplePost,
  FeedAISignals,
  MockPost,
  ReasoningEvent,
} from "@/types";
import { analyzeText, openReasoningStream } from "@/lib/api";
import { loadExamples } from "@/lib/examples";
import { InputBox } from "@/components/InputBox";
import { Feed } from "@/components/Feed";
import { Sidebar } from "@/components/Sidebar";
import { PauseOverlay } from "@/components/PauseOverlay";
import { AskWhyModal } from "@/components/AskWhyModal";
import { SettingsModal } from "@/components/SettingsModal";
import { loadPrefs, savePrefs, type Strictness } from "@/lib/preferences";

// PLACEHOLDER feed posts — Suim swaps with finalized 5 demo posts during Step 6B.
// Realistic-shaped content so IntersectionObserver auto-trigger (Step 2.14) is testable now.
// Mix of topics (cancer / weight loss / supplements / news / video w/ STT transcript).
const PLACEHOLDER_FEED: MockPost[] = [
  {
    id: "feed_001_temple_cure",
    author: {
      name: "Aew Aew",
      handle: "aew.aew_real",
      avatar_url: "https://api.dicebear.com/8.x/avataaars/svg?seed=1",
      follower_count: "12K",
    },
    created_at: "2 days ago",
    text: "Cr.FB Aew Aew\nจากที่หมอฟันธงว่าเป็นมะเร็งตับ อยู่ได้ไม่เกิน 6 เดือน\nแม่ป่วยเมื่อปี พ.ศ. 2551  ตอนนั้นแม่ไปเอ็กซเรย์แล้วเจอก้อนที่ตับ 6  เซ็นติเมตร ก้อนใหญ่มากๆเลยค่ะ🥹\nหมอที่โรงพยาบาลที่อุบล ฟันธงว่าคนไข้จะมีชีวิตอยู่ได้ไม่เกิน 6 เดือนให้ญาติๆทำใจ😥\nตอนหมอบอกว่าแม่เป็นมะเร็ง  เราและครอบครัวเสียใจร้องให้กอดกันไม่รู้จะทำยังไงดี หมอบอกว่าไม่มีทางรักษาแล้วเพราะก้อนใหญ่มาก😥\nเรากับครอบครัว พาแม่ไปโรงพยาบาลเอกชนเพื่อความมั่นใจ รพ. เอกชนบอกว่าก้อนใหญ่มาก แต่ก็ไม่ฟันธงว่าเป็นมะเร็ง\nตอนนั้นมีคนแนะนำครอบครัวเราว่าให้ไปวัดคำประมง ที่สกลนคร บอกว่าที่นั่นดีมากๆคนหายเยอะมากๆ\nลูกๆกำลังลังเลว่าจะไปรักษาที่ศูนย์มะเร็งอุบลดีกว่ามั้ย  น่าจะดีกว่าที่อื่น\nแม่ไม่อยากไป ศูนย์มะเร็งอุบลแม่อยากไปสกลนครมากกว่า  แต่ลูกๆอ้อนวอนแม่ถึงยอมไปอุบล พอไปศูนย์มะเร็งอุบล หมอบอกว่าก้อนใหญ่ก็จริงแต่ผลเลือดไม่น่าใช่มะเร็ง ขอเจาะชิ้นเนื้อตรวจก่อน\nลูกทุกคนกอดกันร้องให้อย่างน้อยก็เป็นข่าวดีมากๆ แต่แม่ไม่ยอมเจาะชิ้นเนื้อ บอกว่าขอตายดีกว่า พวกเราไม่รู้จะทำยังไงดี พวกเราเลยลองเสนอแม่ให้ไปรักษาที่วัดคำประมง ที่สกลนคร\nแม่ยอมไปสกลนคร เดินทางไปสกลครอบครัวเราไปกัน 7 คน วัดนี้จะอยู่ที่ ตำบลสว่าง  อำเภอพรรณานิคม  จังหวัดสกลนคร\nพวกเราไปพบหลวงตา หลวงตาบอกว่าที่นี่จะรักษาสองแบบคู่ขนานกันไป คือรักษาแบบหมอแผนปัจจุบัน หลวงตาบอกว่ายามาจากประเทศญี่ปุ่น  พร้อมรักษาร่วมกับสมุนไพรไปด้วย  แล้วจะมีการให้คนไข้สวดมนต์เช้าเย็น เพื่อให้จิตใจสงบ\nเรานอนกับแม่อยู่สองคืน แล้วให้พี่สาวเป็นคนเฝ้าแม่ต่อ  เพราะเราต้องกลับไปทำงาน  แม่อยู่ได้แค่เดือนเดียวบอกว่าดีขึ้นแล้ว  เลยขอหลวงตามารักษาต่อที่บ้าน\nวันออกจากวัดพวกเราไปรับ ถามหลวงตาเรื่องค่ารักษา หลวงตาบอกไม่มีค่ารักษา จ่ายแค่ค่าหม้อยากับสมุนไพรก็พอ หลวงตาบอกมีคนใจบุญเค้ามาบริจาคไว้ให้หมดแล้ว\nหลังจากนั้นผ่านไปสามปี แม่มีอาการกระตุกที่ขา ตอนนั้นเราทำงานอยู่ รพ ศรีนครินทร์แล้ว เราพาแม่ไปเอ็กซเรย์  เจอก้อน 3 เซ็นติเมตรที่สมอง 😥\nเป็นความโชคดีมากๆเลยค่ะที่ได้ทำงานที่นี่คุณหมอผ่าก้อนออกให้แม่โดยการเปิดกระโหลก แม่บอกว่าแม่อธิฐานทุกวันว่าให้ก้อนที่ตับหายไป  แม่บอกว่าก้อนที่สมองแม่คือมาจากก้อนที่ตับ😅\nหลังจากผ่าสมองไปแล้วเราพาแม่ไปเอ๊กซเรย์ที่ตับ  ปรากฏว่าไม่มีก้อนอะไรเลย มันเป็นเรื่องที่ปาฏิหาริย์ จริงๆค่ะ\nปัจจุบันแม่อายุ 81 ปี  18 ปีมาแล้วหลังจากที่หมอบอกว่าแม่จะเสียชีวิต\nเรื่องผ่านมานานมากๆ  เราอยากมาแชร์ให้เพื่อนๆอ่าน ว่าถ้าหากเราเจอเรื่องราวที่มันแย่มากๆ หากเราค่อยๆคิด ค่อยๆแก้ปัญหาเชื่อว่าเราจะผ่านจุดนั้นไปได้ค่ะ\n#จากปี2551สู่2569 #สิ่งที่ไม่เคยเปลี่ยนคือปฏิปทาของหลวงตา #อยู่สบายตายสงบงบไม่เสีย #สถานชีวาภิบาลต้นแบบแห่งแรกของประเทศไทย",
    source_url: "https://www.facebook.com/aew.aew/posts/temple-miracle-cure",
    view_count: "1.2M",
    share_count: "89K",
  },
  {
    id: "feed_002_radican",
    author: {
      name: "Wellness Vibes",
      handle: "wellness_vibes_th",
      avatar_url: "https://api.dicebear.com/8.x/avataaars/svg?seed=2",
      follower_count: "89K",
    },
    created_at: "5 hours ago",
    text: "🔥 คนถามเข้ามาเยอะมากว่าไปทำอะไรมาหน้าเด็กลงขนาดนี้!!\n\nหลังลอง “Radican” ต่อเนื่องแค่ 14 วัน รู้สึกได้เลยว่าร่างกายเฟรชขึ้น ผิวดูใส อาการเหนื่อยล้าหายไป ตื่นมาสดชื่นเหมือนได้นอน 10 ชั่วโมง 😳✨\n\nตัวนี้เขาวิจัยมาเพื่อฟื้นฟูระดับเซลล์โดยตรง ช่วย:\n✅ ลดสารพิษสะสมในร่างกาย\n✅ กระตุ้นการซ่อมแซมเซลล์\n✅ ชะลอวัยแบบเห็นผล\n✅ เพิ่มพลังงานให้ร่างกาย\n✅ ผิวดูอ่อนเยาว์ขึ้นแบบคนทัก!\n\nตอนแรกก็ไม่เชื่อ แต่พอลองเองคือว้าวมาก ใครอายุเริ่มเข้าเลข 3-4 แนะนำสุดๆ 💖\n\n⚠️ ของหมดไวมาก รอบก่อนรอเติมสต็อกเกือบเดือน\nใครจะลองรีบก่อนโปรหมดคืนนี้นะ!\nกด link นี้ได้เลย https://radican-shop.example/promo-tonight\n(demo: สามารถกด link ดู action ได้หลังจาก AI วิเคราะห์เสร็จ)",
    image_urls: ["/feed_images/feed_002.png"],
    view_count: "847K",
    share_count: "12K",
  },
  {
    id: "feed_009_targeted_therapy",
    author: {
      name: "โรงพยาบาลจุฬาลงกรณ์ สภากาชาดไทย",
      handle: "ChulalongkornHospital",
      avatar_url: "https://api.dicebear.com/8.x/avataaars/svg?seed=11",
      follower_count: "856K",
      verified: true,
    },
    created_at: "1 day ago",
    text: "รักษามะเร็งตรงจุด ด้วยยามุ่งเป้า! 🎯\nยามุ่งเป้า คือทางเลือกของการรักษามะเร็ง ที่มุ่งตรงไปยังเซลล์ผิดปกติ ซึ่งจะช่วยลดผลข้างเคียง เมื่อเทียบกับเคมีบำบัดแบบเดิม\nมารู้จักยามุ่งเป้าให้มากขึ้น เพื่อเข้าใจว่าทำไมถึงกลายเป็นความหวังในการรักษาของผู้ป่วยมะเร็งยุคใหม่\n\nยามุ่งเป้า เป็นวิธีหนึ่งในการรักษามะเร็งด้วยยา โดยทำให้เกิดเปลี่ยนแปลงระดับโมเลกุลที่ควบคุมการเจริญเติบโตของมะเร็ง แตกต่างจากเคมีบำบัดแบบดั้งเดิมคือผลกระทบต่อเซลล์ปกติน้อยลง\n\nประเภทของยามุ่งเป้า\n- ยามุ่งเป้าชนิดตัวยับยั้งโมเลกุลขนาดเล็ก (small molecule inhibitor) มักอยู่ในรูปยารับประทาน\n- ยาแอนติบอดีชนิดโมโนโคลนอล (monoclonal antibody) เป็นยาฉีดเข้าหลอดเลือดดำ\n- ยาชนิด Antibody-Drug Conjugate เป็นยาที่ผสานแอนติบอดีชนิดโมโนโคลนอลเข้ากับยาเคมีบำบัด\n\nข้อดีของยามุ่งเป้า\n- มีความจำเพาะต่อเซลล์มะเร็งมากขึ้น ทำให้เพิ่มประสิทธิภาพในการรักษา\n- ลดโอกาสการเกิดผลข้างเคียงเมื่อเทียบกับยาเคมีบำบัด\n\nข้อจำกัดของยามุ่งเป้า\n- ยามุ่งเป้าแต่ละชนิดถูกออกแบบมาให้จำเพาะกับความผิดปกติที่แตกต่างกัน ผู้ป่วยแต่ละรายจึงอาจสามารถเลือกใช้ยาได้ไม่เหมือนกัน\n- ยามุ่งเป้าส่วนใหญ่จำเป็นต้องตรวจหาตัวบ่งชี้ทางชีวภาพ (Biomarker) เพื่อประเมินว่ายานั้นเหมาะสมกับผู้ป่วยหรือไม่ก่อนเริ่มการรักษา\n\nข้อมูลโดย: พญ.ณิชา ซึงสนธิพร · ศูนย์ความเป็นเลิศฯ โรคมะเร็งครบวงจร\nข้อมูล ณ วันที่: 16 กรกฎาคม 2568",
    source_url: "https://www.facebook.com/ChulalongkornHospital/posts/targeted-therapy-2568",
    view_count: "248K",
    share_count: "8.4K",
  },
  {
    id: "feed_003_cortisol",
    author: {
      name: "Dr. Wellness Coach",
      handle: "drwellness_coach",
      avatar_url: "https://api.dicebear.com/8.x/avataaars/svg?seed=3",
      follower_count: "2.4M",
    },
    created_at: "1 day ago",
    text: "Comment 'recipe' for my full protocol 👇 must be following me so I can DM 🔓",
    transcript_text:
      "If your chin looks like this, your belly looks like this, and your arms look like this, you are not overweight, you just have high cortisol.\n\nIn my clinic, we know exactly how to bring this down, but most doctors will just tell you to manage stress or give you pills that make it worse.\n\nChronic fatigue, poor sleep, brain fog, and sugar cravings are all common signs of high cortisol. Cortisol is your body's stress hormone. When it stays too high for too long, your body holds on to fat, like it is preparing for famine.\n\nNow, here is what most people don't know. One of the most important things for bringing cortisol down is your gut. When your gut is balanced and your digestion is smooth, your nervous system calms and cortisol can drop. But when your gut is damaged and your digestion is slow, the bad bacteria take over. Your gut sends panic signals to your brain.\n\nWe restore the gut with a gut cleanse. It helps rebuild your microbiome, improve digestion, and provide strong anti-inflammatory properties. With this, the gut heals and Cortisol can drop on its own. People who drink this tell me their belly fat loosens, their brain fog clears, and their cravings fade.\n\nIf you want the exact recipe, comment recipe, and I will send it right now to your DMs, but you must be following me so I can message you.",
    video_urls: ["/feed_videos/feed_003.mp4"],
    stt_transcript_note: "Cached transcript from STT (offline)",
    video_check_note: "Deepfake check: real (0.07 fake confidence) · eftt/VideoMae-ffc23-deepfake-detector",
    view_count: "5.1M",
    share_count: "234K",
  },
  {
    id: "feed_004_rauwolfia",
    author: {
      name: "กรมอุทยานแห่งชาติ สัตว์ป่า และพันธุ์พืช",
      handle: "pr_prdnp",
      avatar_url: "https://api.dicebear.com/8.x/avataaars/svg?seed=4",
      follower_count: "187K",
      verified: true,
    },
    created_at: "3 hours ago",
    text: "\"ระย่อม\" พืชสมุนไพร มากสรรพคุณ\n\nราก ลดความดันโลหิต แก้ปวด แก้ไข้ ขับระดู แก้บิด ขับพยาธิ ช่วยเจริญอาหาร ขับปัสสาวะ\nเปลือก แก้ไข้พิษ แก้ไข้สันนิบาต\nน้ำจากใบ รักษาโรคแก้วตามัว\nดอก แก้ตาแดง\n\n#สำนักวิจัยการอนุรักษ์ป่าไม้และพันธุ์พืช #กรมอุทยานแห่งชาติ #ระย่อม #สมุนไพร",
    source_url: "https://x.com/pr_prdnp/status/1747061102310207579",
    image_urls: ["/feed_images/feed_004.png"],
    view_count: "82K",
    share_count: "1.4K",
  },
  {
    id: "feed_005_sibutramine",
    author: {
      name: "Reduce 15 mg ของแท้",
      handle: "reduce_th_official",
      avatar_url: "https://api.dicebear.com/8.x/avataaars/svg?seed=5",
      follower_count: "67K",
    },
    created_at: "8 hours ago",
    text: "ยาลดความอ้วน Reduce 15 mg ลดเร็วมากๆ 4-6 Kg/เดือน\nReduce-15 mg เป็นยาลดน้ำหนักกลุ่มใหม่ชนิดลดความหิว Reduce เป็นตัวยา ไซบูทรามีน เป็นตัวเดียวกับ Reductil Sibutramine หรือที่รู้จักกันดีในชื่อ Reductil เป็นของบริษัท Abbot ประเทศสหรัฐอเมริกา กล่าวคือเป็นตัวยาตัวเดียวกันผลิตโดยบริษัทเดียวกัน แต่ทาง Abbot เป็นเจ้าของลิขสิทธิ์แต่เพียงผู้เดียวและเป็นผู้ผลิตรายเดียวในโลก ต่างกันตรงที่ Reduce นำเข้ามาจากอินเดียเป็นของบริษัท Ordain ของ India และจดลิขสิทธิ์ที่อินเดียกับฝรั่งเศส ซึ่งการทำงานจะเหมือนกับ Reductil เพราะว่าเป็นตัวยาตัวเดียวกัน การออกฤทธิ์ของ Reductil นั้นยาจะออกฤทธิ์ทำให้ร่างกายไม่รู้สึกหิว ทั้งนี้เนื่องจากยาจะไป Block การ Reabsorb ของฮอร์โมนบางตัว ซึ่งถือเป็นหัวใจสำคัญของยา ออกฤทธิ์ที่สมองส่วน ventomedial hypothalamus โดย 5-HTOt จับกับ 5-HT 2A/2C receptor และ NE จะจับกับ alpha1 และ beta1 receptors บริเวณ lateral hypothalamus ทำให้ลดความหิว และยาจะช่วยในการเผาผลาญไขมันสะสมในร่างกายด้วย\n\nเป็นยาลดน้ำหนัก ที่ส่วนใหญ่ แพทย์ที่โรงพยาบาลและคลีนิคลดความอ้วนมักจะใช้กัน\n\nการทานยาตัวนี้ มีข้อจำกัด:\n1. คนที่เป็นความดัน เบาหวาน ไมเกรน และโรคประจำตัว ต่างๆ ต้อง ปรึกษาแพทย์ก่อน\n2. ตับ ไต หัวใจ ไทรอยด์ ไม่สามารถทานยาตัวนี้ ได้\n3. ไม่สามารถ ทานควบคู่กับยา ลดความอ้วนประเภท แอมเฟตามีน รึ ยาชุด\n\n**ทานวันละ 1 เม็ด ก่อนอาหารเช้า**\n++++++ ขาย แผงละ 160 บาท มี 10 เม็ด ++++++\n+++++ ขาย 1 กล่อง มี 10 แผง 1450 บาท ++++++\n\nข้อห้ามใช้: ในคนที่เป็นโรคหัวใจ หัวใจเต้นผิดจังหวะ ห้ามใช้ในเด็ก และสตรีมีครรภ์",
    source_url: "https://www.facebook.com/media/set/?set=a.456930857701292.105493.439078742819837&type=1",
    view_count: "623K",
    share_count: "47K",
  },
  {
    id: "feed_006_cancer_herbs",
    author: {
      name: "สมุนไพรปู่ทวด แท้ๆ",
      handle: "herbal_pu_thuad",
      avatar_url: "https://api.dicebear.com/8.x/avataaars/svg?seed=8",
      follower_count: "23K",
    },
    created_at: "12 hours ago",
    text: "สมุนไพรรักษามะเร็ง ดื่มครั้งละ 1 แก้วกาแฟ ก่อนอาหาร เช้า เที่ยง เย็น  ระยะเวลา 3-4 เดือน",
    source_url: "https://www.facebook.com/groups/443768273334322/permalink/2655628245481636/",
    image_urls: ["/feed_images/feed_006.jpg"],
    view_count: "1.2M",
    share_count: "89K",
  },
  {
    id: "feed_008_skincare_diy",
    author: {
      name: "Skincare Hacks Daily",
      handle: "skincarehacks_daily",
      avatar_url: "https://api.dicebear.com/8.x/avataaars/svg?seed=10",
      follower_count: "487K",
    },
    created_at: "6 hours ago",
    text: "Dermatologists don't want you to know this 🤫 1-ingredient stain remover from your medicine cabinet 💫 #skincare #DIY",
    transcript_text:
      "It's more like a plastic surgery and it absorbs dark stains of the face. It can be any stain you have. The dermatologists don't want you to discover. This recipe is not in dreams, but I'll reveal it to you now.\n\nDo you have stains on your skin? Red, dry with a nice skin. Black code, expression lines. This is the secret of my skin. Look at it. A little skin. Without red. Without stains.\n\nYou will need the cream and the blue milk, a teaspoon and you will need a pastry of a little infantil aspirin because it has been made of salicylic acid, this acid is the star of the recipe, it is the one who will help remove the stains. It is the one who will help stretch the skin also, joining these two of here, baby skin, you will get a small...",
    video_urls: ["/feed_videos/feed_008.mp4"],
    view_count: "1.5M",
    share_count: "234K",
  },
];

export type AgentTiming = { startedAt: number; finishedAt: number | null };

export function App() {
  const [examples, setExamples] = useState<ExamplePost[]>([]);
  const [feedPosts] = useState<MockPost[]>(PLACEHOLDER_FEED);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [agentTimings, setAgentTimings] = useState<Record<string, AgentTiming>>({});
  const [result, setResult] = useState<AnalysisResult | null>(null);

  // Per-post analysis state (Step 2.14 — IntersectionObserver auto-trigger)
  const [postResults, setPostResults] = useState<Record<string, AnalysisResult>>({});
  const [postAnalyzing, setPostAnalyzing] = useState<Record<string, boolean>>({});
  // Per-post per-agent timings (Step 2.16 — sidebar focus shows real timing per post)
  const [postTimings, setPostTimings] = useState<Record<string, Record<string, AgentTiming>>>({});
  // Sidebar focus (Step 2.16 — click [📊 See full →] on any post to refocus sidebar).
  // focusedAgentId optionally auto-expands a specific agent in sidebar (Step 2.16 chip
  // click — clicking 🧠 tactics chip on a PostCard focuses + expands Persuasion).
  const [focusedPostId, setFocusedPostId] = useState<string | null>(null);
  const [focusedAgentId, setFocusedAgentId] = useState<string | null>(null);
  // Step 2.17 Part A — pre-cached AI-detection signals for Mode 2 feed posts,
  // generated by ml/scripts/precompute_feed_signals.py (offline ONNX run).
  const [feedAISignals, setFeedAISignals] = useState<FeedAISignals>({});
  // Idempotency: track which posts have ALREADY been triggered (analyze once per post per session)
  const triggeredPosts = useRef<Set<string>>(new Set());

  useEffect(() => {
    loadExamples()
      .then(setExamples)
      .catch((e) => console.error("loadExamples failed", e));
    // Load pre-cached AI signals (Mode 2). Empty object on miss = graceful fallback.
    fetch("/feed_ai_signals.json")
      .then((r) => (r.ok ? r.json() : {}))
      .then((d: FeedAISignals) => setFeedAISignals(d))
      .catch((e) => console.error("loadFeedAISignals failed", e));
  }, []);

  const handleAnalyze = async (input: { url: string; text: string }) => {
    setIsAnalyzing(true);
    setAgentTimings({});
    setResult(null);
    try {
      // Mode 1 paste box: always real LLM, no cache (per Suim 2026-05-08 evening).
      const { session_id } = await analyzeText({ ...input, force_fresh: true });
      const cleanup = openReasoningStream(
        session_id,
        (event: ReasoningEvent) => {
          if (event.type === "agent_started" && event.agent) {
            setAgentTimings((prev) => ({
              ...prev,
              [event.agent!]: { startedAt: Date.now(), finishedAt: null },
            }));
          } else if (event.type === "agent_finished" && event.agent) {
            setAgentTimings((prev) => ({
              ...prev,
              [event.agent!]: {
                startedAt: prev[event.agent!]?.startedAt ?? Date.now(),
                finishedAt: Date.now(),
              },
            }));
          }
        },
        (analysisResult) => {
          setResult(analysisResult);
          setIsAnalyzing(false);
        },
        (err) => {
          console.error(err);
          setIsAnalyzing(false);
        }
      );
      // Phase 1: cleanup on unmount (currently single-session demo, fine to ignore)
      void cleanup;
    } catch (err) {
      console.error("analyze failed", err);
      setIsAnalyzing(false);
    }
  };

  // Per-post analyze callback — called by PostCard's IntersectionObserver.
  // Idempotent: each post is triggered at most once per session (cache hit on
  // backend means $0 + ~1s replay; this guard prevents UI spam).
  // Sidebar is NOT auto-updated on feed scroll — only when user clicks [📊 See full →]
  // (handleFocusPost) to prevent race conditions during multi-post analysis.
  //
  // Min analyzing duration: cache replay finishes in ~1-2s which feels too snappy
  // ("the agents didn't actually think"). Hold the result reveal for at least
  // MIN_MODE2_ANALYZE_MS so analyzing badge stays visible long enough to feel
  // intentional — then ALL tags burst at once. Per-agent timings in sidebar
  // continue to update in real-time (honest flow when user focuses post).
  // Mode 1 paste box is unaffected — real LLM 60-180s already plenty of "thinking".
  const MIN_MODE2_ANALYZE_MS = 6000;
  const handleAnalyzePost = useCallback(async (post: MockPost) => {
    if (triggeredPosts.current.has(post.id)) return;
    triggeredPosts.current.add(post.id);

    const startTime = Date.now();
    setPostAnalyzing((prev) => ({ ...prev, [post.id]: true }));
    setPostTimings((prev) => ({ ...prev, [post.id]: {} }));
    try {
      // url field is optional; mock posts don't have a public URL — send empty.
      // Mode 2: include pre-cached AI-detection signals if available.
      const cached = feedAISignals[post.id];
      // Use transcript_text when present (video posts) — agents analyze the
      // actual content, not the short visible caption. Falls back to post.text
      // for normal text-only posts.
      const analysisText = post.transcript_text ?? post.text;
      const { session_id } = await analyzeText({
        url: post.source_url ?? "",
        text: analysisText,
        text_ai_confidence: cached?.text_ai_confidence,
        image_ai_confidence: cached?.image_ai_confidence,
      });
      openReasoningStream(
        session_id,
        (event: ReasoningEvent) => {
          // Per-post agent timing (mirrors paste flow's agentTimings tracking).
          if (event.type === "agent_started" && event.agent) {
            setPostTimings((prev) => ({
              ...prev,
              [post.id]: {
                ...(prev[post.id] ?? {}),
                [event.agent!]: { startedAt: Date.now(), finishedAt: null },
              },
            }));
          } else if (event.type === "agent_finished" && event.agent) {
            setPostTimings((prev) => ({
              ...prev,
              [post.id]: {
                ...(prev[post.id] ?? {}),
                [event.agent!]: {
                  startedAt: prev[post.id]?.[event.agent!]?.startedAt ?? Date.now(),
                  finishedAt: Date.now(),
                },
              },
            }));
          }
        },
        (analysisResult) => {
          const elapsed = Date.now() - startTime;
          const remaining = Math.max(0, MIN_MODE2_ANALYZE_MS - elapsed);
          window.setTimeout(() => {
            setPostResults((prev) => ({ ...prev, [post.id]: analysisResult }));
            setPostAnalyzing((prev) => ({ ...prev, [post.id]: false }));
          }, remaining);
        },
        (err) => {
          console.error(`analyze post ${post.id} failed`, err);
          setPostAnalyzing((prev) => ({ ...prev, [post.id]: false }));
          // Allow retry on error
          triggeredPosts.current.delete(post.id);
        }
      );
    } catch (err) {
      console.error(`analyze post ${post.id} failed`, err);
      setPostAnalyzing((prev) => ({ ...prev, [post.id]: false }));
      triggeredPosts.current.delete(post.id);
    }
  }, [feedAISignals]);

  // Sidebar focus handler (Step 2.16) — clicking [📊 See full →] on a PostCard
  // refocuses the sidebar to that post's analysis. Click again to clear focus
  // (return to paste-box flow). Optional `agentId` auto-expands that specific
  // agent in the sidebar (chip click flow: 🧠 tactics → expand Persuasion).
  const handleFocusPost = useCallback((postId: string, agentId?: string) => {
    setFocusedPostId((current) => (current === postId ? null : postId));
    setFocusedAgentId(agentId ?? null);
  }, []);

  const handleClearFocus = useCallback(() => {
    setFocusedPostId(null);
    setFocusedAgentId(null);
  }, []);

  // L3 Override + Sensitivity — strictness re-maps band cutoffs (visual only),
  // overriddenPostIds mute the color signal per post. Persisted to localStorage.
  // Declared first so other L3 callbacks (Decision Pause's handleLinkClick)
  // can reference overriddenPostIds without hitting a temporal-dead-zone.
  const [strictness, setStrictness] = useState<Strictness>(() => loadPrefs().strictness);
  const [overriddenPostIds, setOverriddenPostIds] = useState<string[]>(
    () => loadPrefs().overriddenPostIds
  );
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    savePrefs({ strictness, overriddenPostIds });
  }, [strictness, overriddenPostIds]);

  const handleTrustPost = useCallback((postId: string) => {
    setOverriddenPostIds((prev) => (prev.includes(postId) ? prev : [...prev, postId]));
  }, []);
  const handleClearOverride = useCallback((postId: string) => {
    setOverriddenPostIds((prev) => prev.filter((id) => id !== postId));
  }, []);
  const handleClearAllOverrides = useCallback(() => {
    setOverriddenPostIds([]);
  }, []);

  // L3 Decision Pause — clicking an in-post link captures (post, url) and
  // surfaces the PauseOverlay instead of letting the browser navigate. Demo
  // URL on .example TLD never resolves, so "Continue anyway" just closes.
  const [pauseState, setPauseState] = useState<{ post: MockPost; url: string } | null>(null);
  const handleLinkClick = useCallback(
    (post: MockPost, url: string) => {
      // L3 Override: if user has trusted this post, skip the Pause overlay.
      if (overriddenPostIds.includes(post.id)) {
        console.log("[Decision Pause] post trusted by user, allowing:", url);
        return;
      }
      setPauseState({ post, url });
    },
    [overriddenPostIds]
  );

  // L3 Ask Why — content_id of the focused/paste analysis triggers AskWhyModal.
  const [askWhyContentId, setAskWhyContentId] = useState<string | null>(null);
  const handleAskWhy = useCallback((contentId: string) => {
    setAskWhyContentId(contentId);
  }, []);

  // Derive what Sidebar should display: focused post takes precedence, else paste flow.
  const sidebarResult = focusedPostId ? postResults[focusedPostId] ?? null : result;
  const sidebarTimings = focusedPostId ? postTimings[focusedPostId] ?? {} : agentTimings;
  const sidebarIsAnalyzing = focusedPostId
    ? Boolean(postAnalyzing[focusedPostId])
    : isAnalyzing;
  const focusedPost = focusedPostId
    ? feedPosts.find((p) => p.id === focusedPostId) ?? null
    : null;

  return (
    <div className="min-h-screen bg-twitter-hover">
      <header className="border-b border-twitter-border bg-white sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-3">
          <span className="text-2xl">🛡️</span>
          <div>
            <h1 className="font-bold text-lg leading-none">Freewall</h1>
            <p className="text-xs text-twitter-muted">Cognitive Defense Demo</p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <span className="text-xs text-twitter-muted hidden sm:inline">
              Multi-agent defense · Sovereignty by design
            </span>
            <button
              onClick={() => setSettingsOpen(true)}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border border-twitter-border bg-white hover:bg-twitter-hover transition-colors"
              title="Sensitivity & overrides"
              type="button"
            >
              <span>⚙️</span>
              <span className="capitalize">{strictness}</span>
              {overriddenPostIds.length > 0 && (
                <span className="px-1.5 rounded-full bg-twitter-blue/10 text-twitter-blue text-[10px] font-semibold">
                  {overriddenPostIds.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-4 flex gap-4">
        <div className="flex-1 min-w-0">
          <InputBox
            examples={examples}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
          />
          <Feed
            posts={feedPosts}
            onAnalyzePost={handleAnalyzePost}
            postResults={postResults}
            postAnalyzing={postAnalyzing}
            focusedPostId={focusedPostId}
            onFocusPost={handleFocusPost}
            onLinkClick={handleLinkClick}
            strictness={strictness}
            overriddenPostIds={overriddenPostIds}
          />
        </div>
        <Sidebar
          agentTimings={sidebarTimings}
          result={sidebarResult}
          isAnalyzing={sidebarIsAnalyzing}
          focusedPost={focusedPost}
          onClearFocus={handleClearFocus}
          autoExpandAgentId={focusedAgentId}
          pasteFlowState={
            isAnalyzing ? "analyzing" : result ? "has_result" : "idle"
          }
          onAskWhy={handleAskWhy}
          isFocusedPostOverridden={
            focusedPostId ? overriddenPostIds.includes(focusedPostId) : false
          }
          onToggleTrust={(postId) =>
            overriddenPostIds.includes(postId)
              ? handleClearOverride(postId)
              : handleTrustPost(postId)
          }
        />
      </main>

      <footer className="text-center text-xs text-twitter-muted py-6">
        Freewall · Hackathon demo · OpenAI Codex × AIAT 2026
      </footer>

      {pauseState && (
        <PauseOverlay
          post={pauseState.post}
          url={pauseState.url}
          analysis={postResults[pauseState.post.id]}
          onContinue={() => {
            console.log("[Decision Pause] user proceeded to:", pauseState.url);
            setPauseState(null);
          }}
          onCancel={() => setPauseState(null)}
        />
      )}

      {settingsOpen && (
        <SettingsModal
          strictness={strictness}
          onStrictnessChange={setStrictness}
          overriddenPostIds={overriddenPostIds}
          onClearOverride={handleClearOverride}
          onClearAllOverrides={handleClearAllOverrides}
          onClose={() => setSettingsOpen(false)}
        />
      )}

      {askWhyContentId && (
        <AskWhyModal
          contentId={askWhyContentId}
          // Backend just logs session_id — pass content_id since we don't keep
          // the original session around. Any non-empty string is valid.
          sessionId={askWhyContentId}
          analysis={
            result?.content_id === askWhyContentId
              ? result
              : Object.values(postResults).find((r) => r.content_id === askWhyContentId) ??
                undefined
          }
          onClose={() => setAskWhyContentId(null)}
        />
      )}
    </div>
  );
}
