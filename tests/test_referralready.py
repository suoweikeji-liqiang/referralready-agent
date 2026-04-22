from app.tools import build_referral_packet, check_referral_completeness, get_patient_snapshot, get_recent_clinical_signals


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
