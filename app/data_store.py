"""Data loading utilities for synthetic FHIR-like records and checklists."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from typing import Any
from app.config import DATA_DIR
from app.safety import assert_synthetic_patient, validate_patient_record

class DataNotFoundError(FileNotFoundError):
    """Raised when a requested synthetic patient or checklist does not exist."""

@lru_cache(maxsize=64)
def _json_load(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def normalize_specialty(specialty: str) -> str:
    cleaned = specialty.strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {"renal": "nephrology", "kidney": "nephrology", "cardiac": "cardiology", "heart": "cardiology", "diabetes": "endocrinology", "endocrine": "endocrinology"}
    return aliases.get(cleaned, cleaned)

@lru_cache(maxsize=32)
def load_patient(patient_id: str) -> dict[str, Any]:
    path = DATA_DIR / "synthetic_fhir" / f"{patient_id}.json"
    if not path.exists():
        raise DataNotFoundError(f"Unknown patient_id: {patient_id}")
    record = _json_load(str(path))
    assert_synthetic_patient(record)
    validate_patient_record(record)
    return record

@lru_cache(maxsize=16)
def load_checklist(specialty: str) -> dict[str, Any]:
    normalized = normalize_specialty(specialty)
    path = DATA_DIR / "checklists" / f"{normalized}.json"
    if not path.exists():
        raise DataNotFoundError(f"Unknown specialty: {specialty}")
    return _json_load(str(path))

def list_patient_ids() -> list[str]:
    return sorted(path.stem for path in (DATA_DIR / "synthetic_fhir").glob("*.json"))

def list_specialties() -> list[str]:
    return sorted(path.stem for path in (DATA_DIR / "checklists").glob("*.json"))
