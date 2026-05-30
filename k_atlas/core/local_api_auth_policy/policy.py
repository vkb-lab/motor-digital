from __future__ import annotations

from typing import Any, Mapping


ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
BLOCKED_HOSTS = {"0.0.0.0", "::", "*"}
BLOCKED_FLAGS = [
    "auto_execute",
    "real_execution_enabled",
    "external_api_enabled",
    "external_public_access",
    "remote_control_enabled",
    "mouse_automation",
    "browser_automation",
    "auto_publish",
    "auto_send",
    "auto_deploy",
]


def validate_local_api_runtime_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    host = str(data.get("bind_host", "127.0.0.1")).strip()
    port = int(data.get("port", 8787) or 8787)

    if host in BLOCKED_HOSTS:
        reasons.append(f"public_bind_host_blocked:{host}")

    if host not in ALLOWED_HOSTS:
        reasons.append(f"bind_host_not_allowed:{host}")

    if port < 1024 or port > 65535:
        reasons.append(f"port_out_of_range:{port}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "local_api_runtime_allowed" if not reasons else "local_api_runtime_blocked",
        "bind_host": host,
        "port": port,
        "reasons": reasons or ["local_api_runtime_allowed"],
        "public_access_allowed": False,
        "remote_control_allowed": False,
        "human_approval_required": True,
    }
