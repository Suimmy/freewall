// Loads the 20 prefilled example posts from /public/examples.json.
// Suim curates examples.json on 8 พ.ค. morning per JOURNAL Imminent TODO.

import type { ExamplePost } from "@/types";

let cached: ExamplePost[] | null = null;

export async function loadExamples(): Promise<ExamplePost[]> {
  if (cached) return cached;
  const res = await fetch("/examples.json");
  if (!res.ok) {
    console.warn("examples.json not loadable, using empty array (Suim populates Phase 4)");
    cached = [];
    return cached;
  }
  const data = (await res.json()) as { examples: ExamplePost[] };
  cached = data.examples ?? [];
  return cached;
}
