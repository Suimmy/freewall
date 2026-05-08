/**
 * Fact-check verdict card — shows claim, verdict, RAG citations.
 * Phase 1: bind to FactCheckAgent output (verdict, citations[]) from reasoning store.
 */

interface Props {
  contentId: string
  // TODO (Phase 1): verdict: 'supported' | 'unsupported' | 'mixed'
  // TODO (Phase 1): citations: { source: string; excerpt: string; url: string }[]
}

export function FactCheckCard({ contentId }: Props) {
  return (
    <article
      className="bg-freewall-panel border border-freewall-border rounded-lg p-4
                 text-freewall-text text-sm pointer-events-auto"
      data-freewall-fact-check={contentId}
    >
      <h3 className="font-semibold mb-2">Fact-check</h3>
      <p className="text-freewall-muted">
        {/* TODO (Phase 1): render verdict + claim summary */}
        Awaiting Fact-Check Agent…
      </p>
      {/* TODO (Phase 1): citation list with WHO/CDC/Mayo source links */}
    </article>
  )
}
