from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_command_center_planning_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CommandCenterPlanningRunner:
    def __init__(
        self,
        reports_dir: str | Path = "reports/command_center_planning_runner",
        memory_dir: str | Path = "memory/command_center_planning_runner",
        command_center_dir: str | Path = "memory/command_center",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.command_center_dir = Path(command_center_dir)

        self.intake_queue_path = self.command_center_dir / "mission_intake_queue.json"
        self.planning_queue_path = self.command_center_dir / "planning_queue.json"
        self.planning_runs_path = self.memory_dir / "planning_runs.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def default_payload(self) -> dict[str, Any]:
        return {
            "scope": "all",
            "limit": 25,
            "objective": "transformar tarefas importadas no Command Center em planos operacionais supervisionados",
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

    def task_matches_scope(self, task: Mapping[str, Any], scope: str) -> bool:
        if scope == "all":
            return True

        return str(task.get("layer", "")).strip() == scope

    def classify_complexity(self, task: Mapping[str, Any]) -> dict[str, Any]:
        objective = str(task.get("objective", ""))
        risk = str(task.get("risk", "medium"))

        score = 1

        if len(objective) > 120:
            score += 1

        if risk in {"high", "critical"}:
            score += 2

        if task.get("requires_human_review") is True:
            score += 1

        if score >= 5:
            level = "high"
        elif score >= 3:
            level = "medium"
        else:
            level = "low"

        return {
            "complexity_score": score,
            "complexity_level": level,
            "requires_human_review": True,
        }

    def build_plan(self, task: Mapping[str, Any]) -> dict[str, Any]:
        plan_id = str(uuid4())
        complexity = self.classify_complexity(task)

        objective = str(task.get("objective", ""))
        layer = str(task.get("layer", "ops"))
        risk = str(task.get("risk", "medium"))

        deliverables = [
            "diagnostico operacional",
            "criterios de aceite",
            "passos supervisionados",
            "pontos de bloqueio",
            "relatorio final",
        ]

        if layer == "social":
            deliverables.extend([
                "pilares editoriais",
                "fila de conteudo",
                "checklist de publicacao segura",
            ])

        if layer == "saas":
            deliverables.extend([
                "escopo MVP",
                "estrutura de produto",
                "lista de modulos",
            ])

        return {
            "plan_id": plan_id,
            "source": "command_center_mission_intake",
            "source_intake_task_id": task.get("intake_task_id"),
            "source_task_id": task.get("source_task_id"),
            "mission_id": task.get("mission_id"),
            "mission_title": task.get("mission_title"),
            "objective": objective,
            "layer": layer,
            "risk": risk,
            "created_at": utc_now(),
            "status": "planned_waiting_human_review",
            "complexity": complexity,
            "phases": [
                {
                    "phase": 1,
                    "name": "diagnostico",
                    "goal": "entender objetivo, contexto, risco e restricoes",
                    "status": "planned",
                },
                {
                    "phase": 2,
                    "name": "decomposicao",
                    "goal": "quebrar em tarefas pequenas e verificaveis",
                    "status": "planned",
                },
                {
                    "phase": 3,
                    "name": "governanca",
                    "goal": "validar Approval Gate, limites e side effects",
                    "status": "planned",
                },
                {
                    "phase": 4,
                    "name": "execucao supervisionada futura",
                    "goal": "preparar payload para executor sem acionar API real",
                    "status": "planned",
                },
            ],
            "deliverables": deliverables,
            "acceptance_criteria": [
                "nenhum token em arquivo",
                "nenhuma chamada externa real",
                "nenhuma publicacao automatica",
                "nenhum envio automatico",
                "nenhum deploy automatico",
                "toda decisao importante registrada",
                "aprovacao humana antes de qualquer execucao real",
            ],
            "next_recommended_action": "revisar plano no cockpit e aprovar para pacote executor futuro",
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "planning runner apenas cria plano",
                "nao executa comando PowerShell",
                "nao chama API externa",
                "nao publica",
                "nao envia mensagem",
                "nao faz deploy",
            ],
        }

    def run(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_command_center_planning_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "61",
                "name": "Command Center Planning Runner",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "blocked_by_policy",
                "payload": data,
                "validation": validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        scope = str(data.get("scope", "all"))
        limit = int(data.get("limit", 25))

        intake_queue = self.load_json_list(self.intake_queue_path)
        planning_queue = self.load_json_list(self.planning_queue_path)

        existing_source_ids = {
            item.get("source_intake_task_id")
            for item in planning_queue
            if item.get("source_intake_task_id")
        }

        candidates = [
            task for task in intake_queue
            if task.get("status") == "queued_for_planning"
            and self.task_matches_scope(task, scope)
            and task.get("intake_task_id") not in existing_source_ids
        ][:limit]

        plans = [self.build_plan(task) for task in candidates]
        planning_queue.extend(plans)

        planned_ids = {plan.get("source_intake_task_id") for plan in plans}

        for task in intake_queue:
            if task.get("intake_task_id") in planned_ids:
                task["status"] = "planned_waiting_human_review"
                task["planned_at"] = utc_now()

        self.save_json_list(self.intake_queue_path, intake_queue)
        self.save_json_list(self.planning_queue_path, planning_queue)

        run_row = {
            "run_id": run_id,
            "created_at": utc_now(),
            "scope": scope,
            "limit": limit,
            "candidates_found": len(candidates),
            "plans_created": len(plans),
            "execution_enabled": False,
            "real_execution_enabled": False,
        }

        runs = self.load_json_list(self.planning_runs_path)
        runs.append(run_row)
        self.save_json_list(self.planning_runs_path, runs)

        report = {
            "ok": True,
            "checkpoint": "61",
            "name": "Command Center Planning Runner",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "planning_completed",
            "payload": data,
            "validation": validation,
            "summary": {
                "scope": scope,
                "intake_tasks_total": len(intake_queue),
                "planning_queue_total": len(planning_queue),
                "candidates_found": len(candidates),
                "plans_created": len(plans),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "revisar planos e preparar Approval Gate de pacote executor",
            },
            "plans": plans,
            "planning_queue_path": str(self.planning_queue_path).replace("\\", "/"),
            "intake_queue_path": str(self.intake_queue_path).replace("\\", "/"),
            "guardrails": [
                "nao executa comandos",
                "nao chama API externa",
                "nao publica",
                "nao envia WhatsApp",
                "nao faz deploy",
                "sem automacao de navegador",
                "aprovacao humana continua obrigatoria",
            ],
            "next_checkpoint": "62 - Planning Approval Packager",
        }

        self.save_report(report)

        self.event("command_center_planning_runner.completed", {
            "run_id": run_id,
            "status": report["status"],
            "plans_created": len(plans),
            "scope": scope,
        })

        return report

    def summary(self) -> dict[str, Any]:
        intake_queue = self.load_json_list(self.intake_queue_path)
        planning_queue = self.load_json_list(self.planning_queue_path)
        runs = self.load_json_list(self.planning_runs_path)

        return {
            "ok": True,
            "checkpoint": "61",
            "name": "Command Center Planning Runner",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "intake_tasks_total": len(intake_queue),
                "planning_queue_total": len(planning_queue),
                "runs_total": len(runs),
                "queued_for_planning": len([task for task in intake_queue if task.get("status") == "queued_for_planning"]),
                "planned_waiting_human_review": len([task for task in intake_queue if task.get("status") == "planned_waiting_human_review"]),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "rodar planning runner ou revisar planos existentes",
            },
            "planning_queue": planning_queue,
            "runs": runs,
            "guardrails": [
                "runner nao executa tarefas",
                "runner nao chama API externa",
                "runner nao publica",
                "runner nao envia mensagem",
                "runner nao faz deploy",
            ],
            "next_checkpoint": "62 - Planning Approval Packager",
        }

    def save_report(self, report: dict[str, Any] | None = None) -> dict[str, Any]:
        final_report = report or self.summary()

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_command_center_planning_runner.json"
        latest_md = self.reports_dir / "latest_command_center_planning_runner.md"

        latest_json.write_text(
            json.dumps(final_report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        latest_md.write_text(self.to_markdown(final_report), encoding="utf-8")

        return final_report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Command Center Planning Runner",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Intake tasks total: {summary.get('intake_tasks_total')}",
            f"- Planning queue total: {summary.get('planning_queue_total')}",
            f"- Plans created: {summary.get('plans_created')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Plans",
            "",
        ]

        plans = report.get("plans", report.get("planning_queue", []))

        for item in plans:
            lines.append(f"- {item.get('plan_id')} | {item.get('status')} | {item.get('objective')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
