"""FHIR context loading and normalization helpers."""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SYNTHETIC_MARKERS = ("synthetic", "deidentified", "de-identified", "test", "demo")


class FhirFetchError(RuntimeError):
    """Raised when remote FHIR context cannot be fetched or normalized."""


def _build_headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/fhir+json, application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request_json(url: str, token: str | None) -> dict[str, Any]:
    request = Request(url, headers=_build_headers(token))
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise FhirFetchError(f"FHIR request failed for {url}: {exc.code}") from exc
    except URLError as exc:
        raise FhirFetchError(f"FHIR request failed for {url}: {exc.reason}") from exc


def _fetch_resource(base_url: str, resource_path: str, token: str | None) -> dict[str, Any]:
    return _request_json(f"{base_url.rstrip('/')}/{resource_path.lstrip('/')}", token)


def _fetch_bundle(
    base_url: str,
    resource_type: str,
    patient_id: str,
    token: str | None,
    extra_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    params = {"patient": patient_id, "_count": 100}
    if extra_params:
        params.update(extra_params)
    try:
        return _request_json(f"{base_url.rstrip('/')}/{resource_type}?{urlencode(params)}", token)
    except FhirFetchError:
        return {"resourceType": "Bundle", "entry": []}


def _entries(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry.get("resource", {}) for entry in bundle.get("entry", []) if isinstance(entry, dict)]


def _text_from_codeable_concept(value: dict[str, Any] | None) -> str | None:
    if not value:
        return None
    if value.get("text"):
        return value["text"]
    for coding in value.get("coding", []):
        for key in ("display", "code"):
            if coding.get(key):
                return str(coding[key])
    return None


def _status_from_concept(resource: dict[str, Any], field: str = "clinicalStatus") -> str:
    concept = resource.get(field) or {}
    text = _text_from_codeable_concept(concept)
    if text:
        return text.lower()
    return str(resource.get("status") or "unknown").lower()


def _date_only(value: str | None) -> str | None:
    if not value:
        return None
    return value[:10]


def _calculate_age(birth_date: str | None) -> int | None:
    if not birth_date:
        return None
    try:
        born = datetime.strptime(birth_date[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def _extract_loinc(concept: dict[str, Any] | None) -> str:
    if not concept:
        return ""
    for coding in concept.get("coding", []):
        system = str(coding.get("system") or "").lower()
        if "loinc" in system and coding.get("code"):
            return str(coding["code"])
    return ""


def _extract_observation_value(resource: dict[str, Any]) -> tuple[Any, str]:
    if resource.get("valueQuantity"):
        quantity = resource["valueQuantity"]
        return quantity.get("value"), str(quantity.get("unit") or "")
    if resource.get("valueString") is not None:
        return resource["valueString"], ""
    if resource.get("valueCodeableConcept"):
        return _text_from_codeable_concept(resource["valueCodeableConcept"]), ""
    if resource.get("valueInteger") is not None:
        return resource["valueInteger"], ""
    if resource.get("valueBoolean") is not None:
        return resource["valueBoolean"], ""
    return None, ""


def _interpretation(resource: dict[str, Any]) -> str | None:
    interpretations = resource.get("interpretation") or []
    if interpretations:
        return _text_from_codeable_concept(interpretations[0])
    return None


def _document_summary(resource: dict[str, Any]) -> dict[str, Any]:
    if resource.get("resourceType") == "DiagnosticReport":
        return {
            "date": _date_only(resource.get("effectiveDateTime") or resource.get("issued")),
            "type": "diagnostic report",
            "title": _text_from_codeable_concept(resource.get("code")) or "Diagnostic report",
            "summary": str(resource.get("conclusion") or "Diagnostic report available from FHIR context."),
        }
    attachment_title = None
    for content in resource.get("content", []):
        attachment = content.get("attachment", {})
        if attachment.get("title"):
            attachment_title = attachment["title"]
            break
    return {
        "date": _date_only(resource.get("date")),
        "type": _text_from_codeable_concept(resource.get("type")) or "document reference",
        "title": attachment_title or _text_from_codeable_concept(resource.get("type")) or "Document reference",
        "summary": str(resource.get("description") or "Document reference available from FHIR context."),
    }


def _encounter_summary(resource: dict[str, Any]) -> dict[str, Any]:
    reasons = resource.get("reasonCode") or []
    summary = _text_from_codeable_concept(reasons[0]) if reasons else None
    if not summary and resource.get("serviceType"):
        summary = _text_from_codeable_concept(resource.get("serviceType"))
    return {
        "date": _date_only(resource.get("period", {}).get("start") or resource.get("actualPeriod", {}).get("start")),
        "type": _text_from_codeable_concept(resource.get("type", [{}])[0] if resource.get("type") else None)
        or str(resource.get("class", {}).get("code") or "encounter"),
        "summary": summary or "Encounter available from FHIR context.",
    }


def _medication_summary(resource: dict[str, Any]) -> dict[str, Any]:
    notes = []
    for note in resource.get("note", []):
        if note.get("text"):
            notes.append(str(note["text"]))
    for instruction in resource.get("dosageInstruction", []):
        if instruction.get("text"):
            notes.append(str(instruction["text"]))
    return {
        "name": _text_from_codeable_concept(resource.get("medicationCodeableConcept")) or "Medication",
        "status": str(resource.get("status") or "unknown"),
        "indication": _text_from_codeable_concept((resource.get("reasonCode") or [None])[0]) or "unspecified indication",
        "last_changed": _date_only(resource.get("authoredOn")),
        "notes": " ".join(notes).strip(),
    }


def _condition_summary(resource: dict[str, Any]) -> dict[str, Any]:
    onset = resource.get("onsetDateTime") or resource.get("onsetString")
    if isinstance(onset, str) and len(onset) >= 4:
        onset = onset[:4]
    return {
        "code": _extract_loinc(resource.get("code")) or str(resource.get("id") or ""),
        "display": _text_from_codeable_concept(resource.get("code")) or "Condition",
        "status": _status_from_concept(resource),
        "onset": onset,
    }


def _observation_summary(resource: dict[str, Any]) -> dict[str, Any]:
    value, unit = _extract_observation_value(resource)
    category = _text_from_codeable_concept((resource.get("category") or [None])[0]) or "observation"
    return {
        "date": _date_only(resource.get("effectiveDateTime") or resource.get("issued")),
        "category": str(category).lower().replace(" ", "_"),
        "name": _text_from_codeable_concept(resource.get("code")) or "Observation",
        "loinc": _extract_loinc(resource.get("code")),
        "value": value,
        "unit": unit,
        "interpretation": _interpretation(resource),
        "specialties": ["all"],
    }


def _is_synthetic_patient(patient: dict[str, Any]) -> bool:
    patient_id = str(patient.get("id") or "")
    if patient_id.upper().startswith("SYN-"):
        return True
    for identifier in patient.get("identifier", []):
        value = str(identifier.get("value") or "")
        if value.upper().startswith("SYN-"):
            return True
    for tag in patient.get("meta", {}).get("tag", []):
        haystack = " ".join(
            str(tag.get(key) or "") for key in ("code", "display", "text")
        ).lower()
        if any(marker in haystack for marker in SYNTHETIC_MARKERS):
            return True
    for extension in patient.get("extension", []):
        haystack = json.dumps(extension).lower()
        if any(marker in haystack for marker in SYNTHETIC_MARKERS):
            return True
    return False


def fetch_patient_record_from_fhir(patient_id: str, platform_context: dict[str, str | None]) -> dict[str, Any]:
    base_url = platform_context.get("fhir_server_url")
    token = platform_context.get("fhir_access_token")
    if not base_url:
        raise FhirFetchError("No FHIR URL provided in platform context.")

    patient = _fetch_resource(base_url, f"Patient/{patient_id}", token)
    if patient.get("resourceType") != "Patient":
        raise FhirFetchError(f"FHIR Patient/{patient_id} did not return a Patient resource.")
    if not _is_synthetic_patient(patient):
        raise ValueError("FHIR patient context is not marked synthetic or de-identified.")

    condition_bundle = _fetch_bundle(base_url, "Condition", patient_id, token)
    observation_bundle = _fetch_bundle(base_url, "Observation", patient_id, token)
    encounter_bundle = _fetch_bundle(base_url, "Encounter", patient_id, token, {"_sort": "-date", "_count": 20})
    medication_bundle = _fetch_bundle(base_url, "MedicationRequest", patient_id, token)
    document_bundle = _fetch_bundle(base_url, "DocumentReference", patient_id, token, {"_count": 50})
    diagnostic_bundle = _fetch_bundle(base_url, "DiagnosticReport", patient_id, token, {"_count": 50})

    encounters = [_encounter_summary(resource) for resource in _entries(encounter_bundle)]
    documents = [_document_summary(resource) for resource in _entries(document_bundle)] + [
        _document_summary(resource) for resource in _entries(diagnostic_bundle)
    ]
    referral_reason = (
        (encounters[0]["summary"] if encounters else None)
        or (documents[0]["summary"] if documents else None)
        or "Referral packet generated from Prompt Opinion FHIR context."
    )

    return {
        "patient_id": patient_id,
        "source": "fhir",
        "patient": {
            "id": patient_id,
            "synthetic": True,
            "age": _calculate_age(patient.get("birthDate")),
            "sex": str(patient.get("gender") or "unknown"),
            "note": f"Synthetic/de-identified patient loaded from Prompt Opinion FHIR context at {base_url}.",
        },
        "referral_reason": referral_reason,
        "conditions": [_condition_summary(resource) for resource in _entries(condition_bundle)],
        "encounters": encounters,
        "observations": [
            obs for obs in (_observation_summary(resource) for resource in _entries(observation_bundle)) if obs["name"]
        ],
        "medications": [_medication_summary(resource) for resource in _entries(medication_bundle)],
        "documents": documents,
    }
