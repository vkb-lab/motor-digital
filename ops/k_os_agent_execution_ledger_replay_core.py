# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "agent_ledger" / "k_os_agent_execution_ledger_replay_policy.json"
LEDGER_DIR = ROOT / "local_secrets" / "k_os_agent_ledger"
LEDGER_PATH = LEDGER_DIR / "agent_execution_ledger.json"

REPORT_DIR = ROOT / "reports" / "agent_ledger"
MEMORY_DIR = ROOT / "memory" / "agent_ledger"

LATEST_JSON = REPORT_DIR / "latest_agent_execution_ledger_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_execution_ledger_report.md"
SNAPSHOT_JSON = REPORT_DIR / "latest_agent_execution_evidence_snapshot.json"
SNAPSHOT_MD = REPORT_DIR / "latest_agent_execution_evidence_snapshot.md"
REPLAY_JSON = REPORT_DIR / "latest_agent_execution_replay_report.json"
REPLAY_MD = REPORT_DIR / "latest_agent_execution_replay_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

COMMAND_CENTER_SCRIPT = ROOT / "ops" / "k_os_command_center_action_router.py"
COMMAND_CENTER_EXECUTION = ROOT / "reports" / "command_center" / "latest_action_execution_report.json"
COMMAND_CENTER_CATALOG = ROOT / "reports" / "command_center" / "latest_action_catalog.json"
AGENT_QUEUE_DISPATCH = ROOT / "reports" / "agent_queue" / "latest_agent_dispatch_report.json"
AGENT_QUEUE_REPORT = ROOT / "reports" / "agent_queue" / "latest_agent_orchestration_queue_report.json"
AGENT_RUNTIME_REPORT = ROOT / "reports" / "agent_runtime" / "latest_agent_runtime_supervisor_report.json"
PERMISSION_MATRIX = ROOT / "config" / "governance" / "k_os_agent_permission_matrix.json"


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


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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
        raise RuntimeError("Agent ledger policy not found.")
    return data


def ensure_ledger() -> dict[str, Any]:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not LEDGER_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_publish_enabled": False,
            "entries": [],
            "replays": [],
            "activities": []
        }
        write_json(LEDGER_PATH, data)

    ledger = read_json(LEDGER_PATH)
    if not ledger:
        raise RuntimeError("Could not load execution ledger.")
    return ledger


def save_ledger(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(LEDGER_PATH, data)


def safe_text(value: Any, limit: int = 300) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", "\n")
    if len(text) > limit:
        return text[:limit] + "...[truncated]"
    return text


def command_action_exists(action_id: str) -> bool:
    catalog = read_json(COMMAND_CENTER_CATALOG) or {}
    for item in catalog.get("actions", []):
        if item.get("action_id") == action_id:
            return True
    return False


def command_action_risk(action_id: str) -> str:
    catalog = read_json(COMMAND_CENTER_CATALOG) or {}
    for item in catalog.get("actions", []):
        if item.get("action_id") == action_id:
            return item.get("risk", "unknown")
    return "unknown"


def latest_source_payload() -> tuple[str, dict[str, Any]]:
    dispatch = read_json(AGENT_QUEUE_DISPATCH)
    if dispatch and not dispatch.get("_read_error"):
        return "agent_queue_dispatch", dispatch

    command = read_json(COMMAND_CENTER_EXECUTION)
    if command and not command.get("_read_error"):
        return "command_center_execution", command

    return "synthetic_demo", {
        "ok": True,
        "status": "synthetic_demo",
        "action_id": "cockpit_audit",
        "agent_id": "k_atlas_engineer",
        "dry_run": True,
        "command_executed": False,
        "summary": "Synthetic demo entry because no execution source report was available."
    }


def build_entry(source_type: str, payload: dict[str, Any], reason: str) -> dict[str, Any]:
    task = payload.get("task", {}) if isinstance(payload.get("task"), dict) else {}
    command_result = payload.get("command_center_result", {}) if isinstance(payload.get("command_center_result"), dict) else {}

    action_id = (
        payload.get("action_id")
        or task.get("action_id")
        or command_result.get("action_id")
        or "unknown"
    )

    agent_id = (
        payload.get("agent_id")
        or task.get("agent_id")
        or "k_atlas_engineer"
    )

    source_execution_id = (
        payload.get("execution_id")
        or payload.get("dispatch_id")
        or command_result.get("execution_id")
        or ""
    )

    command_executed = bool(
        payload.get("command_executed", False)
        or command_result.get("command_executed", False)
    )

    dry_run = bool(
        payload.get("dry_run", True)
        if "dry_run" in payload
        else command_result.get("dry_run", True)
    )

    ok = bool(payload.get("ok", False))
    if command_result:
        ok = bool(command_result.get("ok", ok))

    status = payload.get("status") or command_result.get("status") or "recorded"

    sanitized_input = {
        "source_type": source_type,
        "action_id": action_id,
        "agent_id": agent_id,
        "task_id": task.get("task_id") or payload.get("task_id", ""),
        "dry_run": dry_run,
        "reason": reason or "ledger_record"
    }

    sanitized_output = {
        "ok": ok,
        "status": status,
        "command_executed": command_executed,
        "external_send_performed": False,
        "external_publish_performed": False,
        "returncode": payload.get("command_center_returncode", payload.get("returncode", "")),
        "stdout_tail_preview": safe_text(payload.get("stdout_tail") or command_result.get("stdout_tail") or ""),
        "stderr_tail_preview": safe_text(payload.get("stderr_tail") or command_result.get("stderr_tail") or "")
    }

    return {
        "ledger_id": "led_" + uuid.uuid4().hex[:12],
        "created_at": now(),
        "source_type": source_type,
        "source_execution_id": source_execution_id,
        "agent_id": agent_id,
        "action_id": action_id,
        "task_id": sanitized_input.get("task_id", ""),
        "status": status,
        "ok": ok,
        "risk": command_action_risk(action_id),
        "dry_run": dry_run,
        "command_executed": command_executed,
        "reason": reason or "ledger_record",
        "input_hash": stable_hash(sanitized_input),
        "output_hash": stable_hash(sanitized_output),
        "payload_hash": stable_hash(payload),
        "sanitized_input": sanitized_input,
        "sanitized_output": sanitized_output,
        "external_send_performed": False,
        "external_publish_performed": False,
        "replay_allowed": action_id != "unknown",
        "review_status": "pending_review"
    }


def safe_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "ledger_id": entry.get("ledger_id"),
        "created_at": entry.get("created_at"),
        "source_type": entry.get("source_type"),
        "source_execution_id": entry.get("source_execution_id"),
        "agent_id": entry.get("agent_id"),
        "action_id": entry.get("action_id"),
        "task_id": entry.get("task_id", ""),
        "status": entry.get("status"),
        "ok": entry.get("ok"),
        "risk": entry.get("risk"),
        "dry_run": entry.get("dry_run"),
        "command_executed": entry.get("command_executed"),
        "input_hash": entry.get("input_hash"),
        "output_hash": entry.get("output_hash"),
        "payload_hash": entry.get("payload_hash"),
        "review_status": entry.get("review_status", "pending_review"),
        "replay_allowed": entry.get("replay_allowed", False),
        "external_send_performed": False,
        "external_publish_performed": False
    }


def safe_replay(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "replay_id": item.get("replay_id"),
        "ledger_id": item.get("ledger_id"),
        "action_id": item.get("action_id"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "dry_run": item.get("dry_run"),
        "command_executed": item.get("command_executed"),
        "approved": item.get("approved"),
        "created_at": item.get("created_at")
    }


def record_latest(reason: str) -> dict[str, Any]:
    ledger = ensure_ledger()
    source_type, payload = latest_source_payload()
    entry = build_entry(source_type, payload, reason)

    ledger.setdefault("entries", []).append(entry)
    ledger.setdefault("activities", []).append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "execution_recorded",
        "summary": "Execution recorded from " + source_type,
        "created_at": now(),
        "created_by": "k_os_agent_execution_ledger"
    })

    ledger["entries"] = ledger["entries"][-500:]
    ledger["activities"] = ledger["activities"][-500:]
    save_ledger(ledger)
    event("agent_ledger.execution_recorded", {"ledger_id": entry["ledger_id"], "source_type": source_type})
    return audit_report()


def create_demo() -> dict[str, Any]:
    ledger = ensure_ledger()
    if not ledger.get("entries"):
        return record_latest("demo_execution_ledger_record")
    return audit_report()


def find_entry(ledger_id: str) -> dict[str, Any] | None:
    ledger = ensure_ledger()
    for entry in ledger.get("entries", []):
        if entry.get("ledger_id") == ledger_id:
            return entry
    return None


def write_replay(result: dict[str, Any]) -> None:
    REPLAY_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Execution Replay Report",
        "",
        "- Replay ID: " + str(result.get("replay_id")),
        "- Ledger ID: " + str(result.get("ledger_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Dry run: " + str(result.get("dry_run")),
        "- Approved: " + str(result.get("approved")),
        "- Command executed: " + str(result.get("command_executed")),
        "- External send performed: " + str(result.get("external_send_performed")),
        "- External publish performed: " + str(result.get("external_publish_performed")),
        "",
        "## Blockers",
        ""
    ]

    blockers = result.get("blockers", [])
    if blockers:
        for item in blockers:
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    entry = result.get("entry", {})
    if entry:
        lines.extend([
            "",
            "## Entry",
            "",
            "- Action: " + str(entry.get("action_id")),
            "- Agent: " + str(entry.get("agent_id")),
            "- Input hash: " + str(entry.get("input_hash")),
            "- Output hash: " + str(entry.get("output_hash"))
        ])

    REPLAY_MD.write_text("\n".join(lines), encoding="utf-8")


def record_replay(ledger: dict[str, Any], result: dict[str, Any]) -> None:
    ledger.setdefault("replays", []).append({
        "replay_id": result.get("replay_id"),
        "ledger_id": result.get("ledger_id"),
        "action_id": result.get("action_id") or result.get("entry", {}).get("action_id"),
        "status": result.get("status"),
        "ok": result.get("ok"),
        "dry_run": result.get("dry_run"),
        "command_executed": result.get("command_executed"),
        "approved": result.get("approved"),
        "created_at": result.get("generated_at")
    })

    ledger.setdefault("activities", []).append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "replay_recorded",
        "summary": "Replay recorded for ledger " + str(result.get("ledger_id")),
        "created_at": now(),
        "created_by": "k_os_agent_execution_ledger"
    })

    ledger["replays"] = ledger["replays"][-300:]
    ledger["activities"] = ledger["activities"][-500:]
    save_ledger(ledger)


def replay_entry(ledger_id: str, execute: bool, approved: bool, reason: str) -> dict[str, Any]:
    ledger = ensure_ledger()
    policy = load_policy()
    entry = find_entry(ledger_id)

    replay_id = "rpl_" + uuid.uuid4().hex[:12]
    blockers = []

    if not entry:
        blockers.append("ledger_entry_not_found")
        result = {
            "ok": False,
            "checkpoint": "041",
            "module": "k_os_agent_execution_ledger_replay_core",
            "status": "replay_blocked",
            "generated_at": now(),
            "replay_id": replay_id,
            "ledger_id": ledger_id,
            "blockers": blockers,
            "warnings": [],
            "dry_run": not execute,
            "approved": approved,
            "command_executed": False,
            "external_send_performed": False,
            "external_publish_performed": False
        }
        write_replay(result)
        return result

    action_id = entry.get("action_id", "")

    if not entry.get("replay_allowed"):
        blockers.append("replay_not_allowed_for_entry")

    if not command_action_exists(action_id):
        blockers.append("action_not_found_in_command_center_catalog")

    if not COMMAND_CENTER_SCRIPT.exists():
        blockers.append("command_center_script_missing")

    if execute and not approved:
        blockers.append("replay_execution_requires_approval")

    if execute and not reason:
        blockers.append("replay_execution_requires_operator_reason")

    if blockers:
        result = {
            "ok": False,
            "checkpoint": "041",
            "module": "k_os_agent_execution_ledger_replay_core",
            "status": "replay_blocked",
            "generated_at": now(),
            "replay_id": replay_id,
            "ledger_id": ledger_id,
            "entry": safe_entry(entry),
            "blockers": blockers,
            "warnings": [],
            "dry_run": not execute,
            "approved": approved,
            "reason": reason,
            "command_executed": False,
            "external_send_performed": False,
            "external_publish_performed": False,
            "required_gates_before_replay": policy.get("required_gates_before_replay", [])
        }
        write_replay(result)
        record_replay(ledger, result)
        event("agent_ledger.replay_blocked", {"ledger_id": ledger_id, "blockers": blockers})
        return result

    args = [
        sys.executable,
        str(COMMAND_CENTER_SCRIPT),
        "--mode",
        "route",
        "--action-id",
        action_id,
        "--reason",
        reason or ("ledger_replay_" + ledger_id)
    ]

    if approved:
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

    try:
        router_payload = json.loads(completed.stdout)
    except Exception:
        router_payload = {
            "stdout_tail": completed.stdout[-2000:],
            "stderr_tail": completed.stderr[-2000:]
        }

    command_executed = bool(router_payload.get("command_executed", False))
    ok = completed.returncode == 0 and bool(router_payload.get("ok", False))

    result = {
        "ok": ok,
        "checkpoint": "041",
        "module": "k_os_agent_execution_ledger_replay_core",
        "status": "replay_completed" if ok else "replay_failed",
        "generated_at": now(),
        "replay_id": replay_id,
        "ledger_id": ledger_id,
        "entry": safe_entry(entry),
        "action_id": action_id,
        "dry_run": not execute,
        "approved": approved,
        "reason": reason,
        "command_executed": command_executed,
        "command_center_returncode": completed.returncode,
        "command_center_result_hash": stable_hash(router_payload),
        "command_center_status": router_payload.get("status", ""),
        "command_center_decision": router_payload.get("decision", ""),
        "blockers": router_payload.get("blockers", []),
        "warnings": [],
        "external_send_performed": False,
        "external_publish_performed": False
    }

    write_replay(result)
    record_replay(ledger, result)
    event("agent_ledger.replay_completed", {"ledger_id": ledger_id, "ok": ok, "command_executed": command_executed})
    return result


def compute_metrics(entries: list[dict[str, Any]], replays: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = {}
    action_counts = {}
    agent_counts = {}

    for entry in entries:
        status = entry.get("status", "unknown")
        action_id = entry.get("action_id", "unknown")
        agent_id = entry.get("agent_id", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        action_counts[action_id] = action_counts.get(action_id, 0) + 1
        agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1

    return {
        "ledger_entry_count": len(entries),
        "replay_count": len(replays),
        "executed_entry_count": sum(1 for item in entries if item.get("command_executed")),
        "dry_run_entry_count": sum(1 for item in entries if item.get("dry_run")),
        "failed_entry_count": sum(1 for item in entries if item.get("ok") is False),
        "replay_dry_run_count": sum(1 for item in replays if item.get("dry_run")),
        "replay_executed_count": sum(1 for item in replays if item.get("command_executed")),
        "status_counts": status_counts,
        "action_counts": action_counts,
        "agent_counts": agent_counts
    }


def evidence_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    entries = report.get("entries", [])
    replays = report.get("recent_replays", [])

    snapshot = {
        "ok": True,
        "checkpoint": "041",
        "module": "k_os_agent_execution_ledger_replay_core",
        "status": "evidence_snapshot_generated",
        "generated_at": now(),
        "entry_count": len(entries),
        "replay_count": len(replays),
        "latest_entries": entries[:20],
        "latest_replays": replays[:20],
        "hash_chain_preview": [
            {
                "ledger_id": item.get("ledger_id"),
                "input_hash": item.get("input_hash"),
                "output_hash": item.get("output_hash"),
                "payload_hash": item.get("payload_hash")
            }
            for item in entries[:20]
        ],
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    SNAPSHOT_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Execution Evidence Snapshot",
        "",
        "- Generated at: " + str(snapshot.get("generated_at")),
        "- Entries: " + str(snapshot.get("entry_count")),
        "- Replays: " + str(snapshot.get("replay_count")),
        "- External send enabled: " + str(snapshot.get("external_send_enabled")),
        "",
        "## Hash chain preview",
        ""
    ]

    if snapshot["hash_chain_preview"]:
        for item in snapshot["hash_chain_preview"]:
            lines.append(
                "- " + str(item.get("ledger_id")) +
                " | input=" + str(item.get("input_hash")) +
                " | output=" + str(item.get("output_hash"))
            )
    else:
        lines.append("- Nenhuma evidência registrada.")

    SNAPSHOT_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def audit_report() -> dict[str, Any]:
    ledger = ensure_ledger()
    policy = load_policy()

    entries = [safe_entry(item) for item in ledger.get("entries", [])]
    entries = list(reversed(entries))[:100]
    replays = [safe_replay(item) for item in reversed(ledger.get("replays", []))][:50]

    metrics = compute_metrics(entries, replays)

    report = {
        "ok": True,
        "checkpoint": "041",
        "module": "k_os_agent_execution_ledger_replay_core",
        "status": "audit_generated",
        "generated_at": now(),
        "ledger_path": "local_secrets/k_os_agent_ledger/agent_execution_ledger.json",
        "ledger_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "replay_dry_run_default": True,
        "replay_execution_requires_approval": True,
        "command_center_available": COMMAND_CENTER_SCRIPT.exists(),
        "command_center_catalog_available": COMMAND_CENTER_CATALOG.exists(),
        "agent_queue_report_available": AGENT_QUEUE_REPORT.exists(),
        "agent_runtime_report_available": AGENT_RUNTIME_REPORT.exists(),
        "permission_matrix_available": PERMISSION_MATRIX.exists(),
        "entries": entries,
        "recent_replays": replays,
        "metrics": metrics,
        "required_gates_before_replay": policy.get("required_gates_before_replay", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "042 - K-Memory Event Bus and Context Index Core")
    }

    write_report(report)
    evidence_snapshot(report)
    event("agent_ledger.audit_generated", {"entry_count": metrics["ledger_entry_count"]})
    return report


def write_report(report: dict[str, Any]) -> None:
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    metrics = report.get("metrics", {})

    lines = [
        "# K-OS Agent Execution Ledger and Replay Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- Ledger committed: " + str(report.get("ledger_committed")),
        "- Replay dry-run default: " + str(report.get("replay_dry_run_default")),
        "- Replay execution requires approval: " + str(report.get("replay_execution_requires_approval")),
        "- Command Center available: " + str(report.get("command_center_available")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Ledger entries", ""])

    if report.get("entries"):
        for item in report.get("entries", [])[:30]:
            lines.append(
                "- " + str(item.get("ledger_id")) +
                " | " + str(item.get("agent_id")) +
                " | " + str(item.get("action_id")) +
                " | status=" + str(item.get("status")) +
                " | dry_run=" + str(item.get("dry_run")) +
                " | executed=" + str(item.get("command_executed"))
            )
    else:
        lines.append("- Nenhuma entrada registrada.")

    lines.extend(["", "## Recent replays", ""])

    if report.get("recent_replays"):
        for item in report.get("recent_replays", [])[:20]:
            lines.append(
                "- " + str(item.get("replay_id")) +
                " | ledger=" + str(item.get("ledger_id")) +
                " | status=" + str(item.get("status")) +
                " | dry_run=" + str(item.get("dry_run")) +
                " | executed=" + str(item.get("command_executed"))
            )
    else:
        lines.append("- Nenhum replay registrado.")

    lines.extend(["", "## Required gates before replay", ""])

    for gate in report.get("required_gates_before_replay", []):
        lines.append("- " + str(gate))

    lines.extend(["", "## Blocked actions", ""])

    for item in report.get("blocked_actions", []):
        lines.append("- " + str(item))

    lines.extend(["", "## Next checkpoint", "", "- " + str(report.get("next_checkpoint"))])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def show_latest() -> int:
    if LATEST_JSON.exists():
        print(LATEST_JSON.read_text(encoding="utf-8-sig"))
    else:
        print("{}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "record-latest", "create-demo", "replay", "audit", "show"], required=True)
    parser.add_argument("--ledger-id", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_ledger()
        result = audit_report()

    elif args.mode == "record-latest":
        result = record_latest(args.reason)

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "replay":
        if not args.ledger_id:
            raise SystemExit("Informe --ledger-id")
        result = replay_entry(args.ledger_id, args.execute, args.approved, args.reason)

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