# ReferralReady Agent

**FHIR-aware referral packet generation for safer specialist handoffs.**

ReferralReady is an MCP-powered healthcare workflow tool that assembles specialist-ready referral packets from **synthetic FHIR-like patient data**. It selects relevant clinical context, identifies missing referral information, and generates care coordination tasks for human review.

> Safety boundary: ReferralReady does **not** diagnose, recommend treatment, or process real PHI. It is a workflow assistant for clinician review using synthetic data only.

## Why this project

Specialty referrals are often delayed because key labs, medication context, imaging, or referral rationale are missing. ReferralReady helps care teams turn fragmented clinical context into a structured packet that is easier for specialists and care coordinators to review.

## Demo scenarios

| Patient ID | Scenario | Specialty |
|---|---|---|
| `SYN-CKD-001` | Diabetes + hypertension + declining eGFR | Nephrology |
| `SYN-CKD-004` | More complete CKD referral packet with UACR and renal imaging | Nephrology |
| `SYN-HF-002` | Heart failure symptoms + elevated BNP + ED visit | Cardiology |
| `SYN-HF-005` | More complete cardiology packet with echo and medication reconciliation | Cardiology |
| `SYN-DM-003` | Poor glycemic control + medication changes | Endocrinology |
| `SYN-DM-006` | More complete endocrinology packet with metabolic and medication context | Endocrinology |

## MCP tools

ReferralReady exposes six tools:

1. `get_patient_snapshot(patient_id)`
2. `get_recent_clinical_signals(patient_id, specialty, lookback_days)`
3. `get_medication_context(patient_id)`
4. `check_referral_completeness(patient_id, specialty)`
5. `build_referral_packet(patient_id, specialty, referral_reason)`
6. `generate_care_coordination_tasks(patient_id, specialty)`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_local_demo.py --patient SYN-CKD-001 --specialty nephrology
```

Run tests:

```bash
pytest -q
```

Run the internal competition scorecard:

```bash
python scripts/score_submission.py
```

Run as an MCP server:

```bash
python -m app.mcp_server
```

## Example prompt for Prompt Opinion

```text
Prepare a nephrology referral packet for synthetic patient SYN-CKD-001. Include the referral rationale, key clinical evidence, missing information before referral, and care coordinator tasks. Do not diagnose or recommend treatment.
```

## Repository structure

```text
referralready-agent/
  app/                  # Core implementation and MCP server
  data/                 # Synthetic FHIR-like patient records and checklists
  docs/                 # Architecture, safety, demo, and marketplace notes
  prompts/              # Prompt templates for platform agent configuration
  scripts/              # Local demo runner
  submission/           # Devpost copy and marketplace manifest template
  tests/                # Basic unit tests
```

## Submission positioning

**Title:** ReferralReady Agent  
**Tagline:** FHIR-aware referral packet generation for safer specialist handoffs.  
**Built with:** MCP, Python, synthetic FHIR-like data, Prompt Opinion, LLM summarization.

## Competition readiness workflow

ReferralReady includes an internal scorecard for the Agents Assemble judging rubric. The scorecard:

- checks Stage 1 readiness blockers separately from Stage 2 scoring
- runs multiple judge personas with controlled artifact context
- averages scores across `AI Factor`, `Potential Impact`, and `Feasibility`
- highlights the highest-priority submission gaps before we stop iterating
