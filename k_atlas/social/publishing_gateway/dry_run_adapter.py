from __future__ import annotations

from typing import Any, Mapping

from .audit_log import AuditLog, sanitize_for_audit
from .permission_model import PermissionDecision, evaluate_permission


class DryRunAdapter:
    def __init__(self, audit_log: AuditLog | None = None) -> None:
        self.audit_log = audit_log or AuditLog()

    def publish(self, payload: Mapping[str, Any], actor: str = "k_social_operator") -> dict[str, Any]:
        channel = str(payload.get("channel", "dry_run"))
        autonomy_level = payload.get("autonomy_level", "level_0_strategy")
        decision, reasons = evaluate_permission(channel, autonomy_level, payload)

        if decision == PermissionDecision.DENY:
            status = "blocked"
            result = {
                "ok": False,
                "status": status,
                "adapter": "dry_run_adapter",
                "side_effects": "none",
                "reasons": reasons,
                "preview": sanitize_for_audit(payload),
            }
        else:
            status = "dry_run_ready"
            result = {
                "ok": True,
                "status": status,
                "adapter": "dry_run_adapter",
                "side_effects": "none",
                "reasons": reasons,
                "preview": sanitize_for_audit(payload),
            }

        self.audit_log.write_event(
            action="dry_run_adapter.publish",
            status=status,
            actor=actor,
            payload=result,
            reasons=reasons,
        )

        return result