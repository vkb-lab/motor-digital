from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AutonomyAuditMonitor:
    def __init__(
        self,
        supervised_queue_path: str | Path = "live/supervised_autonomy_queue/supervised_autonomy_queue.json",
        reports_dir: str | Path = "reports/autonomy_audit_monitor",
        memory_dir: str | Path = "memory/autonomy_audit_monitor",
    ) -> None:
        self.supervised_queue_path = Path(supervised_queue_path)
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"

    def load_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def audit(self) -> dict[str, Any]:
        queue = self.load_list(self.supervised_queue_path)
        violations: list[dict[str, Any]] = []

        for item in queue:
            if item.get("automatic_execution_allowed") is True:
                violations.append({"queue_id": item.get("queue_id"), "reason": "automatic_execution_allowed"})
            if item.get("real_execution_enabled") is True:
                violations.append({"queue_id": item.get("queue_id"), "reason": "real_execution_enabled"})
            if item.get("external_side_effects") not in {"none", None}:
                violations.append({"queue_id": item.get("queue_id"), "reason": "external_side_effects_not_none"})

        report = {
            "ok": len(violations) == 0,
            "checkpoint": "97",
            "name": "Autonomy Audit Monitor",
            "generated_at": utc_now(),
            "status": "audit_clean" if not violations else "audit_violations_detected",
            "summary": {
                "queue_items_total": len(queue),
                "violations_total": len(violations),
                "execution_enabled": False,
                "real_execution_enabled": False,
            },
            "violations": violations,
        }

        self.save_report(report)
        self.event("autonomy_audit_monitor.audit_completed", {"status": report["status"], "violations": len(violations)})
        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_autonomy_audit_monitor.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_autonomy_audit_monitor.md").write_text(
            "# K-Atlas Autonomy Audit Monitor\n\n"
            f"Checkpoint: {report.get('checkpoint')}\n"
            f"Status: {report.get('status')}\n"
            f"Violations: {report.get('summary', {}).get('violations_total')}\n",
            encoding="utf-8",
        )
        return report
