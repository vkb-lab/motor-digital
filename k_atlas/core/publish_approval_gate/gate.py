from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_publish_approval_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SecurePublishApprovalGate:
    def __init__(
        self,
        reports_dir: str | Path = "reports/publish_approval_gate",
        memory_dir: str | Path = "memory/publish_approval_gate",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.queue_path = self.memory_dir / "approval_queue.json"
        self.decisions_path = self.memory_dir / "approval_decisions.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def default_payload(self) -> dict[str, Any]:
        return {
            "title": "Revisar publicação manifesto K-Atlas",
            "objective": "aprovar manualmente um conteúdo oficial antes de qualquer publicação externa",
            "action_type": "instagram_publish",
            "channel": "instagram",
            "risk_level": "high",
            "requested_by": "k_atlas_operator",
            "content_preview": "K-Atlas OS: sistema operacional de agentes IA com memória, cockpit, SaaS Factory e supervisão humana.",
            "target": "Instagram oficial K-Atlas",
            "human_approved": False,
            "live_call": False,
            "official_publish": False,
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
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def classify_risk(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        action_type = str(payload.get("action_type", ""))
        channel = str(payload.get("channel", ""))

        high_risk_actions = {
            "instagram_publish",
            "whatsapp_send",
            "render_deploy",
            "github_release",
            "campaign_launch",
        }

        if action_type in high_risk_actions:
            level = "high"
        elif channel in {"instagram", "whatsapp", "render", "github"}:
            level = "medium"
        else:
            level = "low"

        return {
            "risk_level": level,
            "requires_human_approval": True,
            "requires_second_review": level == "high",
            "can_execute_automatically": False,
        }

    def create_request(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        request_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_publish_approval_payload(data)
        risk = self.classify_risk(data)

        request = {
            "ok": validation["ok"],
            "checkpoint": "54",
            "request_id": request_id,
            "created_at": utc_now(),
            "status": "pending_human_approval" if validation["ok"] else "blocked_by_policy",
            "payload": data,
            "validation": validation,
            "risk": risk,
            "execution_allowed": False,
            "external_side_effects": "none",
            "guardrails": [
                "não executar ação externa nesta etapa",
                "não publicar automaticamente",
                "não enviar WhatsApp automaticamente",
                "não fazer deploy automaticamente",
                "não salvar token em arquivo",
                "não permitir bypass de aprovação humana",
            ],
        }

        queue = self.load_json_list(self.queue_path)
        queue.append(request)
        self.save_json_list(self.queue_path, queue)

        self.event("publish_approval.request.created", {
            "request_id": request_id,
            "status": request["status"],
            "action_type": data.get("action_type"),
            "channel": data.get("channel"),
        })

        self.save_report()
        return request

    def decide(self, request_id: str, decision: str, reviewer: str = "human_operator", notes: str = "") -> dict[str, Any]:
        if decision not in {"approved", "denied"}:
            raise ValueError("decision must be approved or denied")

        queue = self.load_json_list(self.queue_path)
        decisions = self.load_json_list(self.decisions_path)

        target = None
        for item in queue:
            if item.get("request_id") == request_id:
                target = item
                break

        if target is None:
            result = {
                "ok": False,
                "status": "request_not_found",
                "request_id": request_id,
            }
            self.event("publish_approval.decision.failed", result)
            self.save_report()
            return result

        now = utc_now()

        target["status"] = "approved_waiting_execution_gate" if decision == "approved" else "denied"
        target["decision"] = {
            "decision": decision,
            "reviewer": reviewer,
            "notes": notes,
            "decided_at": now,
        }

        target["execution_allowed"] = False
        target["external_side_effects"] = "none"

        decision_row = {
            "request_id": request_id,
            "decision": decision,
            "reviewer": reviewer,
            "notes": notes,
            "decided_at": now,
            "execution_allowed": False,
            "reason": "approval registered only; execution adapter still disabled",
        }

        decisions.append(decision_row)

        self.save_json_list(self.queue_path, queue)
        self.save_json_list(self.decisions_path, decisions)

        self.event("publish_approval.decision.recorded", decision_row)
        self.save_report()

        return {
            "ok": True,
            "status": target["status"],
            "request": target,
            "decision": decision_row,
        }

    def pending(self) -> list[dict[str, Any]]:
        return [
            item for item in self.load_json_list(self.queue_path)
            if item.get("status") == "pending_human_approval"
        ]

    def approved(self) -> list[dict[str, Any]]:
        return [
            item for item in self.load_json_list(self.queue_path)
            if item.get("status") == "approved_waiting_execution_gate"
        ]

    def denied(self) -> list[dict[str, Any]]:
        return [
            item for item in self.load_json_list(self.queue_path)
            if item.get("status") == "denied"
        ]

    def summary(self) -> dict[str, Any]:
        queue = self.load_json_list(self.queue_path)
        decisions = self.load_json_list(self.decisions_path)

        return {
            "ok": True,
            "checkpoint": "54",
            "name": "Secure Publish Approval Gate",
            "generated_at": utc_now(),
            "status": "operational",
            "counts": {
                "total_requests": len(queue),
                "pending": len(self.pending()),
                "approved_waiting_execution_gate": len(self.approved()),
                "denied": len(self.denied()),
                "decisions": len(decisions),
            },
            "execution_enabled": False,
            "external_side_effects": "none",
            "next_action": "usar a fila para aprovar/recusar ações; execução real fica para checkpoint futuro",
            "queue": queue,
            "decisions": decisions,
            "guardrails": [
                "aprovação não executa ação externa",
                "execução real exige adapter específico",
                "sem publicação automática",
                "sem envio automático",
                "sem deploy automático",
                "sem tokens em texto puro",
            ],
            "next_checkpoint": "55 - External Action Execution Stub",
        }

    def save_report(self) -> dict[str, Any]:
        report = self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_publish_approval_gate.json"
        latest_md = self.reports_dir / "latest_publish_approval_gate.md"

        latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        counts = report.get("counts", {})

        lines = [
            "# K-Atlas Secure Publish Approval Gate",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Execution enabled: {report.get('execution_enabled')}",
            "",
            "## Counts",
            "",
            f"- Total requests: {counts.get('total_requests')}",
            f"- Pending: {counts.get('pending')}",
            f"- Approved waiting execution gate: {counts.get('approved_waiting_execution_gate')}",
            f"- Denied: {counts.get('denied')}",
            f"- Decisions: {counts.get('decisions')}",
            "",
            "## Guardrails",
            "",
        ]

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
