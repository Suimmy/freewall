/**
 * Track scroll velocity + dwell time as a *gating signal* — never primary detection
 * (CLAUDE.md anti-pattern #3). Phase 1 will use this to adjust Coordinator dispatch
 * priority (rapid skim → less analysis depth).
 */

export function startUserState(): void {
  // TODO (Phase 1): track lastScrollY + lastScrollTime in module scope, compute
  //                 velocity = abs(dy / dt) on each scroll, emit "rapid_skim" message
  //                 to the background when velocity > THRESHOLD (tune against demo content).
  window.addEventListener(
    'scroll',
    () => {
      // placeholder — Phase 1 implements velocity tracking
    },
    { passive: true },
  )

  // TODO (Phase 1): per-element dwell time — use IntersectionObserver to record
  //                 time-in-view, surface as a hint when user spends > N seconds on a
  //                 high-risk post.
}
