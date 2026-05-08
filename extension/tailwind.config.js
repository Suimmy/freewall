/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{ts,tsx,html}', './index.html'],
  // important: ':host' bumps specificity inside the Shadow DOM root injected by content/injector.ts
  // so host-page styles cannot leak in or override our overlay.
  important: ':host',
  theme: {
    extend: {
      colors: {
        // Sovereignty Score bands — cutoffs 70 / 30 (see shared/ENUMS.md ScoreBand)
        score: {
          high: '#10b981', // emerald-500 — score ≥ 70 (likely safe)
          mid:  '#f59e0b', // amber-500   — 30 ≤ score < 70 (caution)
          low:  '#ef4444', // red-500     — score < 30 (high-risk)
        },
        // Overlay surface palette — chosen to read on top of arbitrary host backgrounds
        freewall: {
          bg:     '#0f172a',
          panel:  '#1e293b',
          border: '#334155',
          text:   '#f1f5f9',
          muted:  '#94a3b8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
