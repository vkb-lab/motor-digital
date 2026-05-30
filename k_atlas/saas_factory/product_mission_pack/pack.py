from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.mission_planner.planner import MissionPlanner

from .policy import validate_saas_product_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SaasProductMissionPack:
    def __init__(
        self,
        reports_dir: str | Path = "reports/saas_product_mission_pack",
        memory_dir: str | Path = "memory/saas_product_mission_pack",
        mission_planner: MissionPlanner | None = None,
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"
        self.mission_planner = mission_planner or MissionPlanner()

    def default_payload(self) -> dict[str, Any]:
        return {
            "product_name": "K-Atlas Mini SaaS Factory",
            "audience": "pequenos negocios, agencias, operadores de marketing e empreendedores locais",
            "problem": "criar MVPs, landing pages, campanhas e automacoes ainda exige muita ferramenta solta e retrabalho",
            "solution": "um cockpit que transforma uma ideia em MVP operacional, campanha, memoria, relatorio e plano de deploy",
            "pricing_hint": "assinatura mensal + setup de implantacao",
            "market_position": "sistema operacional de agentes IA para gerar produtos digitais e operacoes comerciais",
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

    def build_mvp_modules(self, payload: Mapping[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "module": "intake",
                "name": "Briefing inteligente",
                "description": "captura problema, publico, oferta, restricoes e objetivo comercial",
                "priority": "P0",
            },
            {
                "module": "planner",
                "name": "Mission Planner",
                "description": "transforma o briefing em plano de produto, tarefas e checkpoints",
                "priority": "P0",
            },
            {
                "module": "builder",
                "name": "SaaS Builder Agent",
                "description": "gera estrutura inicial do MVP, app, paginas e dados",
                "priority": "P0",
            },
            {
                "module": "creative",
                "name": "Creative Media Gateway",
                "description": "gera prompts, briefs e assets planejados para audiovisual e identidade",
                "priority": "P1",
            },
            {
                "module": "campaign",
                "name": "Campaign Pack",
                "description": "gera oferta, copy, calendario, canais e funil inicial",
                "priority": "P1",
            },
            {
                "module": "deploy",
                "name": "Deploy Pipeline Assistido",
                "description": "valida readiness, rollback e checklist sem deploy automatico",
                "priority": "P1",
            },
            {
                "module": "reporting",
                "name": "AutoReporter",
                "description": "gera relatorio operacional e historico de evolucao",
                "priority": "P0",
            },
        ]

    def build_landing_spec(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        product_name = payload.get("product_name", "Produto SaaS")
        audience = payload.get("audience", "usuarios")
        problem = payload.get("problem", "problema operacional")
        solution = payload.get("solution", "solucao operacional")

        return {
            "headline": f"{product_name}: transforme ideia em operacao digital executavel",
            "subheadline": f"Para {audience} que precisam resolver: {problem}.",
            "promise": solution,
            "sections": [
                "hero com promessa clara",
                "dor do mercado",
                "como funciona",
                "modulos do MVP",
                "prova operacional",
                "planos e chamada para conversa",
                "FAQ e proximos passos",
            ],
            "primary_cta": "Entrar na lista de implantacao",
            "secondary_cta": "Ver demonstracao operacional",
            "visual_direction": "premium tecnico, cockpit IA, cards limpos, video hero, prova com logs",
        }

    def build_monetization(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "model": "assinatura + setup",
            "plans": [
                {
                    "name": "Starter",
                    "price_range": "R$ 297 - R$ 697/mês",
                    "target": "negocio local ou criador validando MVP",
                },
                {
                    "name": "Operator",
                    "price_range": "R$ 997 - R$ 2.997/mês",
                    "target": "agencia, operador comercial ou time enxuto",
                },
                {
                    "name": "Factory",
                    "price_range": "R$ 5.000+/mês",
                    "target": "operacao que cria multiplos produtos digitais",
                },
            ],
            "setup": "implantacao, personalizacao, integrações e treinamento supervisionado",
        }

    def build_execution_checklist(self, payload: Mapping[str, Any]) -> list[str]:
        return [
            "validar problema e publico",
            "gerar MVP spec",
            "gerar landing spec",
            "gerar campanha inicial",
            "gerar plano audiovisual",
            "rodar smoke tests",
            "criar deploy readiness",
            "criar relatorio de decisao humana",
            "aprovar proximo checkpoint",
        ]

    def build_mission_payload(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "title": "Missao SaaS Product K-Atlas",
            "mission_type": "saas_build",
            "objective": "transformar uma ideia de SaaS em MVP operacional, landing spec, plano comercial e deploy assistido",
            "priority": "high",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
            "source_pack": "saas_product_mission_pack",
            "product_name": payload.get("product_name"),
        }

    def generate(self, payload: Mapping[str, Any] | None = None, enqueue_mission: bool = True) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_saas_product_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "47",
                "name": "SaaS Product Mission Pack",
                "run_id": run_id,
                "status": "blocked_by_policy",
                "created_at": utc_now(),
                "payload": data,
                "validation": validation,
            }
            self.save_report(report)
            return report

        mvp_modules = self.build_mvp_modules(data)
        landing_spec = self.build_landing_spec(data)
        monetization = self.build_monetization(data)
        execution_checklist = self.build_execution_checklist(data)
        mission_payload = self.build_mission_payload(data)

        mission_result = {
            "ok": False,
            "status": "not_enqueued",
        }

        if enqueue_mission:
            mission_result = self.mission_planner.plan_and_enqueue(mission_payload)

        report = {
            "ok": True,
            "checkpoint": "47",
            "name": "SaaS Product Mission Pack",
            "run_id": run_id,
            "status": "planned",
            "created_at": utc_now(),
            "payload": data,
            "validation": validation,
            "mvp_modules": mvp_modules,
            "landing_spec": landing_spec,
            "monetization": monetization,
            "execution_checklist": execution_checklist,
            "mission_payload": mission_payload,
            "mission_result": mission_result,
            "guardrails": [
                "sem deploy automatico",
                "sem publicacao automatica",
                "sem API externa real",
                "sem mensagem em massa",
                "sem token em texto puro",
                "MVP apenas planejado e supervisionado",
            ],
            "next_checkpoint": "48 - Daily Operator Cockpit",
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_saas_product_mission_pack.json"
        latest_md = self.reports_dir / "latest_saas_product_mission_pack.md"
        run_json = self.reports_dir / f"{report.get('run_id', 'unknown')}.json"

        latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        run_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        self.event("saas_product_pack.generated", {
            "run_id": report.get("run_id"),
            "status": report.get("status"),
            "ok": report.get("ok"),
        })

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas SaaS Product Mission Pack",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Product: {report.get('payload', {}).get('product_name')}",
            "",
            "## MVP Modules",
            "",
        ]

        for item in report.get("mvp_modules", []):
            lines.append(f"- {item.get('priority')} | {item.get('name')}: {item.get('description')}")

        lines.extend([
            "",
            "## Landing",
            "",
            f"Headline: {report.get('landing_spec', {}).get('headline')}",
            f"CTA: {report.get('landing_spec', {}).get('primary_cta')}",
            "",
            "## Monetization",
            "",
            f"Model: {report.get('monetization', {}).get('model')}",
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
