import { useEffect, useLayoutEffect, useRef, useState } from "react";
import type { AnalysisResult, MockPost, ScoreBand, Verdict } from "@/types";
import { effectiveBand, type Strictness } from "@/lib/preferences";

interface Props {
  post: MockPost;
  onAnalyze: (post: MockPost) => void;
  analysis?: AnalysisResult;
  isAnalyzing: boolean;
  isFocused: boolean;
  // Optional agentId auto-expands that section in the sidebar (Step 2.16 chip click).
  onFocus: (postId: string, agentId?: string) => void;
  // L3 Decision Pause: clicking an in-post link triggers this with the URL.
  // Parent (App) opens the PauseOverlay instead of letting the browser navigate.
  onLinkClick?: (post: MockPost, url: string) => void;
  // L3 Override + Sensitivity: user-controlled strictness re-maps band cutoffs
  // (visual color signal only — score number unchanged). isOverridden mutes
  // the color signal entirely on this specific post.
  strictness?: Strictness;
  isOverridden?: boolean;
}

// Capture-group regex so String.split returns alternating [text, url, text, url, ...] segments.
const URL_REGEX = /(https?:\/\/[^\s)]+)/g;

function renderTextWithLinks(
  text: string,
  onLinkClick: (url: string) => void
): React.ReactNode[] {
  const parts = text.split(URL_REGEX);
  return parts.map((part, i) => {
    // Odd indices = captured URLs.
    if (i % 2 === 1) {
      return (
        <a
          key={i}
          href={part}
          onClick={(e) => {
            e.preventDefault();
            onLinkClick(part);
          }}
          className="text-twitter-blue hover:underline break-all"
        >
          {part}
        </a>
      );
    }
    return part;
  });
}

const BAND_LABEL: Record<ScoreBand, string> = {
  safe: "Safe",
  caution: "Caution",
  high_risk: "High Risk",
};

const BAND_ICON: Record<ScoreBand, string> = {
  safe: "✓",
  caution: "⚠",
  high_risk: "⚠",
};

const BAND_CLASS: Record<ScoreBand, string> = {
  safe: "score-badge-safe",
  caution: "score-badge-caution",
  high_risk: "score-badge-high-risk",
};

// Color signal indicator (Suim's "A+D" choice) — top-right dot + subtle card
// background tint. Renders only after analysis returns a score. Reduces
// cognitive load: user can scan the feed and spot risk levels at a glance
// without parsing the analysis chip text.
const BAND_DOT: Record<ScoreBand, string> = {
  safe: "bg-emerald-500",
  caution: "bg-amber-500",
  high_risk: "bg-red-500",
};

const BAND_BG_TINT: Record<ScoreBand, string> = {
  safe: "",                      // no tint — reads as normal post
  caution: "bg-amber-50/40",     // very subtle yellow ambient
  high_risk: "bg-red-50/50",     // slightly more visible red ambient
};

// Compress fact-check claims into a single-word summary for the inline badge.
// Honest: prefers strongest signal (contradicted > supported > unverifiable > not_a_claim).
function summarizeFactCheck(analysis: AnalysisResult | undefined): {
  label: string;
  count: number;
} | null {
  if (!analysis?.fact_check?.claims?.length) return null;
  const claims = analysis.fact_check.claims;
  const verdicts = claims.map((c) => c.verdict);
  const tally = (v: Verdict) => verdicts.filter((x) => x === v).length;
  const contradicted = tally("contradicted");
  const supported = tally("supported");
  const unverifiable = tally("unverifiable");
  if (contradicted > 0) return { label: "contradicted", count: contradicted };
  if (supported > 0 && unverifiable === 0) return { label: "supported", count: supported };
  if (unverifiable > 0 && supported === 0) return { label: "unverifiable", count: unverifiable };
  return { label: "mixed", count: claims.length };
}

// Long-text uses CSS line-clamp (3 visual lines) — accurate regardless of how
// many newlines the source contains. We measure scrollHeight vs clientHeight
// once on mount to decide whether to render the "Show more" button. Doesn't
// interfere with the IntersectionObserver (observer disconnects after first
// fire) or any chip / focus button — they are independent click targets.
const TEXT_LINE_CLAMP = 3;

export function PostCard({
  post,
  onAnalyze,
  analysis,
  isAnalyzing,
  isFocused,
  onFocus,
  onLinkClick,
  strictness = "standard",
  isOverridden = false,
}: Props) {
  const cardRef = useRef<HTMLElement>(null);
  const textRef = useRef<HTMLParagraphElement>(null);
  const [expanded, setExpanded] = useState(false);
  const [isOverflowing, setIsOverflowing] = useState(false);

  // Measure once on mount (and if post.text changes). Run while line-clamp is
  // active — scrollHeight = full text height, clientHeight = clamped height,
  // so overflow = truthy iff text exceeds N lines.
  useLayoutEffect(() => {
    if (textRef.current) {
      setIsOverflowing(textRef.current.scrollHeight > textRef.current.clientHeight + 1);
    }
  }, [post.text]);

  // Step 2.14 — IntersectionObserver: trigger /perceive-text once the post is
  // comfortably in view, after a short delay. Goal: user sees the clean post
  // first ("feels like a real feed") before the analyzing badge appears.
  //
  // Dedup is the App-level `triggeredPosts` Set inside `handleAnalyzePost` —
  // we deliberately do NOT keep a local "hasTriggered" ref. Reason: in
  // StrictMode dev (and on fetch-resolved useEffect re-runs) the effect's
  // cleanup clears the pending timer; if a local hasTriggered=true had been
  // set during the first run, the remounted observer would skip its own fire
  // and onAnalyze would never be called. Letting App.tsx dedup means each
  // observer instance is free to schedule a fresh timer; the first one whose
  // timer survives wins, the rest no-op via `triggeredPosts.has(post.id)`.
  //
  // Threshold 0.5 (was 0.8) — for posts with images the article can be taller
  // than the viewport, so 80% visibility is unreachable. 0.5 = "half visible"
  // which still feels deliberate but works for tall posts. Delay 1500ms gives
  // the post a moment to "exist" before agents start working.
  useEffect(() => {
    const node = cardRef.current;
    if (!node) return;

    const TRIGGER_DELAY_MS = 1500;
    let timer: number | null = null;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            // Delay so user sees clean post for a moment before "Analyzing..." appears
            timer = window.setTimeout(() => onAnalyze(post), TRIGGER_DELAY_MS);
            observer.disconnect();
            return;
          }
        }
      },
      { threshold: 0.5 }
    );

    observer.observe(node);
    return () => {
      observer.disconnect();
      if (timer !== null) window.clearTimeout(timer);
    };
  }, [post, onAnalyze]);

  // Pre-cached annotations (Phase 4 — Suim curates) take precedence; otherwise live-analyzed.
  const hasPrecached = post.precached_score !== undefined && post.precached_band !== undefined;
  const liveScore = analysis?.score;
  const liveBand = analysis?.band;
  const showScore = hasPrecached || liveScore !== undefined;
  const score = liveScore ?? post.precached_score!;
  // Re-map band based on user's strictness preference. Score number is
  // unchanged — only the color signal cutoffs shift. Falls back to backend's
  // band if score is undefined (defensive — should never happen when
  // showScore is true).
  const band: ScoreBand = score !== undefined
    ? effectiveBand(score, strictness)
    : (liveBand ?? post.precached_band!);
  const tacticCount = analysis?.persuasion?.tactics?.length ?? 0;
  const factCheckSummary = summarizeFactCheck(analysis);

  return (
    <article
      ref={cardRef}
      data-freewall-post
      data-freewall-id={post.id}
      className={`twitter-card px-4 py-3 border-b relative ${
        isFocused
          ? "ring-2 ring-twitter-blue/50 bg-twitter-blue/5"
          : showScore && !isOverridden
            ? BAND_BG_TINT[band]
            : ""
      }`}
    >
      {showScore && (
        <span
          className={`absolute top-3 right-3 w-3 h-3 rounded-full ring-2 ring-white shadow-sm ${
            isOverridden ? "bg-twitter-muted/40" : BAND_DOT[band]
          }`}
          aria-label={
            isOverridden
              ? "Trusted by user — color signal muted"
              : `Sovereignty band: ${band}`
          }
          title={
            isOverridden
              ? `Trusted by user — score ${score.toFixed(score % 1 === 0 ? 0 : 1)} (${BAND_LABEL[band]})`
              : `${BAND_LABEL[band]} · score ${score.toFixed(score % 1 === 0 ? 0 : 1)}`
          }
        />
      )}
      <div className="flex gap-3">
        <img
          src={post.author.avatar_url}
          alt=""
          className="w-12 h-12 rounded-full bg-twitter-border shrink-0"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 text-sm">
            <span className="font-bold truncate">{post.author.name}</span>
            {post.author.verified && (
              <span className="text-twitter-blue" aria-label="verified">
                ✓
              </span>
            )}
            <span className="text-twitter-muted truncate">
              @{post.author.handle}
            </span>
            <span className="text-twitter-muted">·</span>
            <span className="text-twitter-muted text-xs">{post.created_at}</span>
          </div>

          {post.author.follower_count && (
            <div className="text-xs text-twitter-muted">
              {post.author.follower_count} followers
              {post.author.is_ai_generated && (
                <span className="ml-2 text-orange-600">⚠ AI-generated profile</span>
              )}
            </div>
          )}

          <p
            ref={textRef}
            className={`mt-2 text-[15px] whitespace-pre-wrap leading-snug ${
              !expanded ? "line-clamp-3" : ""
            }`}
          >
            {onLinkClick
              ? renderTextWithLinks(post.text, (url) => onLinkClick(post, url))
              : post.text}
          </p>
          {isOverflowing && (
            <button
              onClick={() => setExpanded((v) => !v)}
              className="text-twitter-blue text-sm font-medium hover:underline mt-1"
              aria-expanded={expanded}
            >
              {expanded ? "Show less" : "Show more"}
            </button>
          )}

          {/* AI-detection badge — 2-tier (Step 2.17 Part A). Honest about model uncertainty:
                > 0.5  → "AI-generated detected" (red, high-confidence flag)
                0.15-0.5 → "AI signal elevated" (amber, moderate — 6x+ over human baseline)
                < 0.15 → no badge (likely human). Surface from Provenance Agent's signal
              (cached for Mode 2, future live Mode 1).
              Honest pitch caveat: AI detectors are unreliable; threshold tuned on Hello-SimpleAI baseline. */}
          {(() => {
            const conf = analysis?.provenance?.text_ai_confidence;
            if (conf === undefined) return null;
            if (conf > 0.5) {
              return (
                <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-red-50 text-red-700 border border-red-300 text-xs font-semibold">
                  <span>🚨</span>
                  <span>AI-generated text detected · {(conf * 100).toFixed(0)}% confidence</span>
                </div>
              );
            }
            if (conf > 0.15) {
              return (
                <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-orange-50 text-orange-700 border border-orange-300 text-xs font-medium">
                  <span>🤖</span>
                  <span>AI signal elevated · {(conf * 100).toFixed(0)}% (above human baseline)</span>
                </div>
              );
            }
            return null;
          })()}

          {/* Image AI-detection badge — same 2-tier pattern as text. Backend Provenance
              Agent surfaces image confidence via `avatar_ai_confidence` (legacy field name —
              actually represents post-content image AI signal, not just author avatar).
              Model = prithivMLmods/deepfake-detector-model-v1 (Suim runs offline, pasted
              into feed_ai_signals.json per-post). */}
          {(() => {
            const conf = analysis?.provenance?.avatar_ai_confidence;
            if (conf === undefined) return null;
            if (conf > 0.5) {
              return (
                <div className="mt-2 ml-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-red-50 text-red-700 border border-red-300 text-xs font-semibold">
                  <span>🚨</span>
                  <span>AI-generated image detected · {(conf * 100).toFixed(0)}% confidence</span>
                </div>
              );
            }
            if (conf > 0.15) {
              return (
                <div className="mt-2 ml-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-orange-50 text-orange-700 border border-orange-300 text-xs font-medium">
                  <span>🖼️</span>
                  <span>Image AI signal elevated · {(conf * 100).toFixed(0)}% (above baseline)</span>
                </div>
              );
            }
            return null;
          })()}

          {post.image_urls && post.image_urls.length > 0 && (
            <div
              className={`mt-3 rounded-2xl overflow-hidden ${
                post.image_urls.length === 1 ? "" : "grid grid-cols-2 gap-1 bg-twitter-hover"
              }`}
            >
              {post.image_urls.map((url, i) => (
                <img
                  key={i}
                  src={url}
                  alt=""
                  loading="lazy"
                  className={
                    post.image_urls!.length === 1
                      ? "block max-w-full max-h-[320px] mx-auto object-contain rounded-2xl"
                      : "w-full h-40 object-cover"
                  }
                />
              ))}
            </div>
          )}

          {post.video_urls && post.video_urls.length > 0 && (
            <div className="mt-3 rounded-2xl overflow-hidden bg-black">
              {post.video_urls.map((url, i) => (
                <video
                  key={i}
                  src={url}
                  controls
                  className="w-full max-h-96 object-contain"
                />
              ))}
            </div>
          )}

          <div className="flex items-center gap-6 mt-3 text-twitter-muted text-xs">
            {post.view_count && (
              <span className="flex items-center gap-1">📊 {post.view_count} views</span>
            )}
            {post.share_count && (
              <span className="flex items-center gap-1">🔁 {post.share_count}</span>
            )}
          </div>

          {/* Inline analysis status (Steps 2.14 + 2.15): analyzing | rich annotation | precached.
              "See full →" focus button is available during analyzing too — lets user open
              sidebar to watch per-agent live timing while the pipeline runs. */}
          {(isAnalyzing || showScore) && (
            <div className="mt-3 flex flex-wrap items-center gap-2">
              {isAnalyzing && !showScore && (
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-twitter-blue/10 text-twitter-blue border border-twitter-blue/30">
                  <span className="animate-pulse">⚙️</span>
                  <span>Analyzing...</span>
                  <span className="text-twitter-muted">6 agents working</span>
                </div>
              )}

              {showScore && (
                <>
                  {/* Score chip — clickable, focuses sidebar (no specific agent expand) */}
                  <button
                    onClick={() => onFocus(post.id)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border transition-opacity hover:opacity-80 cursor-pointer ${BAND_CLASS[band]}`}
                    title="Open this post in sidebar"
                  >
                    <span>{BAND_ICON[band]}</span>
                    <span>{score.toFixed(score % 1 === 0 ? 0 : 1)}</span>
                    <span className="font-normal opacity-70">·</span>
                    <span>{BAND_LABEL[band]}</span>
                  </button>

                  {tacticCount > 0 && (
                    <button
                      onClick={() => onFocus(post.id, "persuasion")}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-twitter-hover border border-twitter-border hover:bg-twitter-blue/5 hover:border-twitter-blue/40 transition-colors cursor-pointer"
                      title="See manipulation tactics in sidebar"
                    >
                      <span>🧠</span>
                      <span className="font-semibold">{tacticCount}</span>
                      <span className="text-twitter-muted">tactic{tacticCount === 1 ? "" : "s"}</span>
                    </button>
                  )}

                  {factCheckSummary && (
                    <button
                      onClick={() => onFocus(post.id, "fact_check")}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-twitter-hover border border-twitter-border hover:bg-twitter-blue/5 hover:border-twitter-blue/40 transition-colors cursor-pointer"
                      title="See fact-check claims + sources in sidebar"
                    >
                      <span>🩺</span>
                      <span className="font-semibold">{factCheckSummary.count}</span>
                      <span className="text-twitter-muted">{factCheckSummary.label}</span>
                    </button>
                  )}
                </>
              )}

              <button
                onClick={() => onFocus(post.id)}
                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs border transition-colors ${
                  isFocused
                    ? "bg-twitter-blue text-white border-twitter-blue"
                    : "bg-white text-twitter-blue border-twitter-blue/40 hover:bg-twitter-blue/10"
                }`}
                title={
                  isFocused
                    ? "Click again to clear sidebar focus"
                    : isAnalyzing
                      ? "Open sidebar to watch per-agent live timing"
                      : "Open this post in sidebar"
                }
              >
                <span>📊</span>
                <span className="font-semibold">
                  {isFocused ? "Focused" : isAnalyzing ? "Watch live" : "See full"}
                </span>
                {!isFocused && <span>→</span>}
              </button>

              {liveScore !== undefined && (
                <span className="text-[10px] text-twitter-muted/70 font-mono">
                  live
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
