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

## Recommended deployment command

For Prompt Opinion validation, prefer streamable HTTP with stateless mode enabled:

```bash
python -m app.mcp_server --transport streamable-http --host 0.0.0.0 --port 8000 --stateless-http
```

Equivalent environment variables:

```bash
REFERRALREADY_MCP_TRANSPORT=streamable-http
REFERRALREADY_HOST=0.0.0.0
PORT=8000
REFERRALREADY_STATELESS_HTTP=true
REFERRALREADY_STREAMABLE_HTTP_PATH=/mcp
```

## Deployment checks before marketplace registration

- [ ] Public HTTPS URL returns `200` on `/healthz`
- [ ] MCP endpoint is reachable at the configured streamable HTTP path, default `/mcp`
- [ ] Only synthetic demo data is used
- [ ] `pytest -q` passes locally
- [ ] `python scripts/score_submission.py` reviewed

## Prompt Opinion context notes

- Prompt Opinion examples and participant reports indicate SHARP-style headers such as `X-FHIR-Server-URL`, `X-FHIR-Access-Token`, and `X-Patient-ID`
- At least one participant reported a fallback header mismatch where patient context appeared as `x-inc-sd`
- ReferralReady now tolerates both `x-patient-id` and `x-inc-sd` when resolving `patient_id`

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
- [ ] Deployment URL and `/healthz` verified
- [ ] Platform search and invocation proof captured inside Prompt Opinion
