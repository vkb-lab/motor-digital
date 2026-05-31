# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "agent_queue" / "k_os_agent_orchestration_queue_policy.json"
QUEUE_DIR = ROOT / "local_secrets" / "k_os_agent_queue"
QUEUE_PATH = QUEUE_DIR / "agent_orchestration_queue.json"

REPORT_DIR = ROOT / "reports" / "agent_queue"
MEMORY_DIR = ROOT / "memory" / "agent_queue"

LATEST_JSON = REPORT_DIR / "latest_agent_orchestration_queue_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_orchestration_queue_report.md"
SNAPSHOT_JSON = REPORT_DIR / "latest_agent_queue_snapshot.json"
SNAPSHOT_MD = REPORT_DIR / "latest_agent_queue_snapshot.md"
DISPATCH_JSON = REPORT_DIR / "latest_agent_dispatch_report.json"
DISPATCH_MD = REPORT_DIR / "latest_agent_dispatch_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

PERMISSION_MATRIX = ROOT / "config" / "governance" / "k_os_agent_permission_matrix.json"
COMMAND_CENTER_SCRIPT = ROOT / "ops" / "k_os_command_center_action_router.py"
COMMAND_CENTER_CATALOG = ROOT / "reports" / "command_center" / "latest_action_catalog.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
        raise RuntimeError("Agent queue policy not found.")
    return data


def ensure_queue() -> dict[str, Any]:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not QUEUE_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_publish_enabled": False,
            "dry_run_default": True,
            "tasks": [],
            "dispatches": [],
            "activities": []
        }
        write_json(QUEUE_PATH, data)

    queue = read_json(QUEUE_PATH)
    if not queue:
        raise RuntimeError("Could not load agent queue.")
    return queue


def save_queue(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(QUEUE_PATH, data)


def command_center_catalog() -> list[dict[str, Any]]:
    data = read_json(COMMAND_CENTER_CATALOG) or {}
    return data.get("actions", [])


def get_action(action_id: str) -> dict[str, Any] | None:
    for item in command_center_catalog():
        if item.get("action_id") == action_id:
            return item
    return None


def matrix_contains_agent(agent_id: str) -> bool:
    policy = load_policy()
    allowed = set(policy.get("allowed_agent_ids", []))

    if agent_id in allowed:
        return True

    data = read_json(PERMISSION_MATRIX)
    if not data:
        return False

    serialized = json.dumps(data, ensure_ascii=False)
    return agent_id in serialized


def safe_task(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": item.get("task_id"),
        "agent_id": item.get("agent_id"),
        "action_id": item.get("action_id"),
        "title": item.get("title"),
        "domain": item.get("domain"),
        "priority": item.get("priority"),
        "risk": item.get("risk"),
        "status": item.get("status"),
        "requires_approval": item.get("requires_approval", True),
        "approved": item.get("approved", False),
        "blocked_reason": item.get("blocked_reason", ""),
        "next_action": item.get("next_action", ""),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def safe_dispatch(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "dispatch_id": item.get("dispatch_id"),
        "task_id": item.get("task_id"),
        "agent_id": item.get("agent_id"),
        "action_id": item.get("action_id"),
        "status": item.get("status"),
        "dry_run": item.get("dry_run", True),
        "command_executed": item.get("command_executed", False),
        "ok": item.get("ok"),
        "created_at": item.get("created_at")
    }


def safe_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": item.get("activity_id"),
        "activity_type": item.get("activity_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by")
    }


def create_task(agent_id: str, action_id: str, title: str, priority: str, reason: str) -> dict[str, Any]:
    policy = load_policy()

    if priority not in set(policy.get("priority_levels", [])):
        raise RuntimeError(f"Invalid priority: {priority}")

    queue = ensure_queue()
    action = get_action(action_id)

    blockers = []

    if not matrix_contains_agent(agent_id):
        blockers.append("agent_not_allowed_by_permission_matrix")

    if not action:
        blockers.append("action_not_found_in_command_center_catalog")

    task_id = "agtq_" + uuid.uuid4().hex[:12]

    risk = action.get("risk", "unknown") if action else "unknown"
    domain = action.get("domain", "unknown") if action else "unknown"
    requires_approval = True if risk in {"medium", "high", "critical", "unknown"} else False

    task = {
        "task_id": task_id,
        "agent_id": agent_id,
        "action_id": action_id,
        "title": title or f"Agent task for {action_id}",
        "domain": domain,
        "priority": priority,
        "risk": risk,
        "reason": reason or "manual_queue_task",
        "status": "blocked" if blockers else "queued",
        "requires_approval": requires_approval,
        "approved": False,
        "blocked_reason": ";".join(blockers),
        "next_action": "resolver blockers" if blockers else "aguardar approval ou dispatch dry-run",
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "created_at": now(),
        "updated_at": now()
    }

    queue["tasks"].append(task)
    queue["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "task_created",
        "summary": f"Tarefa criada para agente {agent_id} e ação {action_id}.",
        "created_at": now(),
        "created_by": "k_os_agent_queue"
    })

    save_queue(queue)
    event("agent_queue.task_created", {"task_id": task_id, "agent_id": agent_id, "action_id": action_id, "blockers": blockers})
    return audit_report()


def create_demo() -> dict[str, Any]:
    queue = ensure_queue()

    if not queue.get("tasks"):
        return create_task(
            agent_id="k_atlas_engineer",
            action_id="cockpit_audit",
            title="Auditar cockpit executivo via fila de agentes",
            priority="medium",
            reason="demo_agent_orchestration_queue"
        )

    return audit_report()


def approve_task(task_id: str, reason: str) -> dict[str, Any]:
    queue = ensure_queue()
    found = False

    for task in queue.get("tasks", []):
        if task.get("task_id") == task_id:
            if task.get("status") == "blocked":
                raise RuntimeError("Blocked task cannot be approved until blockers are resolved.")
            task["approved"] = True
            task["approval_reason"] = reason or "operator_approval"
            task["approved_at"] = now()
            task["status"] = "approved_for_dispatch"
            task["next_action"] = "pronto para dispatch controlado"
            task["updated_at"] = now()
            found = True

            queue["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "activity_type": "task_approved",
                "summary": f"Tarefa {task_id} aprovada para dispatch.",
                "created_at": now(),
                "created_by": "operator"
            })

    if not found:
        raise RuntimeError(f"Task not found: {task_id}")

    save_queue(queue)
    event("agent_queue.task_approved", {"task_id": task_id})
    return audit_report()


def dispatch_task(task_id: str, execute: bool, approved: bool, reason: str) -> dict[str, Any]:
    queue = ensure_queue()
    task = next((item for item in queue.get("tasks", []) if item.get("task_id") == task_id), None)

    if not task:
        raise RuntimeError(f"Task not found: {task_id}")

    blockers = []

    if task.get("status") == "blocked":
        blockers.append("task_is_blocked")

    if not matrix_contains_agent(task.get("agent_id", "")):
        blockers.append("agent_not_allowed_by_permission_matrix")

    if not get_action(task.get("action_id", "")):
        blockers.append("action_not_found_in_command_center_catalog")

    if execute and not task.get("approved") and not approved:
        blockers.append("execution_requires_task_approval")

    if execute and not reason:
        blockers.append("execution_requires_operator_reason")

    dispatch_id = "disp_" + uuid.uuid4().hex[:12]

    if blockers:
        result = {
            "ok": False,
            "checkpoint": "039",
            "module": "k_os_agent_orchestration_queue_core",
            "status": "dispatch_blocked",
            "generated_at": now(),
            "dispatch_id": dispatch_id,
            "task": safe_task(task),
            "blockers": blockers,
            "dry_run": not execute,
            "command_executed": False,
            "external_send_performed": False,
            "external_publish_performed": False
        }
        write_dispatch(result)
        record_dispatch(queue, result)
        event("agent_queue.dispatch_blocked", {"task_id": task_id, "blockers": blockers})
        return result

    args = [
        sys.executable,
        str(COMMAND_CENTER_SCRIPT),
        "--mode",
        "route",
        "--action-id",
        task.get("action_id", ""),
        "--reason",
        reason or "agent_queue_dispatch"
    ]

    if task.get("approved") or approved:
        args.append("--approved")

    if execute:
        args.append("--execute")

    completed = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    command_center_payload: dict[str, Any] = {}
    try:
        command_center_payload = json.loads(completed.stdout)
    except Exception:
        command_center_payload = {
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:]
        }

    command_executed = bool(command_center_payload.get("command_executed", False))
    ok = completed.returncode == 0 and bool(command_center_payload.get("ok", False))

    task["status"] = "completed_pending_review" if command_executed and ok else "dispatched_dry_run"
    if not ok and execute:
        task["status"] = "failed"
    task["updated_at"] = now()
    task["last_dispatch_id"] = dispatch_id

    result = {
        "ok": ok,
        "checkpoint": "039",
        "module": "k_os_agent_orchestration_queue_core",
        "status": "dispatch_completed",
        "generated_at": now(),
        "dispatch_id": dispatch_id,
        "task": safe_task(task),
        "dry_run": not execute,
        "command_executed": command_executed,
        "command_center_returncode": completed.returncode,
        "command_center_result": command_center_payload,
        "external_send_performed": False,
        "external_publish_performed": False
    }

    write_dispatch(result)
    record_dispatch(queue, result)
    save_queue(queue)
    event("agent_queue.dispatch_completed", {"task_id": task_id, "ok": ok, "command_executed": command_executed})
    return result


def record_dispatch(queue: dict[str, Any], result: dict[str, Any]) -> None:
    queue.setdefault("dispatches", []).append({
        "dispatch_id": result.get("dispatch_id"),
        "task_id": result.get("task", {}).get("task_id"),
        "agent_id": result.get("task", {}).get("agent_id"),
        "action_id": result.get("task", {}).get("action_id"),
        "status": result.get("status"),
        "dry_run": result.get("dry_run"),
        "command_executed": result.get("command_executed"),
        "ok": result.get("ok"),
        "created_at": result.get("generated_at")
    })

    queue.setdefault("activities", []).append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "task_dispatched",
        "summary": f"Dispatch registrado para task {result.get('task', {}).get('task_id')}.",
        "created_at": now(),
        "created_by": "k_os_agent_queue"
    })

    queue["dispatches"] = queue["dispatches"][-200:]
    save_queue(queue)


def write_dispatch(result: dict[str, Any]) -> None:
    DISPATCH_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Queue Dispatch Report",
        "",
        f"- Dispatch ID: {result.get('dispatch_id')}",
        f"- Status: {result.get('status')}",
        f"- OK: {result.get('ok')}",
        f"- Dry run: {result.get('dry_run')}",
        f"- Command executed: {result.get('command_executed')}",
        f"- External send performed: {result.get('external_send_performed')}",
        f"- External publish performed: {result.get('external_publish_performed')}",
        "",
        "## Task",
        "",
        f"- Task ID: {result.get('task', {}).get('task_id')}",
        f"- Agent: {result.get('task', {}).get('agent_id')}",
        f"- Action: {result.get('task', {}).get('action_id')}",
        f"- Status: {result.get('task', {}).get('status')}",
        "",
        "## Blockers",
        ""
    ]

    if result.get("blockers"):
        for item in result.get("blockers", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker.")

    DISPATCH_MD.write_text("\n".join(lines), encoding="utf-8")


def queue_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    tasks = report.get("tasks", [])
    pending = [item for item in tasks if item.get("status") in {"queued", "triage", "approved_for_dispatch", "dispatched_dry_run"}]
    blocked = [item for item in tasks if item.get("status") == "blocked"]

    snapshot = {
        "ok": True,
        "checkpoint": "039",
        "module": "k_os_agent_orchestration_queue_core",
        "status": "queue_snapshot",
        "generated_at": now(),
        "pending_count": len(pending),
        "blocked_count": len(blocked),
        "pending_tasks": pending,
        "blocked_tasks": blocked,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    SNAPSHOT_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Queue Snapshot",
        "",
        f"- Generated at: {snapshot.get('generated_at')}",
        f"- Pending: {snapshot.get('pending_count')}",
        f"- Blocked: {snapshot.get('blocked_count')}",
        f"- External send enabled: {snapshot.get('external_send_enabled')}",
        "",
        "## Pending tasks",
        ""
    ]

    if pending:
        for item in pending:
            lines.append(f"- {item.get('task_id')} | {item.get('agent_id')} | {item.get('action_id')} | {item.get('status')}")
    else:
        lines.append("- Nenhuma tarefa pendente.")

    lines.extend(["", "## Blocked tasks", ""])

    if blocked:
        for item in blocked:
            lines.append(f"- {item.get('task_id')} | {item.get('agent_id')} | {item.get('blocked_reason')}")
    else:
        lines.append("- Nenhuma tarefa bloqueada.")

    SNAPSHOT_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def compute_metrics(tasks: list[dict[str, Any]], dispatches: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    agent_counts: dict[str, int] = {}

    for task in tasks:
        status_counts[task.get("status", "unknown")] = status_counts.get(task.get("status", "unknown"), 0) + 1
        priority_counts[task.get("priority", "unknown")] = priority_counts.get(task.get("priority", "unknown"), 0) + 1
        agent_counts[task.get("agent_id", "unknown")] = agent_counts.get(task.get("agent_id", "unknown"), 0) + 1

    return {
        "task_count": len(tasks),
        "dispatch_count": len(dispatches),
        "blocked_task_count": status_counts.get("blocked", 0),
        "queued_task_count": status_counts.get("queued", 0),
        "approved_task_count": status_counts.get("approved_for_dispatch", 0),
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "agent_counts": agent_counts
    }


def audit_report() -> dict[str, Any]:
    queue = ensure_queue()
    policy = load_policy()

    tasks = [safe_task(item) for item in queue.get("tasks", [])]
    dispatches = [safe_dispatch(item) for item in queue.get("dispatches", [])[-50:]]
    activities = [safe_activity(item) for item in queue.get("activities", [])[-30:]]

    metrics = compute_metrics(tasks, dispatches)

    report = {
        "ok": True,
        "checkpoint": "039",
        "module": "k_os_agent_orchestration_queue_core",
        "status": "audit_generated",
        "generated_at": now(),
        "agent_queue_path": "local_secrets/k_os_agent_queue/agent_orchestration_queue.json",
        "agent_queue_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "arbitrary_agent_execution_allowed": False,
        "dispatch_via_command_center_only": True,
        "dry_run_default": True,
        "command_center_available": COMMAND_CENTER_SCRIPT.exists(),
        "command_center_catalog_available": COMMAND_CENTER_CATALOG.exists(),
        "permission_matrix_available": PERMISSION_MATRIX.exists(),
        "tasks": tasks,
        "recent_dispatches": dispatches,
        "recent_activities": activities,
        "metrics": metrics,
        "required_gates_before_dispatch": policy.get("required_gates_before_dispatch", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "040 - K-Agent Runtime Supervisor Core")
    }

    write_report(report)
    queue_snapshot(report)
    event("agent_queue.audit_generated", {"task_count": metrics["task_count"]})
    return report


def write_report(report: dict[str, Any]) -> None:
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Orchestration Queue Core",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Queue committed: {report.get('agent_queue_committed')}",
        f"- Command Center available: {report.get('command_center_available')}",
        f"- Permission Matrix available: {report.get('permission_matrix_available')}",
        f"- Dry-run default: {report.get('dry_run_default')}",
        f"- Dispatch via Command Center only: {report.get('dispatch_via_command_center_only')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in report.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Tasks", ""])

    if report.get("tasks"):
        for item in report.get("tasks", []):
            lines.append(
                f"- {item.get('task_id')} | {item.get('agent_id')} | {item.get('action_id')} | "
                f"priority={item.get('priority')} | status={item.get('status')} | approved={item.get('approved')}"
            )
    else:
        lines.append("- Nenhuma tarefa registrada.")

    lines.extend(["", "## Recent dispatches", ""])

    if report.get("recent_dispatches"):
        for item in report.get("recent_dispatches", []):
            lines.append(
                f"- {item.get('dispatch_id')} | task={item.get('task_id')} | status={item.get('status')} | "
                f"dry_run={item.get('dry_run')} | executed={item.get('command_executed')}"
            )
    else:
        lines.append("- Nenhum dispatch registrado.")

    lines.extend(["", "## Required gates before dispatch", ""])

    for gate in report.get("required_gates_before_dispatch", []):
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
    parser.add_argument("--mode", choices=["init", "create-demo", "create-task", "approve-task", "dispatch-task", "audit", "show"], required=True)
    parser.add_argument("--agent-id", default="k_atlas_engineer")
    parser.add_argument("--action-id", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--reason", default="")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_queue()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "create-task":
        if not args.action_id:
            raise SystemExit("Informe --action-id")
        result = create_task(args.agent_id, args.action_id, args.title, args.priority, args.reason)

    elif args.mode == "approve-task":
        if not args.task_id:
            raise SystemExit("Informe --task-id")
        result = approve_task(args.task_id, args.reason)

    elif args.mode == "dispatch-task":
        if not args.task_id:
            raise SystemExit("Informe --task-id")
        result = dispatch_task(args.task_id, args.execute, args.approved, args.reason)

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