from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupervisedAutonomyQueue:
    def __init__(
        self,
        plan_queue_path: str | Path = "live/safe_task_planner/task_plan_queue.json",
        live_dir: str | Path = "live/supervised_autonomy_queue",
        memory_dir: str | Path = "memory/supervised_autonomy_queue",
        reports_dir: str | Path = "reports/supervised_autonomy_queue",
    ) -> None:
        self.plan_queue_path = Path(plan_queue_path)
        self.live_dir = Path(live_dir)
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.queue_path = self.live_dir / "supervised_autonomy_queue.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def load_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_list(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_queue(self) -> dict[str, Any]:
        plans = self.load_list(self.plan_queue_path)
        queue = self.load_list(self.queue_path)
        existing = {item.get("source_plan_id") for item in queue if item.get("source_plan_id")}
        created: list[dict[str, Any]] = []

        for plan in plans:
            plan_id = plan.get("plan_id")
            if not plan_id or plan_id in existing:
                continue

            item = {
                "queue_id": str(uuid4()),
                "source_plan_id": plan_id,
                "created_at": utc_now(),
                "status": "waiting_human_approval",
                "goal": plan.get("goal"),
                "plan_snapshot": plan,
                "automatic_execution_allowed": False,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "required_decision": "approve_or_reject_in_operator_console",
            }
            queue.append(item)
            created.append(item)

        self.save_list(self.queue_path, queue)

        report = {
            "ok": True,
            "checkpoint": "96",
            "name": "Supervised Autonomy Queue",
            "generated_at": utc_now(),
            "status": "queue_built",
            "summary": {
                "plans_total": len(plans),
                "created_items": len(created),
                "queue_total": len(queue),
                "waiting_human_approval": len([item for item in queue if item.get("status") == "waiting_human_approval"]),
                "execution_enabled": False,
                "real_execution_enabled": False,
            },
            "created_items": created,
        }
        self.save_report(report)
        self.event("supervised_autonomy_queue.built", {"created": len(created)})
        return report

    def summary(self) -> dict[str, Any]:
        queue = self.load_list(self.queue_path)
        return {
            "ok": True,
            "checkpoint": "96",
            "name": "Supervised Autonomy Queue",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "queue_total": len(queue),
                "waiting_human_approval": len([item for item in queue if item.get("status") == "waiting_human_approval"]),
                "execution_enabled": False,
                "real_execution_enabled": False,
            },
            "items": queue,
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_supervised_autonomy_queue.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_supervised_autonomy_queue.md").write_text(
            "# K-Atlas Supervised Autonomy Queue\n\n"
            f"Checkpoint: {report.get('checkpoint')}\n"
            f"Status: {report.get('status')}\n",
            encoding="utf-8",
        )
        return report
