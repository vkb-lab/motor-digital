from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from k_atlas.core.local_api_approval_bridge.bridge import LocalApiApprovalBridge
from k_atlas.core.local_api_audit_ledger.ledger import LocalApiAuditLedger
from k_atlas.core.secure_local_api_runtime.runtime import SecureLocalApiRuntime


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SecureLocalApiDashboard:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/secure_local_api_dashboard",
        memory_dir: str | Path = "memory/secure_local_api_dashboard",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir
        self.memory_dir = self.project_root / memory_dir

    def exists(self, path: str) -> bool:
        return (self.project_root / path).exists()

    def build_report(self) -> dict[str, Any]:
        runtime = SecureLocalApiRuntime(project_root=self.project_root).status()
        approval = LocalApiApprovalBridge(project_root=self.project_root).summary()
        audit = LocalApiAuditLedger(project_root=self.project_root).summary()

        modules = [
            {"checkpoint": "89", "name": "Secure Local API Runtime", "ready": self.exists("k_atlas/core/secure_local_api_runtime")},
            {"checkpoint": "90", "name": "Local API Auth Policy", "ready": self.exists("k_atlas/core/local_api_auth_policy")},
            {"checkpoint": "91", "name": "Local API Approval Bridge", "ready": self.exists("k_atlas/core/local_api_approval_bridge")},
            {"checkpoint": "92", "name": "Local API Audit Ledger", "ready": self.exists("k_atlas/core/local_api_audit_ledger")},
            {"checkpoint": "93", "name": "Secure Local API Dashboard", "ready": self.exists("k_atlas/core/secure_local_api_dashboard")},
        ]

        ready_total = len([item for item in modules if item["ready"]])

        report = {
            "ok": ready_total == len(modules),
            "checkpoint": "93",
            "name": "Secure Local API Dashboard",
            "generated_at": utc_now(),
            "status": "operational" if ready_total == len(modules) else "partial",
            "summary": {
                "modules_total": len(modules),
                "modules_ready": ready_total,
                "api_runtime_status": runtime.get("status"),
                "approval_queue_total": approval.get("summary", {}).get("approval_queue_total", 0),
                "audit_events_total": audit.get("summary", {}).get("audit_events_total", 0),
                "public_access_allowed": False,
                "remote_control_allowed": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_batch": "94-98 supervised autonomy layer",
            },
            "modules": modules,
            "runtime": runtime,
            "approval": approval,
            "audit": audit,
            "guardrails": [
                "dashboard apenas observa",
                "API local somente localhost por padrao",
                "sem porta publica aberta",
                "sem controle remoto real",
                "sem automacao de mouse",
                "sem execucao automatica",
                "toda acao real exige aprovacao humana",
            ],
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_secure_local_api_dashboard.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_secure_local_api_dashboard.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Secure Local API Dashboard",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Modules ready: {summary.get('modules_ready')}/{summary.get('modules_total')}",
            f"- Public access allowed: {summary.get('public_access_allowed')}",
            f"- Remote control allowed: {summary.get('remote_control_allowed')}",
            f"- Real execution enabled: {summary.get('real_execution_enabled')}",
            f"- Next batch: {summary.get('next_batch')}",
        ]
        return "\n".join(lines)
