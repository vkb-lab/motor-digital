from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.mission_planner.planner import MissionPlanner

from .policy import validate_social_growth_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SocialGrowthMissionPack:
    def __init__(
        self,
        reports_dir: str | Path = "reports/social_growth_mission_pack",
        memory_dir: str | Path = "memory/social_growth_mission_pack",
        mission_planner: MissionPlanner | None = None,
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"
        self.mission_planner = mission_planner or MissionPlanner()

    def default_payload(self) -> dict[str, Any]:
        return {
            "brand": "K-Atlas OS",
            "channel": "instagram",
            "objective": "construir autoridade publica do K-Atlas como sistema operacional de agentes IA",
            "audience": "empreendedores, operadores de marketing, criadores de SaaS, agencias e negocios locais",
            "tone": "arrojado, tecnico, direto, visionario e comercial",
            "offer": "K-Atlas como central de agentes, automacoes, SaaS Factory e cockpit operacional",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
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

    def build_content_calendar(self, payload: Mapping[str, Any]) -> list[dict[str, Any]]:
        brand = payload.get("brand", "K-Atlas OS")
        audience = payload.get("audience", "empreendedores")
        offer = payload.get("offer", "sistema de agentes IA")

        return [
            {
                "day": 1,
                "format": "reel",
                "theme": "manifesto",
                "hook": "O futuro nao e um app. E um sistema operacional de agentes IA.",
                "angle": f"{brand} como infraestrutura para {audience}.",
                "cta": "acompanhe a construcao publica do K-Atlas",
            },
            {
                "day": 2,
                "format": "carousel",
                "theme": "arquitetura",
                "hook": "Como transformar comandos soltos em operacao autonoma supervisionada.",
                "angle": "Local Daemon, Command Center, Mission Planner e SaaS Factory.",
                "cta": "salve para estudar a arquitetura",
            },
            {
                "day": 3,
                "format": "reel",
                "theme": "prova operacional",
                "hook": "Um agente nao precisa prometer. Precisa executar, registrar e prestar contas.",
                "angle": "logs, smoke tests, GitHub, Render e cockpit.",
                "cta": "veja o cockpit em evolucao",
            },
            {
                "day": 4,
                "format": "story_sequence",
                "theme": "bastidores",
                "hook": "Hoje o K-Atlas ganhou uma nova camada de autonomia assistida.",
                "angle": "mostrar progresso sem expor segredos nem tokens.",
                "cta": "responda qual modulo voce criaria primeiro",
            },
            {
                "day": 5,
                "format": "carousel",
                "theme": "SaaS Factory",
                "hook": "A proxima agencia nao entrega posts. Entrega maquinas de receita.",
                "angle": f"{offer} aplicado a produtos digitais reais.",
                "cta": "entre na lista de acompanhamento",
            },
            {
                "day": 6,
                "format": "reel",
                "theme": "governanca",
                "hook": "Autonomia sem auditoria e brinquedo perigoso.",
                "angle": "por que o K-Atlas bloqueia publicacao automatica ate estar pronto.",
                "cta": "comente AUTONOMIA para receber o mapa",
            },
            {
                "day": 7,
                "format": "post_static",
                "theme": "convite",
                "hook": "Estamos construindo um unicornio gerador de unicornios.",
                "angle": "visao publica do ecossistema K-Atlas.",
                "cta": "siga a jornada",
            },
        ]

    def build_creative_briefs(self, payload: Mapping[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "asset": "hero_video",
                "duration": "15s",
                "style": "futurista, limpo, startup AI, cockpit operacional",
                "script": "K-Atlas OS: agentes, memoria, automacao, SaaS Factory e supervisao humana.",
                "status": "planned_no_api",
            },
            {
                "asset": "profile_identity",
                "format": "avatar + banner",
                "style": "tecnico premium, minimalista, IA operacional",
                "status": "planned_no_api",
            },
            {
                "asset": "carousel_template",
                "slides": 7,
                "style": "dark clean, codigo, cockpit, grafos, produto",
                "status": "planned_no_api",
            },
        ]

    def build_mission_payload(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "title": "Missao Social Growth K-Atlas",
            "mission_type": "growth_planning",
            "objective": "planejar crescimento social do K-Atlas com calendario, criativos e auditoria sem publicacao automatica",
            "priority": "high",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
            "source_pack": "social_growth_mission_pack",
            "brand": payload.get("brand"),
            "channel": payload.get("channel"),
        }

    def generate(self, payload: Mapping[str, Any] | None = None, enqueue_mission: bool = True) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_social_growth_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "46",
                "name": "Social Growth Mission Pack",
                "run_id": run_id,
                "status": "blocked_by_policy",
                "created_at": utc_now(),
                "payload": data,
                "validation": validation,
            }
            self.save_report(report)
            return report

        calendar = self.build_content_calendar(data)
        creative_briefs = self.build_creative_briefs(data)
        mission_payload = self.build_mission_payload(data)

        mission_result = {
            "ok": False,
            "status": "not_enqueued",
        }

        if enqueue_mission:
            mission_result = self.mission_planner.plan_and_enqueue(mission_payload)

        report = {
            "ok": True,
            "checkpoint": "46",
            "name": "Social Growth Mission Pack",
            "run_id": run_id,
            "status": "planned",
            "created_at": utc_now(),
            "payload": data,
            "validation": validation,
            "calendar": calendar,
            "creative_briefs": creative_briefs,
            "mission_payload": mission_payload,
            "mission_result": mission_result,
            "guardrails": [
                "sem publicacao automatica",
                "sem API externa real",
                "sem automacao de navegador",
                "sem mensagem em massa",
                "sem token em texto puro",
                "conteudo aprovado apenas para planejamento e uso manual",
            ],
            "next_checkpoint": "47 - SaaS Product Mission Pack",
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_social_growth_mission_pack.json"
        latest_md = self.reports_dir / "latest_social_growth_mission_pack.md"
        run_json = self.reports_dir / f"{report.get('run_id', 'unknown')}.json"

        latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        run_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        self.event("social_growth_pack.generated", {
            "run_id": report.get("run_id"),
            "status": report.get("status"),
            "ok": report.get("ok"),
        })

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas Social Growth Mission Pack",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Brand: {report.get('payload', {}).get('brand')}",
            f"Channel: {report.get('payload', {}).get('channel')}",
            "",
            "## Calendario de 7 dias",
            "",
        ]

        for item in report.get("calendar", []):
            lines.append(f"- Dia {item.get('day')}: {item.get('format')} | {item.get('hook')}")

        lines.extend([
            "",
            "## Creative briefs",
            "",
        ])

        for item in report.get("creative_briefs", []):
            lines.append(f"- {item.get('asset')}: {item.get('style')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
