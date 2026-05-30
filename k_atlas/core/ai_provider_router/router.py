from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_router_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AIProviderRouter:
    def __init__(
        self,
        reports_dir: str | Path = "reports/ai_provider_router",
        memory_dir: str | Path = "memory/ai_provider_router",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"

    def route_table(self) -> dict[str, dict[str, Any]]:
        return {
            "text_reasoning": {
                "primary": "openai",
                "fallback": "google_ai",
                "mode": "reasoning",
                "required_env": ["OPENAI_API_KEY"],
            },
            "agent_orchestration": {
                "primary": "openai",
                "fallback": "local_stub",
                "mode": "tool_orchestration",
                "required_env": ["OPENAI_API_KEY"],
            },
            "image_generation": {
                "primary": "google_vertex",
                "fallback": "openai",
                "mode": "image_generation",
                "required_env": ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"],
            },
            "video_generation": {
                "primary": "google_vertex",
                "fallback": "google_ai",
                "mode": "video_generation",
                "required_env": ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"],
            },
            "audio_generation": {
                "primary": "openai",
                "fallback": "google_ai",
                "mode": "audio_generation",
                "required_env": ["OPENAI_API_KEY"],
            },
            "social_caption": {
                "primary": "openai",
                "fallback": "google_ai",
                "mode": "marketing_copy",
                "required_env": ["OPENAI_API_KEY"],
            },
            "saas_build": {
                "primary": "openai",
                "fallback": "local_stub",
                "mode": "code_and_architecture",
                "required_env": ["OPENAI_API_KEY"],
            },
            "deploy_analysis": {
                "primary": "openai",
                "fallback": "local_stub",
                "mode": "ops_review",
                "required_env": ["OPENAI_API_KEY"],
            },
            "embedding": {
                "primary": "openai",
                "fallback": "local_stub",
                "mode": "embedding",
                "required_env": ["OPENAI_API_KEY"],
            },
            "multimodal_analysis": {
                "primary": "google_vertex",
                "fallback": "openai",
                "mode": "multimodal",
                "required_env": ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"],
            },
        }

    def default_payload(self) -> dict[str, Any]:
        return {
            "task_type": "video_generation",
            "objective": "planejar geracao audiovisual premium para campanhas K-Atlas",
            "preferred_provider": "",
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

    def env_status(self, names: list[str]) -> list[dict[str, Any]]:
        rows = []

        for name in names:
            present = bool(os.environ.get(name))
            rows.append({
                "name": name,
                "present": present,
                "value_preview": "configured" if present else "missing",
                "value_exposed": False,
            })

        return rows

    def provider_ready(self, provider: str, required_env: list[str]) -> bool:
        if provider == "local_stub":
            return True

        if not required_env:
            return False

        return all(bool(os.environ.get(name)) for name in required_env)

    def load_external_readiness(self) -> dict[str, Any]:
        path = Path("reports/external_api_adapter/latest_external_api_adapter_readiness.json")

        if not path.exists():
            return {
                "ok": False,
                "status": "missing",
                "path": str(path).replace("\\", "/"),
            }

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                "ok": True,
                "status": data.get("status", "loaded"),
                "path": str(path).replace("\\", "/"),
                "summary": data.get("summary", {}),
            }
        except Exception as exc:
            return {
                "ok": False,
                "status": "read_error",
                "path": str(path).replace("\\", "/"),
                "error": f"{type(exc).__name__}: {exc}",
            }

    def route(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())

        validation = validate_router_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "50",
                "name": "AI Provider Router",
                "run_id": run_id,
                "status": "blocked_by_policy",
                "generated_at": utc_now(),
                "payload": data,
                "validation": validation,
            }
            self.save_report(report)
            return report

        task_type = data["task_type"]
        table = self.route_table()
        route_config = table[task_type]

        preferred = str(data.get("preferred_provider", "")).strip()
        primary = preferred or route_config["primary"]
        fallback = route_config["fallback"]
        required_env = route_config["required_env"]

        primary_ready = self.provider_ready(primary, required_env)
        fallback_ready = self.provider_ready(fallback, [] if fallback == "local_stub" else required_env)

        if primary_ready:
            selected = primary
            selected_reason = "primary_ready"
        elif fallback_ready:
            selected = fallback
            selected_reason = "fallback_ready"
        else:
            selected = "local_stub"
            selected_reason = "credentials_missing_using_stub"

        report = {
            "ok": True,
            "checkpoint": "50",
            "name": "AI Provider Router",
            "run_id": run_id,
            "status": "route_planned",
            "generated_at": utc_now(),
            "payload": data,
            "validation": validation,
            "task_type": task_type,
            "mode": route_config["mode"],
            "selected_provider": selected,
            "selected_reason": selected_reason,
            "primary_provider": primary,
            "fallback_provider": fallback,
            "required_env": required_env,
            "env_status": self.env_status(required_env),
            "live_call_enabled": False,
            "external_readiness": self.load_external_readiness(),
            "execution_contract": {
                "can_execute_now": selected == "local_stub",
                "live_execution_requires": [
                    "variaveis de ambiente configuradas",
                    "approval gate humano",
                    "adapter especifico por provider",
                    "logs e rollback",
                ],
                "current_behavior": "route_only_no_external_api_call",
            },
            "guardrails": [
                "sem chamada externa real",
                "sem token em arquivo",
                "sem publicacao automatica",
                "sem deploy automatico",
                "sem automacao de navegador",
                "provider selecionado apenas para planejamento",
            ],
            "next_checkpoint": "51 - Google Audiovisual Adapter Sandbox",
        }

        self.save_report(report)
        return report

    def build_matrix(self) -> dict[str, Any]:
        rows = []

        for task_type, config in self.route_table().items():
            payload = {
                "task_type": task_type,
                "objective": f"avaliar rota para {task_type}",
                "live_call": False,
                "official_publish": False,
                "auto_publish": False,
                "auto_deploy": False,
                "mass_messaging": False,
                "browser_automation": False,
            }

            routed = self.route(payload)

            rows.append({
                "task_type": task_type,
                "mode": routed.get("mode"),
                "selected_provider": routed.get("selected_provider"),
                "selected_reason": routed.get("selected_reason"),
                "required_env": routed.get("required_env", []),
            })

        matrix = {
            "ok": True,
            "checkpoint": "50",
            "name": "AI Provider Router Matrix",
            "generated_at": utc_now(),
            "status": "matrix_generated",
            "routes": rows,
            "live_call_enabled": False,
        }

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_ai_provider_router_matrix.json").write_text(
            json.dumps(matrix, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return matrix

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_ai_provider_router.json"
        latest_md = self.reports_dir / "latest_ai_provider_router.md"
        run_json = self.reports_dir / f"{report.get('run_id', 'unknown')}.json"

        latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        run_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        self.event("ai_provider_router.route.planned", {
            "run_id": report.get("run_id"),
            "task_type": report.get("task_type"),
            "selected_provider": report.get("selected_provider"),
            "status": report.get("status"),
        })

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas AI Provider Router",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Task type: {report.get('task_type')}",
            f"Mode: {report.get('mode')}",
            f"Selected provider: {report.get('selected_provider')}",
            f"Reason: {report.get('selected_reason')}",
            f"Live call enabled: {report.get('live_call_enabled')}",
            "",
            "## Required env",
            "",
        ]

        for item in report.get("env_status", []):
            lines.append(f"- {item.get('name')}: {item.get('value_preview')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for guardrail in report.get("guardrails", []):
            lines.append(f"- {guardrail}")

        return "\n".join(lines)
