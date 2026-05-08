/**
 * Explanation modal — surfaced when user clicks "Why?" on an annotation.
 * Phase 1: call /ask-why for cached ReasoningState; render reasoning trace + citations.
 */

interface Props {
  contentId: string
  onClose?: () => void
}

export function AskWhyModal({ contentId, onClose }: Props) {
  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-[2147483646]
                 pointer-events-auto"
      data-freewall-ask-why={contentId}
    >
      <div className="bg-freewall-panel border border-freewall-border rounded-lg p-6 max-w-lg text-freewall-text">
        <header className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Why was this flagged?</h3>
          <button
            type="button"
            onClick={onClose}
            className="text-freewall-muted text-xs"
          >
            close
          </button>
        </header>
        <p className="text-sm text-freewall-muted">
          {/* TODO (Phase 1): render explanation + citations from /ask-why response */}
          Loading explanation…
        </p>
      </div>
    </div>
  )
}
