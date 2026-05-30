from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from k_atlas.core.local_action_contracts.contracts import LocalActionContractRegistry
from k_atlas.core.local_action_router.router import LocalActionRouter
from k_atlas.core.local_execution_queue.queue import LocalExecutionQueue
from k_atlas.core.local_action_audit_ledger.ledger import LocalActionAuditLedger


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AssistedExecutionDashboard:
    def __init__(self, reports_dir: str | Path = "reports/assisted_execution_dashboard") -> None:
        self.reports_dir = Path(reports_dir)

    def build_report(self) -> dict[str, Any]:
        contracts = LocalActionContractRegistry().summary()
        router = LocalActionRouter().summary()
        queue = LocalExecutionQueue().summary()
        ledger = LocalActionAuditLedger().build_report()

        report = {
            "ok": True,
            "checkpoint": "88",
            "name": "Assisted Execution Dashboard",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "contracts_total": contracts.get("summary", {}).get("contracts_total", 0),
                "routes_total": router.get("summary", {}).get("routes_total", 0),
                "execution_queue_total": queue.get("summary", {}).get("queued_total", 0),
                "waiting_human_execution": queue.get("summary", {}).get("waiting_human_execution", 0),
                "real_execution_enabled": False,
                "automatic_execution_allowed": False,
                "external_side_effects": "local_files_only",
            },
            "contracts": contracts,
            "router": router,
            "execution_queue": queue,
            "ledger": ledger,
            "guardrails": [
                "dashboard nao executa acoes automaticamente",
                "toda acao real exige humano",
                "sem controle remoto",
                "sem mouse automatico",
                "sem api externa",
                "sem deploy automatico",
            ],
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.reports_dir / "latest_assisted_execution_dashboard.json"
        md_path = self.reports_dir / "latest_assisted_execution_dashboard.md"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {}) or {}
        lines = [
            "# K-Atlas Assisted Execution Dashboard",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Contracts: {summary.get('contracts_total')}",
            f"- Routes: {summary.get('routes_total')}",
            f"- Execution queue: {summary.get('execution_queue_total')}",
            f"- Waiting human execution: {summary.get('waiting_human_execution')}",
            f"- Real execution enabled: {summary.get('real_execution_enabled')}",
            "",
            "## Guardrails",
            "",
        ]
        for item in report.get("guardrails", []):
            lines.append(f"- {item}")
        return "\n".join(lines)
