import { useEffect, useState } from "react";
import type { AnalysisResult, MockPost } from "@/types";
import type { AgentTiming } from "@/App";

interface Props {
  agentTimings: Record<string, AgentTiming>;
  result: AnalysisResult | null;
  isAnalyzing: boolean;
  focusedPost: MockPost | null;
  onClearFocus: () => void;
  // Auto-expand a specific agent (Step 2.16 chip-click flow: 🧠 tactics chip on
  // a PostCard sets this to "persuasion" so the sidebar opens that section).
  autoExpandAgentId: string | null;
  // For back-to-paste-flow indicator: lets the focus header show whether the
  // paste-box analysis is currently running OR has a result waiting.
  pasteFlowState: "idle" | "analyzing" | "has_result";
  // L3 Ask Why — score banner shows a "🔍 Why?" button when a result exists.
  // Click bubbles up to App which opens the AskWhyModal with the content_id.
  onAskWhy?: (contentId: string) => void;
  // L3 Override — when a post is focused, sidebar shows "Trust this post" /
  // "Untrust" button. Toggles user-acknowledged state in App's localStorage.
  isFocusedPostOverridden?: boolean;
  onToggleTrust?: (postId: string) => void;
}

interface AgentMeta {
  id: string;
  label: string;
  emoji: string;
  description: string;
  layer: "L1" | "L2";
  isSubAgent?: boolean; // L2 specialists indented under Coordinator
}

// Hardcoded runtime metadata per CLAUDE.md decision #17 (single model, reasoning tiering).
// Surfaces in expanded agent card so judges/mentors see the cost-optimization story.
const AGENT_RUNTIME: Record<string, { reasoning: string; tools: string }> = {
  classifier: { reasoning: "none", tools: "—" },
  coordinator: { reasoning: "low", tools: "—" },
  persuasion: { reasoning: "medium", tools: "—" },
  fact_check: { reasoning: "medium", tools: "rag_search" },
  provenance: { reasoning: "low", tools: "source_lookup" },
  counter: { reasoning: "high", tools: "WebSearchTool" },
};

const AGENTS: AgentMeta[] = [
  {
    id: "classifier",
    label: "Classifier",
    emoji: "🔍",
    description: "Reads content text + images and labels the type (health_claim / ad / social / news / meme / unknown). Sets the rest of the pipeline.",
    layer: "L1",
  },
  {
    id: "coordinator",
    label: "Coordinator",
    emoji: "🎯",
    description: "Reads the L1 category and decides which Layer 2 specialists to run in parallel. Keeps cost low by skipping unnecessary agents.",
    layer: "L2",
  },
  {
    id: "persuasion",
    label: "Persuasion",
    emoji: "🧠",
    description: "Detects 21 manipulation tactics (PersuSafety 15 + Cialdini 6 hybrid). Flags evidence span in the post text.",
    layer: "L2",
    isSubAgent: true,
  },
  {
    id: "fact_check",
    label: "Fact-Check",
    emoji: "🩺",
    description: "Extracts atomic claims, queries WHO/CDC/Mahidol corpus via RAG, and assigns supported / contradicted / unverifiable per claim.",
    layer: "L2",
    isSubAgent: true,
  },
  {
    id: "provenance",
    label: "Provenance",
    emoji: "🤖",
    description: "Domain reputation lookup + AI-generated avatar/text detection + account age & velocity. Synthesizes a trust signal.",
    layer: "L2",
    isSubAgent: true,
  },
  {
    id: "counter",
    label: "Counter-Persp.",
    emoji: "💬",
    description: "When trust score < 50, generates a balanced steelman using real expert sources. Surfaces the alternative — never blocks the user.",
    layer: "L2",
    isSubAgent: true,
  },
];

const BAND_BG: Record<string, string> = {
  safe: "bg-risk-safe/10 border-risk-safe/40",
  caution: "bg-risk-caution/10 border-risk-caution/40",
  high_risk: "bg-risk-high/10 border-risk-high/40",
};
const BAND_TEXT: Record<string, string> = {
  safe: "text-risk-safe",
  caution: "text-risk-caution",
  high_risk: "text-risk-high",
};
const BAND_LABEL: Record<string, string> = {
  safe: "✓ Safe",
  caution: "⚠ Caution",
  high_risk: "⚠ High Risk",
};

export function Sidebar({
  agentTimings,
  result,
  isAnalyzing,
  focusedPost,
  onClearFocus,
  autoExpandAgentId,
  pasteFlowState,
  onAskWhy,
  isFocusedPostOverridden = false,
  onToggleTrust,
}: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [now, setNow] = useState(Date.now());

  // Live tick — re-render every 200ms while any agent is still running so the
  // ⏱️ badge counter advances visibly. Stops automatically when all agents finish.
  useEffect(() => {
    const hasRunning = Object.values(agentTimings).some((t) => t.finishedAt === null);
    if (!hasRunning) return;
    const id = setInterval(() => setNow(Date.now()), 200);
    return () => clearInterval(id);
  }, [agentTimings]);

  // Auto-expand requested agent when chip on PostCard is clicked (Step 2.16).
  useEffect(() => {
    if (!autoExpandAgentId) return;
    setExpanded((prev) => {
      if (prev.has(autoExpandAgentId)) return prev;
      const next = new Set(prev);
      next.add(autoExpandAgentId);
      return next;
    });
  }, [autoExpandAgentId]);

  // Counter-Perspective auto-expand removed (Suim 2026-05-07 evening) — the dedicated
  // Counter card below the score banner already surfaces the steelman; expanding the
  // L2 pill too would duplicate content.

  const renderTimingBadge = (agentId: string) => {
    const t = agentTimings[agentId];
    if (!t) {
      return <span className="text-twitter-muted/60 text-[10px]">—</span>;
    }
    if (t.finishedAt === null) {
      const elapsed = ((now - t.startedAt) / 1000).toFixed(1);
      return (
        <span className="text-twitter-blue text-[11px] font-mono flex items-center gap-1">
          <span className="animate-pulse">⏱</span> {elapsed}s
        </span>
      );
    }
    const elapsed = ((t.finishedAt - t.startedAt) / 1000).toFixed(1);
    return (
      <span className="text-emerald-600 text-[11px] font-mono">
        ✓ {elapsed}s
      </span>
    );
  };

  const toggle = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const renderAgentFinding = (id: string) => {
    if (!result) return null;
    switch (id) {
      case "classifier":
        if (!result.classifier) return null;
        return (
          <div className="text-xs space-y-1">
            <div>
              <span className="font-bold">{result.classifier.category}</span>
              {" · "}
              {(result.classifier.confidence * 100).toFixed(0)}% confident
            </div>
            {result.classifier.topic && (
              <div className="text-twitter-muted">topic: {result.classifier.topic.replace(/_/g, " ")}</div>
            )}
          </div>
        );
      case "coordinator":
        if (!result.coordinator) return null;
        return (
          <div className="text-xs space-y-1">
            <div className="text-twitter-muted">{result.coordinator.reason}</div>
            <div>
              dispatched →{" "}
              {result.coordinator.dispatched.map((d) => (
                <span key={d} className="inline-block px-1.5 py-0.5 mr-1 mb-1 rounded bg-twitter-blue/10 text-twitter-blue text-[10px]">
                  {d}
                </span>
              ))}
            </div>
          </div>
        );
      case "persuasion":
        if (!result.persuasion) return null;
        return (
          <ul className="text-xs space-y-1">
            {result.persuasion.tactics.map((t) => (
              <li key={t.tactic}>
                <span className="font-semibold">{t.tactic.replace(/_/g, " ")}</span>{" "}
                <span className="text-twitter-muted">({(t.confidence * 100).toFixed(0)}%)</span>
                {t.evidence && (
                  <div className="text-twitter-muted italic pl-2 break-words">
                    "{t.evidence}"
                  </div>
                )}
              </li>
            ))}
          </ul>
        );
      case "fact_check":
        if (!result.fact_check?.claims?.length) return null;
        return (
          <div className="text-xs space-y-2">
            {result.fact_check.claims.map((c, i) => (
              <div key={i}>
                <div>
                  <span className="font-semibold">{c.verdict}</span>
                  {" — "}
                  {c.explanation}
                </div>
                {c.sources.map((s, j) => (
                  <a
                    key={j}
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-twitter-blue hover:underline block mt-1"
                  >
                    {s.publisher} ↗
                  </a>
                ))}
              </div>
            ))}
          </div>
        );
      case "provenance":
        if (!result.provenance) return null;
        return (
          <div className="text-xs space-y-1">
            <div>
              source:{" "}
              <span className="font-semibold">{result.provenance.source_reputation_category}</span>
            </div>
            {result.provenance.avatar_ai_confidence !== undefined && (
              <div className="text-twitter-muted">
                avatar AI confidence: {(result.provenance.avatar_ai_confidence * 100).toFixed(0)}%
              </div>
            )}
            {result.provenance.text_ai_confidence !== undefined && (
              <div className="text-twitter-muted">
                text AI confidence: {(result.provenance.text_ai_confidence * 100).toFixed(0)}%
              </div>
            )}
          </div>
        );
      case "counter":
        if (!result.counter) return null;
        return (
          <div className="text-xs space-y-2">
            <div className="text-twitter-text whitespace-pre-wrap">
              {result.counter.steelman}
            </div>
            {result.counter.sources.length > 0 && (
              <div>
                {result.counter.sources.map((s, i) => (
                  <a
                    key={i}
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-twitter-blue hover:underline block mt-1"
                  >
                    {s.publisher} ↗
                  </a>
                ))}
              </div>
            )}
          </div>
        );
      default:
        return null;
    }
  };

  const renderAgent = (agent: AgentMeta) => {
    const timing = agentTimings[agent.id];
    const isRunning = Boolean(timing && timing.finishedAt === null);
    const isDone = Boolean(timing && timing.finishedAt !== null);
    const isActive = isRunning || isDone;
    const isExpanded = expanded.has(agent.id);
    const hasFinding = Boolean(
      result && (result as unknown as Record<string, unknown>)[agent.id]
    );
    const runtime = AGENT_RUNTIME[agent.id];

    return (
      <li key={agent.id} className={agent.isSubAgent ? "ml-4" : ""}>
        <button
          onClick={() => toggle(agent.id)}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            isActive
              ? "bg-twitter-blue/10 text-twitter-text"
              : "text-twitter-muted hover:bg-twitter-hover"
          }`}
        >
          <span>{agent.emoji}</span>
          <span className={isActive ? "font-semibold" : ""}>{agent.label}</span>
          <span className="ml-auto flex items-center gap-2">
            {renderTimingBadge(agent.id)}
            <span className="text-twitter-muted text-xs">
              {isExpanded ? "▲" : "▼"}
            </span>
          </span>
        </button>
        {isExpanded && (
          <div className="mx-3 mb-2 p-3 bg-twitter-hover rounded-lg border border-twitter-border">
            {runtime && (
              <div className="text-[10px] font-mono text-twitter-muted mb-2 pb-2 border-b border-twitter-border/50">
                gpt-5.5 · reasoning={runtime.reasoning} · tools={runtime.tools}
              </div>
            )}
            <p className="text-xs text-twitter-muted mb-2 leading-relaxed">
              {agent.description}
            </p>
            {hasFinding ? (
              <div className="pt-2 border-t border-twitter-border">
                {renderAgentFinding(agent.id)}
              </div>
            ) : (
              <p className="text-xs text-twitter-muted italic">
                {isRunning ? "running..." : isAnalyzing ? "waiting to start..." : "no result yet"}
              </p>
            )}
          </div>
        )}
      </li>
    );
  };

  return (
    <aside className="w-80 shrink-0 sticky top-4 self-start space-y-3 max-h-[calc(100vh-2rem)] overflow-y-auto">
      {focusedPost && (
        <div className="border border-twitter-blue bg-twitter-blue/5 rounded-2xl p-3">
          <div className="flex items-start gap-2 mb-2.5">
            <span className="text-base">📍</span>
            <div className="flex-1 min-w-0">
              <div className="text-[10px] uppercase tracking-wider text-twitter-blue font-semibold">
                Focused on feed post (Mode 2)
              </div>
              <div className="text-xs font-semibold truncate">@{focusedPost.author.handle}</div>
              <div className="text-xs text-twitter-muted truncate">
                "{focusedPost.text.slice(0, 60)}..."
              </div>
            </div>
          </div>
          <button
            onClick={onClearFocus}
            className="w-full text-xs text-twitter-blue hover:text-twitter-blue/90 hover:bg-twitter-blue/10 border border-twitter-blue/40 rounded-md py-2 font-medium transition-colors flex items-center justify-center gap-1.5"
          >
            <span>←</span>
            <span>
              {pasteFlowState === "analyzing"
                ? "Back to paste analysis (running...)"
                : pasteFlowState === "has_result"
                  ? "Back to your paste result"
                  : "Back to paste box (Mode 1)"}
            </span>
          </button>
        </div>
      )}

      <div className="border border-twitter-border bg-white rounded-2xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl">🛡️</span>
          <h3 className="font-bold text-base">Freewall Agents</h3>
        </div>

        <div className="text-[10px] uppercase tracking-wider text-twitter-muted px-1 mt-2 mb-1">
          Layer 1 · Perception
        </div>
        <ul className="space-y-1">
          {AGENTS.filter((a) => a.layer === "L1").map(renderAgent)}
        </ul>

        <div className="text-[10px] uppercase tracking-wider text-twitter-muted px-1 mt-3 mb-1">
          Layer 2 · Reasoning
        </div>
        <ul className="space-y-1">
          {AGENTS.filter((a) => a.layer === "L2").map(renderAgent)}
        </ul>
      </div>

      {/* Sovereignty Score banner — Layer 3 surface */}
      {(isAnalyzing || result) && (
        <div
          className={`border rounded-2xl p-4 ${
            result ? BAND_BG[result.band] : "border-twitter-border bg-white"
          }`}
        >
          <div className="text-[10px] uppercase tracking-wider text-twitter-muted mb-1">
            Sovereignty Score · Layer 3
          </div>
          {result ? (
            <>
              <div className="flex items-baseline gap-2">
                <span className={`text-3xl font-bold ${BAND_TEXT[result.band] ?? ""}`}>
                  {result.score.toFixed(1)}
                </span>
                <span className="text-twitter-muted text-sm">/ 100</span>
              </div>
              <div className={`text-sm font-semibold mt-1 ${BAND_TEXT[result.band] ?? ""}`}>
                {BAND_LABEL[result.band]}
              </div>
              {result.topic && (
                <div className="text-xs text-twitter-muted mt-2">
                  topic: {result.topic.replace(/_/g, " ")}
                </div>
              )}
              <div className="mt-3 flex flex-wrap gap-2">
                {onAskWhy && (
                  <button
                    onClick={() => onAskWhy(result.content_id)}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-white border border-twitter-border hover:bg-twitter-blue/5 hover:border-twitter-blue/40 transition-colors"
                    title="Plain-language explanation of this score"
                    type="button"
                  >
                    <span>🔍</span>
                    <span>Why this score?</span>
                  </button>
                )}
                {onToggleTrust && focusedPost && (
                  <button
                    onClick={() => onToggleTrust(focusedPost.id)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                      isFocusedPostOverridden
                        ? "bg-twitter-blue text-white border-twitter-blue hover:bg-twitter-blue/90"
                        : "bg-white border-twitter-border hover:bg-twitter-hover"
                    }`}
                    title={
                      isFocusedPostOverridden
                        ? "Untrust — re-flag this post"
                        : "Trust this post — mute color signal"
                    }
                    type="button"
                  >
                    <span>{isFocusedPostOverridden ? "✓" : "🤝"}</span>
                    <span>{isFocusedPostOverridden ? "Trusted" : "Trust this post"}</span>
                  </button>
                )}
              </div>
            </>
          ) : (
            <p className="text-sm text-twitter-muted">
              <span className="inline-block animate-pulse">⚙️</span> Agents working...
            </p>
          )}
        </div>
      )}

      {/* Counter-Perspective dedicated card — always visible when present (decision: force user to read alternative view) */}
      {result?.counter && (
        <div className="border-2 border-amber-400 bg-amber-50 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">💬</span>
            <h3 className="font-bold text-amber-900">Counter-Perspective</h3>
          </div>
          <div className="text-[10px] uppercase tracking-wider text-amber-700 mb-3">
            What experts actually say
          </div>
          <p className="text-sm text-amber-950 whitespace-pre-wrap leading-relaxed mb-3">
            {result.counter.steelman}
          </p>
          {result.counter.sources.length > 0 && (
            <div className="border-t border-amber-200 pt-2">
              <div className="text-[10px] uppercase tracking-wider text-amber-700 mb-1">
                Verified sources
              </div>
              {result.counter.sources.map((s, i) => (
                <a
                  key={i}
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-twitter-blue hover:underline block mt-0.5"
                >
                  {s.publisher} ↗
                </a>
              ))}
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
