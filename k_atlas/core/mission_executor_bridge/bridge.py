from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.command_center.center import CommandCenter
from k_atlas.core.command_center.policy import validate_command_payload

from .policy import validate_execution_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MissionExecutorBridge:
    def __init__(
        self,
        reports_dir: str | Path = "reports/mission_executor_bridge",
        memory_dir: str | Path = "memory/mission_executor_bridge",
        command_center: CommandCenter | None = None,
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"
        self.command_center = command_center or CommandCenter()

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }

        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def load_latest_plan(self, path: str | Path = "reports/mission_planner/latest_mission_plan.json") -> dict[str, Any]:
        target = Path(path)

        if not target.exists():
            return {
                "ok": False,
                "status": "latest_mission_plan_missing",
                "path": str(target).replace("\\", "/"),
                "tasks": [],
            }

        data = json.loads(target.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            return {
                "ok": False,
                "status": "latest_mission_plan_invalid",
                "path": str(target).replace("\\", "/"),
                "tasks": [],
            }

        return data

    def execute_plan(
        self,
        plan: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = {
            "dry_run": True,
            "max_tasks": 10,
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
            **dict(payload or {}),
        }

        validation = validate_execution_payload(data)
        execution_id = str(uuid4())
        started_at = utc_now()

        mission_plan = dict(plan or self.load_latest_plan())

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "45",
                "name": "Mission Executor Bridge",
                "execution_id": execution_id,
                "status": "blocked_by_policy",
                "started_at": started_at,
                "finished_at": utc_now(),
                "validation": validation,
                "payload": data,
                "plan": mission_plan,
                "executed": [],
            }
            self.save_report(report)
            return report

        if not mission_plan.get("ok", False):
            report = {
                "ok": False,
                "checkpoint": "45",
                "name": "Mission Executor Bridge",
                "execution_id": execution_id,
                "status": "mission_plan_not_ready",
                "started_at": started_at,
                "finished_at": utc_now(),
                "validation": validation,
                "payload": data,
                "plan": mission_plan,
                "executed": [],
            }
            self.save_report(report)
            return report

        dry_run = bool(data.get("dry_run", True))
        max_tasks = int(data.get("max_tasks", 10) or 10)
        tasks = list(mission_plan.get("tasks", []))[:max_tasks]

        executed: list[dict[str, Any]] = []

        for task in tasks:
            command_payload = {
                "action": task.get("action"),
                "objective": task.get("objective", ""),
                "mission_id": mission_plan.get("mission_id"),
                "official_publish": False,
                "auto_publish": False,
                "auto_deploy": False,
                "mass_messaging": False,
                "browser_automation": False,
                "external_api_enabled": False,
            }

            command_validation = validate_command_payload(command_payload)

            if not command_validation["ok"]:
                row = {
                    "task_id": task.get("task_id"),
                    "action": task.get("action"),
                    "status": "blocked",
                    "validation": command_validation,
                    "result": {
                        "ok": False,
                        "status": "blocked_by_command_policy",
                    },
                }
                executed.append(row)
                continue

            if dry_run:
                result = {
                    "ok": True,
                    "status": "dry_run_ready",
                    "side_effects": "none",
                    "action": task.get("action"),
                }
            else:
                result = self.command_center.execute_task({
                    "task_id": task.get("task_id"),
                    "action": task.get("action"),
                    "objective": task.get("objective", ""),
                    "mission_id": mission_plan.get("mission_id"),
                    "status": "running",
                })

            row = {
                "task_id": task.get("task_id"),
                "action": task.get("action"),
                "status": "finished" if result.get("ok") else "failed",
                "validation": command_validation,
                "result": result,
            }

            executed.append(row)

            self.event("mission_executor.task.processed", {
                "execution_id": execution_id,
                "mission_id": mission_plan.get("mission_id"),
                "task_id": task.get("task_id"),
                "action": task.get("action"),
                "status": row["status"],
                "dry_run": dry_run,
            })

        ok = all(item["result"].get("ok") for item in executed)

        report = {
            "ok": ok,
            "checkpoint": "45",
            "name": "Mission Executor Bridge",
            "execution_id": execution_id,
            "mission_id": mission_plan.get("mission_id"),
            "status": "completed" if ok else "needs_review",
            "started_at": started_at,
            "finished_at": utc_now(),
            "dry_run": dry_run,
            "validation": validation,
            "payload": data,
            "plan_summary": {
                "mission_id": mission_plan.get("mission_id"),
                "title": mission_plan.get("payload", {}).get("title"),
                "mission_type": mission_plan.get("payload", {}).get("mission_type"),
                "tasks_total": len(mission_plan.get("tasks", [])),
            },
            "executed": executed,
            "guardrails": [
                "sem publicacao automatica",
                "sem deploy automatico",
                "sem mensagem em massa",
                "sem API externa real",
                "sem token em texto puro",
                "execucao real apenas via Command Center e politicas",
            ],
            "side_effects": "dry_run" if dry_run else "local_command_center_execution_only",
            "next_checkpoint": "46 - Social Growth Mission Pack",
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_mission_executor_bridge.json"
        latest_md = self.reports_dir / "latest_mission_executor_bridge.md"
        run_json = self.reports_dir / f"{report.get('execution_id', 'unknown')}.json"

        latest_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        run_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        self.event("mission_executor.report.saved", {
            "execution_id": report.get("execution_id"),
            "status": report.get("status"),
            "ok": report.get("ok"),
        })

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas Mission Executor Bridge",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Execution ID: {report.get('execution_id')}",
            f"Mission ID: {report.get('mission_id')}",
            f"Dry run: {report.get('dry_run')}",
            "",
            "## Executed tasks",
            "",
        ]

        for item in report.get("executed", []):
            lines.append(f"- {item.get('action')} | {item.get('status')} | {item.get('result', {}).get('status')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for guardrail in report.get("guardrails", []):
            lines.append(f"- {guardrail}")

        return "\n".join(lines)
