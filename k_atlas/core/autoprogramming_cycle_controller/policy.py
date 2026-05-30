from __future__ import annotations

BLOCKED_FLAGS = [
    "auto_execute", "real_execution_enabled", "external_api_enabled",
    "auto_publish", "auto_send", "auto_deploy",
    "browser_automation", "mouse_automation",
]

def validate_cycle_control_request(payload: dict) -> dict:
    data = dict(payload or {})
    reasons = []
    mode = str(data.get("mode", "recommend"))
    if mode not in {"observe", "plan", "recommend"}:
        reasons.append(f"invalid_mode:{mode}")
    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")
    return {
        "ok": len(reasons) == 0,
        "status": "cycle_control_request_allowed" if not reasons else "cycle_control_request_blocked",
        "mode": mode,
        "reasons": reasons or ["cycle_control_request_allowed"],
    }
