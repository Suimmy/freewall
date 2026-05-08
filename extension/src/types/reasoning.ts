// AUTO-GENERATED from shared/schemas/reasoning.json. Regenerate via: bash shared/codegen.sh

/**
 * L2 → L3 contract. Each SSE event sent on GET /stream/{session_id} matches one of the event variants below. UI dispatches on the 'type' field. Enum values must match shared/ENUMS.md verbatim.
 */
export type ReasoningEvent =
  | CoordinatorDispatchedEvent
  | AgentStartedEvent
  | AgentFinishedEvent
  | ScoreUpdateEvent
  | FinalEvent
  | ErrorEvent;
/**
 * Identifier for one of the 6 agents. Coordinator dispatches the others; classifier runs in L1.
 */
export type AgentName = "coordinator" | "classifier" | "persuasion" | "fact_check" | "provenance" | "counter";

/**
 * Fired first, after Coordinator decides which agents to run. UI renders agent slots based on this.
 */
export interface CoordinatorDispatchedEvent {
  type: "coordinator_dispatched";
  session_id: string;
  content_id: string;
  timestamp: string;
  dispatched_agents: AgentName[];
  skipped_agents?: {
    agent: AgentName;
    reason: string;
    [k: string]: unknown;
  }[];
}
/**
 * Fired when a dispatched agent begins execution. UI shows 'thinking' spinner on its slot.
 */
export interface AgentStartedEvent {
  type: "agent_started";
  session_id: string;
  content_id: string;
  timestamp: string;
  agent: AgentName;
}
/**
 * Fired when an agent completes with its finding. Shape of 'finding' varies by 'agent' — UI dispatches on agent name.
 */
export interface AgentFinishedEvent {
  type: "agent_finished";
  session_id: string;
  content_id: string;
  timestamp: string;
  agent: AgentName;
  /**
   * Concrete shape depends on agent: persuasion → PersuasionFinding, fact_check → FactCheckFinding, provenance → ProvenanceFinding, counter → CounterPerspectiveFinding.
   */
  finding: PersuasionFinding | FactCheckFinding | ProvenanceFinding | CounterPerspectiveFinding;
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
/**
 * Output of Counter-Perspective Agent. Optional — runs auto when score < 50, lazy on click otherwise.
 */
export interface CounterPerspectiveFinding {
  /**
   * Best-faith opposing view to the content's claim, written as a coherent argument the user can engage with.
   */
  steelman: string;
  /**
   * Higher-credibility sources offering a different angle.
   */
  alternative_sources?: {
    url: string;
    title: string;
    publisher?: string;
    credibility?: "credible" | "mixed" | "unreliable" | "unknown";
  }[];
}
/**
 * Fired when Coordinator computes (or recomputes) sovereignty score. Can fire mid-stream as agents complete.
 */
export interface ScoreUpdateEvent {
  type: "score_update";
  session_id: string;
  content_id: string;
  timestamp: string;
  score: SovereigntyScore;
}
/**
 * Aggregated risk score 0-100 (higher = safer). Computed by Coordinator using XGBoost (or weighted-sum fallback per triage).
 */
export interface SovereigntyScore {
  /**
   * Sovereignty score. Higher = lower manipulation risk.
   */
  value: number;
  /**
   * See ENUMS.md → ScoreBand. Derived from value (70-100 safe, 30-69 caution, 0-29 high_risk).
   */
  band: "safe" | "caution" | "high_risk";
  /**
   * Coordinator's confidence in this score (lowered when agents disagree or returned errors).
   */
  confidence: number;
  /**
   * Top reasons for the score, ordered by weight. Used by 'Ask why' modal.
   */
  contributing_factors?: {
    /**
     * Human-readable factor (e.g., 'Fear-mongering tactic detected', 'Source rated unreliable').
     */
    factor: string;
    /**
     * Signed contribution to score (negative reduces score).
     */
    weight: number;
  }[];
}
/**
 * Last event for a content_id. Carries full ReasoningState — UI reconnecting late uses this to render complete view.
 */
export interface FinalEvent {
  type: "final";
  session_id: string;
  content_id: string;
  timestamp: string;
  state: ReasoningState;
}
/**
 * Full reasoning result for one content_id. Carried by the 'final' event so a UI reconnecting late gets complete state.
 */
export interface ReasoningState {
  score: SovereigntyScore;
  /**
   * Which L2 agents Coordinator decided to run for this content.
   */
  dispatched_agents: AgentName[];
  /**
   * Agents Coordinator deliberately skipped, with reason (e.g., 'meme → skip Fact-Check').
   */
  skipped_agents?: {
    agent: AgentName;
    reason: string;
  }[];
  persuasion?: PersuasionFinding;
  fact_check?: FactCheckFinding;
  provenance?: ProvenanceFinding;
  counter?: CounterPerspectiveFinding;
}
/**
 * Per-agent or global failure. UI degrades gracefully — show partial findings rather than blocking.
 */
export interface ErrorEvent {
  type: "error";
  session_id: string;
  content_id: string;
  timestamp: string;
  /**
   * Identifier for one of the 6 agents. Coordinator dispatches the others; classifier runs in L1.
   */
  agent?: "coordinator" | "classifier" | "persuasion" | "fact_check" | "provenance" | "counter";
  error: {
    /**
     * Stable error code (e.g., 'llm_timeout', 'rag_unavailable', 'invalid_input').
     */
    code: string;
    /**
     * Human-readable message. Safe to show in dev UI; production UI should map by code.
     */
    message: string;
  };
}
