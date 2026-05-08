import { useEffect } from "react";
import {
  STRICTNESS_DESCRIPTIONS,
  STRICTNESS_LABELS,
  type Strictness,
} from "@/lib/preferences";

interface Props {
  strictness: Strictness;
  onStrictnessChange: (s: Strictness) => void;
  overriddenPostIds: string[];
  onClearOverride: (postId: string) => void;
  onClearAllOverrides: () => void;
  onClose: () => void;
}

const LEVELS: Strictness[] = ["light", "standard", "strict"];

export function SettingsModal({
  strictness,
  onStrictnessChange,
  overriddenPostIds,
  onClearOverride,
  onClearAllOverrides,
  onClose,
}: Props) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-title"
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-3">
          <div className="text-2xl shrink-0">⚙️</div>
          <div className="flex-1 min-w-0">
            <h2 id="settings-title" className="text-lg font-bold text-twitter-text">
              Sensitivity & overrides
            </h2>
            <p className="text-xs text-twitter-muted">
              Tune how much attention Freewall surfaces. Score numbers stay the same — only the color signal cutoffs shift.
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

        {/* Strictness selector */}
        <div className="mt-5">
          <div className="text-[10px] uppercase tracking-wider text-twitter-muted font-semibold mb-2">
            Flag strictness
          </div>
          <div className="grid grid-cols-3 gap-2">
            {LEVELS.map((s) => (
              <button
                key={s}
                onClick={() => onStrictnessChange(s)}
                className={`px-3 py-2 rounded-md text-sm font-semibold border transition-colors ${
                  strictness === s
                    ? "bg-twitter-blue text-white border-twitter-blue"
                    : "bg-white text-twitter-text border-twitter-border hover:bg-twitter-hover"
                }`}
                type="button"
              >
                {STRICTNESS_LABELS[s]}
              </button>
            ))}
          </div>
          <p className="text-xs text-twitter-muted mt-2 italic">
            {STRICTNESS_DESCRIPTIONS[strictness]}
          </p>
          <div className="mt-2 text-[10px] text-twitter-muted/70 space-y-0.5 font-mono">
            <div>Light · high_risk &lt; 20 · caution &lt; 50 · safe ≥ 50</div>
            <div>Standard · high_risk &lt; 30 · caution &lt; 70 · safe ≥ 70</div>
            <div>Strict · high_risk &lt; 50 · caution &lt; 80 · safe ≥ 80</div>
          </div>
        </div>

        {/* Per-post overrides */}
        <div className="mt-5 pt-5 border-t border-twitter-border">
          <div className="flex items-center justify-between mb-2">
            <div className="text-[10px] uppercase tracking-wider text-twitter-muted font-semibold">
              Trusted posts ({overriddenPostIds.length})
            </div>
            {overriddenPostIds.length > 0 && (
              <button
                onClick={onClearAllOverrides}
                className="text-xs text-twitter-blue hover:underline"
                type="button"
              >
                Clear all
              </button>
            )}
          </div>
          {overriddenPostIds.length === 0 ? (
            <p className="text-xs text-twitter-muted italic">
              No overrides yet. Click "✓ Trust this post" in the sidebar to mute Freewall's signals on a specific post.
            </p>
          ) : (
            <ul className="space-y-1.5 max-h-40 overflow-y-auto">
              {overriddenPostIds.map((id) => (
                <li
                  key={id}
                  className="flex items-center justify-between gap-2 px-2.5 py-1.5 bg-twitter-hover rounded-md text-xs"
                >
                  <span className="font-mono truncate text-twitter-text">{id}</span>
                  <button
                    onClick={() => onClearOverride(id)}
                    className="text-twitter-muted hover:text-red-600 shrink-0"
                    title="Remove override (re-flag this post)"
                    type="button"
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-5 pt-4 border-t border-twitter-border flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-twitter-blue text-white rounded-md hover:bg-twitter-blue/90 font-medium"
            type="button"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
