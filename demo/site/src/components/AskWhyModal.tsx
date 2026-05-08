import { useEffect, useState } from "react";
import { askWhy } from "@/lib/api";
import type { AnalysisResult, ScoreBand } from "@/types";

// L3 explainability — opens when user clicks "Why this score?" on a focused
// post. Backend reads cached state and calls gpt-5.5 (reasoning=low) to
// produce 3-5 plain sentences. Mock model picker visually demonstrates the
// "Sovereign AI" pitch (provider-swappable) without requiring multi-vendor
// integration this round — all options except gpt-5.5 are disabled with a
// "Year 2 plan" tooltip.
interface Props {
  contentId: string;
  sessionId: string;
  analysis?: AnalysisResult;
  onClose: () => void;
}

interface ModelOption {
  id: string;
  label: string;
  provider: string;
  active: boolean;
  note?: string;
}

const MODELS: ModelOption[] = [
  { id: "gpt-5.5", label: "GPT-5.5", provider: "OpenAI", active: true },
  { id: "gpt-4", label: "GPT-4", provider: "OpenAI", active: false, note: "Year 2 plan" },
  {
    id: "claude-sonnet-4-6",
    label: "Claude Sonnet 4.6",
    provider: "Anthropic",
    active: false,
    note: "Year 2 plan · Sovereign AI",
  },
  {
    id: "llama-3.3-70b",
    label: "Llama 3.3 70B",
    provider: "Meta",
    active: false,
    note: "Year 2 plan · open-source fallback",
  },
  {
    id: "qwen-thai",
    label: "Qwen-Thai",
    provider: "Alibaba",
    active: false,
    note: "Year 2 plan · Thai-localized",
  },
];

const BAND_LABEL: Record<ScoreBand, string> = {
  safe: "Safe",
  caution: "Caution",
  high_risk: "High Risk",
};

const BAND_BG: Record<ScoreBand, string> = {
  safe: "bg-emerald-50 border-emerald-300 text-emerald-800",
  caution: "bg-amber-50 border-amber-300 text-amber-800",
  high_risk: "bg-red-50 border-red-300 text-red-800",
};

export function AskWhyModal({ contentId, sessionId, analysis, onClose }: Props) {
  const [selectedModel, setSelectedModel] = useState("gpt-5.5");
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // ESC closes modal.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  // Auto-fetch on open (gpt-5.5 default). Re-fetches if user changes to
  // another active model — currently only gpt-5.5 is active so this is a
  // single fetch in practice.
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setExplanation(null);
    askWhy(sessionId, contentId)
      .then((res) => {
        if (!cancelled) setExplanation(res.explanation);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [contentId, sessionId, selectedModel]);

  const score = analysis?.score;
  const band = analysis?.band;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="ask-why-title"
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-3">
          <div className="text-2xl shrink-0">🔍</div>
          <div className="flex-1 min-w-0">
            <h2 id="ask-why-title" className="text-lg font-bold text-twitter-text">
              Why this score?
            </h2>
            <p className="text-xs text-twitter-muted">
              Plain-language summary of the agent findings.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-twitter-muted hover:text-twitter-text text-xl leading-none"
            aria-label="Close"
            type="button"
          >
            ✕
          </button>
        </div>

        {score !== undefined && band && (
          <div className={`mt-4 px-3 py-2 rounded-md border ${BAND_BG[band]}`}>
            <div className="text-xs font-semibold uppercase tracking-wider opacity-70">
              Sovereignty Score
            </div>
            <div className="text-2xl font-bold">
              {score.toFixed(score % 1 === 0 ? 0 : 1)}
              <span className="text-sm font-normal opacity-70">
                {" / 100 · "}
                {BAND_LABEL[band]}
              </span>
            </div>
          </div>
        )}

        {/* Model picker — Sovereign AI pitch surface. Mock for round 1.
            Year 2 plan: BGE-M3 + open-source LLM fallback (Llama / Qwen-Thai). */}
        <div className="mt-4">
          <div className="text-[10px] uppercase tracking-wider text-twitter-muted font-semibold mb-1">
            Reasoning model
          </div>
          <div className="flex flex-wrap gap-1.5">
            {MODELS.map((m) => (
              <button
                key={m.id}
                onClick={() => m.active && setSelectedModel(m.id)}
                disabled={!m.active}
                title={m.note ?? `${m.provider} · ${m.label}`}
                className={`px-2.5 py-1 rounded-md text-xs border transition-colors ${
                  selectedModel === m.id
                    ? "bg-twitter-blue text-white border-twitter-blue"
                    : m.active
                      ? "bg-white text-twitter-text border-twitter-border hover:bg-twitter-hover"
                      : "bg-twitter-hover text-twitter-muted/70 border-twitter-border cursor-not-allowed"
                }`}
                type="button"
              >
                {m.label}
                {!m.active && <span className="ml-1 opacity-60">🔒</span>}
              </button>
            ))}
          </div>
          <p className="text-[10px] text-twitter-muted mt-1.5 italic">
            Year 2 plan: BGE-M3 on-device embeddings + open-source LLM fallback (Llama 3.3 / Qwen-Thai) for sovereign deployment.
          </p>
        </div>

        {/* Explanation body */}
        <div className="mt-4 min-h-[100px]">
          {loading && (
            <div className="text-sm text-twitter-muted flex items-center gap-2">
              <span className="animate-pulse">⚙️</span>
              <span>Asking {MODELS.find((m) => m.id === selectedModel)?.label}…</span>
            </div>
          )}
          {error && (
            <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-md p-3">
              <strong>Error:</strong> {error}
            </div>
          )}
          {explanation && !loading && (
            <div className="text-sm text-twitter-text whitespace-pre-wrap leading-relaxed">
              {explanation}
            </div>
          )}
        </div>

        <div className="mt-5 pt-4 border-t border-twitter-border flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-twitter-blue text-white rounded-md hover:bg-twitter-blue/90 font-medium"
            type="button"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
