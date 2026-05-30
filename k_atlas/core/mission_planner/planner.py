from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.command_center.center import CommandCenter
from k_atlas.core.command_center.policy import validate_command_payload

from .policy import validate_mission_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MissionPlanner:
    def __init__(
        self,
        memory_dir: str | Path = "memory/mission_planner",
        reports_dir: str | Path = "reports/mission_planner",
        command_center: CommandCenter | None = None,
    ) -> None:
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.missions_path = self.memory_dir / "missions.json"
        self.events_path = self.memory_dir / "events.jsonl"
        self.command_center = command_center or CommandCenter()

    def default_payload(self) -> dict[str, Any]:
        return {
            "title": "Missao diaria K-Atlas OS",
            "mission_type": "daily_operator",
            "objective": "manter K-Atlas operacional, auditado e pronto para construir SaaS e midias digitais",
            "priority": "high",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
        }

    def load_missions(self) -> list[dict[str, Any]]:
        if not self.missions_path.exists():
            return []

        try:
            data = json.loads(self.missions_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_missions(self, missions: list[dict[str, Any]]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.missions_path.write_text(
            json.dumps(missions, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def mission_to_actions(self, mission_type: str) -> list[str]:
        mapping = {
            "system_health": [
                "health_check",
                "check_daemon",
                "check_git",
                "generate_autoreport",
            ],
            "growth_planning": [
                "check_git",
                "sandbox_creative_plan",
                "generate_autoreport",
            ],
            "creative_media": [
                "sandbox_creative_plan",
                "generate_autoreport",
            ],
            "saas_build": [
                "saas_factory_plan",
                "deploy_assisted_check",
                "generate_autoreport",
            ],
            "deploy_readiness": [
                "check_git",
                "deploy_assisted_check",
                "generate_autoreport",
            ],
            "daily_operator": [
                "health_check",
                "check_daemon",
                "check_git",
                "sandbox_creative_plan",
                "deploy_assisted_check",
                "generate_autoreport",
            ],
        }

        return mapping.get(mission_type, ["health_check", "generate_autoreport"])

    def build_plan(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        data = dict(payload or self.default_payload())
        validation = validate_mission_payload(data)
        mission_id = str(uuid4())

        if not validation["ok"]:
            plan = {
                "ok": False,
                "checkpoint": "44",
                "mission_id": mission_id,
                "status": "blocked_by_policy",
                "created_at": utc_now(),
                "payload": data,
                "validation": validation,
                "tasks": [],
            }

            self.persist_plan(plan)
            return plan

        actions = self.mission_to_actions(str(data.get("mission_type")))

        tasks = []
        for order, action in enumerate(actions, start=1):
            command_payload = {
                "action": action,
                "objective": data.get("objective", ""),
                "mission_id": mission_id,
                "mission_title": data.get("title", ""),
                "official_publish": False,
                "auto_publish": False,
                "auto_deploy": False,
                "mass_messaging": False,
                "browser_automation": False,
                "external_api_enabled": False,
            }

            command_validation = validate_command_payload(command_payload)

            tasks.append({
                "task_id": str(uuid4()),
                "mission_id": mission_id,
                "order": order,
                "status": "pending" if command_validation["ok"] else "blocked",
                "action": action,
                "objective": data.get("objective", ""),
                "validation": command_validation,
                "payload": command_payload,
            })

        plan = {
            "ok": True,
            "checkpoint": "44",
            "name": "Autonomy Mission Planner",
            "mission_id": mission_id,
            "status": "planned",
            "created_at": utc_now(),
            "payload": data,
            "validation": validation,
            "tasks": tasks,
            "next_checkpoints": [
                "45 - Mission Executor Bridge",
                "46 - Social Growth Mission Pack",
                "47 - SaaS Product Mission Pack",
                "48 - Daily Operator Cockpit",
                "49 - External API Adapter Readiness",
            ],
            "guardrails": [
                "sem publicacao automatica",
                "sem deploy automatico",
                "sem mensagem em massa",
                "sem API externa real",
                "sem token em texto puro",
                "toda execucao passa pelo Command Center",
            ],
        }

        self.persist_plan(plan)
        return plan

    def persist_plan(self, plan: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        missions = self.load_missions()
        missions.append(plan)
        self.save_missions(missions)

        latest_json = self.reports_dir / "latest_mission_plan.json"
        latest_md = self.reports_dir / "latest_mission_plan.md"

        latest_json.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        latest_md.write_text(self.to_markdown(plan), encoding="utf-8")

        self.event("mission.planned", {
            "mission_id": plan.get("mission_id"),
            "status": plan.get("status"),
            "tasks": len(plan.get("tasks", [])),
        })

    def enqueue_to_command_center(self, plan: dict[str, Any]) -> dict[str, Any]:
        if not plan.get("ok"):
            return {
                "ok": False,
                "status": "plan_not_allowed",
                "mission_id": plan.get("mission_id"),
            }

        queue = self.command_center.load_queue()
        created = []

        for task in plan.get("tasks", []):
            item = {
                "task_id": task["task_id"],
                "cycle_id": f"mission:{plan['mission_id']}",
                "mission_id": plan["mission_id"],
                "created_at": utc_now(),
                "status": task["status"],
                "validation": task["validation"],
                "action": task["action"],
                "objective": task["objective"],
            }

            queue.append(item)
            created.append(item)

        self.command_center.save_queue(queue)

        result = {
            "ok": True,
            "status": "mission_enqueued",
            "mission_id": plan["mission_id"],
            "tasks_enqueued": len(created),
            "tasks": created,
        }

        self.event("mission.enqueued", result)
        return result

    def plan_and_enqueue(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        plan = self.build_plan(payload)
        enqueue = self.enqueue_to_command_center(plan)

        result = {
            "ok": bool(plan.get("ok")) and bool(enqueue.get("ok")),
            "checkpoint": "44",
            "status": "planned_and_enqueued" if enqueue.get("ok") else "blocked",
            "plan": plan,
            "enqueue": enqueue,
        }

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_mission_execution_request.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return result

    def to_markdown(self, plan: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas Mission Plan",
            "",
            f"Checkpoint: {plan.get('checkpoint')}",
            f"Status: {plan.get('status')}",
            f"Mission ID: {plan.get('mission_id')}",
            f"Title: {plan.get('payload', {}).get('title')}",
            f"Type: {plan.get('payload', {}).get('mission_type')}",
            "",
            "## Objective",
            "",
            str(plan.get("payload", {}).get("objective", "")),
            "",
            "## Tasks",
            "",
        ]

        for task in plan.get("tasks", []):
            lines.append(f"- {task.get('order')}. {task.get('action')} | {task.get('status')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for guardrail in plan.get("guardrails", []):
            lines.append(f"- {guardrail}")

        lines.extend([
            "",
            "## Next checkpoints",
            "",
        ])

        for item in plan.get("next_checkpoints", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
