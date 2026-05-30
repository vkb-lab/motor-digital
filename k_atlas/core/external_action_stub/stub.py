from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.publish_approval_gate.gate import SecurePublishApprovalGate

from .policy import validate_external_action_execution_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExternalActionExecutionStub:
    def __init__(
        self,
        reports_dir: str | Path = "reports/external_action_stub",
        memory_dir: str | Path = "memory/external_action_stub",
        approval_gate: SecurePublishApprovalGate | None = None,
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"
        self.executions_path = self.memory_dir / "stub_executions.json"
        self.approval_gate = approval_gate or SecurePublishApprovalGate()

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def load_executions(self) -> list[dict[str, Any]]:
        if not self.executions_path.exists():
            return []

        try:
            data = json.loads(self.executions_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_executions(self, rows: list[dict[str, Any]]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.executions_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def build_stub_result(self, request: Mapping[str, Any]) -> dict[str, Any]:
        payload = dict(request.get("payload", {}))
        action_type = str(payload.get("action_type", "manual_review"))

        adapter_map = {
            "instagram_publish": "instagram_graph_stub",
            "whatsapp_send": "whatsapp_cloud_stub",
            "render_deploy": "render_deploy_stub",
            "github_release": "github_release_stub",
            "external_api_call": "external_api_stub",
            "campaign_launch": "campaign_launch_stub",
            "content_generation": "content_generation_stub",
            "manual_review": "manual_review_stub",
        }

        return {
            "adapter": adapter_map.get(action_type, "unknown_stub"),
            "action_type": action_type,
            "channel": payload.get("channel"),
            "target": payload.get("target"),
            "content_preview": payload.get("content_preview"),
            "simulated_result": "ready_for_future_live_adapter",
            "real_external_call": False,
            "external_side_effects": "none",
            "message": "Execução simulada. Nenhuma API externa foi chamada.",
        }

    def execute_request_stub(self, request: Mapping[str, Any]) -> dict[str, Any]:
        execution_id = str(uuid4())
        payload = dict(request.get("payload", {}))

        validation_payload = {
            "request_id": request.get("request_id"),
            "action_type": payload.get("action_type"),
            "live_call": False,
            "real_execute": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "bypass_human_approval": False,
        }

        validation = validate_external_action_execution_payload(validation_payload)

        if not validation["ok"]:
            result = {
                "ok": False,
                "checkpoint": "55",
                "execution_id": execution_id,
                "request_id": request.get("request_id"),
                "status": "blocked_by_policy",
                "created_at": utc_now(),
                "validation": validation,
                "external_side_effects": "none",
            }
            self.record_execution(result)
            return result

        if request.get("status") != "approved_waiting_execution_gate":
            result = {
                "ok": False,
                "checkpoint": "55",
                "execution_id": execution_id,
                "request_id": request.get("request_id"),
                "status": "request_not_approved",
                "created_at": utc_now(),
                "validation": validation,
                "external_side_effects": "none",
            }
            self.record_execution(result)
            return result

        result = {
            "ok": True,
            "checkpoint": "55",
            "name": "External Action Execution Stub",
            "execution_id": execution_id,
            "request_id": request.get("request_id"),
            "created_at": utc_now(),
            "status": "stub_executed_no_external_call",
            "validation": validation,
            "request_snapshot": request,
            "stub_result": self.build_stub_result(request),
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "nenhuma API externa chamada",
                "nenhuma publicação realizada",
                "nenhuma mensagem enviada",
                "nenhum deploy realizado",
                "nenhum token lido ou salvo",
                "execução real continua bloqueada",
            ],
        }

        self.record_execution(result)
        return result

    def execute_approved_stubs(self, limit: int = 10) -> dict[str, Any]:
        approved = self.approval_gate.approved()[:limit]
        results = [self.execute_request_stub(item) for item in approved]

        report = {
            "ok": all(item.get("ok") for item in results) if results else True,
            "checkpoint": "55",
            "name": "External Action Execution Stub",
            "generated_at": utc_now(),
            "status": "completed",
            "approved_found": len(approved),
            "executed_stubs": len(results),
            "results": results,
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "next_action": "validar stubs no cockpit antes de qualquer adapter real",
            "next_checkpoint": "56 - Live Adapter Contract Registry",
        }

        self.save_report(report)
        return report

    def record_execution(self, row: dict[str, Any]) -> None:
        rows = self.load_executions()
        rows.append(row)
        self.save_executions(rows)

        self.event("external_action_stub.execution.recorded", {
            "execution_id": row.get("execution_id"),
            "request_id": row.get("request_id"),
            "status": row.get("status"),
        })

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_external_action_stub.json"
        latest_md = self.reports_dir / "latest_external_action_stub.md"

        latest_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas External Action Execution Stub",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Approved found: {report.get('approved_found')}",
            f"Executed stubs: {report.get('executed_stubs')}",
            f"Real execution enabled: {report.get('real_execution_enabled')}",
            "",
            "## Results",
            "",
        ]

        for item in report.get("results", []):
            lines.append(f"- {item.get('request_id')} | {item.get('status')} | {item.get('stub_result', {}).get('adapter')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
            "- nenhuma API externa chamada",
            "- nenhuma publicação realizada",
            "- nenhuma mensagem enviada",
            "- nenhum deploy realizado",
            "- execução real continua bloqueada",
        ])

        return "\n".join(lines)
