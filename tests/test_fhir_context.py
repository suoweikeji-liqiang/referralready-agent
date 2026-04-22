import json

from app.platform_context import extract_platform_context
from app.tools import get_patient_snapshot
from tests.test_server_runtime import _make_context


def test_extract_platform_context_reads_prompt_opinion_fhir_context_payload():
    ctx = _make_context(
        {
            "x-promptopinion-fhir-context": json.dumps(
                {
                    "fhirUrl": "https://fhir.example.com/r4",
                    "fhirToken": "secret-token",
                    "patientId": "SYN-FHIR-001",
                }
            )
        }
    )

    platform_context = extract_platform_context(ctx)

    assert platform_context["fhir_server_url"] == "https://fhir.example.com/r4"
    assert platform_context["fhir_access_token"] == "secret-token"
    assert platform_context["patient_id"] == "SYN-FHIR-001"


def test_patient_snapshot_can_load_from_fhir_context_without_local_file(monkeypatch):
    fake_record = {
        "patient_id": "SYN-FHIR-001",
        "patient": {"id": "SYN-FHIR-001", "synthetic": True, "age": 51, "sex": "female"},
        "referral_reason": "Referral packet generated from Prompt Opinion FHIR context.",
        "conditions": [{"display": "Type 2 diabetes mellitus", "status": "active", "onset": "2021"}],
        "encounters": [{"date": "2026-04-10", "type": "primary care", "summary": "FHIR encounter summary."}],
        "observations": [
            {
                "date": "2026-04-09",
                "category": "lab",
                "name": "A1c",
                "loinc": "4548-4",
                "value": 8.1,
                "unit": "%",
                "interpretation": "high",
                "specialties": ["all"],
            }
        ],
        "medications": [{"name": "Metformin", "status": "active", "indication": "type 2 diabetes", "notes": ""}],
        "documents": [{"date": "2026-04-10", "type": "primary care note", "title": "Referral note", "summary": "FHIR note."}],
    }
    ctx = _make_context(
        {
            "x-promptopinion-fhir-context": json.dumps(
                {
                    "fhirUrl": "https://fhir.example.com/r4",
                    "fhirToken": "secret-token",
                    "patientId": "SYN-FHIR-001",
                }
            )
        }
    )

    def _fake_fetch(patient_id: str, platform_context: dict[str, str | None]) -> dict:
        assert patient_id == "SYN-FHIR-001"
        assert platform_context["fhir_server_url"] == "https://fhir.example.com/r4"
        return fake_record

    monkeypatch.setattr("app.data_store.fetch_patient_record_from_fhir", _fake_fetch)

    snapshot = get_patient_snapshot(None, ctx)

    assert snapshot["patient_id"] == "SYN-FHIR-001"
    assert snapshot["age"] == 51
    assert snapshot["available_observation_count"] == 1
