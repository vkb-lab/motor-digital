from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.ai_provider_router.router import AIProviderRouter

from .policy import validate_audiovisual_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GoogleAudiovisualAdapterSandbox:
    def __init__(
        self,
        reports_dir: str | Path = "reports/google_audiovisual_adapter",
        memory_dir: str | Path = "memory/google_audiovisual_adapter",
        router: AIProviderRouter | None = None,
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"
        self.router = router or AIProviderRouter()

    def default_payload(self) -> dict[str, Any]:
        return {
            "brand": "K-Atlas OS",
            "asset_format": "hero_video",
            "objective": "criar video manifesto premium para apresentar o K-Atlas como sistema operacional de agentes IA",
            "audience": "empreendedores, agencias, operadores de marketing e criadores de SaaS",
            "duration_seconds": 15,
            "visual_style": "futurista limpo, cockpit operacional, IA premium, preto grafite, neon sutil, interface modular",
            "message": "O futuro nao e um app. E um sistema operacional de agentes IA.",
            "cta": "Acompanhe a construcao publica do K-Atlas",
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

    def env_status(self) -> list[dict[str, Any]]:
        names = [
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_CLOUD_PROJECT",
            "GOOGLE_CLOUD_LOCATION",
            "GOOGLE_API_KEY",
        ]

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

    def build_video_prompt(self, payload: Mapping[str, Any]) -> str:
        return (
            f"Create a premium cinematic {payload.get('duration_seconds', 15)} second video for {payload.get('brand')}. "
            f"Objective: {payload.get('objective')}. "
            f"Audience: {payload.get('audience')}. "
            f"Visual style: {payload.get('visual_style')}. "
            f"Core message: {payload.get('message')}. "
            "Show an AI operating system cockpit with modular agents, memory, automation pipelines, dashboards, "
            "GitHub persistence, cloud deployment and human supervision. "
            "No fake logos, no third-party trademarks, no exaggerated claims. "
            f"End with CTA: {payload.get('cta')}."
        )

    def build_shotlist(self, payload: Mapping[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "shot": 1,
                "duration": "0-3s",
                "scene": "dark premium cockpit booting up with modular AI nodes",
                "caption": "K-Atlas OS",
            },
            {
                "shot": 2,
                "duration": "3-6s",
                "scene": "agents moving tasks through memory, GitHub, reports and cockpit",
                "caption": "Agentes. Memoria. Execucao.",
            },
            {
                "shot": 3,
                "duration": "6-10s",
                "scene": "SaaS Factory generating product, landing, campaign and deploy checklist",
                "caption": "Ideia para produto operacional",
            },
            {
                "shot": 4,
                "duration": "10-13s",
                "scene": "human operator supervising approvals and safety gates",
                "caption": "Autonomia com supervisao",
            },
            {
                "shot": 5,
                "duration": "13-15s",
                "scene": "final brand lockup with clean futuristic interface",
                "caption": str(payload.get("cta", "Acompanhe")),
            },
        ]

    def build_image_prompt(self, payload: Mapping[str, Any]) -> str:
        return (
            f"Premium visual identity concept for {payload.get('brand')}. "
            f"Theme: {payload.get('objective')}. "
            f"Style: {payload.get('visual_style')}. "
            "Create a clean AI operating system cockpit, modular cards, agent nodes, task queues, memory streams, "
            "audit logs, subtle neon accents, dark graphite background, high-end SaaS aesthetic, no real brand logos."
        )

    def build_production_spec(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "provider_target": "google_vertex_or_google_ai_future",
            "asset_format": payload.get("asset_format"),
            "duration_seconds": payload.get("duration_seconds"),
            "aspect_ratios": {
                "instagram_reel": "9:16",
                "youtube_short": "9:16",
                "hero_video": "16:9",
                "ad_video": "1:1 or 9:16",
                "product_demo": "16:9",
                "image_concept": "1:1",
                "carousel_visual": "4:5",
            },
            "outputs_planned": [
                "video_prompt",
                "image_prompt",
                "shotlist",
                "caption",
                "approval_checklist",
            ],
            "approval_checklist": [
                "validar mensagem",
                "validar promessa comercial",
                "validar ausencia de marcas terceiras",
                "validar ausencia de dados sensiveis",
                "validar CTA",
                "aprovar manualmente antes de gerar/publicar",
            ],
        }

    def generate(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_audiovisual_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "51",
                "name": "Google Audiovisual Adapter Sandbox",
                "run_id": run_id,
                "status": "blocked_by_policy",
                "generated_at": utc_now(),
                "payload": data,
                "validation": validation,
            }
            self.save_report(report)
            return report

        router_result = self.router.route({
            "task_type": "video_generation" if data.get("asset_format") != "image_concept" else "image_generation",
            "objective": data.get("objective", ""),
            "preferred_provider": "google_vertex",
            "live_call": False,
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
        })

        report = {
            "ok": True,
            "checkpoint": "51",
            "name": "Google Audiovisual Adapter Sandbox",
            "run_id": run_id,
            "status": "sandbox_generated",
            "generated_at": utc_now(),
            "payload": data,
            "validation": validation,
            "router": router_result,
            "env_status": self.env_status(),
            "video_prompt": self.build_video_prompt(data),
            "image_prompt": self.build_image_prompt(data),
            "shotlist": self.build_shotlist(data),
            "production_spec": self.build_production_spec(data),
            "live_call_enabled": False,
            "side_effects": "planning_only_no_external_api_call",
            "guardrails": [
                "sem chamada Google real",
                "sem token em arquivo",
                "sem publicacao automatica",
                "sem deploy automatico",
                "sem automacao de navegador",
                "geracao real exige approval gate humano",
            ],
            "next_checkpoint": "52 - Instagram Graph Readiness",
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_google_audiovisual_adapter_sandbox.json"
        latest_md = self.reports_dir / "latest_google_audiovisual_adapter_sandbox.md"
        run_json = self.reports_dir / f"{report.get('run_id', 'unknown')}.json"

        latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        run_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        self.event("google_audiovisual_adapter.sandbox.generated", {
            "run_id": report.get("run_id"),
            "checkpoint": report.get("checkpoint"),
            "status": report.get("status"),
        })

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas Google Audiovisual Adapter Sandbox",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Asset: {report.get('payload', {}).get('asset_format')}",
            f"Live call: {report.get('live_call_enabled')}",
            "",
            "## Video prompt",
            "",
            str(report.get("video_prompt", "")),
            "",
            "## Image prompt",
            "",
            str(report.get("image_prompt", "")),
            "",
            "## Shotlist",
            "",
        ]

        for item in report.get("shotlist", []):
            lines.append(f"- Shot {item.get('shot')} | {item.get('duration')} | {item.get('caption')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
