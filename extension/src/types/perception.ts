// AUTO-GENERATED from shared/schemas/perception.json. Regenerate via: bash shared/codegen.sh

/**
 * L1 → L2 contract. Body of POST /perceive. One payload per content unit entering viewport (definition of 'unit' is site-specific, set by scraper.ts — see CLAUDE.md decision #15). Enum values must match shared/ENUMS.md verbatim.
 */
export interface PerceptionPayload {
  /**
   * Browser tab session UUID. Used to subscribe to SSE stream and to bind reasoning updates back to the originating tab. One tab = one session.
   */
  session_id: string;
  /**
   * Stable ID for one content unit within the session — hash of content text + URL fragment recommended. A 'content unit' is defined by scraper.ts per site type: 1 tweet on Twitter, 1 post on IG, 1 article on news sites, 1 AI message on ChatGPT, etc. Used by L2 to dedupe and by L3 to bind reasoning back to the right DOM element.
   */
  content_id: string;
  /**
   * Full URL of the page hosting the content.
   */
  url: string;
  /**
   * ISO 8601 timestamp when the extension captured this perception.
   */
  captured_at: string;
  content: {
    /**
     * Visible text of the post. Required even if empty (e.g., image-only post → empty string).
     */
    text: string;
    /**
     * URLs of images in the post (in DOM order). Empty array if no images.
     */
    images?: string[];
    /**
     * Output of Content Classifier Agent (L1). See shared/ENUMS.md → ContentCategory.
     */
    category: "news" | "ad" | "health_claim" | "social" | "meme" | "unknown";
    /**
     * Classifier confidence in the category (0..1). Used by Coordinator to decide when to fall through to all-agent dispatch on low confidence.
     */
    category_confidence?: number;
  };
  /**
   * Output of in-browser ML detectors. Optional — extension may omit fields if a detector hasn't loaded. Provenance Agent in L2 must handle missing fields gracefully.
   */
  synthetic_signals?: {
    /**
     * Probability the text is AI-generated (perplexity-based or HF detector).
     */
    ai_text_prob?: number;
    /**
     * Highest AI-gen probability across images in the post (single number — Provenance Agent decides aggregation).
     */
    ai_image_prob?: number;
    /**
     * Whether ANY image in the post carries C2PA Content Credentials metadata.
     */
    c2pa_present?: boolean;
    /**
     * Whether the C2PA chain validates as human-captured (only meaningful if c2pa_present is true).
     */
    c2pa_verified?: boolean;
  };
  source: {
    /**
     * eTLD+1 normalized hostname of the page (e.g., 'example.com' not 'www.example.com').
     */
    domain: string;
    /**
     * From hardcoded list in data/source_reputation/. See shared/ENUMS.md → SourceReputation.
     */
    reputation: "credible" | "mixed" | "unreliable" | "unknown";
  };
  /**
   * Behavioral context. Optional. Per architecture.md, used as gating signal for annotation aggressiveness — NEVER primary detection.
   */
  user_state?: {
    /**
     * Rolling-average scroll speed when this content was captured.
     */
    scroll_velocity_px_per_sec?: number;
    /**
     * Milliseconds the content was visible in viewport before perception was triggered.
     */
    dwell_ms?: number;
  };
}
