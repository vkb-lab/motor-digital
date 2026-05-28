# -*- coding: utf-8 -*-
"""
K-Atlas OS - CLI

Interface de linha de comando para operar o K-Atlas OS localmente.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from k_atlas_boot import build_kernel


def parse_tags(value: str | None) -> List[str]:
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def parse_json_payload(value: str | None) -> Dict[str, Any]:
    if not value:
        return {}

    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit("Payload JSON invalido: " + str(exc)) from exc

    if not isinstance(data, dict):
        raise SystemExit("Payload precisa ser um objeto JSON.")

    return data


def execute(command: str, payload: Dict[str, Any] | None = None) -> int:
    kernel = build_kernel()

    try:
        result = kernel.execute(command, payload=payload or {}).to_dict()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("success") else 1

    finally:
        kernel.stop(save_state=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="k_atlas_cli.py",
        description="CLI operacional do K-Atlas OS.",
    )

    subparsers = parser.add_subparsers(dest="action", required=True)

    subparsers.add_parser("status", help="Mostra status do kernel.")
    subparsers.add_parser("agents", help="Lista agentes registrados.")
    subparsers.add_parser("task-stats", help="Mostra estatisticas de tarefas.")
    subparsers.add_parser("memory-stats", help="Mostra estatisticas de memoria.")
    subparsers.add_parser("learning-stats", help="Mostra estatisticas de aprendizado.")
    subparsers.add_parser("orchestrator-status", help="Mostra visao geral do orquestrador.")
    subparsers.add_parser("report-list", help="Lista relatorios operacionais gerados.")

    events = subparsers.add_parser("events", help="Lista eventos recentes.")
    events.add_argument("--limit", type=int, default=20)

    task_create = subparsers.add_parser("task-create", help="Cria uma tarefa.")
    task_create.add_argument("--title", required=True)
    task_create.add_argument("--description", default="")
    task_create.add_argument("--priority", default="normal")
    task_create.add_argument("--tags", default="")
    task_create.add_argument("--assigned-agent-id", default=None)

    task_list = subparsers.add_parser("task-list", help="Lista tarefas.")
    task_list.add_argument("--status", default=None)
    task_list.add_argument("--limit", type=int, default=50)

    task_complete = subparsers.add_parser("task-complete", help="Conclui uma tarefa.")
    task_complete.add_argument("task_id")

    memory_remember = subparsers.add_parser("memory-remember", help="Registra memoria.")
    memory_remember.add_argument("--title", required=True)
    memory_remember.add_argument("--content", required=True)
    memory_remember.add_argument("--type", default="note")
    memory_remember.add_argument("--tags", default="")
    memory_remember.add_argument("--source", default="operator")
    memory_remember.add_argument("--importance", type=int, default=1)

    memory_search = subparsers.add_parser("memory-search", help="Busca memoria.")
    memory_search.add_argument("query")
    memory_search.add_argument("--limit", type=int, default=50)

    memory_list = subparsers.add_parser("memory-list", help="Lista memorias.")
    memory_list.add_argument("--type", default=None)
    memory_list.add_argument("--tag", default=None)
    memory_list.add_argument("--limit", type=int, default=50)

    learning_learn = subparsers.add_parser("learning-learn", help="Registra aprendizado.")
    learning_learn.add_argument("--title", required=True)
    learning_learn.add_argument("--content", required=True)
    learning_learn.add_argument("--type", default="lesson")
    learning_learn.add_argument("--tags", default="")
    learning_learn.add_argument("--source", default="operator")
    learning_learn.add_argument("--importance", type=int, default=1)

    learning_error = subparsers.add_parser("learning-error", help="Registra erro operacional.")
    learning_error.add_argument("--title", required=True)
    learning_error.add_argument("--symptom", required=True)
    learning_error.add_argument("--cause", default="")
    learning_error.add_argument("--fix", default="")
    learning_error.add_argument("--prevention", default="")
    learning_error.add_argument("--severity", default="medium")
    learning_error.add_argument("--tags", default="")
    learning_error.add_argument("--source", default="operator")

    learning_playbook = subparsers.add_parser("learning-playbook", help="Cria playbook simples.")
    learning_playbook.add_argument("--title", required=True)
    learning_playbook.add_argument("--objective", required=True)
    learning_playbook.add_argument("--steps", required=True)
    learning_playbook.add_argument("--tags", default="")
    learning_playbook.add_argument("--source", default="operator")

    learning_search = subparsers.add_parser("learning-search", help="Busca conhecimento aprendido.")
    learning_search.add_argument("query")
    learning_search.add_argument("--limit", type=int, default=50)

    report_generate = subparsers.add_parser("report-generate", help="Gera relatorio operacional Markdown.")
    report_generate.add_argument("--module-name", required=True)
    report_generate.add_argument("--objective", required=True)
    report_generate.add_argument("--files", default="")
    report_generate.add_argument("--flow", default="")
    report_generate.add_argument("--strengths", default="")
    report_generate.add_argument("--bottlenecks", default="")
    report_generate.add_argument("--risks", default="")
    report_generate.add_argument("--next-step", default="")
    report_generate.add_argument("--not-now", default="")
    report_generate.add_argument("--impact", default="")
    report_generate.add_argument("--decision", default="aprovado com ressalvas")
    report_generate.add_argument("--decision-reason", default="")
    report_generate.add_argument("--tags", default="")

    orchestrator_plan = subparsers.add_parser("orchestrator-plan", help="Cria plano via orquestrador.")
    orchestrator_plan.add_argument("--goal", required=True)
    orchestrator_plan.add_argument("--description", default="Tarefa criada pelo OrchestratorAgent.")
    orchestrator_plan.add_argument("--priority", default="normal")
    orchestrator_plan.add_argument("--tags", default="")
    orchestrator_plan.add_argument("--assigned-agent-id", default="task_agent")

    daily_start = subparsers.add_parser("daily-start", help="Inicia operacao diaria.")
    daily_start.add_argument("--focus", default="Operacao diaria do K-Atlas OS")
    daily_start.add_argument("--priority", default="normal")
    daily_start.add_argument("--tags", default="daily,operations")

    run = subparsers.add_parser("run", help="Executa comando bruto no kernel.")
    run.add_argument("command")
    run.add_argument("--payload", default=None)

    return parser


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    if args.action == "status":
        return execute("system_agent.status")

    if args.action == "agents":
        return execute("system_agent.agents")

    if args.action == "events":
        return execute("system_agent.events", {"limit": args.limit})

    if args.action == "task-stats":
        return execute("task_agent.stats")

    if args.action == "memory-stats":
        return execute("memory_agent.stats")

    if args.action == "learning-stats":
        return execute("learning_agent.stats")

    if args.action == "orchestrator-status":
        return execute("orchestrator_agent.status")

    if args.action == "report-list":
        return execute("auto_reporter.list", {"limit": 50})

    if args.action == "task-create":
        return execute(
            "task_agent.create",
            {
                "title": args.title,
                "description": args.description,
                "priority": args.priority,
                "tags": parse_tags(args.tags),
                "assigned_agent_id": args.assigned_agent_id,
            },
        )

    if args.action == "task-list":
        payload: Dict[str, Any] = {"limit": args.limit}
        if args.status:
            payload["status"] = args.status
        return execute("task_agent.list", payload)

    if args.action == "task-complete":
        return execute("task_agent.complete", {"task_id": args.task_id})

    if args.action == "memory-remember":
        return execute(
            "memory_agent.remember",
            {
                "title": args.title,
                "content": args.content,
                "type": args.type,
                "tags": parse_tags(args.tags),
                "source": args.source,
                "visibility": "internal",
                "importance": args.importance,
            },
        )

    if args.action == "memory-search":
        return execute("memory_agent.search", {"query": args.query, "limit": args.limit})

    if args.action == "memory-list":
        payload: Dict[str, Any] = {"limit": args.limit}
        if args.type:
            payload["type"] = args.type
        if args.tag:
            payload["tag"] = args.tag
        return execute("memory_agent.list", payload)

    if args.action == "learning-learn":
        return execute(
            "learning_agent.learn",
            {
                "title": args.title,
                "content": args.content,
                "type": args.type,
                "tags": parse_tags(args.tags),
                "source": args.source,
                "importance": args.importance,
            },
        )

    if args.action == "learning-error":
        return execute(
            "learning_agent.error",
            {
                "title": args.title,
                "symptom": args.symptom,
                "cause": args.cause,
                "fix": args.fix,
                "prevention": args.prevention,
                "severity": args.severity,
                "tags": parse_tags(args.tags),
                "source": args.source,
            },
        )

    if args.action == "learning-playbook":
        return execute(
            "learning_agent.playbook",
            {
                "title": args.title,
                "objective": args.objective,
                "steps": parse_tags(args.steps),
                "tags": parse_tags(args.tags),
                "source": args.source,
            },
        )

    if args.action == "learning-search":
        return execute(
            "learning_agent.search",
            {
                "query": args.query,
                "limit": args.limit,
            },
        )

    if args.action == "report-generate":
        return execute(
            "auto_reporter.generate",
            {
                "module_name": args.module_name,
                "objective": args.objective,
                "files_changed": parse_tags(args.files),
                "operational_flow": args.flow,
                "strengths": parse_tags(args.strengths),
                "bottlenecks": parse_tags(args.bottlenecks),
                "future_risks": parse_tags(args.risks),
                "next_step": args.next_step,
                "not_now": args.not_now,
                "impact": args.impact,
                "professor_decision": args.decision,
                "decision_reason": args.decision_reason,
                "tags": parse_tags(args.tags),
                "created_by": "k_atlas_cli",
            },
        )

    if args.action == "orchestrator-plan":
        return execute(
            "orchestrator_agent.plan",
            {
                "goal": args.goal,
                "description": args.description,
                "priority": args.priority,
                "tags": parse_tags(args.tags),
                "assigned_agent_id": args.assigned_agent_id,
            },
        )

    if args.action == "daily-start":
        return execute(
            "orchestrator_agent.daily_start",
            {
                "focus": args.focus,
                "priority": args.priority,
                "tags": parse_tags(args.tags),
            },
        )

    if args.action == "run":
        return execute(args.command, parse_json_payload(args.payload))

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
