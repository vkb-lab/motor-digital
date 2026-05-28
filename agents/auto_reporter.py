# -*- coding: utf-8 -*-
"""
K-Atlas OS - Auto Reporter Agent

Agente de relatorios operacionais padronizados.

Objetivo:
Gerar relatorios Markdown para modulos, agentes, tarefas importantes,
mudancas de arquitetura e marcos operacionais do K-Atlas OS.

Uso CLI:
python agents/auto_reporter.py --module-name "Nome do Modulo" --objective "Objetivo" --files "a.py,b.py" --decision "aprovado com ressalvas"

Este agente foi desenhado para futura integracao com:
- kernel
- memory_agent
- learning_agent
- orchestrator_agent
- cockpit
- snapshots
- approvals
- auditoria
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from agents.base_agent import AgentContext, BaseAgent
except Exception:
    AgentContext = Any

    class BaseAgent:  # type: ignore
        def __init__(
            self,
            event_bus: Optional[Any] = None,
            permission_manager: Optional[Any] = None,
            config: Optional[Dict[str, Any]] = None,
        ) -> None:
            self.event_bus = event_bus
            self.permission_manager = permission_manager
            self.config = config or {}


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = ROOT / "reports" / "module_reports"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "module-report"


def as_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]

    text = str(value).strip()
    if not text:
        return []

    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]


def normalize_decision(value: str) -> str:
    allowed = [
        "aprovado",
        "aprovado com ressalvas",
        "reprojetar",
        "não expandir ainda",
        "nao expandir ainda",
    ]

    clean = str(value or "").strip().lower()

    if clean == "nao expandir ainda":
        return "não expandir ainda"

    if clean in allowed:
        return clean

    return "aprovado com ressalvas"


def clamp_score(value: Any, default: float = 7.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default

    if number < 0:
        return 0.0

    if number > 10:
        return 10.0

    return round(number, 1)


@dataclass
class ModuleReportInput:
    module_name: str
    objective: str
    files_changed: List[str] = field(default_factory=list)
    operational_flow: str = ""
    strengths: List[str] = field(default_factory=list)
    bottlenecks: List[str] = field(default_factory=list)
    future_risks: List[str] = field(default_factory=list)
    next_step: str = ""
    not_now: str = ""
    impact: str = ""
    scores: Dict[str, float] = field(default_factory=dict)
    professor_decision: str = "aprovado com ressalvas"
    decision_reason: str = ""
    created_by: str = "auto_reporter"
    tags: List[str] = field(default_factory=list)


class AutoReporter(BaseAgent):
    agent_id = "auto_reporter"
    name = "Auto Reporter"
    description = "Agente gerador de relatorios operacionais padronizados do K-Atlas OS."
    version = "0.1.0"

    capabilities = [
        "reports",
        "markdown",
        "audit",
        "governance",
        "module_analysis",
        "operational_review",
    ]

    permissions = [
        "agent.execute",
        "reports.read",
        "reports.write",
        "memory.read",
        "memory.write",
        "events.read",
    ]

    SCORE_FIELDS = [
        "arquitetura",
        "modularidade",
        "estabilidade",
        "escalabilidade",
        "clareza",
        "risco_operacional",
        "preparacao_futura",
        "maturidade_do_nucleo",
    ]

    REQUIRED_MARKERS = [
        "## 1. Objetivo do módulo",
        "## 2. Arquivos criados/alterados",
        "## 3. Fluxo operacional",
        "## 4. Pontos fortes",
        "## 5. Gargalos",
        "## 6. Riscos futuros",
        "## 7. Próximo passo correto",
        "## 8. Próximo passo que NÃO deve ser feito agora",
        "## 9. Impacto no K-Atlas OS",
        "## 10. Score do módulo",
        "## 11. Decisão do professor",
    ]

    def __init__(
        self,
        output_dir: Optional[str | Path] = None,
        event_bus: Optional[Any] = None,
        permission_manager: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            permission_manager=permission_manager,
            config=config,
        )

        configured_output_dir = self.config.get("output_dir") if hasattr(self, "config") else None
        self.output_dir = Path(output_dir or configured_output_dir or DEFAULT_REPORT_DIR)

    def metadata(self) -> Dict[str, Any]:
        return {
            "base_class": "BaseAgent",
            "type": "reporting",
            "created_for": "K-Atlas OS",
            "module_role": "operational_reporting_and_governance",
            "output_dir": str(self.output_dir),
        }

    def required_permission(self, context: AgentContext) -> str:
        return "agent.execute"

    def run(self, context: AgentContext) -> Dict[str, Any]:
        action = self._action(context.command)

        if action == "ping":
            return self._ping()

        if action in ["help", "commands"]:
            return self._help()

        if action in ["generate", "create", "report"]:
            return self.generate_report_from_payload(context.payload)

        if action in ["validate", "validate_report"]:
            return self.validate_report_file(context.payload)

        if action in ["list", "reports"]:
            return self.list_reports(context.payload)

        return {
            "success": False,
            "message": "Comando nao reconhecido pelo AutoReporter.",
            "action": action,
            "available_actions": [
                "ping",
                "help",
                "generate",
                "validate",
                "list",
            ],
        }

    def _action(self, command: str) -> str:
        clean = str(command).strip().lower()
        if "." in clean:
            return clean.split(".", 1)[1]
        return clean

    def _ping(self) -> Dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "agent_id": self.agent_id,
            "message": "AutoReporter operacional.",
            "output_dir": str(self.output_dir),
        }

    def _help(self) -> Dict[str, Any]:
        return {
            "success": True,
            "commands": {
                "auto_reporter.generate": "Gera relatorio Markdown padronizado.",
                "auto_reporter.validate": "Valida conteudo minimo de um relatorio.",
                "auto_reporter.list": "Lista relatorios gerados.",
            },
            "example_payload": {
                "module_name": "LearningAgent",
                "objective": "Criar sistema de aprendizado operacional.",
                "files_changed": ["agents/learning_agent.py", "smoke_test_learning_agent.py"],
                "professor_decision": "aprovado com ressalvas",
            },
        }

    def generate_report_from_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        report_input = self._build_input(payload)
        markdown = self.render_markdown(report_input)
        path = self.save_markdown(report_input.module_name, markdown)

        validation = self.validate_markdown(markdown)

        metadata = {
            "report_id": str(uuid.uuid4()),
            "module_name": report_input.module_name,
            "created_at": now_iso(),
            "created_by": report_input.created_by,
            "tags": report_input.tags,
            "path": str(path),
            "valid": validation["success"],
        }

        metadata_path = path.with_suffix(".json")
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "success": validation["success"],
            "message": "Relatorio operacional gerado.",
            "report_path": str(path),
            "metadata_path": str(metadata_path),
            "validation": validation,
            "metadata": metadata,
        }

    def validate_report_file(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        report_path = Path(str(payload.get("report_path", ""))).expanduser()

        if not report_path.is_absolute():
            report_path = ROOT / report_path

        if not report_path.exists():
            return {
                "success": False,
                "message": "Arquivo de relatorio nao encontrado.",
                "report_path": str(report_path),
            }

        markdown = report_path.read_text(encoding="utf-8")
        validation = self.validate_markdown(markdown)
        validation["report_path"] = str(report_path)

        return validation

    def list_reports(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        limit = int(payload.get("limit", 50))

        reports = []

        for path in sorted(self.output_dir.glob("*.md"))[-limit:]:
            reports.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                }
            )

        return {
            "success": True,
            "total": len(reports),
            "reports": reports,
        }

    def render_markdown(self, data: ModuleReportInput) -> str:
        scores = self._normalized_scores(data.scores)
        average_score = round(sum(scores.values()) / len(scores), 1)

        return "\n".join(
            [
                "# Relatório Operacional de Módulo - " + data.module_name,
                "",
                "Gerado em: `" + now_iso() + "`",
                "Gerado por: `" + data.created_by + "`",
                "",
                "## 1. Objetivo do módulo",
                "",
                data.objective or "Objetivo não informado.",
                "",
                "## 2. Arquivos criados/alterados",
                "",
                self._render_list(data.files_changed, "Nenhum arquivo informado."),
                "",
                "## 3. Fluxo operacional",
                "",
                data.operational_flow or "Fluxo operacional ainda não detalhado.",
                "",
                "## 4. Pontos fortes",
                "",
                self._render_list(data.strengths, "Nenhum ponto forte informado."),
                "",
                "## 5. Gargalos",
                "",
                self._render_list(data.bottlenecks, "Nenhum gargalo informado."),
                "",
                "## 6. Riscos futuros",
                "",
                self._render_list(data.future_risks, "Nenhum risco futuro informado."),
                "",
                "## 7. Próximo passo correto",
                "",
                data.next_step or "Próximo passo ainda não definido.",
                "",
                "## 8. Próximo passo que NÃO deve ser feito agora",
                "",
                data.not_now or "Nenhuma restrição informada.",
                "",
                "## 9. Impacto no K-Atlas OS",
                "",
                data.impact or "Impacto ainda não detalhado.",
                "",
                "## 10. Score do módulo",
                "",
                "| Critério | Score |",
                "|---|---:|",
                "| Arquitetura | " + str(scores["arquitetura"]) + " |",
                "| Modularidade | " + str(scores["modularidade"]) + " |",
                "| Estabilidade | " + str(scores["estabilidade"]) + " |",
                "| Escalabilidade | " + str(scores["escalabilidade"]) + " |",
                "| Clareza | " + str(scores["clareza"]) + " |",
                "| Risco operacional | " + str(scores["risco_operacional"]) + " |",
                "| Preparação futura | " + str(scores["preparacao_futura"]) + " |",
                "| Maturidade do núcleo | " + str(scores["maturidade_do_nucleo"]) + " |",
                "",
                "**Score médio:** `" + str(average_score) + " / 10`",
                "",
                "## 11. Decisão do professor",
                "",
                "**Decisão:** `" + normalize_decision(data.professor_decision) + "`",
                "",
                "**Motivo:**",
                "",
                data.decision_reason or "Decisão registrada sem justificativa detalhada.",
                "",
                "## Metadados operacionais",
                "",
                "- Tags: " + (", ".join(data.tags) if data.tags else "sem tags"),
                "- Formato: Markdown",
                "- Persistência: reports/module_reports/",
                "- Modo: relatório operacional padronizado",
                "",
            ]
        )

    def save_markdown(self, module_name: str, markdown: str) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = timestamp + "_" + slugify(module_name) + ".md"
        path = self.output_dir / filename

        path.write_text(markdown, encoding="utf-8")

        return path

    def validate_markdown(self, markdown: str) -> Dict[str, Any]:
        missing = [
            marker for marker in self.REQUIRED_MARKERS
            if marker not in markdown
        ]

        return {
            "success": len(missing) == 0,
            "missing_markers": missing,
            "required_total": len(self.REQUIRED_MARKERS),
            "found_total": len(self.REQUIRED_MARKERS) - len(missing),
        }

    def _build_input(self, payload: Dict[str, Any]) -> ModuleReportInput:
        module_name = str(payload.get("module_name", "")).strip()
        objective = str(payload.get("objective", "")).strip()

        if not module_name:
            raise ValueError("Campo obrigatorio ausente: module_name")

        if not objective:
            raise ValueError("Campo obrigatorio ausente: objective")

        return ModuleReportInput(
            module_name=module_name,
            objective=objective,
            files_changed=as_list(payload.get("files_changed", [])),
            operational_flow=str(payload.get("operational_flow", "")).strip(),
            strengths=as_list(payload.get("strengths", [])),
            bottlenecks=as_list(payload.get("bottlenecks", [])),
            future_risks=as_list(payload.get("future_risks", [])),
            next_step=str(payload.get("next_step", "")).strip(),
            not_now=str(payload.get("not_now", "")).strip(),
            impact=str(payload.get("impact", "")).strip(),
            scores=payload.get("scores", {}) if isinstance(payload.get("scores", {}), dict) else {},
            professor_decision=normalize_decision(str(payload.get("professor_decision", "aprovado com ressalvas"))),
            decision_reason=str(payload.get("decision_reason", "")).strip(),
            created_by=str(payload.get("created_by", "auto_reporter")).strip(),
            tags=as_list(payload.get("tags", [])),
        )

    def _normalized_scores(self, scores: Dict[str, Any]) -> Dict[str, float]:
        output: Dict[str, float] = {}

        defaults = {
            "arquitetura": 8.0,
            "modularidade": 8.0,
            "estabilidade": 7.5,
            "escalabilidade": 7.0,
            "clareza": 8.0,
            "risco_operacional": 7.0,
            "preparacao_futura": 8.0,
            "maturidade_do_nucleo": 7.5,
        }

        for field_name in self.SCORE_FIELDS:
            output[field_name] = clamp_score(scores.get(field_name, defaults[field_name]))

        return output

    def _render_list(self, items: List[str], fallback: str) -> str:
        clean_items = [
            str(item).strip()
            for item in items
            if str(item).strip()
        ]

        if not clean_items:
            return "- " + fallback

        return "\n".join("- " + item for item in clean_items)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agents/auto_reporter.py",
        description="Gerador de relatorios operacionais do K-Atlas OS.",
    )

    parser.add_argument("--module-name", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--files", default="")
    parser.add_argument("--flow", default="")
    parser.add_argument("--strengths", default="")
    parser.add_argument("--bottlenecks", default="")
    parser.add_argument("--risks", default="")
    parser.add_argument("--next-step", default="")
    parser.add_argument("--not-now", default="")
    parser.add_argument("--impact", default="")
    parser.add_argument("--decision", default="aprovado com ressalvas")
    parser.add_argument("--decision-reason", default="")
    parser.add_argument("--tags", default="")
    parser.add_argument("--output-dir", default=str(DEFAULT_REPORT_DIR))

    parser.add_argument("--score-arquitetura", type=float, default=8.0)
    parser.add_argument("--score-modularidade", type=float, default=8.0)
    parser.add_argument("--score-estabilidade", type=float, default=7.5)
    parser.add_argument("--score-escalabilidade", type=float, default=7.0)
    parser.add_argument("--score-clareza", type=float, default=8.0)
    parser.add_argument("--score-risco-operacional", type=float, default=7.0)
    parser.add_argument("--score-preparacao-futura", type=float, default=8.0)
    parser.add_argument("--score-maturidade-do-nucleo", type=float, default=7.5)

    return parser


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    reporter = AutoReporter(output_dir=args.output_dir)

    payload = {
        "module_name": args.module_name,
        "objective": args.objective,
        "files_changed": as_list(args.files),
        "operational_flow": args.flow,
        "strengths": as_list(args.strengths),
        "bottlenecks": as_list(args.bottlenecks),
        "future_risks": as_list(args.risks),
        "next_step": args.next_step,
        "not_now": args.not_now,
        "impact": args.impact,
        "professor_decision": args.decision,
        "decision_reason": args.decision_reason,
        "tags": as_list(args.tags),
        "created_by": "auto_reporter_cli",
        "scores": {
            "arquitetura": args.score_arquitetura,
            "modularidade": args.score_modularidade,
            "estabilidade": args.score_estabilidade,
            "escalabilidade": args.score_escalabilidade,
            "clareza": args.score_clareza,
            "risco_operacional": args.score_risco_operacional,
            "preparacao_futura": args.score_preparacao_futura,
            "maturidade_do_nucleo": args.score_maturidade_do_nucleo,
        },
    }

    result = reporter.generate_report_from_payload(payload)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
