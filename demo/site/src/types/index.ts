// Types for the demo site UI. Mirrors backend schemas (shared/schemas/) at a high level.
// Phase 1: replace with auto-generated types from shared/codegen.sh once the codegen
// is wired to emit into demo/site/src/types/api.ts.

export type ScoreBand = "safe" | "caution" | "high_risk";

export type ContentCategory =
  | "news"
  | "ad"
  | "health_claim"
  | "social"
  | "meme"
  | "unknown";

export type Verdict = "supported" | "contradicted" | "unverifiable" | "not_a_claim";

export type ExpectedScoreRange = "high_risk" | "caution" | "safe";

export interface ExamplePost {
  id: string;
  topic: "diabetes" | "cancer" | "weight_loss" | "supplements" | "cardiovascular";
  label: "misinfo" | "borderline" | "legit";
  language: "th" | "en";
  url: string;
  text: string;
  expected_score_range: ExpectedScoreRange;
  display_emoji: string;
  short_label: string; // for chip display, e.g. "ขมิ้นรักษามะเร็ง"
}

export interface MockPost {
  id: string;
  author: {
    name: string;
    handle: string;
    avatar_url: string;
    verified?: boolean;
    follower_count?: string; // formatted, e.g., "89K"
    is_ai_generated?: boolean; // demo decoration only
  };
  created_at: string; // human-readable, e.g., "2 hours ago"
  text: string;
  // Real source URL (e.g., the x.com permalink). Sent to backend so Provenance Agent
  // can do real domain reputation lookup. Defaults to "" if absent (Provenance returns
  // "unknown"). For demo: feed_004 (gov-on-twitter) intentionally hits "social/unknown"
  // to demonstrate "verified ≠ trustworthy" + author-level signals = Year 2 plan.
  source_url?: string;
  image_urls?: string[];
  // Tier 0 video support (per 2026-05-08 evening decision): single fixed clip,
  // transcript pre-included in `text`, video_urls renders <video> for visual realism.
  // Year 1 plan: auto STT pipeline replaces manual transcribe.
  video_urls?: string[];
  stt_transcript_note?: string; // e.g., "Cached transcript from STT model"
  // Optional secondary note crediting a video-level check (e.g., deepfake
  // detector). Renders below stt_transcript_note in the video container.
  video_check_note?: string;
  // Optional separate text that drives backend analysis (e.g., STT transcript
  // for video posts). When present, frontend sends this to /perceive-text
  // INSTEAD of post.text — so the visible caption can stay short/realistic
  // while agents still analyze the actual content. Matches real-world social:
  // most reshares have a short caption, not a transcribed body.
  transcript_text?: string;
  view_count?: string; // e.g., "2.3M"
  share_count?: string;
  // Pre-cached reasoning state for instant display (Phase 4 populates)
  precached_score?: number;
  precached_band?: ScoreBand;
  precached_findings?: PrecachedFindings;
}

export interface PrecachedFindings {
  persuasion_tactics: { tactic: string; confidence: number }[];
  fact_check: {
    verdict: Verdict;
    explanation: string;
    sources: { publisher: string; url: string }[];
  };
  provenance_summary: string;
}

// Step 2.17 Part A — pre-cached AI-detection signals for Mode 2 feed posts.
// Loaded from /feed_ai_signals.json at app startup. Text side is run by
// ml/scripts/precompute_feed_signals.py (Hello-SimpleAI). Image side is run
// manually by Suim using prithivMLmods/deepfake-detector-model-v1 — confidence
// reported per-post and pasted into feed_ai_signals.json.
export interface FeedAISignal {
  text_ai_confidence: number;
  label: string;        // e.g., "Human" | "ChatGPT"
  score_raw: number;
  model: string;        // text model identifier for transparency in UI label
  image_ai_confidence?: number;   // optional — populated when post has an image
  image_ai_model?: string;        // e.g., "prithivMLmods/deepfake-detector-model-v1"
}

export type FeedAISignals = Record<string, FeedAISignal>;

export interface ReasoningEvent {
  type:
    | "coordinator_dispatched"
    | "agent_started"
    | "agent_finished"
    | "score_update"
    | "final"
    | "error";
  content_id: string;
  agent?: string;
  payload?: unknown;
  timestamp: string;
}

export interface ClassifierFinding {
  category: ContentCategory;
  confidence: number;
  topic?: string;
}

export interface CoordinatorFinding {
  dispatched: string[];
  reason: string;
}

export interface PersuasionFinding {
  tactics: { tactic: string; confidence: number; evidence?: string }[];
}

export interface FactCheckFinding {
  claims: {
    claim: string;
    verdict: Verdict;
    explanation: string;
    sources: { title?: string; url: string; publisher: string; snippet?: string }[];
  }[];
}

export interface ProvenanceFinding {
  source_reputation_category: string;
  avatar_ai_confidence?: number;
  text_ai_confidence?: number;
}

export interface CounterFinding {
  steelman: string;
  sources: { publisher: string; url: string }[];
}

/**
 * Full analysis output shown in the Sidebar. Each agent finding is optional
 * — the Sidebar accordion gracefully renders "no data yet" when missing.
 */
export interface AnalysisResult {
  content_id: string;
  topic?: string;
  score: number;
  band: ScoreBand;
  classifier?: ClassifierFinding;
  coordinator?: CoordinatorFinding;
  persuasion?: PersuasionFinding;
  fact_check?: FactCheckFinding;
  provenance?: ProvenanceFinding;
  counter?: CounterFinding;
}
