"""Safety checks and disclaimer text."""
from __future__ import annotations

SAFETY_NOTE = (
    "This output is generated from synthetic FHIR-like data for clinician review. "
    "It does not diagnose, recommend treatment, or replace clinical judgment."
)

REQUIRED_RECORD_KEYS = (
    "patient_id",
    "patient",
    "referral_reason",
    "conditions",
    "encounters",
    "observations",
    "medications",
    "documents",
)

def assert_synthetic_patient(record: dict) -> None:
    patient = record.get("patient", {})
    if not patient.get("synthetic", False):
        raise ValueError("Patient record is not marked synthetic. ReferralReady refuses to process non-synthetic data.")


def validate_patient_record(record: dict) -> None:
    missing = [key for key in REQUIRED_RECORD_KEYS if key not in record]
    if missing:
        raise ValueError(f"Patient record is missing required keys: {', '.join(missing)}")

    patient = record.get("patient", {})
    if patient.get("id") != record.get("patient_id"):
        raise ValueError("Patient record IDs do not match.")

    for key in ("conditions", "encounters", "observations", "medications", "documents"):
        if not isinstance(record.get(key), list):
            raise ValueError(f"Patient record field '{key}' must be a list.")

def append_safety_note(markdown: str) -> str:
    return markdown.rstrip() + f"\n\n## Safety Note\n{SAFETY_NOTE}\n"
