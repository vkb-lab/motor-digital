from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import DEFAULT_AGENT_PERMISSIONS, validate_brain_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalOSBrainGovernance:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/local_os_brain_governance",
        memory_dir: str | Path = "memory/local_os_brain_governance",
        reports_dir: str | Path = "reports/local_os_brain_governance",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.events_path = self.memory_dir / "events.jsonl"
        self.decision_queue_path = self.live_dir / "brain_decision_queue.json"
        self.feedback_queue_path = self.live_dir / "brain_feedback_queue.json"
        self.permission_matrix_path = self.live_dir / "agent_permission_matrix.json"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

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
        path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def save_permission_matrix(self) -> dict[str, Any]:
        payload = {
            "ok": True,
            "checkpoint": "130",
            "name": "Agent Permission Matrix",
            "generated_at": utc_now(),
            "permissions": DEFAULT_AGENT_PERMISSIONS,
            "rules": [
                "agentes nao executam diretamente",
                "agentes propoem ou solicitam",
                "cerebro valida politica",
                "acoes sensiveis exigem humano",
                "acoes bloqueadas nao podem ser liberadas por humano",
            ],
        }
        self.permission_matrix_path.parent.mkdir(parents=True, exist_ok=True)
        self.permission_matrix_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return payload

    def decide(self, request: Mapping[str, Any]) -> dict[str, Any]:
        decision_id = str(uuid4())
        validation = validate_brain_request(request)
        status = validation["status"]

        if status == "approved_safe":
            next_step = "queue_safe_action_for_operator_visibility"
        elif status == "requires_human_approval":
            next_step = "send_to_approval_gate"
        else:
            next_step = "return_to_agent_with_reasons"

        decision = {
            "ok": validation["ok"],
            "checkpoint": "129",
            "name": "Brain Decision Core",
            "decision_id": decision_id,
            "generated_at": utc_now(),
            "status": status,
            "agent": validation["agent"],
            "action": validation["action"],
            "request": dict(request or {}),
            "validation": validation,
            "next_step": next_step,
            "automatic_execution_allowed": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "human_approval_required": bool(validation.get("requires_human_approval")),
            "guardrails": [
                "brain decide, executor executa apenas quando permitido",
                "sem API externa",
                "sem controle de mouse",
                "sem teclado automatico",
                "sem porta publica",
                "sem envio automatico",
                "sem deploy automatico",
            ],
        }

        queue = self.load_list(self.decision_queue_path)
        queue.append(decision)
        self.save_list(self.decision_queue_path, queue)

        self.event("local_os_brain_governance.decision_created", {
            "decision_id": decision_id,
            "status": status,
            "agent": validation["agent"],
            "action": validation["action"],
        })

        self.save_report(self.build_report())
        return decision

    def route_feedback(self, decision: Mapping[str, Any], feedback: str | None = None) -> dict[str, Any]:
        feedback_id = str(uuid4())
        decision_status = str(decision.get("status", ""))

        if decision_status == "blocked":
            route = "agent_revision_required"
        elif decision_status == "requires_human_approval":
            route = "human_approval_console"
        else:
            route = "operator_visibility_queue"

        feedback_item = {
            "ok": True,
            "checkpoint": "132",
            "name": "Brain Feedback Router",
            "feedback_id": feedback_id,
            "created_at": utc_now(),
            "source_decision_id": decision.get("decision_id"),
            "source_status": decision_status,
            "route": route,
            "feedback": feedback or decision.get("next_step"),
        }

        queue = self.load_list(self.feedback_queue_path)
        queue.append(feedback_item)
        self.save_list(self.feedback_queue_path, queue)

        self.event("local_os_brain_governance.feedback_routed", {
            "feedback_id": feedback_id,
            "route": route,
        })

        return feedback_item

    def build_report(self) -> dict[str, Any]:
        self.save_permission_matrix()
        decisions = self.load_list(self.decision_queue_path)
        feedback = self.load_list(self.feedback_queue_path)

        safe = len([item for item in decisions if item.get("status") == "approved_safe"])
        pending = len([item for item in decisions if item.get("status") == "requires_human_approval"])
        blocked = len([item for item in decisions if item.get("status") == "blocked"])

        report = {
            "ok": True,
            "checkpoint": "133",
            "name": "Local OS Brain Governance Dashboard",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "decisions_total": len(decisions),
                "safe_approved": safe,
                "requires_human_approval": pending,
                "blocked": blocked,
                "feedback_total": len(feedback),
                "agents_registered": len(DEFAULT_AGENT_PERMISSIONS),
                "automatic_execution_allowed": False,
                "real_execution_enabled": False,
                "external_api_enabled": False,
            },
            "decisions": decisions[-20:],
            "feedback": feedback[-20:],
            "permission_matrix_path": str(self.permission_matrix_path).replace("\\", "/"),
            "guardrails": [
                "agentes obedecem ao cerebro",
                "cerebro obedece a politica",
                "politica protege a operacao",
                "humano aprova acoes sensiveis",
                "rollback permanece obrigatorio em execucao real",
            ],
        }

        return self.save_report(report)

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.reports_dir / "latest_local_os_brain_governance.json"
        md_path = self.reports_dir / "latest_local_os_brain_governance.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Local OS Brain Governance",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Decisions total: {summary.get('decisions_total')}",
            f"- Safe approved: {summary.get('safe_approved')}",
            f"- Requires human approval: {summary.get('requires_human_approval')}",
            f"- Blocked: {summary.get('blocked')}",
            f"- Agents registered: {summary.get('agents_registered')}",
            f"- Real execution enabled: {summary.get('real_execution_enabled')}",
            "",
            "## Guardrails",
            "",
        ]
        for item in report.get("guardrails", []):
            lines.append(f"- {item}")
        return "\n".join(lines)
