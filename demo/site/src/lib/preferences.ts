// L3 Override + Sensitivity — user-controlled flag thresholds + per-post overrides.
// Persisted to localStorage so settings survive across page reloads.
//
// Strictness re-maps the backend score (which is unchanged) onto user-chosen
// band thresholds. The score number stays the same — only the color signal /
// "is flagged" decision shifts. This is honest: we don't hide the agent's
// findings, we let the user dial how much surface attention they want.

import type { ScoreBand } from "@/types";

export type Strictness = "light" | "standard" | "strict";

interface Prefs {
  strictness: Strictness;
  overriddenPostIds: string[]; // user clicked "Trust this post"
}

const STORAGE_KEY = "freewall_prefs_v1";

const DEFAULT_PREFS: Prefs = {
  strictness: "standard",
  overriddenPostIds: [],
};

export function loadPrefs(): Prefs {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_PREFS };
    const parsed = JSON.parse(raw);
    return {
      strictness: parsed.strictness ?? DEFAULT_PREFS.strictness,
      overriddenPostIds: Array.isArray(parsed.overriddenPostIds)
        ? parsed.overriddenPostIds
        : [],
    };
  } catch {
    return { ...DEFAULT_PREFS };
  }
}

export function savePrefs(prefs: Prefs): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  } catch (e) {
    console.warn("[Freewall] failed to persist prefs", e);
  }
}

/**
 * Re-map a numeric score to a band based on the user's chosen strictness.
 * Score is whatever the backend returned (0-100, unchanged); strictness
 * shifts where the cutoffs land.
 *
 * - Light: only blatant misinfo flags red (< 20 = high_risk). Caution band
 *   spans 20-50; everything 50+ reads as safe.
 * - Standard (default, matches backend): < 30 high_risk, 30-70 caution, > 70 safe.
 * - Strict: catches borderline too. < 50 = high_risk, 50-80 = caution, > 80 safe.
 */
export function effectiveBand(score: number, strictness: Strictness): ScoreBand {
  if (strictness === "light") {
    if (score < 20) return "high_risk";
    if (score < 50) return "caution";
    return "safe";
  }
  if (strictness === "strict") {
    if (score < 50) return "high_risk";
    if (score < 80) return "caution";
    return "safe";
  }
  // standard
  if (score < 30) return "high_risk";
  if (score < 70) return "caution";
  return "safe";
}

export const STRICTNESS_LABELS: Record<Strictness, string> = {
  light: "Light",
  standard: "Standard",
  strict: "Strict",
};

export const STRICTNESS_DESCRIPTIONS: Record<Strictness, string> = {
  light: "Only blatant misinfo flags red. Less attention noise.",
  standard: "Default cutoffs — matches backend score bands.",
  strict: "Catches borderline content too. More vigilant.",
};
