from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_render_blueprint_exists_with_expected_free_web_service_settings():
    blueprint_path = PROJECT_ROOT / "render.yaml"

    assert blueprint_path.exists()

    text = blueprint_path.read_text(encoding="utf-8")
    assert "type: web" in text
    assert "runtime: python" in text
    assert "plan: free" in text
    assert "buildCommand: pip install -r requirements.txt" in text
    assert (
        "startCommand: python -m app.mcp_server --transport streamable-http --host 0.0.0.0 --port $PORT --stateless-http"
        in text
    )
    assert "healthCheckPath: /healthz" in text
