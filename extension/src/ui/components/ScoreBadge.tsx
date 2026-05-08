/**
 * Sovereignty Score pill — colored by band per shared/ENUMS.md ScoreBand cutoffs (70/30).
 */

interface Props {
  score: number // 0–100
}

const BAND_COLOR = {
  high: 'bg-score-high',
  mid: 'bg-score-mid',
  low: 'bg-score-low',
} as const

export function ScoreBadge({ score }: Props) {
  const band: keyof typeof BAND_COLOR = score >= 70 ? 'high' : score >= 30 ? 'mid' : 'low'
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-white text-xs font-medium ${BAND_COLOR[band]}`}
    >
      {Math.round(score)}
    </span>
  )
}
