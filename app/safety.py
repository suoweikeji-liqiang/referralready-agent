"""Safety checks and disclaimer text."""
from __future__ import annotations

SAFETY_NOTE = (
    "This output is generated from synthetic FHIR-like data for clinician review. "
    "It does not diagnose, recommend treatment, or replace clinical judgment."
)

def assert_synthetic_patient(record: dict) -> None:
    patient = record.get("patient", {})
    if not patient.get("synthetic", False):
        raise ValueError("Patient record is not marked synthetic. ReferralReady refuses to process non-synthetic data.")

def append_safety_note(markdown: str) -> str:
    return markdown.rstrip() + f"\n\n## Safety Note\n{SAFETY_NOTE}\n"
