"""Configuration helpers for ReferralReady."""
from __future__ import annotations
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("REFERRALREADY_DATA_DIR", PROJECT_ROOT / "data"))
SYNTHETIC_ONLY = os.getenv("REFERRALREADY_SYNTHETIC_ONLY", "true").lower() == "true"
