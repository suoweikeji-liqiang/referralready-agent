# ReferralReady Competition Readiness Design

## Goal

Prepare ReferralReady for the Agents Assemble submission by improving three things in a controlled way:

- submission readiness against the official Stage 1 pass/fail requirements
- internal judging discipline against the Stage 2 scoring criteria
- confidence in the synthetic data and deterministic workflow through broader test coverage

The design keeps the product narrow: ReferralReady remains a referral-packet workflow assistant for synthetic data demos. It does not become a diagnostic agent or a general-purpose clinical copilot.

## Competition Constraints

- Prompt Opinion Marketplace publication and direct platform invocation are mandatory Stage 1 gates.
- The project must remain explicitly MCP-based and synthetic-data-only.
- Stage 2 judging is equally weighted across `AI Factor`, `Potential Impact`, and `Feasibility`.
- Ties are broken by the first listed criterion, so `AI Factor` deserves extra attention.

## Scope

### 1. Internal Judging Scorecard

Add an internal scorecard workflow that evaluates the repository against the competition rubric.

Design choices:

- keep it internal to the repo, not a user-facing Marketplace feature
- use controlled context by reading only selected project artifacts
- run multiple independent judge personas over the same rubric
- aggregate criterion averages and surface disagreement between judges
- include a separate Stage 1 readiness check so the team does not confuse "good scores" with actual eligibility

The scorecard is intended to answer one question repeatedly: "Are we ready to submit yet?"

### 2. Synthetic Data Expansion

Expand the synthetic dataset with more useful test fixtures instead of adding volume for its own sake.

Target data shapes:

- one more nephrology patient with a more complete packet
- one more cardiology patient with a more complete packet
- one more endocrinology patient with a more complete packet
- preserve existing incomplete cases so missing-information behavior stays testable

This gives us both positive and negative coverage for checklist logic, care-coordination task generation, and packet rendering.

### 3. Validation and Test Expansion

Strengthen the reliability story with deterministic validation and broader tests.

Add coverage for:

- specialty alias normalization
- unknown patient and specialty errors
- complete versus incomplete referral scenarios
- care-coordination behavior when no checklist gaps remain
- scorecard aggregation and Stage 1 gating
- output stability, including safety text and Markdown sections

Also tighten record validation enough to keep synthetic fixtures coherent without over-engineering a full FHIR validator.

## Non-Goals

- no real PHI support
- no diagnosis or treatment recommendations
- no external LLM dependency for internal judging
- no public-facing "judge agent" in the Marketplace
- no expansion into a generic EHR summarizer

## Architecture

### Internal Scorecard Flow

1. Select a small set of canonical project artifacts.
2. Trim or normalize those artifacts into a bounded context bundle.
3. Run several judge profiles against the same evidence.
4. Produce:
   - Stage 1 readiness summary
   - per-judge criterion scores
   - averaged criterion scores
   - score spread and major risks
   - next actions ordered by competition impact

The scoring engine should be deterministic and explainable so results are stable in CI and local development.

### Data and Validation Flow

1. Load a synthetic patient record.
2. Assert synthetic-only safety.
3. Validate the minimal record structure needed by ReferralReady.
4. Reuse the validated record across completeness checks, packet generation, and tests.

## Success Criteria

- the repo can produce a repeatable competition scorecard report from local artifacts
- the scorecard clearly shows current Stage 1 gaps instead of hiding them
- the dataset contains both complete and incomplete examples for all three specialties
- tests cover the new judging logic and the expanded data behaviors
- the project remains focused on referral handoff quality, not broader clinical reasoning
