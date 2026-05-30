from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalActionAuditLedger:
    def __init__(
        self,
        route_queue_path: str | Path = "live/local_action_router/action_route_queue.json",
        execution_queue_path: str | Path = "live/local_execution_queue/execution_queue.json",
        memory_dir: str | Path = "memory/local_action_audit_ledger",
        reports_dir: str | Path = "reports/local_action_audit_ledger",
    ) -> None:
        self.route_queue_path = Path(route_queue_path)
        self.execution_queue_path = Path(execution_queue_path)
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.ledger_path = self.memory_dir / "action_audit_ledger.jsonl"

    def load_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def append(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.ledger_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_report(self) -> dict[str, Any]:
        routes = self.load_list(self.route_queue_path)
        executions = self.load_list(self.execution_queue_path)

        report = {
            "ok": True,
            "checkpoint": "87",
            "name": "Local Action Audit Ledger",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "routes_total": len(routes),
                "executions_total": len(executions),
                "waiting_human_execution": len([item for item in executions if item.get("status") == "waiting_human_execution"]),
                "real_execution_enabled": False,
                "automatic_execution_allowed": False,
            },
            "latest_route": routes[-1] if routes else None,
            "latest_execution": executions[-1] if executions else None,
        }

        self.save_report(report)
        self.append("local_action_audit_ledger.report_built", report["summary"])
        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.reports_dir / "latest_local_action_audit_ledger.json"
        md_path = self.reports_dir / "latest_local_action_audit_ledger.md"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {}) or {}
        return "\n".join([
            "# K-Atlas Local Action Audit Ledger",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Routes total: {summary.get('routes_total')}",
            f"Executions total: {summary.get('executions_total')}",
            f"Waiting human execution: {summary.get('waiting_human_execution')}",
        ])
