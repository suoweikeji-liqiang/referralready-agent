"""Configuration helpers for ReferralReady."""
from __future__ import annotations
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Literal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("REFERRALREADY_DATA_DIR", PROJECT_ROOT / "data"))
SYNTHETIC_ONLY = os.getenv("REFERRALREADY_SYNTHETIC_ONLY", "true").lower() == "true"


@dataclass(frozen=True)
class ServerRuntimeConfig:
    transport: Literal["stdio", "sse", "streamable-http"]
    host: str
    port: int
    streamable_http_path: str
    stateless_http: bool
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def get_server_runtime_config() -> ServerRuntimeConfig:
    port_value = os.getenv("PORT") or os.getenv("REFERRALREADY_PORT") or "8000"
    return ServerRuntimeConfig(
        transport=os.getenv("REFERRALREADY_MCP_TRANSPORT", "stdio"),  # type: ignore[arg-type]
        host=os.getenv("REFERRALREADY_HOST", "127.0.0.1"),
        port=int(port_value),
        streamable_http_path=os.getenv("REFERRALREADY_STREAMABLE_HTTP_PATH", "/mcp"),
        stateless_http=_env_flag("REFERRALREADY_STATELESS_HTTP", True),
        log_level=os.getenv("REFERRALREADY_LOG_LEVEL", "INFO"),  # type: ignore[arg-type]
    )
