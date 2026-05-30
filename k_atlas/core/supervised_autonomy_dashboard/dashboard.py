from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from k_atlas.core.autonomy_policy_engine.policy import AutonomyPolicyEngine
from k_atlas.core.safe_task_planner.planner import SafeTaskPlanner
from k_atlas.core.supervised_autonomy_queue.queue import SupervisedAutonomyQueue
from k_atlas.core.autonomy_audit_monitor.monitor import AutonomyAuditMonitor


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupervisedAutonomyDashboard:
    def __init__(
        self,
        reports_dir: str | Path = "reports/supervised_autonomy_dashboard",
        memory_dir: str | Path = "memory/supervised_autonomy_dashboard",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_report(self) -> dict[str, Any]:
        policy = AutonomyPolicyEngine().evaluate({"mode": "observe", "risk_level": "low"})
        planner = SafeTaskPlanner().summary()
        queue = SupervisedAutonomyQueue().summary()
        audit = AutonomyAuditMonitor().audit()

        report = {
            "ok": bool(policy.get("ok")) and bool(audit.get("ok")),
            "checkpoint": "98",
            "name": "Supervised Autonomy Dashboard",
            "generated_at": utc_now(),
            "status": "operational" if policy.get("ok") and audit.get("ok") else "attention_required",
            "summary": {
                "policy_status": policy.get("status"),
                "task_plans_total": planner.get("summary", {}).get("task_plans_total", 0),
                "autonomy_queue_total": queue.get("summary", {}).get("queue_total", 0),
                "audit_status": audit.get("status"),
                "violations_total": audit.get("summary", {}).get("violations_total", 0),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_checkpoint": "99 - MVP Local OS Release Candidate",
            },
            "policy": policy,
            "planner": planner,
            "queue": queue,
            "audit": audit,
        }

        self.save_report(report)
        self.event("supervised_autonomy_dashboard.report_built", {"status": report["status"]})
        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_supervised_autonomy_dashboard.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_supervised_autonomy_dashboard.md").write_text(
            "# K-Atlas Supervised Autonomy Dashboard\n\n"
            f"Checkpoint: {report.get('checkpoint')}\n"
            f"Status: {report.get('status')}\n"
            f"Next: {report.get('summary', {}).get('next_checkpoint')}\n",
            encoding="utf-8",
        )
        return report
