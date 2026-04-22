"""ReferralReady MCP server.

Run with:
    python -m app.mcp_server
"""
from __future__ import annotations
import argparse

try:
    from mcp.server.fastmcp import Context, FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit("The MCP SDK is not installed. Run `pip install -r requirements.txt` first.") from exc

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import SYNTHETIC_ONLY, ServerRuntimeConfig, get_server_runtime_config
from app.platform_context import PROMPTOPINION_FHIR_EXTENSION_URI
from app.tools import (
    build_referral_packet as _build_referral_packet,
    check_referral_completeness as _check_referral_completeness,
    generate_care_coordination_tasks as _generate_care_coordination_tasks,
    get_medication_context as _get_medication_context,
    get_patient_snapshot as _get_patient_snapshot,
    get_recent_clinical_signals as _get_recent_clinical_signals,
)


PROMPTOPINION_EXPERIMENTAL_CAPABILITIES = {
    PROMPTOPINION_FHIR_EXTENSION_URI: {}
}


def _attach_promptopinion_capabilities(mcp: FastMCP) -> None:
    original_create_initialization_options = mcp._mcp_server.create_initialization_options

    def create_initialization_options(notification_options=None, experimental_capabilities=None):
        merged_capabilities = dict(PROMPTOPINION_EXPERIMENTAL_CAPABILITIES)
        if experimental_capabilities:
            merged_capabilities.update(experimental_capabilities)
        return original_create_initialization_options(
            notification_options=notification_options,
            experimental_capabilities=merged_capabilities,
        )

    mcp._mcp_server.create_initialization_options = create_initialization_options


def build_mcp_server(config: ServerRuntimeConfig | None = None) -> FastMCP:
    runtime = config or get_server_runtime_config()
    mcp = FastMCP(
        "ReferralReady Agent",
        instructions=(
            "ReferralReady assembles specialist-ready referral packets from synthetic FHIR-like data. "
            "It does not diagnose, recommend treatment, or process real PHI. "
            "If Prompt Opinion provides FHIR context, the server can use patientId, fhirUrl, and fhirToken "
            "to load synthetic or de-identified patient data from a FHIR server."
        ),
        host=runtime.host,
        port=runtime.port,
        streamable_http_path=runtime.streamable_http_path,
        stateless_http=runtime.stateless_http,
        log_level=runtime.log_level,
    )
    _attach_promptopinion_capabilities(mcp)

    @mcp.custom_route("/healthz", methods=["GET"], include_in_schema=False)
    async def healthz(_: Request) -> Response:
        return JSONResponse(
            {
                "status": "ok",
                "service": "ReferralReady Agent",
                "synthetic_only": SYNTHETIC_ONLY,
                "streamable_http_path": runtime.streamable_http_path,
                "stateless_http": runtime.stateless_http,
                "promptopinion_fhir_extension": PROMPTOPINION_FHIR_EXTENSION_URI,
            }
        )

    @mcp.tool()
    def get_patient_snapshot(patient_id: str | None = None, ctx: Context | None = None) -> dict:
        """Return demographics, active conditions, recent encounters, and record counts for a synthetic patient."""
        return _get_patient_snapshot(patient_id, ctx)

    @mcp.tool()
    def get_recent_clinical_signals(
        patient_id: str | None = None,
        specialty: str = "",
        lookback_days: int = 180,
        ctx: Context | None = None,
    ) -> dict:
        """Return specialty-relevant labs, vitals, and diagnostic signals for a synthetic patient."""
        return _get_recent_clinical_signals(patient_id, specialty, lookback_days, ctx)

    @mcp.tool()
    def get_medication_context(patient_id: str | None = None, ctx: Context | None = None) -> dict:
        """Return active medications, recent changes, and medication review gaps."""
        return _get_medication_context(patient_id, ctx)

    @mcp.tool()
    def check_referral_completeness(
        patient_id: str | None = None,
        specialty: str = "",
        ctx: Context | None = None,
    ) -> dict:
        """Check specialty-specific referral completeness and identify missing information."""
        return _check_referral_completeness(patient_id, specialty, ctx)

    @mcp.tool()
    def build_referral_packet(
        patient_id: str | None = None,
        specialty: str = "",
        referral_reason: str | None = None,
        ctx: Context | None = None,
    ) -> dict:
        """Build a specialist-ready referral packet in Markdown for clinician review."""
        return _build_referral_packet(patient_id, specialty, referral_reason, ctx)

    @mcp.tool()
    def generate_care_coordination_tasks(
        patient_id: str | None = None,
        specialty: str = "",
        ctx: Context | None = None,
    ) -> dict:
        """Generate care coordinator tasks from missing referral checklist items."""
        return _generate_care_coordination_tasks(patient_id, specialty, ctx)

    return mcp


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    defaults = get_server_runtime_config()
    parser = argparse.ArgumentParser(description="Run the ReferralReady MCP server")
    parser.add_argument(
        "--transport",
        default=defaults.transport,
        choices=["stdio", "sse", "streamable-http"],
        help="Transport protocol to run",
    )
    parser.add_argument("--host", default=defaults.host, help="Bind host for HTTP transports")
    parser.add_argument("--port", default=defaults.port, type=int, help="Bind port for HTTP transports")
    parser.add_argument(
        "--streamable-http-path",
        default=defaults.streamable_http_path,
        help="HTTP path for streamable MCP transport",
    )
    parser.add_argument(
        "--stateless-http",
        dest="stateless_http",
        action="store_true",
        default=defaults.stateless_http,
        help="Use stateless HTTP mode to tolerate clients that do not persist MCP session IDs",
    )
    parser.add_argument(
        "--stateful-http",
        dest="stateless_http",
        action="store_false",
        help="Use stateful HTTP mode with MCP session IDs",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = ServerRuntimeConfig(
        transport=args.transport,
        host=args.host,
        port=args.port,
        streamable_http_path=args.streamable_http_path,
        stateless_http=args.stateless_http,
        log_level=get_server_runtime_config().log_level,
    )
    build_mcp_server(config).run(transport=config.transport)
    return 0


mcp = build_mcp_server()


if __name__ == "__main__":
    raise SystemExit(main())
