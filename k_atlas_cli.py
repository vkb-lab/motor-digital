# -*- coding: utf-8 -*-
"""
K-Atlas OS - CLI

Interface de linha de comando para operar o K-Atlas OS localmente.

Uso:
python k_atlas_cli.py status
python k_atlas_cli.py agents
python k_atlas_cli.py events --limit 10
python k_atlas_cli.py task-stats
python k_atlas_cli.py memory-stats
python k_atlas_cli.py run system_agent.ping
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
        payload: Dict[str, Any] = {
            "limit": args.limit,
        }

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
        return execute(
            "memory_agent.search",
            {
                "query": args.query,
                "limit": args.limit,
            },
        )

    if args.action == "memory-list":
        payload = {
            "limit": args.limit,
        }

        if args.type:
            payload["type"] = args.type

        if args.tag:
            payload["tag"] = args.tag

        return execute("memory_agent.list", payload)

    if args.action == "run":
        return execute(args.command, parse_json_payload(args.payload))

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
