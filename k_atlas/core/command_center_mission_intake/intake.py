from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_command_center_intake_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CommandCenterMissionIntake:
    def __init__(
        self,
        reports_dir: str | Path = "reports/command_center_mission_intake",
        memory_dir: str | Path = "memory/command_center_mission_intake",
        operator_exports_dir: str | Path = "memory/operator_mission_queue/command_center_exports",
        command_center_dir: str | Path = "memory/command_center",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.operator_exports_dir = Path(operator_exports_dir)
        self.command_center_dir = Path(command_center_dir)
        self.events_path = self.memory_dir / "events.jsonl"
        self.intake_queue_path = self.command_center_dir / "mission_intake_queue.json"
        self.intake_index_path = self.memory_dir / "intake_index.json"

    def default_payload(self) -> dict[str, Any]:
        return {
            "source": "manual_payload",
            "mission_id": "manual-demo",
            "mission_title": "Missão manual de teste para Command Center",
            "tasks": [
                {
                    "objective": "Validar entrada de missão no Command Center sem execução real",
                    "source": "manual_payload",
                    "mission_id": "manual-demo",
                    "task_id": "manual-task-1",
                    "risk": "medium",
                    "layer": "ops",
                    "requires_human_review": True,
                    "live_call": False,
                    "real_execute": False,
                    "auto_publish": False,
                    "auto_send": False,
                    "auto_deploy": False,
                }
            ],
            "live_call": False,
            "real_execute": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "bypass_human_approval": False,
        }

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }

        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def load_json_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_json_list(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def load_json_dict(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save_json_dict(self, path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def discover_exports(self) -> list[Path]:
        if not self.operator_exports_dir.exists():
            return []

        return sorted(self.operator_exports_dir.glob("*.json"))

    def read_export(self, path: Path) -> dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {
                    "ok": False,
                    "status": "invalid_export_shape",
                    "path": str(path).replace("\\", "/"),
                    "data": {},
                }

            return {
                "ok": True,
                "status": "loaded",
                "path": str(path).replace("\\", "/"),
                "data": data,
            }
        except Exception as exc:
            return {
                "ok": False,
                "status": "read_error",
                "path": str(path).replace("\\", "/"),
                "error": f"{type(exc).__name__}: {exc}",
                "data": {},
            }

    def normalize_task(self, mission_payload: Mapping[str, Any], task: Mapping[str, Any]) -> dict[str, Any]:
        intake_task_id = str(uuid4())

        return {
            "intake_task_id": intake_task_id,
            "source": "operator_mission_queue",
            "source_task_id": task.get("task_id"),
            "mission_id": mission_payload.get("mission_id"),
            "mission_title": mission_payload.get("mission_title"),
            "objective": task.get("objective"),
            "layer": task.get("layer", mission_payload.get("layer")),
            "risk": task.get("risk", mission_payload.get("risk")),
            "status": "queued_for_planning",
            "created_at": utc_now(),
            "requires_human_review": True,
            "command_center_ready": True,
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "safety": {
                "live_call": False,
                "real_execute": False,
                "auto_publish": False,
                "auto_send": False,
                "auto_deploy": False,
                "mass_messaging": False,
                "browser_automation": False,
                "bypass_human_approval": False,
            },
        }

    def intake_payload(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        intake_id = str(uuid4())
        data = dict(payload)
        validation = validate_command_center_intake_payload(data)

        if not validation["ok"]:
            result = {
                "ok": False,
                "checkpoint": "60",
                "name": "Command Center Mission Intake",
                "intake_id": intake_id,
                "created_at": utc_now(),
                "status": "blocked_by_policy",
                "payload": data,
                "validation": validation,
                "tasks_imported": 0,
                "external_side_effects": "none",
            }
            self.record_intake_result(result)
            return result

        queue = self.load_json_list(self.intake_queue_path)

        incoming_tasks = data.get("tasks", [])
        normalized_tasks = []

        for task in incoming_tasks:
            normalized_tasks.append(self.normalize_task(data, task))

        queue.extend(normalized_tasks)
        self.save_json_list(self.intake_queue_path, queue)

        result = {
            "ok": True,
            "checkpoint": "60",
            "name": "Command Center Mission Intake",
            "intake_id": intake_id,
            "created_at": utc_now(),
            "status": "intake_completed",
            "mission_id": data.get("mission_id"),
            "mission_title": data.get("mission_title"),
            "validation": validation,
            "tasks_imported": len(normalized_tasks),
            "tasks": normalized_tasks,
            "command_center_queue_path": str(self.intake_queue_path).replace("\\", "/"),
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "intake importa tarefas, nao executa",
                "sem chamada externa real",
                "sem publicacao automatica",
                "sem envio automatico",
                "sem deploy automatico",
                "sem automacao de navegador",
                "aprovacao humana continua obrigatoria",
            ],
        }

        self.record_intake_result(result)
        return result

    def record_intake_result(self, result: dict[str, Any]) -> None:
        index = self.load_json_dict(self.intake_index_path)
        rows = index.get("intakes", [])

        if not isinstance(rows, list):
            rows = []

        rows.append({
            "intake_id": result.get("intake_id"),
            "mission_id": result.get("mission_id"),
            "status": result.get("status"),
            "created_at": result.get("created_at"),
            "tasks_imported": result.get("tasks_imported"),
        })

        index = {
            "updated_at": utc_now(),
            "intakes": rows,
        }

        self.save_json_dict(self.intake_index_path, index)

        self.event("command_center_mission_intake.recorded", {
            "intake_id": result.get("intake_id"),
            "mission_id": result.get("mission_id"),
            "status": result.get("status"),
            "tasks_imported": result.get("tasks_imported"),
        })

        self.save_report()

    def process_exports(self, limit: int = 25) -> dict[str, Any]:
        run_id = str(uuid4())
        paths = self.discover_exports()[:limit]

        processed = []
        imported = 0
        blocked = 0

        for path in paths:
            loaded = self.read_export(path)

            if not loaded["ok"]:
                processed.append(loaded)
                blocked += 1
                continue

            export_payload = dict(loaded["data"])
            export_payload["source"] = "operator_mission_queue"
            export_payload["live_call"] = False
            export_payload["real_execute"] = False
            export_payload["auto_publish"] = False
            export_payload["auto_send"] = False
            export_payload["auto_deploy"] = False
            export_payload["mass_messaging"] = False
            export_payload["browser_automation"] = False
            export_payload["bypass_human_approval"] = False

            result = self.intake_payload(export_payload)
            result["source_export_path"] = loaded["path"]
            processed.append(result)

            if result.get("ok"):
                imported += result.get("tasks_imported", 0)
            else:
                blocked += 1

        report = {
            "ok": blocked == 0,
            "checkpoint": "60",
            "name": "Command Center Mission Intake",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "exports_processed" if blocked == 0 else "exports_processed_with_blocks",
            "exports_found": len(paths),
            "exports_processed": len(processed),
            "exports_blocked": blocked,
            "tasks_imported": imported,
            "command_center_queue_path": str(self.intake_queue_path).replace("\\", "/"),
            "processed": processed,
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "next_action": "revisar fila mission_intake_queue antes de qualquer execução",
            "guardrails": [
                "processamento nao executa tarefas",
                "sem API externa",
                "sem publicacao",
                "sem envio",
                "sem deploy",
                "sem automacao de navegador",
            ],
            "next_checkpoint": "61 - Command Center Planning Runner",
        }

        self.save_report(report)
        return report

    def summary(self) -> dict[str, Any]:
        queue = self.load_json_list(self.intake_queue_path)
        index = self.load_json_dict(self.intake_index_path)
        intakes = index.get("intakes", [])

        if not isinstance(intakes, list):
            intakes = []

        return {
            "ok": True,
            "checkpoint": "60",
            "name": "Command Center Mission Intake",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "command_center_tasks_total": len(queue),
                "intakes_total": len(intakes),
                "queued_for_planning": len([task for task in queue if task.get("status") == "queued_for_planning"]),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "rodar process_exports ou revisar tarefas importadas",
            },
            "queue": queue,
            "intakes": intakes,
            "guardrails": [
                "intake nao executa tarefas",
                "sem chamada externa",
                "sem publicação",
                "sem envio",
                "sem deploy",
            ],
            "next_checkpoint": "61 - Command Center Planning Runner",
        }

    def save_report(self, report: dict[str, Any] | None = None) -> dict[str, Any]:
        final_report = report or self.summary()

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_command_center_mission_intake.json"
        latest_md = self.reports_dir / "latest_command_center_mission_intake.md"

        latest_json.write_text(
            json.dumps(final_report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        latest_md.write_text(self.to_markdown(final_report), encoding="utf-8")

        return final_report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Command Center Mission Intake",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
        ]

        if summary:
            lines.extend([
                f"- Command Center tasks total: {summary.get('command_center_tasks_total')}",
                f"- Intakes total: {summary.get('intakes_total')}",
                f"- Queued for planning: {summary.get('queued_for_planning')}",
                f"- Execution enabled: {summary.get('execution_enabled')}",
                f"- Next action: {summary.get('next_action')}",
            ])
        else:
            lines.extend([
                f"- Exports found: {report.get('exports_found')}",
                f"- Exports processed: {report.get('exports_processed')}",
                f"- Tasks imported: {report.get('tasks_imported')}",
                f"- Execution enabled: {report.get('execution_enabled')}",
            ])

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
