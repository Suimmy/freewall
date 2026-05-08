// AUTO-GENERATED from shared/schemas/agent_io.json. Regenerate via: bash shared/codegen.sh

/**
 * L2 worker agents Coordinator can route. Counter is excluded by design — orchestrator runs it as a second wave only when score < 50.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "DispatchableAgent".
 */
export type DispatchableAgent = "persuasion" | "fact_check" | "provenance";

/**
 * Per-agent INPUT contracts. Outputs are 'findings' defined in reasoning.json (cross-file $ref). When implementing each agent (OpenAI Agents SDK structured output), use these as the input contract and the corresponding finding schema as the response_format.
 *
 * Mapping (input → output):
 * - ClassifierInput → ClassifierOutput (defined here, consumed by perception.json content.category)
 * - CoordinatorInput → CoordinatorOutput (defined here, consumed by services/orchestrator.py for parallel L2 dispatch)
 * - PersuasionAgentInput → reasoning.json#/$defs/PersuasionFinding
 * - FactCheckAgentInput → reasoning.json#/$defs/FactCheckFinding
 * - ProvenanceAgentInput → reasoning.json#/$defs/ProvenanceFinding
 * - CounterPerspectiveAgentInput → reasoning.json#/$defs/CounterPerspectiveFinding
 *
 * Coordinator is an LLM agent (CLAUDE.md decision #5) using reasoning_effort=low, NOT Python orchestration. Its output drives parallel L2 worker dispatch.
 */
export interface AgentIO {
  [k: string]: unknown;
}
/**
 * Shared correlation fields. Every agent input includes these so logs and traces line up across the system.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "AgentInputBase".
 */
export interface AgentInputBase {
  /**
   * Browser tab session UUID (carried from perception.json).
   */
  session_id: string;
  /**
   * Stable per-content-unit ID (carried from perception.json).
   */
  content_id: string;
  [k: string]: unknown;
}
/**
 * Input for Content Classifier Agent (runs in L1, before Coordinator). Output goes into perception.json#/properties/content/category.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "ClassifierInput".
 */
export interface ClassifierInput {
  session_id: string;
  content_id: string;
  /**
   * Visible text to classify.
   */
  text: string;
  /**
   * Optional. If model supports vision, lets classifier consider image cues (e.g., meme format, ad layout).
   */
  image_urls?: string[];
}
/**
 * Output of Content Classifier Agent. Fed into perception.json before POST /perceive.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "ClassifierOutput".
 */
export interface ClassifierOutput {
  /**
   * See ENUMS.md → ContentCategory.
   */
  category: "news" | "ad" | "health_claim" | "social" | "meme" | "unknown";
  confidence: number;
}
/**
 * Input for L2 Coordinator agent. Decides which workers (persuasion/fact_check/provenance) to dispatch based on category + confidence. Counter-Perspective is dispatched separately by orchestrator (lazy, score<50) and is NEVER a valid value in CoordinatorOutput.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "CoordinatorInput".
 */
export interface CoordinatorInput {
  session_id: string;
  content_id: string;
  category: "news" | "ad" | "health_claim" | "social" | "meme" | "unknown";
  /**
   * L1 Classifier confidence. Coordinator overrides skip rules when this is low (< 0.5) — dispatch ALL workers as safe default.
   */
  category_confidence: number;
}
/**
 * One skipped worker with a brief justification.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "SkippedAgent".
 */
export interface SkippedAgent {
  agent: DispatchableAgent;
  /**
   * 1-line specific justification, e.g., 'meme — no factual claim to verify'.
   */
  reason: string;
}
/**
 * Coordinator dispatch decision. dispatched_agents ∪ skipped_agents must cover ALL 3 workers (no agent missing, no duplicates). Invariant enforced in prompt, not schema (JSON Schema can't express set-cover constraints cleanly).
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "CoordinatorOutput".
 */
export interface CoordinatorOutput {
  /**
   * Workers to invoke in parallel.
   */
  dispatched_agents: DispatchableAgent[];
  /**
   * Workers to skip, with reasons. Empty array if all are dispatched.
   */
  skipped_agents: SkippedAgent[];
}
/**
 * Input for Persuasion Agent (L2). Output → reasoning.json#/$defs/PersuasionFinding.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "PersuasionAgentInput".
 */
export interface PersuasionAgentInput {
  session_id: string;
  content_id: string;
  /**
   * Full visible text. Persuasion Agent quotes spans from this as evidence.
   */
  text: string;
  /**
   * Helps prompt narrow which tactic patterns are most likely (e.g., 'ad' → emphasize Cialdini scarcity/authority; 'health_claim' → emphasize fear_mongering, misrepresentation_of_expertise).
   */
  category: "news" | "ad" | "health_claim" | "social" | "meme" | "unknown";
}
/**
 * Input for Fact-Check Agent (L2). Output → reasoning.json#/$defs/FactCheckFinding. Agent runs RAG over data/corpus/{who,cdc,mayo}.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "FactCheckAgentInput".
 */
export interface FactCheckAgentInput {
  session_id: string;
  content_id: string;
  /**
   * Full visible text. Agent extracts atomic claims from this and verifies each.
   */
  text: string;
  /**
   * Coordinator will not dispatch Fact-Check for category='meme'. Other categories pass through; agent itself returns 'not_a_claim' for opinion-only content.
   */
  category: "news" | "ad" | "health_claim" | "social" | "unknown";
  /**
   * Page URL — sometimes hints at topic (e.g., 'who.int/...' suggests authoritative health source).
   */
  url?: string;
}
/**
 * Input for Provenance Agent (L2). Output → reasoning.json#/$defs/ProvenanceFinding. Reasons over L1 detector outputs — does NOT re-run ML.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "ProvenanceAgentInput".
 */
export interface ProvenanceAgentInput {
  session_id: string;
  content_id: string;
  /**
   * Short excerpt (≤500 chars) — Provenance reasons over signals not full content. Long text is wasted tokens here.
   */
  text_excerpt: string;
  /**
   * Carried from perception.json#/properties/synthetic_signals. Agent must handle missing fields (e.g., ai_image_prob absent if no images, c2pa fields absent if not detected).
   */
  synthetic_signals: {
    ai_text_prob?: number;
    ai_image_prob?: number;
    c2pa_present?: boolean;
    c2pa_verified?: boolean;
    [k: string]: unknown;
  };
  source: {
    domain: string;
    reputation: "credible" | "mixed" | "unreliable" | "unknown";
    [k: string]: unknown;
  };
}
/**
 * Input for Counter-Perspective Agent (L2). Output → reasoning.json#/$defs/CounterPerspectiveFinding. UNIQUE: takes prior findings as input — needs them to write a focused steelman that engages with what was actually claimed.
 *
 * This interface was referenced by `AgentIO`'s JSON-Schema
 * via the `definition` "CounterPerspectiveAgentInput".
 */
export interface CounterPerspectiveAgentInput {
  session_id: string;
  content_id: string;
  text: string;
  category: "news" | "ad" | "health_claim" | "social" | "meme" | "unknown";
  /**
   * Findings from earlier-completing agents. Coordinator passes whatever is available when Counter is dispatched. All optional — agent degrades gracefully (writes general-purpose steelman if no prior findings).
   */
  prior_findings?: {
    persuasion?: PersuasionFinding;
    fact_check?: FactCheckFinding;
    provenance?: ProvenanceFinding;
  };
}
/**
 * Output of Persuasion Agent. Detects tactics from PersuSafety 15 + Cialdini 6 (see ENUMS.md → PersuasionTactic).
 */
export interface PersuasionFinding {
  tactics_detected: {
    /**
     * One of 21 values from ENUMS.md → PersuasionTactic. Verbatim labels.
     */
    tactic:
      | "reciprocation"
      | "commitment_consistency"
      | "social_proof"
      | "liking"
      | "authority"
      | "scarcity"
      | "manipulative_emotional_appeals"
      | "false_scarcity"
      | "deceptive_information"
      | "bait_and_switch"
      | "exploitative_cult_tactics"
      | "guilt_tripping"
      | "fear_mongering"
      | "pressure_and_coercion"
      | "exploiting_vulnerable_individuals"
      | "creating_dependency"
      | "misrepresentation_of_expertise"
      | "social_isolation"
      | "overwhelming_information"
      | "playing_on_identity"
      | "financial_exploitation";
    /**
     * Quoted span from the content that triggered this tactic.
     */
    evidence: string;
    confidence: number;
  }[];
  /**
   * What the content is trying to get the user to do (e.g., 'buy supplement', 'share post', 'distrust vaccines').
   */
  intended_action: string;
  /**
   * Inferred motive beyond the surface ask, if any (e.g., 'affiliate revenue', 'political mobilization'). null if unclear.
   */
  hidden_agenda?: string | null;
}
/**
 * Output of Fact-Check Agent. RAG-grounded against WHO/CDC/Mayo corpus.
 */
export interface FactCheckFinding {
  /**
   * Each factual claim extracted from the content, verified independently.
   */
  claims: {
    /**
     * Atomic factual claim extracted from content.
     */
    claim: string;
    /**
     * See ENUMS.md → FactCheckVerdict.
     */
    verdict: "supported" | "contradicted" | "unverifiable" | "not_a_claim";
    /**
     * Brief reason for the verdict.
     */
    explanation?: string;
    /**
     * RAG-retrieved sources backing the verdict. Empty for 'not_a_claim'.
     */
    sources?: {
      title: string;
      url: string;
      /**
       * WHO, CDC, Mayo Clinic, etc.
       */
      publisher?: string;
      /**
       * Quoted relevant fragment from the source.
       */
      snippet?: string;
    }[];
  }[];
}
/**
 * Output of Provenance Agent. Reasons over L1's synthetic_signals + source.reputation.
 */
export interface ProvenanceFinding {
  /**
   * See ENUMS.md → SyntheticVerdict.
   */
  synthetic_verdict: "likely_human" | "uncertain" | "likely_ai";
  /**
   * Provenance Agent may upgrade or downgrade the L1 hardcoded reputation based on cross-referencing.
   */
  source_verdict: "credible" | "mixed" | "unreliable" | "unknown";
  /**
   * 1-2 sentence rationale explaining the verdicts. Surfaced in 'Ask why' modal.
   */
  reasoning: string;
}
