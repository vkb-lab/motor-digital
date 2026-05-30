from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_whatsapp_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WhatsAppCloudReadiness:
    def __init__(
        self,
        reports_dir: str | Path = "reports/whatsapp_cloud_readiness",
        memory_dir: str | Path = "memory/whatsapp_cloud_readiness",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"

    def default_payload(self) -> dict[str, Any]:
        return {
            "objective": "readiness",
            "brand": "K-Atlas OS",
            "channel": "whatsapp_cloud",
            "use_case": "atendimento, captação, suporte e acompanhamento supervisionado",
            "env_vars": [
                "WHATSAPP_ACCESS_TOKEN",
                "WHATSAPP_PHONE_NUMBER_ID",
                "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "META_APP_ID",
                "META_APP_SECRET",
                "META_VERIFY_TOKEN",
            ],
            "live_call": False,
            "auto_send": False,
            "mass_messaging": False,
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "browser_automation": False,
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

    def check_env_var(self, name: str) -> dict[str, Any]:
        present = bool(os.environ.get(name))

        return {
            "name": name,
            "present": present,
            "value_preview": "configured" if present else "missing",
            "value_exposed": False,
        }

    def env_status(self, payload: Mapping[str, Any]) -> list[dict[str, Any]]:
        names = payload.get("env_vars", [])
        return [self.check_env_var(str(name)) for name in names]

    def build_connection_checklist(self) -> list[dict[str, Any]]:
        return [
            {
                "step": 1,
                "title": "Criar ou confirmar Meta Business",
                "status": "manual_required",
                "notes": "Usar estrutura oficial do ecossistema K-Atlas.",
            },
            {
                "step": 2,
                "title": "Ativar WhatsApp Cloud API no Meta App",
                "status": "manual_required",
                "notes": "Associar número de telefone e Business Account.",
            },
            {
                "step": 3,
                "title": "Configurar Webhook futuro",
                "status": "future_checkpoint",
                "notes": "Receber mensagens só depois de endpoint seguro e validação.",
            },
            {
                "step": 4,
                "title": "Salvar variáveis de ambiente",
                "status": "pending",
                "notes": "Nunca colar token no repositório, JSON, README ou chat.",
            },
            {
                "step": 5,
                "title": "Criar templates aprovados",
                "status": "manual_required",
                "notes": "Templates de mensagem precisam seguir política da Meta.",
            },
            {
                "step": 6,
                "title": "Ativar sandbox local",
                "status": "planned",
                "notes": "Simular entrada e saída sem envio real.",
            },
            {
                "step": 7,
                "title": "Criar Approval Gate de mensagem",
                "status": "future_checkpoint",
                "notes": "Nenhuma mensagem sai sem aprovação humana.",
            },
        ]

    def build_message_policy(self) -> dict[str, Any]:
        return {
            "allowed_now": [
                "planejar fluxos",
                "criar templates",
                "validar variáveis de ambiente",
                "simular atendimento",
                "gerar relatórios",
            ],
            "blocked_now": [
                "enviar mensagem real",
                "disparo em massa",
                "responder usuário real automaticamente",
                "usar token em texto puro",
                "automatizar navegador",
            ],
            "future_allowed_with_gate": [
                "responder lead com aprovação",
                "enviar template aprovado",
                "registrar conversa no cockpit",
                "encaminhar lead para operador humano",
            ],
        }

    def build_flow_blueprint(self) -> list[dict[str, Any]]:
        return [
            {
                "flow": "lead_capture",
                "trigger": "usuário chama no WhatsApp",
                "steps": [
                    "registrar entrada",
                    "classificar intenção",
                    "gerar resposta sugerida",
                    "aguardar aprovação humana",
                    "enviar apenas depois do Approval Gate",
                ],
                "status": "planned_no_live_send",
            },
            {
                "flow": "support_triage",
                "trigger": "mensagem de suporte",
                "steps": [
                    "identificar categoria",
                    "buscar memória operacional",
                    "sugerir resposta",
                    "registrar evento",
                    "escalar para humano se necessário",
                ],
                "status": "planned_no_live_send",
            },
            {
                "flow": "campaign_followup",
                "trigger": "lead opt-in futuro",
                "steps": [
                    "validar consentimento",
                    "selecionar template aprovado",
                    "gerar payload",
                    "aguardar aprovação",
                    "registrar envio",
                ],
                "status": "blocked_until_gate",
            },
        ]

    def build_env_commands_template(self) -> dict[str, Any]:
        return {
            "windows_user_env_template": [
                "[Environment]::SetEnvironmentVariable('WHATSAPP_ACCESS_TOKEN', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('WHATSAPP_PHONE_NUMBER_ID', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('WHATSAPP_BUSINESS_ACCOUNT_ID', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('META_APP_ID', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('META_APP_SECRET', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('META_VERIFY_TOKEN', '<valor>', 'User')",
            ],
            "render_env_names": [
                "WHATSAPP_ACCESS_TOKEN",
                "WHATSAPP_PHONE_NUMBER_ID",
                "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "META_APP_ID",
                "META_APP_SECRET",
                "META_VERIFY_TOKEN",
            ],
            "security_note": "Preencher valores manualmente no Windows ou Render. Nunca commitar valores.",
        }

    def generate(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_whatsapp_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "53",
                "name": "WhatsApp Cloud Readiness",
                "run_id": run_id,
                "status": "blocked_by_policy",
                "generated_at": utc_now(),
                "payload": data,
                "validation": validation,
            }
            self.save_report(report)
            return report

        env_checks = self.env_status(data)
        configured = sum(1 for item in env_checks if item["present"])
        required = len(env_checks)

        if configured == required and required > 0:
            readiness_status = "credentials_configured_but_live_disabled"
        elif configured == 0:
            readiness_status = "missing_credentials"
        else:
            readiness_status = "partial_credentials"

        report = {
            "ok": True,
            "checkpoint": "53",
            "name": "WhatsApp Cloud Readiness",
            "run_id": run_id,
            "status": readiness_status,
            "generated_at": utc_now(),
            "payload": data,
            "validation": validation,
            "env_status": env_checks,
            "summary": {
                "required_env_vars": required,
                "configured_env_vars": configured,
                "live_call_enabled": False,
                "message_send_enabled": False,
                "mass_messaging_enabled": False,
                "next_action": "configurar Meta Business, WhatsApp Cloud API e variáveis de ambiente sem expor tokens",
            },
            "connection_checklist": self.build_connection_checklist(),
            "message_policy": self.build_message_policy(),
            "flow_blueprint": self.build_flow_blueprint(),
            "env_commands_template": self.build_env_commands_template(),
            "guardrails": [
                "sem chamada real ao WhatsApp Cloud",
                "sem envio de mensagem real",
                "sem disparo em massa",
                "sem token em arquivo",
                "sem token em JSON",
                "sem automação de navegador",
                "mensagem futura exige Approval Gate humano",
            ],
            "next_checkpoint": "54 - Secure Publish Approval Gate",
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_whatsapp_cloud_readiness.json"
        latest_md = self.reports_dir / "latest_whatsapp_cloud_readiness.md"
        run_json = self.reports_dir / f"{report.get('run_id', 'unknown')}.json"

        latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        run_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        self.event("whatsapp_cloud.readiness.generated", {
            "run_id": report.get("run_id"),
            "checkpoint": report.get("checkpoint"),
            "status": report.get("status"),
        })

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas WhatsApp Cloud Readiness",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Generated at: {report.get('generated_at')}",
            "",
            "## Summary",
            "",
            f"- Required env vars: {summary.get('required_env_vars')}",
            f"- Configured env vars: {summary.get('configured_env_vars')}",
            f"- Live call enabled: {summary.get('live_call_enabled')}",
            f"- Message send enabled: {summary.get('message_send_enabled')}",
            f"- Mass messaging enabled: {summary.get('mass_messaging_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Env vars",
            "",
        ]

        for item in report.get("env_status", []):
            lines.append(f"- {item.get('name')}: {item.get('value_preview')}")

        lines.extend([
            "",
            "## Connection checklist",
            "",
        ])

        for item in report.get("connection_checklist", []):
            lines.append(f"- {item.get('step')}. {item.get('title')} | {item.get('status')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for guardrail in report.get("guardrails", []):
            lines.append(f"- {guardrail}")

        return "\n".join(lines)
