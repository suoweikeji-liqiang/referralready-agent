# ReferralReady Agent — Data README

## 1. Data Source Summary

ReferralReady currently uses **synthetic FHIR-like patient data** created specifically for the hackathon demo.

The project does **not** use:

- Real patient records
- Real EHR data
- Protected Health Information (PHI)
- Insurance claims data
- Hospital production data

This is intentional. The Agents Assemble hackathon requires projects to use **synthetic or de-identified data only**. Using real PHI would create privacy, compliance, and eligibility risks.

---

## 2. Does the Competition Provide a Dataset?

The competition does **not** appear to provide a Kaggle-style official dataset for all teams to download and evaluate against.

Instead, Prompt Opinion provides a healthcare-agent platform with patient/FHIR context support. That means projects can access patient context through the platform when properly configured.

For this project, the safest and most controllable approach is:

1. Create our own synthetic FHIR patient examples.
2. Use them locally for development and demo.
3. Convert them into FHIR R4 Bundles.
4. Import those bundles into Prompt Opinion Patient Data when preparing the final demo.

---

## 3. Current Local Demo Data

The initial repository includes three synthetic patient scenarios:

```text
data/synthetic_fhir/
  SYN-CKD-001.json
  SYN-HF-002.json
  SYN-DM-003.json
```

### Patient Scenarios

| Patient ID | Scenario | Referral Specialty |
|---|---|---|
| `SYN-CKD-001` | Diabetes + hypertension + declining kidney function | Nephrology |
| `SYN-HF-002` | Heart failure symptoms + elevated BNP + recent acute care | Cardiology |
| `SYN-DM-003` | Poor glycemic control + elevated A1c + medication context | Endocrinology |

These records are synthetic demo records. They are not derived from real patients.

---

## 4. Checklist Data

ReferralReady also includes specialty-specific referral completeness checklists:

```text
data/checklists/
  nephrology.json
  cardiology.json
  endocrinology.json
```

These checklists are used to identify missing information before referral, such as:

- Missing lab values
- Missing medication context
- Missing imaging results
- Missing vital sign trends
- Missing follow-up documentation

The checklists are **demo templates**, not clinical guidelines. They should be reviewed and adapted by healthcare professionals before any real-world use.

---

## 5. Recommended Competition Data Strategy

For the competition submission, use a two-layer data strategy.

### Layer 1: Local Fallback Data

Use the existing local synthetic files for development, tests, and fallback demo mode:

```text
data/synthetic_fhir/*.json
```

This allows the MCP server to run even when Prompt Opinion FHIR context is not available.

### Layer 2: Prompt Opinion Imported FHIR Data

Before the final demo, convert the synthetic records into standard FHIR R4 Bundles:

```text
data/fhir_bundles/
  SYN-CKD-001-bundle.json
  SYN-HF-002-bundle.json
  SYN-DM-003-bundle.json
```

Then import them through Prompt Opinion Patient Data.

The bundle should include relevant FHIR R4 resources such as:

- `Patient`
- `Condition`
- `Observation`
- `MedicationRequest`
- `Encounter`
- `DiagnosticReport`
- `DocumentReference`, optional
- `CarePlan`, optional

---

## 6. Prompt Opinion / FHIR Context Plan

When ReferralReady is connected to Prompt Opinion, the MCP server should support two modes.

### Mode A: Platform FHIR Context Available

If Prompt Opinion provides FHIR context headers, the server should use them.

Expected context may include:

```text
X-FHIR-Server-URL
X-FHIR-Access-Token
X-Patient-ID
```

In this mode, tools should fetch patient resources from the provided FHIR server.

### Mode B: No Platform Context Available

If FHIR context is not present, the server should fall back to local synthetic demo data.

This makes the project easier to test and demo locally.

---

## 7. Safety and Compliance Positioning

ReferralReady should be described as a **workflow support tool**, not a diagnosis or treatment tool.

Recommended safety language:

> ReferralReady uses synthetic FHIR data only. It does not process real PHI, diagnose patients, recommend treatment, or replace clinical judgment. All generated referral packets and care coordination tasks are intended for human review.

This should appear in:

- `README.md`
- Devpost submission
- Demo video
- Prompt Opinion marketplace description
- Safety documentation

---

## 8. What the Agent Produces

ReferralReady generates a structured referral packet from synthetic FHIR data.

Example sections:

```markdown
# Nephrology Referral Packet

## Referral Reason
Progressive decline in kidney function in a synthetic patient with diabetes and hypertension.

## Key Clinical Context
- Active conditions
- Recent labs
- Vital signs
- Medication context
- Relevant encounters

## Missing Information Before Referral
- Urine albumin-creatinine ratio
- Blood pressure trend
- Renal ultrasound result
- Medication adherence confirmation

## Care Coordinator Tasks
1. Request missing lab.
2. Confirm medication list.
3. Attach recent imaging if available.
4. Prepare referral handoff for clinician review.

## Safety Note
Generated from synthetic data. Human review required. Not a diagnosis or treatment recommendation.
```

---

## 9. Future Upgrade: Synthea

For a stronger version, use Synthea-generated synthetic patients.

Synthea can generate realistic synthetic health records and export them in HL7 FHIR format. This would make ReferralReady more credible than using only hand-written demo JSON.

Recommended future structure:

```text
data/synthea/
  README.md
  raw_exports/
  selected_referral_cases/
```

Suggested workflow:

1. Generate synthetic patients with Synthea.
2. Select patients with referral-relevant scenarios.
3. Import selected FHIR bundles into Prompt Opinion.
4. Use those patient IDs in the demo.

---

## 10. Data Provenance Statement for Submission

Use this in the Devpost submission or project README:

> ReferralReady uses synthetic FHIR-like patient records created specifically for this hackathon demo. The current demo includes three synthetic referral scenarios: nephrology, cardiology, and endocrinology. These records are not derived from real patients and contain no PHI. For future expansion, ReferralReady can ingest Synthea-generated HL7 FHIR R4 records to test the workflow at larger scale.

---

## 11. Practical Next Step

The next implementation step is to add standard FHIR R4 Bundle files:

```text
data/fhir_bundles/
  SYN-CKD-001-bundle.json
  SYN-HF-002-bundle.json
  SYN-DM-003-bundle.json
```

Then update the MCP server to:

1. Read FHIR context from request headers when available.
2. Query the Prompt Opinion FHIR server when configured.
3. Fall back to local synthetic data when FHIR context is unavailable.

This gives the project a stable local demo and a credible Prompt Opinion integration path.
