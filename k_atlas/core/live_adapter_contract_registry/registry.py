from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_live_adapter_contract


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LiveAdapterContractRegistry:
    def __init__(
        self,
        reports_dir: str | Path = "reports/live_adapter_contract_registry",
        memory_dir: str | Path = "memory/live_adapter_contract_registry",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.registry_path = self.memory_dir / "adapter_contracts.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def default_contracts(self) -> list[dict[str, Any]]:
        base = {
            "enabled": False,
            "live_call": False,
            "real_execution_enabled": False,
            "requires_human_approval": True,
            "requires_approval_gate": True,
            "approval_gate": "SecurePublishApprovalGate",
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "bypass_human_approval": False,
        }

        return [
            {
                **base,
                "adapter_id": "instagram_graph_publish",
                "provider": "meta",
                "purpose": "publicacao futura no Instagram oficial K-Atlas",
                "risk_level": "critical",
                "env_vars": ["META_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ACCOUNT_ID"],
                "allowed_actions_future": ["create_media_container", "publish_media"],
                "current_behavior": "contract_only_no_live_call",
            },
            {
                **base,
                "adapter_id": "instagram_graph_insights",
                "provider": "meta",
                "purpose": "leitura futura de insights Instagram",
                "risk_level": "medium",
                "env_vars": ["META_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ACCOUNT_ID"],
                "allowed_actions_future": ["read_profile", "read_media", "read_insights"],
                "current_behavior": "contract_only_no_live_call",
            },
            {
                **base,
                "adapter_id": "whatsapp_cloud_send",
                "provider": "meta",
                "purpose": "envio futuro de mensagens aprovadas via WhatsApp Cloud",
                "risk_level": "critical",
                "env_vars": ["WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"],
                "allowed_actions_future": ["send_template", "send_approved_reply"],
                "current_behavior": "contract_only_no_live_call",
            },
            {
                **base,
                "adapter_id": "render_deploy",
                "provider": "render",
                "purpose": "deploy futuro assistido",
                "risk_level": "high",
                "env_vars": ["RENDER_API_KEY", "RENDER_SERVICE_ID"],
                "allowed_actions_future": ["trigger_deploy", "read_logs", "read_service_status"],
                "current_behavior": "contract_only_no_live_call",
            },
            {
                **base,
                "adapter_id": "github_release",
                "provider": "github",
                "purpose": "release futura supervisionada",
                "risk_level": "high",
                "env_vars": ["GITHUB_TOKEN"],
                "allowed_actions_future": ["create_release", "tag_version"],
                "current_behavior": "contract_only_no_live_call",
            },
            {
                **base,
                "adapter_id": "openai_live",
                "provider": "openai",
                "purpose": "execucao IA futura via OpenAI",
                "risk_level": "medium",
                "env_vars": ["OPENAI_API_KEY"],
                "allowed_actions_future": ["text_reasoning", "agent_orchestration", "embedding"],
                "current_behavior": "contract_only_no_live_call",
            },
            {
                **base,
                "adapter_id": "google_vertex_live",
                "provider": "google_vertex",
                "purpose": "geracao audiovisual futura via Vertex",
                "risk_level": "high",
                "env_vars": ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"],
                "allowed_actions_future": ["image_generation", "video_generation", "multimodal_analysis"],
                "current_behavior": "contract_only_no_live_call",
            },
            {
                **base,
                "adapter_id": "google_ai_live",
                "provider": "google_ai",
                "purpose": "uso futuro de Google AI Studio/Gemini",
                "risk_level": "medium",
                "env_vars": ["GOOGLE_API_KEY"],
                "allowed_actions_future": ["text_reasoning", "multimodal_analysis"],
                "current_behavior": "contract_only_no_live_call",
            },
        ]

    def env_status(self, env_vars: list[str]) -> list[dict[str, Any]]:
        rows = []
        for name in env_vars:
            present = bool(os.environ.get(name))
            rows.append({
                "name": name,
                "present": present,
                "value_preview": "configured" if present else "missing",
                "value_exposed": False,
            })
        return rows

    def register_contracts(self, contracts: list[Mapping[str, Any]] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        raw_contracts = [dict(item) for item in (contracts or self.default_contracts())]

        rows = []
        blocked = 0

        for item in raw_contracts:
            validation = validate_live_adapter_contract(item)
            if not validation["ok"]:
                blocked += 1

            rows.append({
                "contract": item,
                "validation": validation,
                "env_status": self.env_status(item.get("env_vars", [])),
                "safe_state": {
                    "enabled": False,
                    "live_call": False,
                    "real_execution_enabled": False,
                    "external_side_effects": "none",
                },
            })

        report = {
            "ok": blocked == 0,
            "checkpoint": "56",
            "name": "Live Adapter Contract Registry",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "registered" if blocked == 0 else "needs_review",
            "summary": {
                "contracts_total": len(rows),
                "contracts_allowed": len(rows) - blocked,
                "contracts_blocked": blocked,
                "live_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "revisar contratos e manter real execution bloqueado ate adapter especifico",
            },
            "contracts": rows,
            "guardrails": [
                "contratos nao executam API real",
                "nenhum adapter live habilitado",
                "toda acao externa exige approval gate",
                "tokens somente em variaveis de ambiente",
                "sem publicacao automatica",
                "sem envio automatico",
                "sem deploy automatico",
            ],
            "next_checkpoint": "57 - Adapter Dry Run Orchestrator",
        }

        self.save_registry(report)
        self.save_report(report)

        self.event("live_adapter_contract_registry.registered", {
            "run_id": run_id,
            "status": report["status"],
            "contracts_total": len(rows),
            "contracts_blocked": blocked,
        })

        return report

    def load_latest(self) -> dict[str, Any]:
        latest = self.reports_dir / "latest_live_adapter_contract_registry.json"
        if not latest.exists():
            return self.register_contracts()

        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else self.register_contracts()
        except Exception:
            return self.register_contracts()

    def save_registry(self, report: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(
            json.dumps(report.get("contracts", []), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_live_adapter_contract_registry.json"
        latest_md = self.reports_dir / "latest_live_adapter_contract_registry.md"

        latest_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Live Adapter Contract Registry",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Contracts total: {summary.get('contracts_total')}",
            f"- Contracts allowed: {summary.get('contracts_allowed')}",
            f"- Contracts blocked: {summary.get('contracts_blocked')}",
            f"- Live execution enabled: {summary.get('live_execution_enabled')}",
            f"- External side effects: {summary.get('external_side_effects')}",
            "",
            "## Contracts",
            "",
        ]

        for item in report.get("contracts", []):
            contract = item.get("contract", {})
            validation = item.get("validation", {})
            lines.append(f"- {contract.get('adapter_id')} | {contract.get('provider')} | {contract.get('risk_level')} | {validation.get('status')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for guardrail in report.get("guardrails", []):
            lines.append(f"- {guardrail}")

        return "\n".join(lines)
