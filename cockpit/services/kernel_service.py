# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cockpit Kernel Service

Camada de leitura operacional entre o cockpit Streamlit e o kernel real.
Este servico e propositalmente read-only nesta fase.

Responsabilidades:
- inicializar kernel real via k_atlas_boot.build_kernel
- consultar agentes
- consultar tarefas
- consultar memoria
- consultar learning
- consultar eventos
- carregar reports
- carregar logs
- montar snapshot operacional
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from k_atlas_boot import build_kernel


ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"
LOGS_DIR = ROOT / "logs"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def command_output(result: Dict[str, Any]) -> Dict[str, Any]:
    output = result.get("output")
    if isinstance(output, dict):
        return output
    return {}


def execute_kernel_command(kernel: Any, command: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        result = kernel.execute(command, payload=payload or {})
        return result.to_dict()
    except Exception as exc:
        return {
            "success": False,
            "agent_id": None,
            "action": command,
            "output": {},
            "error": str(exc),
            "created_at": now_iso(),
        }


def load_json_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
            "data": None,
        }

    try:
        return {
            "exists": True,
            "path": str(path),
            "data": json.loads(path.read_text(encoding="utf-8")),
        }
    except Exception as exc:
        return {
            "exists": True,
            "path": str(path),
            "data": None,
            "error": str(exc),
        }


def load_reports() -> List[Dict[str, Any]]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    reports: List[Dict[str, Any]] = []

    for path in sorted(REPORTS_DIR.glob("*.json")):
        item = load_json_file(path)
        item["name"] = path.name
        try:
            item["modified_at"] = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
        except Exception:
            item["modified_at"] = None
        reports.append(item)

    return reports


def load_logs(limit_files: int = 10, tail_lines: int = 80) -> List[Dict[str, Any]]:
    candidates: List[Path] = []

    if LOGS_DIR.exists():
        candidates.extend(sorted(LOGS_DIR.glob("*.log")))

    candidates.extend(sorted(ROOT.glob("*.log")))

    logs: List[Dict[str, Any]] = []

    for path in candidates[-limit_files:]:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            logs.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                    "tail": "\n".join(lines[-tail_lines:]),
                }
            )
        except Exception as exc:
            logs.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "error": str(exc),
                    "tail": "",
                }
            )

    return logs


def build_health(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    data = snapshot.get("data", {})

    agents = data.get("agents", [])
    tasks = data.get("tasks", [])
    memories = data.get("memories", [])
    events = data.get("events", [])

    learning_stats = data.get("learning_stats", {})
    learning_totals = learning_stats.get("totals", {}) if isinstance(learning_stats, dict) else {}

    pending_tasks = [
        task for task in tasks
        if isinstance(task, dict) and task.get("status") == "pending"
    ]

    failed_commands = [
        name for name, result in snapshot.get("commands", {}).items()
        if not result.get("success")
    ]

    status = "ok"
    risk_level = "low"

    if failed_commands:
        status = "degraded"
        risk_level = "medium"

    if len(failed_commands) >= 3:
        status = "attention"
        risk_level = "high"

    return {
        "status": status,
        "risk_level": risk_level,
        "agents_total": len(agents),
        "tasks_total": len(tasks),
        "pending_tasks": len(pending_tasks),
        "memories_total": len(memories),
        "events_total": len(events),
        "learning_totals": learning_totals,
        "failed_commands": failed_commands,
    }


def collect_operational_snapshot(save_state: bool = True) -> Dict[str, Any]:
    kernel = build_kernel()

    commands: Dict[str, Dict[str, Any]] = {}

    try:
        commands["system_status"] = execute_kernel_command(kernel, "system_agent.status")
        commands["agents"] = execute_kernel_command(kernel, "system_agent.agents")
        commands["events"] = execute_kernel_command(kernel, "system_agent.events", {"limit": 50})

        commands["tasks"] = execute_kernel_command(kernel, "task_agent.list", {"limit": 100})
        commands["task_stats"] = execute_kernel_command(kernel, "task_agent.stats")

        commands["memory"] = execute_kernel_command(kernel, "memory_agent.list", {"limit": 100})
        commands["memory_stats"] = execute_kernel_command(kernel, "memory_agent.stats")

        commands["learning_stats"] = execute_kernel_command(kernel, "learning_agent.stats")
        commands["learning_lessons"] = execute_kernel_command(kernel, "learning_agent.lessons", {"limit": 50})
        commands["learning_errors"] = execute_kernel_command(kernel, "learning_agent.errors", {"limit": 50})
        commands["learning_playbooks"] = execute_kernel_command(kernel, "learning_agent.playbooks", {"limit": 50})
        commands["learning_training"] = execute_kernel_command(kernel, "learning_agent.training_items", {"limit": 50})

        commands["orchestrator_status"] = execute_kernel_command(kernel, "orchestrator_agent.status")

        status_output = command_output(commands["system_status"])
        agents_output = command_output(commands["agents"])
        events_output = command_output(commands["events"])
        tasks_output = command_output(commands["tasks"])
        memory_output = command_output(commands["memory"])
        learning_stats_output = command_output(commands["learning_stats"])
        lessons_output = command_output(commands["learning_lessons"])
        errors_output = command_output(commands["learning_errors"])
        playbooks_output = command_output(commands["learning_playbooks"])
        training_output = command_output(commands["learning_training"])

        snapshot = {
            "success": True,
            "created_at": now_iso(),
            "root": str(ROOT),
            "kernel_status": status_output.get("kernel", {}),
            "commands": commands,
            "data": {
                "agents": agents_output.get("agents", []),
                "events": events_output.get("events", []),
                "tasks": tasks_output.get("tasks", []),
                "memories": memory_output.get("entries", []),
                "learning_stats": learning_stats_output,
                "learning_lessons": lessons_output.get("lessons", []),
                "learning_errors": errors_output.get("errors", []),
                "learning_playbooks": playbooks_output.get("playbooks", []),
                "learning_training": training_output.get("training_items", []),
            },
            "reports": load_reports(),
            "logs": load_logs(),
        }

        snapshot["health"] = build_health(snapshot)

        return snapshot

    except Exception as exc:
        return {
            "success": False,
            "created_at": now_iso(),
            "root": str(ROOT),
            "error": str(exc),
            "commands": commands,
            "data": {},
            "reports": load_reports(),
            "logs": load_logs(),
            "health": {
                "status": "failed",
                "risk_level": "high",
                "failed_commands": ["snapshot"],
            },
        }

    finally:
        kernel.stop(save_state=save_state)


def cockpit_boot_check() -> Dict[str, Any]:
    snapshot = collect_operational_snapshot(save_state=False)

    data = snapshot.get("data", {})
    health = snapshot.get("health", {})

    return {
        "success": bool(snapshot.get("success")),
        "created_at": now_iso(),
        "health_status": health.get("status"),
        "agents_total": len(data.get("agents", [])),
        "tasks_total": len(data.get("tasks", [])),
        "memories_total": len(data.get("memories", [])),
        "learning_totals": health.get("learning_totals", {}),
        "has_kernel_status": bool(snapshot.get("kernel_status")),
    }
