from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_operator_mission_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class OperatorMissionQueue:
    def __init__(
        self,
        reports_dir: str | Path = "reports/operator_mission_queue",
        memory_dir: str | Path = "memory/operator_mission_queue",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.queue_path = self.memory_dir / "operator_missions.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def default_payload(self) -> dict[str, Any]:
        return {
            "title": "Preparar crescimento supervisionado do Instagram oficial K-Atlas",
            "objective": "transformar o Instagram oficial em canal publico de construcao, prova operacional e captacao futura sem publicacao automatica",
            "layer": "social",
            "priority": "high",
            "risk": "high",
            "requested_by": "operator",
            "expected_outputs": [
                "plano de conteudo",
                "fila de ideias",
                "criterios de aprovacao",
                "checklist de publicacao segura",
                "tarefas para Command Center",
            ],
            "constraints": [
                "sem publicacao automatica",
                "sem token em texto puro",
                "sem chamada externa real",
                "sem automacao de navegador",
                "governanca humana obrigatoria",
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

    def load_queue(self) -> list[dict[str, Any]]:
        if not self.queue_path.exists():
            return []

        try:
            data = json.loads(self.queue_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_queue(self, rows: list[dict[str, Any]]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.queue_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def build_tasks(self, payload: Mapping[str, Any]) -> list[dict[str, Any]]:
        layer = str(payload.get("layer", "ops"))
        title = str(payload.get("title", "missao"))

        base_tasks = [
            {
                "task_id": str(uuid4()),
                "title": "Validar objetivo da missao",
                "type": "planning",
                "status": "pending",
                "requires_human_review": True,
                "command_center_ready": True,
            },
            {
                "task_id": str(uuid4()),
                "title": "Quebrar missao em entregaveis",
                "type": "decomposition",
                "status": "pending",
                "requires_human_review": True,
                "command_center_ready": True,
            },
            {
                "task_id": str(uuid4()),
                "title": "Gerar checklist de governanca",
                "type": "governance",
                "status": "pending",
                "requires_human_review": True,
                "command_center_ready": True,
            },
            {
                "task_id": str(uuid4()),
                "title": "Gerar plano de execucao supervisionado",
                "type": "execution_plan",
                "status": "pending",
                "requires_human_review": True,
                "command_center_ready": True,
            },
        ]

        if layer == "social":
            base_tasks.extend([
                {
                    "task_id": str(uuid4()),
                    "title": "Criar pilares editoriais do Instagram K-Atlas",
                    "type": "social_strategy",
                    "status": "pending",
                    "requires_human_review": True,
                    "command_center_ready": True,
                },
                {
                    "task_id": str(uuid4()),
                    "title": "Criar fila inicial de posts sem publicar",
                    "type": "content_queue",
                    "status": "pending",
                    "requires_human_review": True,
                    "command_center_ready": True,
                },
            ])

        if layer == "saas":
            base_tasks.extend([
                {
                    "task_id": str(uuid4()),
                    "title": "Gerar escopo MVP SaaS",
                    "type": "saas_scope",
                    "status": "pending",
                    "requires_human_review": True,
                    "command_center_ready": True,
                },
                {
                    "task_id": str(uuid4()),
                    "title": "Gerar estrutura inicial de produto",
                    "type": "saas_product_blueprint",
                    "status": "pending",
                    "requires_human_review": True,
                    "command_center_ready": True,
                },
            ])

        return [
            {
                **task,
                "mission_title": title,
                "layer": layer,
                "external_side_effects": "none",
            }
            for task in base_tasks
        ]

    def enqueue(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        mission_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_operator_mission_payload(data)

        mission = {
            "ok": validation["ok"],
            "checkpoint": "59",
            "mission_id": mission_id,
            "created_at": utc_now(),
            "status": "queued" if validation["ok"] else "blocked_by_policy",
            "payload": data,
            "validation": validation,
            "tasks": self.build_tasks(data) if validation["ok"] else [],
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "missao apenas entra na fila",
                "sem execucao externa real",
                "sem publicacao automatica",
                "sem envio automatico",
                "sem deploy automatico",
                "sem automacao de navegador",
                "aprovacao humana obrigatoria",
            ],
        }

        queue = self.load_queue()
        queue.append(mission)
        self.save_queue(queue)

        self.event("operator_mission.enqueued", {
            "mission_id": mission_id,
            "status": mission["status"],
            "layer": data.get("layer"),
            "priority": data.get("priority"),
            "risk": data.get("risk"),
        })

        self.save_report()
        return mission

    def list_by_status(self, status: str) -> list[dict[str, Any]]:
        return [item for item in self.load_queue() if item.get("status") == status]

    def approve(self, mission_id: str, reviewer: str = "operator", notes: str = "") -> dict[str, Any]:
        queue = self.load_queue()
        found = None

        for item in queue:
            if item.get("mission_id") == mission_id:
                found = item
                break

        if found is None:
            result = {
                "ok": False,
                "status": "mission_not_found",
                "mission_id": mission_id,
            }
            self.event("operator_mission.approval_failed", result)
            self.save_report()
            return result

        if found.get("status") != "queued":
            result = {
                "ok": False,
                "status": "mission_not_queued",
                "mission_id": mission_id,
                "current_status": found.get("status"),
            }
            self.event("operator_mission.approval_failed", result)
            self.save_report()
            return result

        found["status"] = "approved_for_planning"
        found["approval"] = {
            "reviewer": reviewer,
            "notes": notes,
            "approved_at": utc_now(),
        }
        found["execution_enabled"] = False
        found["real_execution_enabled"] = False

        self.save_queue(queue)

        result = {
            "ok": True,
            "status": "approved_for_planning",
            "mission": found,
        }

        self.event("operator_mission.approved_for_planning", {
            "mission_id": mission_id,
            "reviewer": reviewer,
        })

        self.save_report()
        return result

    def export_command_center_tasks(self, mission_id: str) -> dict[str, Any]:
        queue = self.load_queue()
        found = None

        for item in queue:
            if item.get("mission_id") == mission_id:
                found = item
                break

        if found is None:
            return {
                "ok": False,
                "status": "mission_not_found",
                "mission_id": mission_id,
            }

        if found.get("status") != "approved_for_planning":
            return {
                "ok": False,
                "status": "mission_not_approved_for_planning",
                "mission_id": mission_id,
                "current_status": found.get("status"),
            }

        export = {
            "ok": True,
            "checkpoint": "59",
            "exported_at": utc_now(),
            "mission_id": mission_id,
            "mission_title": found.get("payload", {}).get("title"),
            "status": "command_center_payload_created",
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "tasks": [
                {
                    "objective": task.get("title"),
                    "source": "operator_mission_queue",
                    "mission_id": mission_id,
                    "task_id": task.get("task_id"),
                    "risk": found.get("payload", {}).get("risk"),
                    "layer": found.get("payload", {}).get("layer"),
                    "requires_human_review": True,
                    "live_call": False,
                    "real_execute": False,
                    "auto_publish": False,
                    "auto_send": False,
                    "auto_deploy": False,
                }
                for task in found.get("tasks", [])
            ],
        }

        export_dir = self.memory_dir / "command_center_exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = export_dir / f"{mission_id}.json"
        export_path.write_text(
            json.dumps(export, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        found["status"] = "exported_to_command_center_payload"
        found["command_center_export_path"] = str(export_path).replace("\\", "/")
        self.save_queue(queue)

        self.event("operator_mission.exported_to_command_center_payload", {
            "mission_id": mission_id,
            "tasks": len(export["tasks"]),
            "path": str(export_path).replace("\\", "/"),
        })

        self.save_report()
        return export

    def summary(self) -> dict[str, Any]:
        queue = self.load_queue()

        counts = {
            "total": len(queue),
            "queued": len([item for item in queue if item.get("status") == "queued"]),
            "approved_for_planning": len([item for item in queue if item.get("status") == "approved_for_planning"]),
            "exported_to_command_center_payload": len([item for item in queue if item.get("status") == "exported_to_command_center_payload"]),
            "blocked_by_policy": len([item for item in queue if item.get("status") == "blocked_by_policy"]),
        }

        return {
            "ok": True,
            "checkpoint": "59",
            "name": "Operator Mission Queue",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                **counts,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "aprovar uma missao e exportar payload para o Command Center",
            },
            "queue": queue,
            "guardrails": [
                "fila nao executa sozinha",
                "exportacao cria payload, nao executa comando real",
                "sem API externa",
                "sem publicacao automatica",
                "sem envio automatico",
                "sem deploy automatico",
                "sem automacao de navegador",
            ],
            "next_checkpoint": "60 - Command Center Mission Intake",
        }

    def save_report(self) -> dict[str, Any]:
        report = self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_operator_mission_queue.json"
        latest_md = self.reports_dir / "latest_operator_mission_queue.md"

        latest_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Operator Mission Queue",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Total: {summary.get('total')}",
            f"- Queued: {summary.get('queued')}",
            f"- Approved for planning: {summary.get('approved_for_planning')}",
            f"- Exported: {summary.get('exported_to_command_center_payload')}",
            f"- Blocked: {summary.get('blocked_by_policy')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Missions",
            "",
        ]

        for item in report.get("queue", []):
            payload = item.get("payload", {})
            lines.append(f"- {item.get('mission_id')} | {item.get('status')} | {payload.get('title')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
