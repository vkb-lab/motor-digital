from __future__ import annotations

from typing import Any, Mapping


ALLOWED_SOURCE = {
    "operator_mission_queue",
    "manual_payload",
}

ALLOWED_TASK_STATUS = {
    "intake_ready",
    "queued_for_planning",
    "blocked_by_policy",
}

BLOCKED_FLAGS = [
    "live_call",
    "real_execute",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "mass_messaging",
    "browser_automation",
    "bypass_human_approval",
]

BLOCKED_KEYS = [
    "token",
    "api_key",
    "secret",
    "password",
    "client_secret",
    "access_token",
    "refresh_token",
]


def validate_command_center_intake_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    source = str(data.get("source", "operator_mission_queue")).strip()

    if source not in ALLOWED_SOURCE:
        reasons.append(f"source_not_allowed:{source}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    tasks = data.get("tasks", [])

    if tasks and not isinstance(tasks, list):
        reasons.append("tasks_must_be_list")

    if isinstance(tasks, list):
        for index, task in enumerate(tasks):
            if not isinstance(task, dict):
                reasons.append(f"task_{index}_must_be_object")
                continue

            objective = str(task.get("objective", "")).strip()
            if not objective:
                reasons.append(f"task_{index}_objective_required")

            for flag in BLOCKED_FLAGS:
                if task.get(flag) is True:
                    reasons.append(f"task_{index}_{flag}_blocked")

            for key in BLOCKED_KEYS:
                if task.get(key):
                    reasons.append(f"task_{index}_plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "command_center_intake_payload_allowed" if not reasons else "command_center_intake_payload_blocked",
        "reasons": reasons or ["command_center_intake_payload_allowed"],
    }
