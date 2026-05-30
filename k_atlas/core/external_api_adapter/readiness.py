from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_external_api_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExternalAPIAdapterReadiness:
    def __init__(
        self,
        reports_dir: str | Path = "reports/external_api_adapter",
        memory_dir: str | Path = "memory/external_api_adapter",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"

    def provider_registry(self) -> list[dict[str, Any]]:
        return [
            {
                "provider": "openai",
                "purpose": "LLM, agents, reasoning, tool orchestration",
                "env_vars": ["OPENAI_API_KEY"],
                "live_enabled": False,
                "approval_required": True,
            },
            {
                "provider": "google_ai",
                "purpose": "Gemini, imagem, video, multimodal, audiovisual",
                "env_vars": ["GOOGLE_API_KEY"],
                "live_enabled": False,
                "approval_required": True,
            },
            {
                "provider": "google_vertex",
                "purpose": "Vertex AI, Veo, Imagen, Gemini em ambiente cloud",
                "env_vars": ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"],
                "live_enabled": False,
                "approval_required": True,
            },
            {
                "provider": "meta_graph",
                "purpose": "Meta Graph API, Facebook, assets e business",
                "env_vars": ["META_APP_ID", "META_APP_SECRET", "META_ACCESS_TOKEN"],
                "live_enabled": False,
                "approval_required": True,
            },
            {
                "provider": "instagram_graph",
                "purpose": "Instagram oficial K-Atlas, leitura, insights e publicacao futura aprovada",
                "env_vars": ["INSTAGRAM_BUSINESS_ACCOUNT_ID", "META_ACCESS_TOKEN"],
                "live_enabled": False,
                "approval_required": True,
            },
            {
                "provider": "whatsapp_cloud",
                "purpose": "WhatsApp Cloud API para atendimento e automacoes futuras",
                "env_vars": ["WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_ACCESS_TOKEN"],
                "live_enabled": False,
                "approval_required": True,
            },
            {
                "provider": "render",
                "purpose": "deploy, logs e status cloud",
                "env_vars": ["RENDER_API_KEY", "RENDER_SERVICE_ID"],
                "live_enabled": False,
                "approval_required": True,
            },
            {
                "provider": "github",
                "purpose": "memoria persistente, repositorio, releases e auditoria",
                "env_vars": ["GITHUB_TOKEN"],
                "live_enabled": False,
                "approval_required": True,
            },
            {
                "provider": "cloudflare",
                "purpose": "tunel, DNS, proxy e edge futuramente",
                "env_vars": ["CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"],
                "live_enabled": False,
                "approval_required": True,
            },
        ]

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
        exists = bool(os.environ.get(name))

        return {
            "name": name,
            "present": exists,
            "value_preview": "configured" if exists else "missing",
            "value_exposed": False,
        }

    def check_provider(self, provider: Mapping[str, Any]) -> dict[str, Any]:
        payload = {
            "provider": provider.get("provider"),
            "env_vars": provider.get("env_vars", []),
            "live_call": False,
            "auto_publish": False,
            "official_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
        }

        validation = validate_external_api_payload(payload)
        env_checks = [self.check_env_var(name) for name in provider.get("env_vars", [])]

        present = sum(1 for item in env_checks if item["present"])
        total = len(env_checks)

        if not validation["ok"]:
            status = "blocked_by_policy"
        elif total == 0:
            status = "no_credentials_required"
        elif present == total:
            status = "credentials_configured_but_live_disabled"
        elif present == 0:
            status = "missing_credentials"
        else:
            status = "partial_credentials"

        return {
            "provider": provider.get("provider"),
            "purpose": provider.get("purpose"),
            "approval_required": provider.get("approval_required", True),
            "live_enabled": False,
            "status": status,
            "validation": validation,
            "env": env_checks,
            "configured_count": present,
            "required_count": total,
            "safe_to_call_live": False,
            "reason": "readiness_only_no_live_external_calls",
        }

    def generate(self) -> dict[str, Any]:
        run_id = str(uuid4())
        providers = self.provider_registry()
        checks = [self.check_provider(item) for item in providers]

        ready_count = sum(1 for item in checks if item["status"] == "credentials_configured_but_live_disabled")
        missing_count = sum(1 for item in checks if item["status"] == "missing_credentials")
        partial_count = sum(1 for item in checks if item["status"] == "partial_credentials")
        blocked_count = sum(1 for item in checks if item["status"] == "blocked_by_policy")

        report = {
            "ok": True,
            "checkpoint": "49",
            "name": "External API Adapter Readiness",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "readiness_generated",
            "summary": {
                "providers_total": len(checks),
                "credentials_configured": ready_count,
                "credentials_missing": missing_count,
                "credentials_partial": partial_count,
                "blocked": blocked_count,
                "live_external_calls_enabled": False,
                "next_action": "configurar variaveis de ambiente no Windows e Render, sem colar tokens no repositorio",
            },
            "providers": checks,
            "integration_sequence": [
                "50 - AI Provider Router",
                "51 - Google Audiovisual Adapter sandbox",
                "52 - Instagram Graph Readiness",
                "53 - WhatsApp Cloud Readiness",
                "54 - Secure Publish Approval Gate",
            ],
            "guardrails": [
                "nunca salvar token em arquivo",
                "nunca commitar .env",
                "usar apenas nomes de variaveis de ambiente",
                "live_call sempre false nesta fase",
                "publicacao exige aprovacao humana",
                "deploy exige aprovacao humana",
                "API real so depois de readiness e vault",
            ],
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_external_api_adapter_readiness.json"
        latest_md = self.reports_dir / "latest_external_api_adapter_readiness.md"
        run_json = self.reports_dir / f"{report.get('run_id', 'unknown')}.json"

        latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        run_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        self.event("external_api_adapter.readiness.generated", {
            "run_id": report.get("run_id"),
            "checkpoint": report.get("checkpoint"),
            "status": report.get("status"),
        })

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas External API Adapter Readiness",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Providers total: {summary.get('providers_total')}",
            f"- Credentials configured: {summary.get('credentials_configured')}",
            f"- Credentials missing: {summary.get('credentials_missing')}",
            f"- Credentials partial: {summary.get('credentials_partial')}",
            f"- Live external calls enabled: {summary.get('live_external_calls_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Providers",
            "",
        ]

        for item in report.get("providers", []):
            lines.append(f"- {item.get('provider')}: {item.get('status')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for guardrail in report.get("guardrails", []):
            lines.append(f"- {guardrail}")

        return "\n".join(lines)
