import json
from pathlib import Path

import pytest

import app.data_store as data_store
from app.data_store import DataNotFoundError, list_patient_ids, load_patient, normalize_specialty
from app.tools import (
    build_referral_packet,
    check_referral_completeness,
    generate_care_coordination_tasks,
    get_patient_snapshot,
    get_recent_clinical_signals,
)


def test_patient_snapshot_ckd():
    snapshot = get_patient_snapshot("SYN-CKD-001")
    assert snapshot["synthetic"] is True
    assert snapshot["age"] == 58
    assert any(c["display"] == "Type 2 diabetes mellitus" for c in snapshot["active_conditions"])


def test_nephrology_signals_include_egfr():
    result = get_recent_clinical_signals("SYN-CKD-001", "nephrology")
    names = {signal["name"] for signal in result["signals"]}
    assert "eGFR" in names
    assert "Creatinine" in names


def test_ckd_missing_nephrology_items():
    result = check_referral_completeness("SYN-CKD-001", "nephrology")
    missing_ids = {item["id"] for item in result["missing"]}
    assert "urine_acr" in missing_ids
    assert "renal_ultrasound" in missing_ids
    assert result["completion_rate"] < 1.0


def test_packet_contains_safety_and_tasks():
    packet = build_referral_packet("SYN-CKD-001", "nephrology")
    markdown = packet["markdown"]
    assert "Nephrology Referral Packet" in markdown
    assert "Missing Information Before Referral" in markdown
    assert "Care Coordinator Tasks" in markdown
    assert "does not diagnose" in markdown
    assert "—" not in markdown


def test_specialty_aliases_normalize_to_expected_values():
    assert normalize_specialty("renal") == "nephrology"
    assert normalize_specialty("heart") == "cardiology"
    assert normalize_specialty("endocrine") == "endocrinology"


def test_unknown_patient_raises_data_not_found():
    with pytest.raises(DataNotFoundError):
        get_patient_snapshot("SYN-UNKNOWN-999")


def test_unknown_specialty_raises_data_not_found():
    with pytest.raises(DataNotFoundError):
        check_referral_completeness("SYN-CKD-001", "oncology")


def test_complete_nephrology_case_has_no_missing_items():
    result = check_referral_completeness("SYN-CKD-004", "nephrology")

    assert result["missing"] == []
    assert result["completion_rate"] == 1.0


def test_complete_case_routes_packet_without_gap_tasks():
    tasks = generate_care_coordination_tasks("SYN-HF-005", "cardiology")
    packet = build_referral_packet("SYN-DM-006", "endocrinology")

    assert tasks["tasks"] == [
        {
            "task": "Review completed referral packet and route to the specialist team.",
            "owner": "care coordinator",
            "priority": "medium",
            "reason": "Checklist appears complete in the synthetic record.",
            "status": "open",
        }
    ]
    assert "No checklist gaps detected in the synthetic record." in packet["markdown"]


def test_list_patient_ids_includes_expanded_fixtures():
    patient_ids = list_patient_ids()

    assert "SYN-CKD-004" in patient_ids
    assert "SYN-HF-005" in patient_ids
    assert "SYN-DM-006" in patient_ids


def test_malformed_patient_record_is_rejected(tmp_path, monkeypatch):
    data_root = tmp_path / "data"
    synthetic_dir = data_root / "synthetic_fhir"
    synthetic_dir.mkdir(parents=True)
    malformed_path = synthetic_dir / "SYN-BAD-001.json"
    malformed_path.write_text(
        json.dumps(
            {
                "patient_id": "SYN-BAD-001",
                "patient": {"id": "SYN-BAD-001", "synthetic": True},
                "referral_reason": "Malformed synthetic record.",
                "conditions": [],
                "encounters": [],
                "medications": [],
                "documents": [],
            }
        ),
        encoding="utf-8",
    )

    load_patient.cache_clear()
    monkeypatch.setattr(data_store, "DATA_DIR", data_root)

    with pytest.raises(ValueError):
        load_patient("SYN-BAD-001")
