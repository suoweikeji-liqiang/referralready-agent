"""Helpers for reading Prompt Opinion / SHARP-style request context."""
from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from mcp.server.fastmcp import Context


PROMPTOPINION_FHIR_EXTENSION_URI = "https://app.promptopinion.ai/schemas/a2a/v1/fhir-context"
PATIENT_ID_HEADER_CANDIDATES = (
    "x-patient-id",
    "patient-id",
    "x-inc-sd",
)
FHIR_SERVER_HEADER_CANDIDATES = ("x-fhir-server-url",)
FHIR_ACCESS_TOKEN_HEADER_CANDIDATES = ("x-fhir-access-token",)
FHIR_CONTEXT_HEADER_CANDIDATES = (
    "x-promptopinion-fhir-context",
    "x-fhir-context",
    "x-inc-sd",
)


def _normalize_headers(headers: Mapping[str, Any] | None) -> dict[str, str]:
    if headers is None:
        return {}
    return {str(key).lower(): str(value) for key, value in headers.items()}


def request_headers_from_context(ctx: Context | None) -> dict[str, str]:
    if ctx is None:
        return {}
    try:
        request = ctx.request_context.request
    except ValueError:
        return {}
    if request is None or not hasattr(request, "headers"):
        return {}
    return _normalize_headers(request.headers)


def _first_present(headers: dict[str, str], candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        value = headers.get(candidate)
        if value:
            return value
    return None


def _try_extract_patient_id_from_json(value: str) -> str | None:
    if not value:
        return None
    stripped = value.strip()
    if not stripped.startswith("{"):
        return None
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    for key in ("patient_id", "patientId", "x-patient-id", "patient"):
        candidate = payload.get(key)
        if candidate:
            return str(candidate)
    return None


def _try_extract_fhir_payload(value: str) -> dict[str, str | None] | None:
    if not value:
        return None
    stripped = value.strip()
    if not stripped.startswith("{"):
        return None
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    if not any(key in payload for key in ("fhirUrl", "fhirToken", "patientId")):
        return None
    return {
        "fhir_server_url": str(payload.get("fhirUrl")) if payload.get("fhirUrl") else None,
        "fhir_access_token": str(payload.get("fhirToken")) if payload.get("fhirToken") else None,
        "patient_id": str(payload.get("patientId")) if payload.get("patientId") else None,
        "fhir_refresh_token": str(payload.get("fhirRefreshToken")) if payload.get("fhirRefreshToken") else None,
        "fhir_refresh_token_url": str(payload.get("fhirRefreshTokenUrl")) if payload.get("fhirRefreshTokenUrl") else None,
    }


def extract_platform_context(ctx: Context | None) -> dict[str, str | None]:
    headers = request_headers_from_context(ctx)
    fhir_payload = None
    for header in FHIR_CONTEXT_HEADER_CANDIDATES:
        if header in headers:
            fhir_payload = _try_extract_fhir_payload(headers[header])
            if fhir_payload:
                break
    patient_header = _first_present(headers, PATIENT_ID_HEADER_CANDIDATES)
    patient_id = patient_header or (fhir_payload["patient_id"] if fhir_payload else None)
    if patient_id is None and "x-inc-sd" in headers:
        patient_id = _try_extract_patient_id_from_json(headers["x-inc-sd"])
    elif patient_id is not None and patient_id.startswith("{"):
        patient_id = _try_extract_patient_id_from_json(patient_id) or patient_id
    return {
        "patient_id": patient_id,
        "fhir_server_url": (fhir_payload["fhir_server_url"] if fhir_payload else None)
        or _first_present(headers, FHIR_SERVER_HEADER_CANDIDATES),
        "fhir_access_token": (fhir_payload["fhir_access_token"] if fhir_payload else None)
        or _first_present(headers, FHIR_ACCESS_TOKEN_HEADER_CANDIDATES),
        "fhir_refresh_token": fhir_payload["fhir_refresh_token"] if fhir_payload else None,
        "fhir_refresh_token_url": fhir_payload["fhir_refresh_token_url"] if fhir_payload else None,
    }


def resolve_patient_id(patient_id: str | None, ctx: Context | None) -> str:
    if patient_id:
        return patient_id
    platform_context = extract_platform_context(ctx)
    resolved = platform_context["patient_id"]
    if resolved:
        return resolved
    raise ValueError("patient_id is required unless Prompt Opinion provides it via request headers.")
