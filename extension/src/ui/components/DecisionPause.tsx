/**
 * Pause overlay before high-risk action (Buy click on score < 30 content).
 * Phase 1: capture-phase click listener on host buttons matching commerce intent;
 * show modal with score + Persuasion tactics flagged.
 */

interface Props {
  contentId: string
  // TODO (Phase 1): score: number, top_tactics: PersuasionTactic[]
  onContinue?: () => void
  onDismiss?: () => void
}

export function DecisionPause({ contentId, onContinue, onDismiss }: Props) {
  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-[2147483646]
                 pointer-events-auto"
      data-freewall-decision-pause={contentId}
    >
      <div className="bg-freewall-panel border border-freewall-border rounded-lg p-6 max-w-md text-freewall-text">
        <h3 className="font-semibold mb-2">Pause and consider</h3>
        <p className="text-sm text-freewall-muted mb-4">
          {/* TODO (Phase 1): explanation tied to the post's score + tactics */}
          This content uses persuasion patterns we want you to see clearly.
        </p>
        <div className="flex gap-2 justify-end">
          <button
            type="button"
            onClick={onDismiss}
            className="px-3 py-1.5 text-sm rounded border border-freewall-border"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onContinue}
            className="px-3 py-1.5 text-sm rounded bg-score-low text-white"
          >
            Continue anyway
          </button>
        </div>
      </div>
    </div>
  )
}
