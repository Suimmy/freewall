/**
 * Inline overlay anchored over a scraped post element.
 * Phase 1: position absolute over the originating `data-freewall-post` element using
 * its bounding rect; render markers per finding.
 */

interface Props {
  contentId: string
  // TODO (Phase 1): findings: Finding[] (typed from shared/schemas after codegen.sh)
}

export function Annotation({ contentId }: Props) {
  return (
    <div
      className="absolute pointer-events-none"
      data-freewall-annotation={contentId}
    >
      {/* TODO (Phase 1): markers per finding (Persuasion tactic spans, claim highlights) */}
    </div>
  )
}
