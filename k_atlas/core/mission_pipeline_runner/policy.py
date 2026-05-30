from __future__ import annotations

from typing import Any, Mapping


VALID_MODES = {"observe", "dry_run", "supervised"}

BLOCKED_FLAGS = [
    "auto_execute",
    "real_execution_enabled",
    "external_api_enabled",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
]


def validate_pipeline_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    mode = data.get("mode", "dry_run")
    if mode not in VALID_MODES:
        reasons.append(f"invalid_mode:{mode}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    if data.get("install") is True and data.get("human_approved") is not True:
        reasons.append("human_approval_required_for_install")

    if data.get("commit") is True and data.get("human_approved") is not True:
        reasons.append("human_approval_required_for_commit")

    return {
        "ok": len(reasons) == 0,
        "status": "pipeline_request_allowed" if not reasons else "pipeline_request_blocked",
        "reasons": reasons or ["pipeline_request_allowed"],
    }
