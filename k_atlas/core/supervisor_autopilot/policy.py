from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


SAFE_AUTO_APPROVE_ACTIONS = {
    "read_events",
    "summarize_state",
    "generate_report",
    "dry_run",
    "run_smoke_test",
    "prepare_deploy",
    "create_content_package",
    "create_product_structure",
    "generate_app_module",
}

BLOCKED_ACTIONS = {
    "official_publish",
    "mass_messaging",
    "browser_automation",
    "external_api_without_vault",
}

SENSITIVE_KEYS = (
    "token",
    "secret",
    "password",
    "api_key",
    "access_key",
    "credential",
)


@dataclass(frozen=True)
class AutopilotDecision:
    ok: bool
    status: str
    action: str
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def find_sensitive_plaintext(data: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []

    if isinstance(data, Mapping):
        for key, value in data.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text

            if any(part in key_text.lower() for part in SENSITIVE_KEYS):
                if value not in (None, "", []):
                    if not (isinstance(value, str) and value.startswith("vault://")):
                        findings.append(path)

            findings.extend(find_sensitive_plaintext(value, path))

    elif isinstance(data, list):
        for index, item in enumerate(data):
            findings.extend(find_sensitive_plaintext(item, f"{prefix}[{index}]"))

    return sorted(set(findings))


class AutopilotPolicy:
    def evaluate(self, approval_item: Mapping[str, Any]) -> AutopilotDecision:
        task = dict(approval_item.get("task", {}))
        payload = dict(task.get("payload", {}))
        action = str(task.get("action", "")).strip()

        reasons: list[str] = []

        if approval_item.get("status") != "pending_approval":
            reasons.append("not_pending_approval")

        if action in BLOCKED_ACTIONS:
            reasons.append(f"blocked_action:{action}")

        if action not in SAFE_AUTO_APPROVE_ACTIONS:
            reasons.append(f"action_not_auto_approvable:{action}")

        if payload.get("official_publish") is True:
            reasons.append("official_publish_blocked")

        if payload.get("auto_publish") is True:
            reasons.append("auto_publish_blocked")

        if payload.get("mass_messaging") is True:
            reasons.append("mass_messaging_blocked")

        if payload.get("browser_automation") is True:
            reasons.append("browser_automation_blocked")

        if payload.get("external_api_enabled") is True and not payload.get("credential_vault_ref"):
            reasons.append("external_api_requires_credential_vault")

        sensitive = find_sensitive_plaintext(payload)
        if sensitive:
            reasons.append("plaintext_secret_blocked:" + ",".join(sensitive))

        if reasons:
            return AutopilotDecision(
                ok=False,
                status="blocked_or_needs_human_review",
                action=action,
                reasons=reasons,
            )

        return AutopilotDecision(
            ok=True,
            status="auto_approval_allowed",
            action=action,
            reasons=["low_risk_policy_matched"],
        )
