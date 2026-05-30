from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_planning_approval_packager_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PlanningApprovalPackager:
    def __init__(
        self,
        reports_dir: str | Path = "reports/planning_approval_packager",
        memory_dir: str | Path = "memory/planning_approval_packager",
        command_center_dir: str | Path = "memory/command_center",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.command_center_dir = Path(command_center_dir)

        self.planning_queue_path = self.command_center_dir / "planning_queue.json"
        self.package_queue_path = self.command_center_dir / "planning_approval_packages.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def default_payload(self) -> dict[str, Any]:
        return {
            "scope": "all",
            "limit": 25,
            "objective": "empacotar planos do Command Center para aprovacao humana antes de qualquer execucao",
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

    def plan_matches_scope(self, plan: Mapping[str, Any], scope: str) -> bool:
        if scope == "all":
            return True

        return str(plan.get("layer", "")).strip() == scope

    def classify_approval_level(self, plan: Mapping[str, Any]) -> dict[str, Any]:
        risk = str(plan.get("risk", "medium"))
        complexity = plan.get("complexity", {})
        complexity_level = str(complexity.get("complexity_level", "medium"))

        if risk == "critical":
            level = "double_review_required"
        elif risk == "high" or complexity_level == "high":
            level = "human_review_required"
        else:
            level = "standard_human_review"

        return {
            "approval_level": level,
            "requires_human_approval": True,
            "requires_execution_gate": True,
            "allows_auto_execution": False,
        }

    def build_package(self, plan: Mapping[str, Any]) -> dict[str, Any]:
        package_id = str(uuid4())
        approval = self.classify_approval_level(plan)

        return {
            "package_id": package_id,
            "source": "command_center_planning_runner",
            "source_plan_id": plan.get("plan_id"),
            "mission_id": plan.get("mission_id"),
            "mission_title": plan.get("mission_title"),
            "objective": plan.get("objective"),
            "layer": plan.get("layer"),
            "risk": plan.get("risk"),
            "created_at": utc_now(),
            "status": "waiting_human_approval",
            "approval": approval,
            "plan_snapshot": plan,
            "review_checklist": [
                "objetivo esta claro",
                "entregaveis estao corretos",
                "criterios de aceite estao claros",
                "risco esta classificado corretamente",
                "sem token em arquivo",
                "sem chamada externa real",
                "sem publicacao automatica",
                "sem envio automatico",
                "sem deploy automatico",
                "sem automacao de navegador",
            ],
            "operator_decision_options": [
                "approve_for_executor_package",
                "request_changes",
                "deny",
            ],
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "pacote apenas prepara aprovacao",
                "aprovacao ainda nao executa",
                "execucao real segue bloqueada",
                "sem API externa",
                "sem publicacao",
                "sem envio",
                "sem deploy",
            ],
        }

    def package_plans(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_planning_approval_packager_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "62",
                "name": "Planning Approval Packager",
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

        planning_queue = self.load_json_list(self.planning_queue_path)
        package_queue = self.load_json_list(self.package_queue_path)

        existing_plan_ids = {
            item.get("source_plan_id")
            for item in package_queue
            if item.get("source_plan_id")
        }

        candidates = [
            plan for plan in planning_queue
            if plan.get("status") == "planned_waiting_human_review"
            and self.plan_matches_scope(plan, scope)
            and plan.get("plan_id") not in existing_plan_ids
        ][:limit]

        packages = [self.build_package(plan) for plan in candidates]
        package_queue.extend(packages)

        packaged_ids = {package.get("source_plan_id") for package in packages}

        for plan in planning_queue:
            if plan.get("plan_id") in packaged_ids:
                plan["status"] = "packaged_waiting_human_approval"
                plan["packaged_at"] = utc_now()

        self.save_json_list(self.planning_queue_path, planning_queue)
        self.save_json_list(self.package_queue_path, package_queue)

        report = {
            "ok": True,
            "checkpoint": "62",
            "name": "Planning Approval Packager",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "packaging_completed",
            "payload": data,
            "validation": validation,
            "summary": {
                "scope": scope,
                "planning_queue_total": len(planning_queue),
                "approval_packages_total": len(package_queue),
                "candidates_found": len(candidates),
                "packages_created": len(packages),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "revisar pacotes e aprovar manualmente no proximo checkpoint",
            },
            "packages": packages,
            "planning_queue_path": str(self.planning_queue_path).replace("\\", "/"),
            "package_queue_path": str(self.package_queue_path).replace("\\", "/"),
            "guardrails": [
                "nao executa comandos",
                "nao chama API externa",
                "nao publica",
                "nao envia WhatsApp",
                "nao faz deploy",
                "sem automacao de navegador",
                "aprovacao humana continua obrigatoria",
            ],
            "next_checkpoint": "63 - Human Approval Decision Center",
        }

        self.save_report(report)

        self.event("planning_approval_packager.completed", {
            "run_id": run_id,
            "status": report["status"],
            "packages_created": len(packages),
            "scope": scope,
        })

        return report

    def summary(self) -> dict[str, Any]:
        planning_queue = self.load_json_list(self.planning_queue_path)
        package_queue = self.load_json_list(self.package_queue_path)

        return {
            "ok": True,
            "checkpoint": "62",
            "name": "Planning Approval Packager",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "planning_queue_total": len(planning_queue),
                "approval_packages_total": len(package_queue),
                "planned_waiting_human_review": len([plan for plan in planning_queue if plan.get("status") == "planned_waiting_human_review"]),
                "packaged_waiting_human_approval": len([plan for plan in planning_queue if plan.get("status") == "packaged_waiting_human_approval"]),
                "waiting_human_approval": len([package for package in package_queue if package.get("status") == "waiting_human_approval"]),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "rodar empacotamento ou revisar pacotes existentes",
            },
            "planning_queue": planning_queue,
            "package_queue": package_queue,
            "guardrails": [
                "packager nao executa tarefas",
                "packager nao chama API externa",
                "packager nao publica",
                "packager nao envia mensagem",
                "packager nao faz deploy",
            ],
            "next_checkpoint": "63 - Human Approval Decision Center",
        }

    def save_report(self, report: dict[str, Any] | None = None) -> dict[str, Any]:
        final_report = report or self.summary()

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_planning_approval_packager.json"
        latest_md = self.reports_dir / "latest_planning_approval_packager.md"

        latest_json.write_text(
            json.dumps(final_report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        latest_md.write_text(self.to_markdown(final_report), encoding="utf-8")

        return final_report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Planning Approval Packager",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Planning queue total: {summary.get('planning_queue_total')}",
            f"- Approval packages total: {summary.get('approval_packages_total')}",
            f"- Packages created: {summary.get('packages_created')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Packages",
            "",
        ]

        packages = report.get("packages", report.get("package_queue", []))

        for item in packages:
            lines.append(f"- {item.get('package_id')} | {item.get('status')} | {item.get('objective')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
