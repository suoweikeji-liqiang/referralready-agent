"""ReferralReady business logic tools.

These functions are intentionally deterministic so the local demo is reliable.
The Prompt Opinion agent can use these MCP tool outputs as context for final wording.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Iterable
from app.data_store import load_checklist, load_patient, normalize_specialty
from app.safety import append_safety_note

def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()

def _latest_date(observations: Iterable[dict]) -> date | None:
    dates = []
    for obs in observations:
        try: dates.append(_parse_date(obs["date"]))
        except Exception: pass
    return max(dates) if dates else None

def get_patient_snapshot(patient_id: str) -> dict:
    record = load_patient(patient_id)
    patient = record["patient"]
    active_conditions = [
        {"display": c["display"], "status": c.get("status", "unknown"), "onset": c.get("onset")}
        for c in record.get("conditions", []) if c.get("status", "active") == "active"
    ]
    recent_encounters = sorted(record.get("encounters", []), key=lambda e: e.get("date", ""), reverse=True)[:3]
    return {
        "patient_id": patient_id,
        "synthetic": bool(patient.get("synthetic")),
        "age": patient.get("age"),
        "sex": patient.get("sex"),
        "referral_reason": record.get("referral_reason"),
        "active_conditions": active_conditions,
        "recent_encounters": recent_encounters,
        "available_observation_count": len(record.get("observations", [])),
        "available_medication_count": len(record.get("medications", [])),
        "available_document_count": len(record.get("documents", [])),
    }

def get_recent_clinical_signals(patient_id: str, specialty: str, lookback_days: int = 180) -> dict:
    record = load_patient(patient_id)
    normalized = normalize_specialty(specialty)
    observations = record.get("observations", [])
    reference = _latest_date(observations)
    cutoff = reference - timedelta(days=lookback_days) if reference else None
    results = []
    for obs in observations:
        specialties = [normalize_specialty(s) for s in obs.get("specialties", [])]
        if normalized not in specialties and "all" not in specialties:
            continue
        if cutoff:
            try:
                if _parse_date(obs["date"]) < cutoff:
                    continue
            except Exception:
                pass
        results.append(obs)
    results.sort(key=lambda x: (x.get("name", ""), x.get("date", "")))
    grouped: dict[str, list[dict]] = {}
    for obs in results:
        grouped.setdefault(obs.get("name", "unknown"), []).append(obs)
    return {"patient_id": patient_id, "specialty": normalized, "lookback_days": lookback_days, "reference_date": reference.isoformat() if reference else None, "signals": results, "grouped_by_name": grouped}

def get_medication_context(patient_id: str) -> dict:
    record = load_patient(patient_id)
    active = [m for m in record.get("medications", []) if m.get("status") == "active"]
    inactive = [m for m in record.get("medications", []) if m.get("status") != "active"]
    adherence_notes = [m for m in record.get("medications", []) if "adherence" in m.get("notes", "").lower() or "reconciliation" in m.get("notes", "").lower()]
    return {"patient_id": patient_id, "active_medications": active, "inactive_or_recently_changed_medications": inactive, "adherence_notes": adherence_notes, "medication_review_needed": len(adherence_notes) == 0}

def _observations_matching(record: dict, names: list[str]) -> list[dict]:
    wanted = {name.lower() for name in names}
    return [obs for obs in record.get("observations", []) if obs.get("name", "").lower() in wanted or obs.get("loinc", "").lower() in wanted]

def _documents_matching(record: dict, names: list[str]) -> list[dict]:
    wanted = [name.lower() for name in names]
    matches = []
    for doc in record.get("documents", []):
        haystack = " ".join([doc.get("type", ""), doc.get("title", ""), doc.get("summary", "")]).lower()
        if any(term in haystack for term in wanted):
            matches.append(doc)
    return matches

def _medication_notes_matching(record: dict, terms: list[str]) -> list[dict]:
    wanted = [term.lower() for term in terms]
    matches = []
    for med in record.get("medications", []):
        haystack = " ".join([med.get("name", ""), med.get("indication", ""), med.get("notes", "")]).lower()
        if any(term in haystack for term in wanted):
            matches.append(med)
    return matches

def _conditions_matching(record: dict, names: list[str]) -> list[dict]:
    wanted = [name.lower() for name in names]
    matches = []
    for condition in record.get("conditions", []):
        haystack = " ".join([condition.get("display", ""), condition.get("code", "")]).lower()
        if any(term in haystack for term in wanted):
            matches.append(condition)
    return matches

def check_referral_completeness(patient_id: str, specialty: str) -> dict:
    record = load_patient(patient_id)
    normalized = normalize_specialty(specialty)
    checklist = load_checklist(normalized)
    present, missing = [], []
    for item in checklist.get("required_items", []):
        typ = item.get("type")
        if typ == "observation":
            evidence = _observations_matching(record, item.get("names", [])); ok = len(evidence) >= int(item.get("minimum_count", 1))
        elif typ == "document":
            evidence = _documents_matching(record, item.get("names", [])); ok = len(evidence) >= int(item.get("minimum_count", 1))
        elif typ == "medication_note":
            evidence = _medication_notes_matching(record, item.get("terms", [])); ok = len(evidence) >= int(item.get("minimum_count", 1))
        elif typ == "condition":
            evidence = _conditions_matching(record, item.get("names", [])); ok = len(evidence) >= int(item.get("minimum_count", 1))
        else:
            evidence = []; ok = False
        result = {"id": item["id"], "label": item["label"], "why_it_matters": item.get("why_it_matters"), "status": "present" if ok else "missing", "evidence_count": len(evidence), "evidence": evidence}
        (present if ok else missing).append(result)
    return {"patient_id": patient_id, "specialty": normalized, "present": present, "missing": missing, "completion_rate": round(len(present) / max(1, len(present)+len(missing)), 3), "human_review_required": True}

def generate_care_coordination_tasks(patient_id: str, specialty: str) -> dict:
    completeness = check_referral_completeness(patient_id, specialty)
    tasks = []
    for item in completeness["missing"]:
        label = item.get("label", "missing referral element")
        tasks.append({"task": f"Collect or confirm: {label}", "owner": "care coordinator", "priority": "high" if "lab" in label.lower() or "trend" in label.lower() else "medium", "reason": item.get("why_it_matters", "Needed to complete the referral packet."), "status": "open"})
    if not tasks:
        tasks.append({"task": "Review completed referral packet and route to the specialist team.", "owner": "care coordinator", "priority": "medium", "reason": "Checklist appears complete in the synthetic record.", "status": "open"})
    return {"patient_id": patient_id, "specialty": completeness["specialty"], "tasks": tasks, "human_review_required": True}

def _format_observation(obs: dict) -> str:
    interp = f" ({obs.get('interpretation')})" if obs.get("interpretation") else ""
    return f"{obs.get('date')}: {obs.get('name')} = {obs.get('value')} {obs.get('unit', '')}{interp}".strip()

def build_referral_packet(patient_id: str, specialty: str, referral_reason: str | None = None) -> dict:
    snapshot = get_patient_snapshot(patient_id)
    signals = get_recent_clinical_signals(patient_id, specialty)
    meds = get_medication_context(patient_id)
    completeness = check_referral_completeness(patient_id, specialty)
    tasks = generate_care_coordination_tasks(patient_id, specialty)
    reason = referral_reason or snapshot.get("referral_reason") or "Referral reason not specified."
    lines = [f"# {signals['specialty'].title()} Referral Packet", "", "## Referral Reason", reason, "", "## Patient Context", f"- Synthetic patient ID: {patient_id}", f"- Age: {snapshot.get('age')}", f"- Sex: {snapshot.get('sex')}", "", "## Active Conditions"]
    for condition in snapshot.get("active_conditions", []):
        onset = f", onset {condition.get('onset')}" if condition.get("onset") else ""
        lines.append(f"- {condition.get('display')} ({condition.get('status')}{onset})")
    lines += ["", "## Key Clinical Signals"]
    grouped = signals.get("grouped_by_name", {})
    if grouped:
        for name, observations in grouped.items():
            lines.append(f"### {name}")
            for obs in observations[-4:]:
                lines.append(f"- {_format_observation(obs)}")
    else:
        lines.append("- No specialty-specific signals found in synthetic record.")
    lines += ["", "## Medication Context"]
    active_meds = meds.get("active_medications", [])
    if active_meds:
        for med in active_meds:
            notes = f" - {med.get('notes')}" if med.get("notes") else ""
            lines.append(f"- {med.get('name')} for {med.get('indication')}{notes}")
    else:
        lines.append("- No active medications documented in synthetic record.")
    lines += ["", "## Missing Information Before Referral"]
    if completeness["missing"]:
        for item in completeness["missing"]:
            lines.append(f"- {item.get('label')} - {item.get('why_it_matters')}")
    else:
        lines.append("- No checklist gaps detected in the synthetic record.")
    lines += ["", "## Care Coordinator Tasks"]
    for idx, task in enumerate(tasks["tasks"], start=1):
        lines.append(f"{idx}. {task['task']} ({task['priority']} priority) - {task['reason']}")
    lines += ["", "## FHIR-like Evidence References", f"- Conditions reviewed: {len(snapshot.get('active_conditions', []))}", f"- Clinical signals reviewed: {len(signals.get('signals', []))}", f"- Active medications reviewed: {len(active_meds)}", f"- Completeness rate: {completeness['completion_rate'] * 100:.0f}%"]
    markdown = append_safety_note("\n".join(lines))
    return {"patient_id": patient_id, "specialty": signals["specialty"], "referral_reason": reason, "completion_rate": completeness["completion_rate"], "missing_count": len(completeness["missing"]), "markdown": markdown, "human_review_required": True}
