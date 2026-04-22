# Devpost Draft

## Title

ReferralReady Agent

## Tagline

FHIR-aware referral packet generation for safer specialist handoffs.

## What it does

ReferralReady is an MCP-powered healthcare workflow assistant that assembles specialist-ready referral packets from synthetic FHIR-like patient data. It extracts relevant clinical context, checks specialty-specific referral completeness, identifies missing information, and generates care coordination tasks for human review.

## Inspiration

Specialty referrals often require follow-up because key labs, medication context, imaging, or referral rationale are missing. ReferralReady focuses on a narrow, realistic workflow: making the handoff cleaner before the patient reaches the specialist.

## How we built it

- Built a Python MCP server with six healthcare workflow tools.
- Created synthetic FHIR-like patient records for nephrology, cardiology, and endocrinology referral scenarios.
- Added specialty checklists to identify missing referral packet elements.
- Generated structured Markdown packets designed for clinician review.
- Added safety boundaries: synthetic data only, no PHI, no diagnosis, no treatment recommendations.

## Built with

MCP, Python, synthetic FHIR-like data, Prompt Opinion, structured workflow tools.

## Safety

ReferralReady uses synthetic data only. It does not process real PHI, diagnose, recommend treatment, or replace clinical judgment. All outputs include a human-review requirement.
