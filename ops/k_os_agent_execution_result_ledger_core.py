# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "execution_result_ledger" / "k_os_agent_execution_result_ledger_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_execution_result_ledger"
STATE_PATH = STATE_DIR / "agent_execution_result_ledger_state.json"

REPORT_DIR = ROOT / "reports" / "execution_result_ledger"
MEMORY_DIR = ROOT / "memory" / "execution_result_ledger"

LATEST_JSON = REPORT_DIR / "latest_agent_execution_result_ledger_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_execution_result_ledger_report.md"
RECORD_JSON = REPORT_DIR / "latest_execution_result_ledger_record.json"
RECORD_MD = REPORT_DIR / "latest_execution_result_ledger_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_execution_result_ledger_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_execution_result_ledger_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

ALLOWLISTED_EXECUTION = ROOT / "reports" / "allowlisted_action_executor" / "latest_allowlisted_action_execution.json"
ALLOWLISTED_VALIDATION = ROOT / "reports" / "allowlisted_action_executor" / "latest_allowlisted_action_execution_validation_report.json"
ALLOWLISTED_REPORT = ROOT / "reports" / "allowlisted_action_executor" / "latest_agent_allowlisted_action_executor_report.json"

SAFE_ROUTE = ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route.json"
APPROVAL_DECISION = ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_decision.json"
DRY_RUN_RESULT = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_result.json"
PROMPT_PACKAGE = ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_package.json"
EXECUTION_PLAN = ROOT / "reports" / "prompt_assembly" / "latest_agent_execution_plan.json"
AGENT_LEDGER_REPORT = ROOT / "reports" / "agent_ledger" / "latest_agent_execution_ledger_report.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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
        raise RuntimeError("Execution Result Ledger policy not found.")
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
            "append_only": True,
            "records": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load execution result ledger state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def report_ref(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if not data or data.get("_read_error"):
        return {
            "available": False,
            "path": str(path).replace(str(ROOT) + "\\", "").replace(str(ROOT) + "/", ""),
            "hash": ""
        }

    return {
        "available": True,
        "path": str(path).replace(str(ROOT) + "\\", "").replace(str(ROOT) + "/", ""),
        "checkpoint": data.get("checkpoint", ""),
        "module": data.get("module", ""),
        "status": data.get("status", ""),
        "ok": data.get("ok", None),
        "generated_at": data.get("generated_at", data.get("created_at", "")),
        "hash": stable_hash(data)
    }


def load_execution() -> dict[str, Any]:
    data = read_json(ALLOWLISTED_EXECUTION)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "execution_id": "",
        "executed_action": "",
        "execution_evidence_hash": "",
        "pre_execution_evidence_hash": "",
        "post_execution_evidence_hash": "",
        "approval_token_included": False,
        "arbitrary_command_executed": False,
        "shell_command_executed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": ["allowlisted_execution_missing"]
    }


def load_execution_validation() -> dict[str, Any]:
    data = read_json(ALLOWLISTED_VALIDATION)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "execution_id": "",
        "blockers": ["allowlisted_execution_validation_missing"]
    }


def ledger_gate_check(execution: dict[str, Any], validation: dict[str, Any]) -> list[str]:
    blockers = []

    if not execution.get("execution_id"):
        blockers.append("execution_id_missing")

    if execution.get("status") != "executed":
        blockers.append("execution_status_not_executed")

    if validation.get("ok") is not True:
        blockers.append("execution_validation_not_ok")

    if validation.get("status") != "validated":
        blockers.append("execution_validation_status_not_validated")

    if validation.get("execution_id") and execution.get("execution_id") and validation.get("execution_id") != execution.get("execution_id"):
        blockers.append("execution_validation_id_mismatch")

    if not execution.get("execution_evidence_hash"):
        blockers.append("execution_evidence_hash_missing")

    if not execution.get("pre_execution_evidence_hash"):
        blockers.append("pre_execution_evidence_hash_missing")

    if not execution.get("post_execution_evidence_hash"):
        blockers.append("post_execution_evidence_hash_missing")

    if execution.get("approval_token_included") is True:
        blockers.append("approval_token_included")

    if execution.get("arbitrary_command_executed") is True:
        blockers.append("arbitrary_command_executed")

    if execution.get("shell_command_executed") is True:
        blockers.append("shell_command_executed")

    if execution.get("external_send_performed") is True:
        blockers.append("external_send_performed")

    if execution.get("external_publish_performed") is True:
        blockers.append("external_publish_performed")

    if execution.get("external_provider_called") is True:
        blockers.append("external_provider_called")

    return blockers


def previous_record_hash(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    return records[-1].get("ledger_record_hash", "")


def create_record(reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    execution = load_execution()
    validation = load_execution_validation()
    blockers = ledger_gate_check(execution, validation)

    record_id = "led_" + uuid.uuid4().hex[:12]
    prev_hash = previous_record_hash(state.get("records", []))

    record_body = {
        "record_id": record_id,
        "previous_record_hash": prev_hash,
        "execution_id": execution.get("execution_id", ""),
        "executed_action": execution.get("executed_action", ""),
        "execution_evidence_hash": execution.get("execution_evidence_hash", ""),
        "pre_execution_evidence_hash": execution.get("pre_execution_evidence_hash", ""),
        "post_execution_evidence_hash": execution.get("post_execution_evidence_hash", ""),
        "route_id": execution.get("route_id", ""),
        "approval_token_hash": execution.get("approval_token_hash", ""),
        "dry_run_evidence_hash": execution.get("dry_run_evidence_hash", ""),
        "source_refs": {
            "allowlisted_execution": report_ref(ALLOWLISTED_EXECUTION),
            "allowlisted_validation": report_ref(ALLOWLISTED_VALIDATION),
            "safe_route": report_ref(SAFE_ROUTE),
            "approval_decision": report_ref(APPROVAL_DECISION),
            "dry_run_result": report_ref(DRY_RUN_RESULT),
            "prompt_package": report_ref(PROMPT_PACKAGE),
            "execution_plan": report_ref(EXECUTION_PLAN)
        }
    }

    record_hash = stable_hash(record_body)

    record = {
        "ok": len(blockers) == 0,
        "checkpoint": "050",
        "module": "k_os_agent_execution_result_ledger_core",
        "status": "recorded" if len(blockers) == 0 else "blocked",
        "ledger_record_id": record_id,
        "created_at": now(),
        "reason": reason or "execution_result_recorded",
        "previous_record_hash": prev_hash,
        "ledger_record_hash": record_hash,
        "chain_hash": stable_hash({"previous": prev_hash, "current": record_hash}),
        "execution_id": execution.get("execution_id", ""),
        "executed_action": execution.get("executed_action", ""),
        "agent_id": execution.get("agent_id", ""),
        "task_id": execution.get("task_id", ""),
        "route_id": execution.get("route_id", ""),
        "execution_status": execution.get("status", ""),
        "execution_evidence_hash": execution.get("execution_evidence_hash", ""),
        "pre_execution_evidence_hash": execution.get("pre_execution_evidence_hash", ""),
        "post_execution_evidence_hash": execution.get("post_execution_evidence_hash", ""),
        "approval_token_hash": execution.get("approval_token_hash", ""),
        "approval_token_included": False,
        "dry_run_evidence_hash": execution.get("dry_run_evidence_hash", ""),
        "arbitrary_command_executed": False,
        "shell_command_executed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "external_provider_called": False,
        "raw_payload_included": False,
        "source_refs": record_body["source_refs"],
        "blockers": blockers,
        "required_gates_before_ledger_record": policy.get("required_gates_before_ledger_record", []),
        "next_action": "replay_and_forensics_viewer" if len(blockers) == 0 else "resolve_blockers"
    }

    state.setdefault("records", []).append(record)
    state["records"] = state["records"][-500:]
    save_state(state)

    write_record(record)

    event("execution_result_ledger.record_created", {
        "ledger_record_id": record_id,
        "execution_id": execution.get("execution_id", ""),
        "ok": record.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def latest_record_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("records", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_record_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("ledger_record_not_found")
    else:
        if record.get("status") != "recorded":
            blockers.append("ledger_record_not_recorded")

        if not record.get("ledger_record_hash"):
            blockers.append("ledger_record_hash_missing")

        if not record.get("chain_hash"):
            blockers.append("chain_hash_missing")

        if not record.get("execution_id"):
            blockers.append("execution_id_missing")

        if not record.get("execution_evidence_hash"):
            blockers.append("execution_evidence_hash_missing")

        if record.get("approval_token_included") is True:
            blockers.append("approval_token_included")

        if record.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if record.get("arbitrary_command_executed") is True:
            blockers.append("arbitrary_command_executed")

        if record.get("shell_command_executed") is True:
            blockers.append("shell_command_executed")

        if record.get("external_send_performed") is True:
            blockers.append("external_send_performed")

        if record.get("external_publish_performed") is True:
            blockers.append("external_publish_performed")

        if record.get("previous_record_hash") == record.get("ledger_record_hash"):
            blockers.append("record_hash_self_reference")

        if not record.get("previous_record_hash"):
            warnings.append("first_ledger_record")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "050",
        "module": "k_os_agent_execution_result_ledger_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "ledger_record_id": record.get("ledger_record_id") if record else "",
        "execution_id": record.get("execution_id") if record else "",
        "executed_action": record.get("executed_action") if record else "",
        "ledger_record_hash": record.get("ledger_record_hash") if record else "",
        "chain_hash": record.get("chain_hash") if record else "",
        "approval_token_included": False,
        "raw_payload_included": False,
        "arbitrary_command_executed": False,
        "shell_command_executed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if record and len(blockers) == 0:
        record["status"] = "validated"
        record["validated_at"] = validation["generated_at"]

    save_state(state)
    write_validation(validation)

    event("execution_result_ledger.validation_completed", {
        "ledger_record_id": validation.get("ledger_record_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_record_for_report(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "ledger_record_id": item.get("ledger_record_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "execution_id": item.get("execution_id"),
        "executed_action": item.get("executed_action"),
        "agent_id": item.get("agent_id"),
        "task_id": item.get("task_id"),
        "route_id": item.get("route_id"),
        "ledger_record_hash": item.get("ledger_record_hash"),
        "previous_record_hash": item.get("previous_record_hash"),
        "chain_hash": item.get("chain_hash"),
        "execution_evidence_hash": item.get("execution_evidence_hash"),
        "approval_token_included": False,
        "raw_payload_included": False,
        "arbitrary_command_executed": False,
        "shell_command_executed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": item.get("blockers", [])
    }


def compute_metrics(records: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}

    for item in records:
        status = item.get("status", "unknown")
        action = item.get("executed_action", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        action_counts[action] = action_counts.get(action, 0) + 1

    return {
        "ledger_record_count": len(records),
        "validation_count": len(validations),
        "recorded_count": status_counts.get("recorded", 0),
        "validated_count": status_counts.get("validated", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "approval_token_in_report_count": 0,
        "raw_payload_record_count": 0,
        "external_send_count": 0,
        "external_publish_count": 0,
        "status_counts": status_counts,
        "action_counts": action_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    records = [safe_record_for_report(item) for item in reversed(state.get("records", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(records, validations)

    report = {
        "ok": True,
        "checkpoint": "050",
        "module": "k_os_agent_execution_result_ledger_core",
        "status": "audit_generated",
        "generated_at": now(),
        "ledger_state_path": "local_secrets/k_os_execution_result_ledger/agent_execution_result_ledger_state.json",
        "ledger_state_committed": False,
        "ledger_append_only": True,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "raw_payload_storage_allowed": False,
        "approval_token_storage_in_reports_allowed": False,
        "allowlisted_execution_available": ALLOWLISTED_EXECUTION.exists(),
        "allowlisted_validation_available": ALLOWLISTED_VALIDATION.exists(),
        "safe_route_available": SAFE_ROUTE.exists(),
        "approval_decision_available": APPROVAL_DECISION.exists(),
        "dry_run_result_available": DRY_RUN_RESULT.exists(),
        "prompt_package_available": PROMPT_PACKAGE.exists(),
        "execution_plan_available": EXECUTION_PLAN.exists(),
        "agent_ledger_report_available": AGENT_LEDGER_REPORT.exists(),
        "metrics": metrics,
        "recent_records": records,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_ledger_record": policy.get("required_gates_before_ledger_record", []),
        "next_checkpoint": policy.get("next_checkpoint", "051 - K-Agent Replay and Forensics Viewer Core")
    }

    write_report(report)
    event("execution_result_ledger.audit_generated", {
        "ledger_record_count": metrics.get("ledger_record_count")
    })
    return report


def write_record(record: dict[str, Any]) -> None:
    RECORD_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Execution Result Ledger Record",
        "",
        "- Ledger Record ID: " + str(record.get("ledger_record_id")),
        "- Status: " + str(record.get("status")),
        "- OK: " + str(record.get("ok")),
        "- Execution ID: " + str(record.get("execution_id")),
        "- Executed action: " + str(record.get("executed_action")),
        "- Agent: " + str(record.get("agent_id")),
        "- Route ID: " + str(record.get("route_id")),
        "- Ledger record hash: " + str(record.get("ledger_record_hash")),
        "- Previous record hash: " + str(record.get("previous_record_hash")),
        "- Chain hash: " + str(record.get("chain_hash")),
        "- Execution evidence hash: " + str(record.get("execution_evidence_hash")),
        "- Approval token included: " + str(record.get("approval_token_included")),
        "- Raw payload included: " + str(record.get("raw_payload_included")),
        "- External publish performed: " + str(record.get("external_publish_performed")),
        "",
        "## Blockers",
        ""
    ]

    if record.get("blockers"):
        for item in record.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    RECORD_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Execution Result Ledger Validation",
        "",
        "- Ledger Record ID: " + str(result.get("ledger_record_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Execution ID: " + str(result.get("execution_id")),
        "- Executed action: " + str(result.get("executed_action")),
        "- Ledger record hash: " + str(result.get("ledger_record_hash")),
        "- Chain hash: " + str(result.get("chain_hash")),
        "- Approval token included: " + str(result.get("approval_token_included")),
        "- Raw payload included: " + str(result.get("raw_payload_included")),
        "- External publish performed: " + str(result.get("external_publish_performed")),
        "",
        "## Blockers",
        ""
    ]

    if result.get("blockers"):
        for item in result.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    lines.extend(["", "## Warnings", ""])

    if result.get("warnings"):
        for item in result.get("warnings", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum warning.")

    VALIDATION_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(report: dict[str, Any]) -> None:
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    metrics = report.get("metrics", {})

    lines = [
        "# K-OS Agent Execution Result Ledger Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("ledger_state_committed")),
        "- Append only: " + str(report.get("ledger_append_only")),
        "- Raw payload storage allowed: " + str(report.get("raw_payload_storage_allowed")),
        "- Approval token storage in reports allowed: " + str(report.get("approval_token_storage_in_reports_allowed")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent ledger records", ""])

    if report.get("recent_records"):
        for item in report.get("recent_records", [])[:30]:
            lines.append(
                "- " + str(item.get("ledger_record_id")) +
                " | status=" + str(item.get("status")) +
                " | execution=" + str(item.get("execution_id")) +
                " | action=" + str(item.get("executed_action"))
            )
    else:
        lines.append("- Nenhum registro no ledger.")

    lines.extend(["", "## Required gates before ledger record", ""])

    for gate in report.get("required_gates_before_ledger_record", []):
        lines.append("- " + str(gate))

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
    parser.add_argument("--mode", choices=["init", "record", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "record":
        result = create_record(args.reason)

    elif args.mode == "validate-latest":
        result = validate_latest()

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