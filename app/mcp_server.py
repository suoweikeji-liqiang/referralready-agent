"""ReferralReady MCP server.

Run with:
    python -m app.mcp_server
"""
from __future__ import annotations
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit("The MCP SDK is not installed. Run `pip install -r requirements.txt` first.") from exc

from app.tools import (
    build_referral_packet as _build_referral_packet,
    check_referral_completeness as _check_referral_completeness,
    generate_care_coordination_tasks as _generate_care_coordination_tasks,
    get_medication_context as _get_medication_context,
    get_patient_snapshot as _get_patient_snapshot,
    get_recent_clinical_signals as _get_recent_clinical_signals,
)

mcp = FastMCP("ReferralReady Agent")

@mcp.tool()
def get_patient_snapshot(patient_id: str) -> dict:
    """Return demographics, active conditions, recent encounters, and record counts for a synthetic patient."""
    return _get_patient_snapshot(patient_id)

@mcp.tool()
def get_recent_clinical_signals(patient_id: str, specialty: str, lookback_days: int = 180) -> dict:
    """Return specialty-relevant labs, vitals, and diagnostic signals for a synthetic patient."""
    return _get_recent_clinical_signals(patient_id, specialty, lookback_days)

@mcp.tool()
def get_medication_context(patient_id: str) -> dict:
    """Return active medications, recent changes, and medication review gaps."""
    return _get_medication_context(patient_id)

@mcp.tool()
def check_referral_completeness(patient_id: str, specialty: str) -> dict:
    """Check specialty-specific referral completeness and identify missing information."""
    return _check_referral_completeness(patient_id, specialty)

@mcp.tool()
def build_referral_packet(patient_id: str, specialty: str, referral_reason: str | None = None) -> dict:
    """Build a specialist-ready referral packet in Markdown for clinician review."""
    return _build_referral_packet(patient_id, specialty, referral_reason)

@mcp.tool()
def generate_care_coordination_tasks(patient_id: str, specialty: str) -> dict:
    """Generate care coordinator tasks from missing referral checklist items."""
    return _generate_care_coordination_tasks(patient_id, specialty)

if __name__ == "__main__":
    mcp.run()
