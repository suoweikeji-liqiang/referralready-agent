# 3-Minute Demo Script

## 0:00–0:20 — Problem

Specialty referrals are often delayed because key labs, medication context, imaging, or referral rationale are missing.

## 0:20–0:45 — Prompt Opinion invocation

```text
Prepare a nephrology referral packet for synthetic patient SYN-CKD-001. Include the referral rationale, key clinical evidence, missing information before referral, and care coordinator tasks. Do not diagnose or recommend treatment.
```

## 0:45–1:30 — MCP tools

Show calls to `get_patient_snapshot`, `get_recent_clinical_signals`, `get_medication_context`, `check_referral_completeness`, and `build_referral_packet`.

## 1:30–2:20 — Result

Show referral reason, active conditions, eGFR / creatinine / A1c / BP context, missing items, and care coordinator tasks.

## 2:20–2:45 — Safety

Synthetic data only. No PHI. No diagnosis. No treatment recommendation. Human review required.

## 2:45–3:00 — Closing

ReferralReady turns fragmented FHIR context into a specialist-ready handoff inside the Prompt Opinion agent ecosystem.
