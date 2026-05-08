import { useEffect } from "react";
import type { AnalysisResult, MockPost, ScoreBand } from "@/types";

// L3 Decision Pause: when a user clicks an in-post link on a flagged post,
// intercept and surface this overlay before navigating. Demo behavior —
// "Continue anyway" closes the overlay (the fake URL on the .example TLD
// never resolves). Production extension would intercept native commerce
// buttons (Lazada/Shopee/affiliate links) the same way.
interface Props {
  post: MockPost;
  url: string;
  analysis?: AnalysisResult;
  onContinue: () => void;
  onCancel: () => void;
}

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

export function PauseOverlay({ post, url, analysis, onContinue, onCancel }: Props) {
  // ESC key closes overlay (treat as cancel — safer default).
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onCancel]);

  const score = analysis?.score;
  const band = analysis?.band;
  const tactics = analysis?.persuasion?.tactics ?? [];
  const factCheckClaims = analysis?.fact_check?.claims ?? [];
  const contradictedCount = factCheckClaims.filter((c) => c.verdict === "contradicted").length;

  const isFlagged = band === "high_risk" || band === "caution";

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4"
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="pause-title"
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-3">
          <div className="text-3xl shrink-0">🛡️</div>
          <div className="flex-1 min-w-0">
            <h2 id="pause-title" className="text-lg font-bold text-twitter-text">
              {isFlagged ? "Hold up — Freewall flagged this" : "Just to confirm…"}
            </h2>
            <p className="mt-1 text-sm text-twitter-muted">
              You're about to leave to a link from{" "}
              <span className="font-semibold">@{post.author.handle}</span>.
            </p>
          </div>
        </div>

        {score !== undefined && band && (
          <div className={`mt-4 px-3 py-2 rounded-md border ${BAND_BG[band]}`}>
            <div className="text-xs font-semibold uppercase tracking-wider opacity-70">
              Sovereignty Score
            </div>
            <div className="text-2xl font-bold">
              {score.toFixed(score % 1 === 0 ? 0 : 1)}
              <span className="text-sm font-normal opacity-70"> / 100 · {BAND_LABEL[band]}</span>
            </div>
          </div>
        )}

        {(tactics.length > 0 || contradictedCount > 0) && (
          <div className="mt-3 text-sm space-y-2">
            {tactics.length > 0 && (
              <div>
                <div className="font-semibold text-twitter-text">
                  🧠 Manipulation tactics ({tactics.length})
                </div>
                <ul className="mt-1 list-disc list-inside text-twitter-muted text-xs space-y-0.5">
                  {tactics.slice(0, 4).map((t, i) => (
                    <li key={i}>
                      <span className="font-mono">{t.tactic}</span>
                    </li>
                  ))}
                  {tactics.length > 4 && (
                    <li className="opacity-70">+{tactics.length - 4} more</li>
                  )}
                </ul>
              </div>
            )}
            {contradictedCount > 0 && (
              <div>
                <div className="font-semibold text-twitter-text">
                  🩺 Fact-check: {contradictedCount} contradicted claim{contradictedCount > 1 ? "s" : ""}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="mt-4 px-3 py-2 bg-twitter-hover rounded-md">
          <div className="text-[10px] uppercase tracking-wider text-twitter-muted font-semibold">
            Destination
          </div>
          <div className="text-xs font-mono break-all text-twitter-text mt-0.5">{url}</div>
        </div>

        <div className="mt-6 flex gap-2 justify-end">
          <button
            onClick={onContinue}
            className="px-4 py-2 text-sm text-twitter-muted hover:bg-twitter-hover rounded-md transition-colors"
            type="button"
          >
            Continue anyway
          </button>
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-twitter-blue text-white rounded-md hover:bg-twitter-blue/90 font-medium text-sm transition-colors"
            type="button"
          >
            🛡️ Stay safe — Cancel
          </button>
        </div>

        <p className="mt-3 text-[10px] text-twitter-muted/70 italic text-center">
          Demo: production extension intercepts native commerce buttons (Lazada/Shopee/affiliate).
        </p>
      </div>
    </div>
  );
}
