from __future__ import annotations

from typing import Any, Mapping


SAFE_ACTIONS = {
    "observe_status",
    "generate_report",
    "create_local_mission",
    "queue_for_human_approval",
    "run_dry_run",
    "request_feedback",
}

SENSITIVE_ACTIONS = {
    "apply_local_change",
    "rollback_local_change",
    "start_local_service",
    "stop_local_service",
    "open_lan_access",
}

BLOCKED_ACTIONS = {
    "publish_external",
    "send_message",
    "deploy_external",
    "control_mouse",
    "control_keyboard",
    "capture_password",
    "expose_public_port",
    "external_api_call",
}

BLOCKED_FLAGS = [
    "auto_execute",
    "real_execution_enabled",
    "external_api_enabled",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
    "keyboard_automation",
    "public_network_enabled",
]

DEFAULT_AGENT_PERMISSIONS = {
    "operator": {
        "can_observe": True,
        "can_propose": True,
        "can_plan": True,
        "can_request_apply": True,
        "can_apply_without_human": False,
        "can_use_external_api": False,
    },
    "mission_generator": {
        "can_observe": True,
        "can_propose": True,
        "can_plan": True,
        "can_request_apply": False,
        "can_apply_without_human": False,
        "can_use_external_api": False,
    },
    "execution_agent": {
        "can_observe": True,
        "can_propose": False,
        "can_plan": False,
        "can_request_apply": True,
        "can_apply_without_human": False,
        "can_use_external_api": False,
    },
    "remote_assist_agent": {
        "can_observe": True,
        "can_propose": True,
        "can_plan": True,
        "can_request_apply": False,
        "can_apply_without_human": False,
        "can_use_external_api": False,
    },
}


def normalize_action(value: Any) -> str:
    return str(value or "").strip().lower()


def validate_brain_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []
    warnings: list[str] = []

    agent = str(data.get("agent", "operator")).strip() or "operator"
    action = normalize_action(data.get("action"))

    if not action:
        reasons.append("action_required")

    if action in BLOCKED_ACTIONS:
        reasons.append(f"blocked_action:{action}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    permissions = DEFAULT_AGENT_PERMISSIONS.get(agent)
    if permissions is None:
        warnings.append(f"unknown_agent:{agent}")
        permissions = DEFAULT_AGENT_PERMISSIONS["operator"]

    requires_human = True

    if action in SAFE_ACTIONS:
        requires_human = False

    if action in SENSITIVE_ACTIONS:
        requires_human = True

    if action == "apply_local_change" and permissions.get("can_request_apply") is not True:
        reasons.append("agent_cannot_request_apply")

    if data.get("human_approved") is True and action in BLOCKED_ACTIONS:
        reasons.append("human_approval_cannot_override_blocked_action")

    decision_status = "blocked"
    if not reasons and requires_human:
        decision_status = "requires_human_approval"
    if not reasons and not requires_human:
        decision_status = "approved_safe"

    return {
        "ok": len(reasons) == 0,
        "status": decision_status,
        "agent": agent,
        "action": action,
        "requires_human_approval": requires_human,
        "reasons": reasons or [decision_status],
        "warnings": warnings,
        "permissions": permissions,
        "automatic_execution_allowed": False,
        "real_execution_enabled": False,
        "external_api_enabled": False,
    }
