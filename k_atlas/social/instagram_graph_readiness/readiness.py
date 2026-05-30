from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.external_api_adapter.readiness import ExternalAPIAdapterReadiness

from .policy import validate_instagram_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InstagramGraphReadiness:
    def __init__(
        self,
        reports_dir: str | Path = "reports/instagram_graph_readiness",
        memory_dir: str | Path = "memory/instagram_graph_readiness",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"
        self.external_readiness = ExternalAPIAdapterReadiness()

    def default_payload(self) -> dict[str, Any]:
        return {
            "objective": "readiness",
            "brand": "K-Atlas OS",
            "channel": "instagram",
            "account_role": "official_public_channel",
            "env_vars": [
                "META_APP_ID",
                "META_APP_SECRET",
                "META_ACCESS_TOKEN",
                "META_BUSINESS_ID",
                "INSTAGRAM_BUSINESS_ACCOUNT_ID",
                "INSTAGRAM_PAGE_ID",
            ],
            "live_call": False,
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
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
                "title": "Criar ou definir Instagram oficial K-Atlas",
                "status": "manual_required",
                "notes": "Conta deve representar o ecossistema K-Atlas, nao apenas midias digitais.",
            },
            {
                "step": 2,
                "title": "Converter para conta profissional",
                "status": "manual_required",
                "notes": "Usar Business ou Creator conforme estrategia.",
            },
            {
                "step": 3,
                "title": "Conectar Instagram a uma Facebook Page",
                "status": "manual_required",
                "notes": "Necessario para Instagram Graph API.",
            },
            {
                "step": 4,
                "title": "Criar Meta App",
                "status": "manual_required",
                "notes": "Gerar App ID e configurar produtos do Meta for Developers.",
            },
            {
                "step": 5,
                "title": "Configurar permissoes",
                "status": "manual_required",
                "notes": "instagram_basic, instagram_manage_insights e futuras permissoes de publishing.",
            },
            {
                "step": 6,
                "title": "Salvar credenciais somente em variaveis de ambiente",
                "status": "pending",
                "notes": "Nunca colar tokens em codigo, README, JSON ou chat.",
            },
            {
                "step": 7,
                "title": "Rodar readiness novamente",
                "status": "pending",
                "notes": "Validar nomes de variaveis sem expor valores.",
            },
            {
                "step": 8,
                "title": "Ativar live API somente com Approval Gate",
                "status": "future_checkpoint",
                "notes": "Publicacao e automacao ficam bloqueadas ate checkpoint especifico.",
            },
        ]

    def build_permissions_matrix(self) -> list[dict[str, Any]]:
        return [
            {
                "capability": "profile_read",
                "permission": "instagram_basic",
                "risk": "low",
                "current_status": "planned_no_live_call",
                "human_approval_required": True,
            },
            {
                "capability": "insights_read",
                "permission": "instagram_manage_insights",
                "risk": "medium",
                "current_status": "planned_no_live_call",
                "human_approval_required": True,
            },
            {
                "capability": "media_list",
                "permission": "instagram_basic",
                "risk": "low",
                "current_status": "planned_no_live_call",
                "human_approval_required": True,
            },
            {
                "capability": "comment_management",
                "permission": "instagram_manage_comments",
                "risk": "medium",
                "current_status": "future",
                "human_approval_required": True,
            },
            {
                "capability": "content_publish",
                "permission": "instagram_content_publish",
                "risk": "high",
                "current_status": "blocked_until_publish_gate",
                "human_approval_required": True,
            },
        ]

    def build_content_contract(self) -> dict[str, Any]:
        return {
            "brand_scope": "K-Atlas OS como ecossistema completo de agentes IA, SaaS Factory, automacao, memoria e cockpit.",
            "not_only": [
                "nao limitar a Parada Atlantida",
                "nao limitar a midias digitais",
                "nao prometer autonomia total sem supervisao",
                "nao publicar prova sensivel, token, cliente ou dado privado",
            ],
            "allowed_themes": [
                "arquitetura do K-Atlas",
                "autonomia assistida",
                "SaaS Factory",
                "cockpit operacional",
                "agentes IA",
                "marketing inteligente",
                "memoria persistente",
                "bastidores tecnicos",
                "prova operacional com logs seguros",
            ],
            "publishing_policy": {
                "auto_publish": False,
                "official_publish": False,
                "requires_human_approval": True,
            },
        }

    def build_env_commands_template(self) -> dict[str, Any]:
        return {
            "windows_user_env_template": [
                "[Environment]::SetEnvironmentVariable('META_APP_ID', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('META_APP_SECRET', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('META_ACCESS_TOKEN', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('META_BUSINESS_ID', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('INSTAGRAM_BUSINESS_ACCOUNT_ID', '<valor>', 'User')",
                "[Environment]::SetEnvironmentVariable('INSTAGRAM_PAGE_ID', '<valor>', 'User')",
            ],
            "render_env_names": [
                "META_APP_ID",
                "META_APP_SECRET",
                "META_ACCESS_TOKEN",
                "META_BUSINESS_ID",
                "INSTAGRAM_BUSINESS_ACCOUNT_ID",
                "INSTAGRAM_PAGE_ID",
            ],
            "security_note": "Preencher valores manualmente no Windows/Render. Nunca commitar valores.",
        }

    def generate(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_instagram_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "52",
                "name": "Instagram Graph Readiness",
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
            "checkpoint": "52",
            "name": "Instagram Graph Readiness",
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
                "publishing_enabled": False,
                "next_action": "configurar conta Instagram profissional e variaveis de ambiente sem expor tokens",
            },
            "connection_checklist": self.build_connection_checklist(),
            "permissions_matrix": self.build_permissions_matrix(),
            "content_contract": self.build_content_contract(),
            "env_commands_template": self.build_env_commands_template(),
            "external_api_readiness_snapshot": self.external_readiness.generate().get("summary", {}),
            "guardrails": [
                "sem chamada real ao Instagram Graph",
                "sem publicacao automatica",
                "sem token em arquivo",
                "sem token em JSON",
                "sem automacao de navegador",
                "sem mensagem em massa",
                "publicacao futura exige Approval Gate humano",
            ],
            "next_checkpoint": "53 - WhatsApp Cloud Readiness",
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_instagram_graph_readiness.json"
        latest_md = self.reports_dir / "latest_instagram_graph_readiness.md"
        run_json = self.reports_dir / f"{report.get('run_id', 'unknown')}.json"

        latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        run_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        self.event("instagram_graph.readiness.generated", {
            "run_id": report.get("run_id"),
            "checkpoint": report.get("checkpoint"),
            "status": report.get("status"),
        })

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Instagram Graph Readiness",
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
            f"- Publishing enabled: {summary.get('publishing_enabled')}",
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
