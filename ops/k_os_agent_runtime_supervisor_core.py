# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "agent_runtime" / "k_os_agent_runtime_supervisor_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_agent_runtime"
STATE_PATH = STATE_DIR / "agent_runtime_supervisor_state.json"

REPORT_DIR = ROOT / "reports" / "agent_runtime"
MEMORY_DIR = ROOT / "memory" / "agent_runtime"

LATEST_JSON = REPORT_DIR / "latest_agent_runtime_supervisor_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_runtime_supervisor_report.md"
WATCHDOG_JSON = REPORT_DIR / "latest_agent_runtime_watchdog_report.json"
WATCHDOG_MD = REPORT_DIR / "latest_agent_runtime_watchdog_report.md"
HEARTBEAT_JSON = REPORT_DIR / "latest_agent_runtime_heartbeat_report.json"
HEARTBEAT_MD = REPORT_DIR / "latest_agent_runtime_heartbeat_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

AGENT_QUEUE_REPORT = ROOT / "reports" / "agent_queue" / "latest_agent_orchestration_queue_report.json"
AGENT_QUEUE_STATE = ROOT / "local_secrets" / "k_os_agent_queue" / "agent_orchestration_queue.json"
PERMISSION_MATRIX = ROOT / "config" / "governance" / "k_os_agent_permission_matrix.json"
COMMAND_CENTER_SCRIPT = ROOT / "ops" / "k_os_command_center_action_router.py"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def minutes_since(value: str) -> float | None:
    dt = parse_dt(value)
    if not dt:
        return None
    return (datetime.now(timezone.utc) - dt).total_seconds() / 60


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_read_error": str(exc), "_path": str(path)}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def event(name: str, data: dict[str, Any]) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": name,
            "created_at": now(),
            "data": data
        }, ensure_ascii=False) + "\n")


def load_policy() -> dict[str, Any]:
    data = read_json(POLICY_PATH)
    if not data:
        raise RuntimeError("Agent runtime policy not found.")
    return data


def ensure_state() -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not STATE_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_publish_enabled": False,
            "agents": [],
            "runtime_events": [],
            "watchdog_events": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load runtime supervisor state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def agent_allowed(agent_id: str) -> bool:
    policy = load_policy()
    if agent_id in set(policy.get("allowed_agent_ids", [])):
        return True

    matrix = read_json(PERMISSION_MATRIX)
    if not matrix:
        return False

    return agent_id in json.dumps(matrix, ensure_ascii=False)


def find_agent(state: dict[str, Any], agent_id: str) -> dict[str, Any] | None:
    for item in state.get("agents", []):
        if item.get("agent_id") == agent_id:
            return item
    return None


def safe_agent(item: dict[str, Any]) -> dict[str, Any]:
    last_heartbeat = item.get("last_heartbeat_at", "")
    age = minutes_since(last_heartbeat)

    return {
        "agent_id": item.get("agent_id"),
        "status": item.get("status"),
        "health": item.get("health"),
        "current_task_id": item.get("current_task_id", ""),
        "last_action_id": item.get("last_action_id", ""),
        "last_heartbeat_at": last_heartbeat,
        "heartbeat_age_minutes": round(age, 2) if age is not None else None,
        "failure_count": item.get("failure_count", 0),
        "blocked_reason": item.get("blocked_reason", ""),
        "registered_at": item.get("registered_at"),
        "updated_at": item.get("updated_at")
    }


def safe_runtime_event(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": item.get("event_id"),
        "event_type": item.get("event_type"),
        "agent_id": item.get("agent_id"),
        "task_id": item.get("task_id", ""),
        "action_id": item.get("action_id", ""),
        "status": item.get("status", ""),
        "summary": item.get("summary", ""),
        "created_at": item.get("created_at")
    }


def register_agent(agent_id: str, reason: str) -> dict[str, Any]:
    state = ensure_state()

    if not agent_allowed(agent_id):
        raise RuntimeError(f"Agent not allowed: {agent_id}")

    agent = find_agent(state, agent_id)

    if not agent:
        agent = {
            "agent_id": agent_id,
            "status": "registered",
            "health": "healthy",
            "current_task_id": "",
            "last_action_id": "",
            "last_heartbeat_at": "",
            "failure_count": 0,
            "blocked_reason": "",
            "registered_at": now(),
            "updated_at": now()
        }
        state.setdefault("agents", []).append(agent)

    agent["status"] = "idle"
    agent["health"] = "healthy"
    agent["blocked_reason"] = ""
    agent["updated_at"] = now()

    state.setdefault("runtime_events", []).append({
        "event_id": "rte_" + uuid.uuid4().hex[:12],
        "event_type": "agent_registered",
        "agent_id": agent_id,
        "summary": reason or "agent_registered",
        "created_at": now()
    })

    state["runtime_events"] = state["runtime_events"][-300:]
    save_state(state)

    event("agent_runtime.agent_registered", {"agent_id": agent_id})
    return audit_report()


def heartbeat(agent_id: str, task_id: str, action_id: str, status: str, reason: str) -> dict[str, Any]:
    state = ensure_state()

    if not agent_allowed(agent_id):
        raise RuntimeError(f"Agent not allowed: {agent_id}")

    agent = find_agent(state, agent_id)

    if not agent:
        register_agent(agent_id, "auto_register_before_heartbeat")
        state = ensure_state()
        agent = find_agent(state, agent_id)

    if not agent:
        raise RuntimeError(f"Could not register agent: {agent_id}")

    allowed_statuses = set(load_policy().get("runtime_statuses", []))
    if status not in allowed_statuses:
        status = "active"

    agent["status"] = status
    agent["health"] = "healthy"
    agent["current_task_id"] = task_id
    agent["last_action_id"] = action_id
    agent["last_heartbeat_at"] = now()
    agent["blocked_reason"] = ""
    agent["updated_at"] = now()

    hb = {
        "ok": True,
        "checkpoint": "040",
        "module": "k_os_agent_runtime_supervisor_core",
        "status": "heartbeat_recorded",
        "generated_at": now(),
        "agent_id": agent_id,
        "task_id": task_id,
        "action_id": action_id,
        "runtime_status": status,
        "external_send_performed": False,
        "external_publish_performed": False
    }

    state.setdefault("runtime_events", []).append({
        "event_id": "rte_" + uuid.uuid4().hex[:12],
        "event_type": "heartbeat",
        "agent_id": agent_id,
        "task_id": task_id,
        "action_id": action_id,
        "status": status,
        "summary": reason or "heartbeat",
        "created_at": now()
    })

    state["runtime_events"] = state["runtime_events"][-300:]
    save_state(state)
    write_heartbeat(hb)
    event("agent_runtime.heartbeat", {"agent_id": agent_id, "task_id": task_id})
    return hb


def create_demo() -> dict[str, Any]:
    register_agent("k_atlas_engineer", "demo_runtime_registration")
    heartbeat(
        agent_id="k_atlas_engineer",
        task_id="demo_runtime_task",
        action_id="cockpit_audit",
        status="idle",
        reason="demo_runtime_heartbeat"
    )
    return audit_report()


def queue_summary() -> dict[str, Any]:
    report = read_json(AGENT_QUEUE_REPORT) or {}
    metrics = report.get("metrics", {})
    tasks = report.get("tasks", [])
    recent_dispatches = report.get("recent_dispatches", [])

    return {
        "queue_report_available": AGENT_QUEUE_REPORT.exists(),
        "queue_state_available": AGENT_QUEUE_STATE.exists(),
        "task_count": metrics.get("task_count", len(tasks)),
        "blocked_task_count": metrics.get("blocked_task_count", 0),
        "queued_task_count": metrics.get("queued_task_count", 0),
        "approved_task_count": metrics.get("approved_task_count", 0),
        "dispatch_count": metrics.get("dispatch_count", len(recent_dispatches)),
        "pending_tasks": [
            item for item in tasks
            if item.get("status") in {"queued", "triage", "approved_for_dispatch", "dispatched_dry_run", "in_progress"}
        ][:20],
        "blocked_tasks": [
            item for item in tasks
            if item.get("status") == "blocked"
        ][:20]
    }


def run_watchdog() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()
    rules = policy.get("watchdog_rules", {})
    max_age = float(rules.get("heartbeat_max_age_minutes", 30))
    max_blocked = int(rules.get("max_blocked_tasks_before_attention", 1))
    max_stale = int(rules.get("max_stale_agents_before_blocked", 1))

    agents = state.get("agents", [])
    queue = queue_summary()

    stale_agents = []
    blocked_agents = []

    for agent in agents:
        age = minutes_since(agent.get("last_heartbeat_at", ""))

        if agent.get("last_heartbeat_at") == "":
            agent["status"] = "stale"
            agent["health"] = "attention"
            agent["blocked_reason"] = "missing_heartbeat"
            stale_agents.append(agent)
        elif age is not None and age > max_age:
            agent["status"] = "stale"
            agent["health"] = "attention"
            agent["blocked_reason"] = "heartbeat_stale"
            stale_agents.append(agent)

        if int(agent.get("failure_count", 0)) >= int(rules.get("max_failed_runtime_events", 3)):
            agent["status"] = "blocked"
            agent["health"] = "blocked"
            agent["blocked_reason"] = "too_many_failures"
            blocked_agents.append(agent)

        agent["updated_at"] = now()

    blockers = []
    warnings = []

    if len(stale_agents) >= max_stale and len(stale_agents) > 0:
        blockers.append("stale_agents_detected")

    if blocked_agents:
        blockers.append("blocked_agents_detected")

    if int(queue.get("blocked_task_count", 0)) >= max_blocked and int(queue.get("blocked_task_count", 0)) > 0:
        warnings.append("blocked_queue_tasks_detected")

    if not COMMAND_CENTER_SCRIPT.exists():
        blockers.append("command_center_missing")

    if not PERMISSION_MATRIX.exists():
        blockers.append("permission_matrix_missing")

    if blockers:
        health = "blocked"
    elif warnings:
        health = "attention"
    else:
        health = "healthy"

    result = {
        "ok": len(blockers) == 0,
        "checkpoint": "040",
        "module": "k_os_agent_runtime_supervisor_core",
        "status": "watchdog_completed",
        "generated_at": now(),
        "health_level": health,
        "agent_count": len(agents),
        "stale_agent_count": len(stale_agents),
        "blocked_agent_count": len(blocked_agents),
        "queue_summary": queue,
        "blockers": blockers,
        "warnings": warnings,
        "stale_agents": [safe_agent(item) for item in stale_agents],
        "blocked_agents": [safe_agent(item) for item in blocked_agents],
        "external_send_performed": False,
        "external_publish_performed": False,
        "next_checkpoint": policy.get("next_checkpoint", "041 - K-Agent Execution Ledger and Replay Core")
    }

    state.setdefault("watchdog_events", []).append({
        "event_id": "wdg_" + uuid.uuid4().hex[:12],
        "created_at": now(),
        "health_level": health,
        "stale_agent_count": len(stale_agents),
        "blocked_agent_count": len(blocked_agents),
        "blocked_task_count": queue.get("blocked_task_count", 0)
    })

    state["watchdog_events"] = state["watchdog_events"][-300:]
    save_state(state)
    write_watchdog(result)
    event("agent_runtime.watchdog_completed", {"health_level": health})
    return result


def compute_metrics(agents: list[dict[str, Any]], queue: dict[str, Any], watchdog: dict[str, Any]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    health_counts: dict[str, int] = {}

    for agent in agents:
        status = agent.get("status", "unknown")
        health = agent.get("health", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        health_counts[health] = health_counts.get(health, 0) + 1

    return {
        "agent_count": len(agents),
        "healthy_agent_count": health_counts.get("healthy", 0),
        "attention_agent_count": health_counts.get("attention", 0),
        "blocked_agent_count": health_counts.get("blocked", 0),
        "stale_agent_count": watchdog.get("stale_agent_count", 0),
        "queue_task_count": queue.get("task_count", 0),
        "queue_blocked_task_count": queue.get("blocked_task_count", 0),
        "queue_dispatch_count": queue.get("dispatch_count", 0),
        "status_counts": status_counts,
        "health_counts": health_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()
    watchdog = run_watchdog()
    state = ensure_state()

    agents = [safe_agent(item) for item in state.get("agents", [])]
    queue = queue_summary()
    events = [safe_runtime_event(item) for item in state.get("runtime_events", [])[-50:]]

    metrics = compute_metrics(agents, queue, watchdog)

    report = {
        "ok": True,
        "checkpoint": "040",
        "module": "k_os_agent_runtime_supervisor_core",
        "status": "audit_generated",
        "generated_at": now(),
        "runtime_state_path": "local_secrets/k_os_agent_runtime/agent_runtime_supervisor_state.json",
        "runtime_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "arbitrary_agent_execution_allowed": False,
        "heartbeat_required": True,
        "watchdog_enabled": True,
        "stale_agent_blocking_enabled": True,
        "permission_matrix_available": PERMISSION_MATRIX.exists(),
        "command_center_available": COMMAND_CENTER_SCRIPT.exists(),
        "agent_queue_report_available": AGENT_QUEUE_REPORT.exists(),
        "agents": agents,
        "queue_summary": queue,
        "watchdog": {
            "health_level": watchdog.get("health_level"),
            "stale_agent_count": watchdog.get("stale_agent_count"),
            "blocked_agent_count": watchdog.get("blocked_agent_count"),
            "blockers": watchdog.get("blockers", []),
            "warnings": watchdog.get("warnings", [])
        },
        "metrics": metrics,
        "recent_runtime_events": events,
        "required_gates_before_runtime_execution": policy.get("required_gates_before_runtime_execution", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "041 - K-Agent Execution Ledger and Replay Core")
    }

    write_report(report)
    event("agent_runtime.audit_generated", {"agent_count": metrics["agent_count"]})
    return report


def write_heartbeat(data: dict[str, Any]) -> None:
    HEARTBEAT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Runtime Heartbeat",
        "",
        f"- Agent: {data.get('agent_id')}",
        f"- Task: {data.get('task_id')}",
        f"- Action: {data.get('action_id')}",
        f"- Runtime status: {data.get('runtime_status')}",
        f"- Generated at: {data.get('generated_at')}",
        f"- External send performed: {data.get('external_send_performed')}",
        f"- External publish performed: {data.get('external_publish_performed')}"
    ]

    HEARTBEAT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_watchdog(data: dict[str, Any]) -> None:
    WATCHDOG_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Runtime Watchdog",
        "",
        f"- Status: {data.get('status')}",
        f"- OK: {data.get('ok')}",
        f"- Health: {data.get('health_level')}",
        f"- Agent count: {data.get('agent_count')}",
        f"- Stale agents: {data.get('stale_agent_count')}",
        f"- Blocked agents: {data.get('blocked_agent_count')}",
        f"- External send performed: {data.get('external_send_performed')}",
        f"- External publish performed: {data.get('external_publish_performed')}",
        "",
        "## Blockers",
        ""
    ]

    if data.get("blockers"):
        for item in data.get("blockers", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker.")

    lines.extend(["", "## Warnings", ""])

    if data.get("warnings"):
        for item in data.get("warnings", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum warning.")

    WATCHDOG_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(report: dict[str, Any]) -> None:
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    metrics = report.get("metrics", {})
    watchdog = report.get("watchdog", {})

    lines = [
        "# K-OS Agent Runtime Supervisor Core",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Watchdog health: {watchdog.get('health_level')}",
        f"- Runtime state committed: {report.get('runtime_state_committed')}",
        f"- Permission Matrix available: {report.get('permission_matrix_available')}",
        f"- Command Center available: {report.get('command_center_available')}",
        f"- Agent Queue report available: {report.get('agent_queue_report_available')}",
        f"- External publish enabled: {report.get('external_publish_enabled')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Agents", ""])

    if report.get("agents"):
        for item in report.get("agents", []):
            lines.append(
                f"- {item.get('agent_id')} | status={item.get('status')} | health={item.get('health')} | "
                f"heartbeat_age={item.get('heartbeat_age_minutes')}"
            )
    else:
        lines.append("- Nenhum agente registrado.")

    lines.extend(["", "## Watchdog blockers", ""])

    if watchdog.get("blockers"):
        for item in watchdog.get("blockers", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker.")

    lines.extend(["", "## Required gates before runtime execution", ""])

    for gate in report.get("required_gates_before_runtime_execution", []):
        lines.append(f"- {gate}")

    lines.extend(["", "## Blocked actions", ""])

    for item in report.get("blocked_actions", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Next checkpoint", "", f"- {report.get('next_checkpoint')}"])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def show_latest() -> int:
    if LATEST_JSON.exists():
        print(LATEST_JSON.read_text(encoding="utf-8-sig"))
    else:
        print("{}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "register-agent", "heartbeat", "watchdog", "create-demo", "audit", "show"], required=True)
    parser.add_argument("--agent-id", default="k_atlas_engineer")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--action-id", default="")
    parser.add_argument("--status", default="active")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "register-agent":
        result = register_agent(args.agent_id, args.reason)

    elif args.mode == "heartbeat":
        result = heartbeat(args.agent_id, args.task_id, args.action_id, args.status, args.reason)

    elif args.mode == "watchdog":
        result = run_watchdog()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "audit":
        result = audit_report()

    elif args.mode == "show":
        return show_latest()

    else:
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())