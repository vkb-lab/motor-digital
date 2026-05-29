from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .agent_registry import AgentDefinition


class ControlDecision(str, Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


@dataclass(frozen=True)
class PolicyResult:
    decision: ControlDecision
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reasons": list(self.reasons),
        }


SENSITIVE_KEY_PARTS = ("token", "secret", "password", "api_key", "access_key")


def find_plaintext_secrets(data: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []

    if isinstance(data, Mapping):
        for key, value in data.items():
            key_text = str(key)
            lowered = key_text.lower()
            path = f"{prefix}.{key_text}" if prefix else key_text

            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                if value not in (None, "", []):
                    if not (isinstance(value, str) and value.startswith("vault://")):
                        findings.append(path)

            findings.extend(find_plaintext_secrets(value, path))

    elif isinstance(data, list):
        for index, item in enumerate(data):
            findings.extend(find_plaintext_secrets(item, f"{prefix}[{index}]"))

    return sorted(set(findings))


class AutonomyPolicy:
    def evaluate(
        self,
        agent: AgentDefinition,
        action: str,
        payload: Mapping[str, Any] | None = None,
    ) -> PolicyResult:
        request_payload = dict(payload or {})
        reasons: list[str] = []

        if action in agent.blocked_actions:
            reasons.append(f"action_blocked_for_agent:{action}")

        if action not in agent.allowed_actions:
            reasons.append(f"action_not_allowed_for_agent:{action}")

        plaintext_secrets = find_plaintext_secrets(request_payload)
        if plaintext_secrets:
            reasons.append("plaintext_secret_blocked:" + ",".join(plaintext_secrets))

        if bool(request_payload.get("official_publish")):
            reasons.append("official_publish_requires_dedicated_level_4_gate")

        if bool(request_payload.get("mass_messaging")):
            reasons.append("mass_messaging_blocked")

        if bool(request_payload.get("browser_automation")):
            reasons.append("browser_automation_blocked")

        if reasons:
            return PolicyResult(ControlDecision.DENY, reasons)

        if agent.requires_supervision:
            return PolicyResult(ControlDecision.REQUIRE_APPROVAL, ["supervision_required"])

        return PolicyResult(ControlDecision.ALLOW, ["policy_allowed"])