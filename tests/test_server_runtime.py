from starlette.testclient import TestClient

from mcp.server.fastmcp import Context
from mcp.server.fastmcp.server import RequestContext

from app.config import get_server_runtime_config
from app.mcp_server import build_mcp_server
from app.tools import get_patient_snapshot


class _DummyRequest:
    def __init__(self, headers: dict[str, str]):
        self.headers = headers


def _make_context(headers: dict[str, str]) -> Context:
    request_context = RequestContext(
        request_id="test-request",
        meta=None,
        session=object(),
        lifespan_context=None,
        request=_DummyRequest(headers),
    )
    return Context(request_context=request_context, fastmcp=None)


def test_patient_snapshot_can_resolve_patient_id_from_prompt_opinion_header():
    snapshot = get_patient_snapshot(None, _make_context({"x-patient-id": "SYN-CKD-001"}))

    assert snapshot["patient_id"] == "SYN-CKD-001"


def test_patient_snapshot_accepts_platform_header_fallback_alias():
    snapshot = get_patient_snapshot(None, _make_context({"x-inc-sd": "SYN-HF-002"}))

    assert snapshot["patient_id"] == "SYN-HF-002"


def test_server_runtime_config_reads_publish_friendly_env(monkeypatch):
    monkeypatch.setenv("REFERRALREADY_MCP_TRANSPORT", "streamable-http")
    monkeypatch.setenv("REFERRALREADY_HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "9001")
    monkeypatch.setenv("REFERRALREADY_STATELESS_HTTP", "true")
    monkeypatch.setenv("REFERRALREADY_STREAMABLE_HTTP_PATH", "/agent/mcp")

    config = get_server_runtime_config()

    assert config.transport == "streamable-http"
    assert config.host == "0.0.0.0"
    assert config.port == 9001
    assert config.stateless_http is True
    assert config.streamable_http_path == "/agent/mcp"


def test_streamable_http_app_exposes_healthz_route():
    server = build_mcp_server()

    with TestClient(server.streamable_http_app()) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["synthetic_only"] is True
