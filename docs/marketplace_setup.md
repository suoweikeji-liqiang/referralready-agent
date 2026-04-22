# Prompt Opinion Marketplace Setup Notes

This file is a checklist, not an official platform document. Replace placeholders with exact settings shown in Prompt Opinion.

## Suggested marketplace name

ReferralReady Agent

## Suggested description

ReferralReady assembles specialist-ready referral packets from synthetic FHIR-like data. It identifies missing referral information and generates care coordination tasks for human review.

## MCP server command

```bash
python -m app.mcp_server
```

## Tools to expose

- get_patient_snapshot
- get_recent_clinical_signals
- get_medication_context
- check_referral_completeness
- build_referral_packet
- generate_care_coordination_tasks

## Submission checklist

- [ ] Marketplace URL added to Devpost
- [ ] MCP tools visible and callable
- [ ] Demo uses synthetic patient IDs
- [ ] Video is under 3 minutes
- [ ] Safety boundary is stated clearly
- [ ] Internal scorecard reviewed with `python scripts/score_submission.py`
