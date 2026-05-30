from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.autonomy_policy_engine.policy import validate_autonomy_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SafeTaskPlanner:
    def __init__(
        self,
        live_dir: str | Path = "live/safe_task_planner",
        memory_dir: str | Path = "memory/safe_task_planner",
        reports_dir: str | Path = "reports/safe_task_planner",
    ) -> None:
        self.live_dir = Path(live_dir)
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.plan_queue_path = self.live_dir / "task_plan_queue.json"
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

    def create_plan(self, goal: str = "prepare_next_safe_local_mission") -> dict[str, Any]:
        policy = validate_autonomy_request({
            "mode": "plan",
            "risk_level": "low",
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
            "remote_control_enabled": False,
        })

        plan = {
            "ok": policy["ok"],
            "checkpoint": "95",
            "name": "Safe Task Planner",
            "plan_id": str(uuid4()),
            "created_at": utc_now(),
            "status": "waiting_operator_review" if policy["ok"] else "blocked_by_policy",
            "goal": goal,
            "policy": policy,
            "steps": [
                {"order": 1, "component": "local_control_plane", "action": "observe_state", "executes": False},
                {"order": 2, "component": "mission_pack_generator", "action": "prepare_candidate_mission", "executes": False},
                {"order": 3, "component": "operator_approval_console", "action": "request_human_approval", "executes": False},
                {"order": 4, "component": "local_mission_installer", "action": "install_only_after_approval", "executes": False},
            ],
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
        }

        queue = self.load_list(self.plan_queue_path)
        queue.append(plan)
        self.save_list(self.plan_queue_path, queue)
        self.save_report(plan)
        self.event("safe_task_planner.plan_created", {"plan_id": plan["plan_id"], "status": plan["status"]})
        return plan

    def summary(self) -> dict[str, Any]:
        queue = self.load_list(self.plan_queue_path)
        return {
            "ok": True,
            "checkpoint": "95",
            "name": "Safe Task Planner",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "task_plans_total": len(queue),
                "waiting_operator_review": len([item for item in queue if item.get("status") == "waiting_operator_review"]),
                "execution_enabled": False,
                "real_execution_enabled": False,
            },
            "latest_plan": queue[-1] if queue else None,
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_safe_task_planner.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_safe_task_planner.md").write_text(
            "# K-Atlas Safe Task Planner\n\n"
            f"Checkpoint: {report.get('checkpoint')}\n"
            f"Status: {report.get('status')}\n"
            f"Goal: {report.get('goal')}\n",
            encoding="utf-8",
        )
        return report
