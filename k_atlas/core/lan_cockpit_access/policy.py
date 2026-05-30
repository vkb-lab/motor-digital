from __future__ import annotations

from typing import Any, Mapping


def validate_lan_access_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    mode = data.get("mode", "readiness")
    if mode not in {"readiness", "plan"}:
        reasons.append(f"invalid_mode:{mode}")

    if data.get("public_exposure") is True:
        reasons.append("public_exposure_blocked")

    if data.get("open_firewall") is True:
        reasons.append("open_firewall_blocked")

    if data.get("start_server") is True and data.get("human_approved_lan") is not True:
        reasons.append("start_server_requires_human_approval")

    return {
        "ok": len(reasons) == 0,
        "status": "lan_access_request_allowed" if not reasons else "lan_access_request_blocked",
        "reasons": reasons or ["lan_access_request_allowed"],
    }
