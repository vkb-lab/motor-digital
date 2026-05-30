from __future__ import annotations

from typing import Any, Mapping


ALLOWED_ADAPTERS = {
    "instagram_graph_publish",
    "instagram_graph_insights",
    "whatsapp_cloud_send",
    "render_deploy",
    "github_release",
    "openai_live",
    "google_vertex_live",
    "google_ai_live",
}

ALLOWED_RISK = {
    "low",
    "medium",
    "high",
    "critical",
}

BLOCKED_KEYS = [
    "token",
    "api_key",
    "secret",
    "password",
    "client_secret",
    "access_token",
    "refresh_token",
]

BLOCKED_FLAGS = [
    "enabled",
    "live_call",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "mass_messaging",
    "browser_automation",
    "bypass_human_approval",
]


def validate_live_adapter_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(contract or {})
    reasons: list[str] = []

    adapter_id = str(data.get("adapter_id", "")).strip()
    risk_level = str(data.get("risk_level", "")).strip()
    env_vars = data.get("env_vars", [])

    if adapter_id not in ALLOWED_ADAPTERS:
        reasons.append(f"adapter_not_allowed:{adapter_id}")

    if risk_level not in ALLOWED_RISK:
        reasons.append(f"risk_level_not_allowed:{risk_level}")

    if not isinstance(env_vars, list):
        reasons.append("env_vars_must_be_list")
    else:
        for item in env_vars:
            if not isinstance(item, str):
                reasons.append("env_var_name_must_be_string")
                continue
            if "=" in item:
                reasons.append("env_var_must_not_contain_value")
            if not item.strip() or item.strip() != item:
                reasons.append("env_var_invalid_name")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    if data.get("requires_human_approval") is not True:
        reasons.append("requires_human_approval_required")

    if data.get("requires_approval_gate") is not True:
        reasons.append("requires_approval_gate_required")

    if data.get("real_execution_enabled") is True:
        reasons.append("real_execution_enabled_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "live_adapter_contract_allowed" if not reasons else "live_adapter_contract_blocked",
        "reasons": reasons or ["live_adapter_contract_allowed"],
    }
