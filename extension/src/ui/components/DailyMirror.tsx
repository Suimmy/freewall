/**
 * End-of-session reflection. Shows session metrics: posts analysed, tactics encountered,
 * score distribution. Phase 1: render from /daily-mirror response.
 */

export function DailyMirror() {
  return (
    <section
      className="bg-freewall-panel border border-freewall-border rounded-lg p-4
                 text-freewall-text text-sm pointer-events-auto"
      data-freewall-daily-mirror
    >
      <h3 className="font-semibold mb-3">Today&apos;s mirror</h3>
      <p className="text-freewall-muted">
        {/* TODO (Phase 1): counts (posts seen, posts paused), top tactics bar chart, score histogram */}
        Session metrics will appear here.
      </p>
    </section>
  )
}
