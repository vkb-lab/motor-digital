from __future__ import annotations

from typing import Any, Mapping

ALLOWED_MODES = {"observe", "lan_readiness", "remote_readiness", "tunnel_proposal"}
ALLOWED_NETWORK_SCOPES = {"local_only", "lan_only", "tunnel_proposal_only"}

BLOCKED_TRUE_FLAGS = [
    "public_exposure_enabled",
    "remote_control_enabled",
    "unattended_access_enabled",
    "mouse_automation",
    "keyboard_automation",
    "credential_capture_enabled",
    "password_storage_enabled",
    "auto_execute",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "external_api_enabled",
]


def validate_remote_assist_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    mode = str(data.get("mode", "observe"))
    network_scope = str(data.get("network_scope", "local_only"))

    if mode not in ALLOWED_MODES:
        reasons.append(f"invalid_mode:{mode}")

    if network_scope not in ALLOWED_NETWORK_SCOPES:
        reasons.append(f"invalid_network_scope:{network_scope}")

    if mode == "tunnel_proposal" and network_scope != "tunnel_proposal_only":
        reasons.append("tunnel_proposal_requires_tunnel_proposal_only_scope")

    if network_scope == "tunnel_proposal_only" and data.get("human_approved") is not True:
        reasons.append("human_approval_required_for_tunnel_proposal")

    for flag in BLOCKED_TRUE_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "remote_assist_request_allowed" if not reasons else "remote_assist_request_blocked",
        "mode": mode,
        "network_scope": network_scope,
        "reasons": reasons or ["remote_assist_request_allowed"],
        "remote_control_allowed": False,
        "public_exposure_allowed": False,
        "unattended_access_allowed": False,
    }
