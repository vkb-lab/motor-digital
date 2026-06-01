# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "recovery_gate" / "k_os_agent_recovery_gate_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_recovery_gate"
STATE_PATH = STATE_DIR / "agent_recovery_gate_state.json"

REPORT_DIR = ROOT / "reports" / "recovery_gate"
MEMORY_DIR = ROOT / "memory" / "recovery_gate"

LATEST_JSON = REPORT_DIR / "latest_agent_recovery_gate_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_recovery_gate_report.md"
GATE_JSON = REPORT_DIR / "latest_recovery_gate_record.json"
GATE_MD = REPORT_DIR / "latest_recovery_gate_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_recovery_gate_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_recovery_gate_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

PLAN_PATH = ROOT / "reports" / "recovery_plan_builder" / "latest_recovery_plan.json"
PLAN_VALIDATION = ROOT / "reports" / "recovery_plan_builder" / "latest_recovery_plan_validation_report.json"
PLAN_REPORT = ROOT / "reports" / "recovery_plan_builder" / "latest_agent_recovery_plan_builder_report.json"
READINESS_MATRIX = ROOT / "reports" / "recovery_readiness_matrix" / "latest_recovery_readiness_matrix.json"
GOVERNANCE_SUMMARY = ROOT / "reports" / "rollback_governance_summary" / "latest_rollback_governance_summary.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


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
        raise RuntimeError("Recovery gate policy not found.")
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
            "gate_executes_recovery": False,
            "gate_executes_rollback": False,
            "gate_records": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load recovery gate state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def source_ref(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if not data or data.get("_read_error"):
        return {
            "available": False,
            "path": rel(path),
            "status": "missing",
            "hash": ""
        }

    return {
        "available": True,
        "path": rel(path),
        "checkpoint": data.get("checkpoint", ""),
        "module": data.get("module", ""),
        "status": data.get("status", ""),
        "ok": data.get("ok", None),
        "created_at": data.get("created_at", data.get("generated_at", "")),
        "hash": stable_hash(data)
    }


def load_plan() -> dict[str, Any]:
    data = read_json(PLAN_PATH)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "recovery_plan_id": "",
        "recovery_plan_hash": "",
        "readiness_level": "not_ready",
        "risk_level": "high",
        "blockers": ["recovery_plan_missing"]
    }


def normalize_mode(mode: str) -> str:
    value = (mode or "block_recovery").strip().lower()
    if value not in {"block_recovery", "approve_future_recovery", "revoke_recovery"}:
        return "block_recovery"
    return value


def gate_check(plan: dict[str, Any], mode: str, operator: str, confirmation: str, reason: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not confirmation:
        blockers.append("operator_confirmation_missing")

    if not reason:
        blockers.append("reason_missing")

    if not plan.get("recovery_plan_id"):
        blockers.append("recovery_plan_missing")

    if not plan.get("recovery_plan_hash"):
        blockers.append("recovery_plan_hash_missing")

    if plan.get("plan_executes_recovery") is True:
        blockers.append("plan_executes_recovery")

    if plan.get("plan_executes_rollback") is True:
        blockers.append("plan_executes_rollback")

    if plan.get("plan_deletes_data") is True:
        blockers.append("plan_deletes_data")

    if plan.get("plan_modifies_target_files") is True:
        blockers.append("plan_modifies_target_files")

    if plan.get("plan_runs_git_reset") is True:
        blockers.append("plan_runs_git_reset")

    if plan.get("plan_runs_git_force_push") is True:
        blockers.append("plan_runs_git_force_push")

    if plan.get("plan_executes_shell_commands") is True:
        blockers.append("plan_executes_shell_commands")

    if mode == "approve_future_recovery":
        if plan.get("status") != "plan_prepared_review_required":
            blockers.append("recovery_plan_not_prepared_for_approval")

        if plan.get("readiness_level") != "controlled_ready":
            blockers.append("readiness_not_controlled_ready")

        if plan.get("blockers"):
            blockers.append("recovery_plan_has_blockers")

    return sorted(set(blockers))


def create_gate(mode: str, operator: str, confirmation: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    mode = normalize_mode(mode)
    operator = operator or "operator_k_os"
    plan = load_plan()

    blockers = gate_check(plan, mode, operator, confirmation, reason)
    gate_id = "rag_" + uuid.uuid4().hex[:12]

    local_token = ""
    local_token_hash = ""

    if mode == "approve_future_recovery" and len(blockers) == 0:
        status = "approved_for_future_recovery"
        local_token = "kos_recovery_gate_" + secrets.token_urlsafe(32)
        local_token_hash = stable_hash({"token": local_token})
    elif mode == "revoke_recovery":
        status = "revoked"
    else:
        status = "blocked"
        if "operator_blocked_recovery" not in blockers:
            blockers.append("operator_blocked_recovery")

    source_refs = {
        "recovery_plan": source_ref(PLAN_PATH),
        "recovery_plan_validation": source_ref(PLAN_VALIDATION),
        "recovery_plan_report": source_ref(PLAN_REPORT),
        "readiness_matrix": source_ref(READINESS_MATRIX),
        "governance_summary": source_ref(GOVERNANCE_SUMMARY)
    }

    gate_body = {
        "gate_id": gate_id,
        "mode": mode,
        "status": status,
        "operator": operator,
        "confirmation_hash": stable_hash({"confirmation": confirmation}),
        "recovery_plan_id": plan.get("recovery_plan_id", ""),
        "recovery_plan_hash": plan.get("recovery_plan_hash", ""),
        "readiness_level": plan.get("readiness_level", ""),
        "risk_level": plan.get("risk_level", ""),
        "source_refs": source_refs
    }

    record = {
        "ok": True,
        "checkpoint": "063",
        "module": "k_os_agent_recovery_approval_gate_core",
        "status": status,
        "recovery_gate_id": gate_id,
        "created_at": now(),
        "mode": mode,
        "operator": operator,
        "reason": reason or "recovery_gate",
        "operator_confirmation_hash": stable_hash({"confirmation": confirmation}),
        "recovery_plan_id": plan.get("recovery_plan_id", ""),
        "recovery_plan_hash": plan.get("recovery_plan_hash", ""),
        "readiness_matrix_id": plan.get("readiness_matrix_id", ""),
        "readiness_matrix_hash": plan.get("readiness_matrix_hash", ""),
        "readiness_level": plan.get("readiness_level", ""),
        "risk_level": plan.get("risk_level", ""),
        "recovery_gate_record_hash": stable_hash(gate_body),
        "local_recovery_token_hash": local_token_hash,
        "local_recovery_token_stored_local_only": True,
        "local_recovery_token_included": False,
        "gate_executes_recovery": False,
        "gate_executes_rollback": False,
        "gate_deletes_data": False,
        "gate_modifies_target_files": False,
        "gate_runs_git_reset": False,
        "gate_runs_git_force_push": False,
        "gate_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "source_refs": source_refs,
        "blockers": blockers,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_gate": policy.get("required_gates_before_recovery_gate", []),
        "next_action": "recovery_dry_run_simulator" if status == "approved_for_future_recovery" else "recovery_remains_blocked"
    }

    local_record = dict(record)
    local_record["local_recovery_token"] = local_token

    state.setdefault("gate_records", []).append(local_record)
    state["gate_records"] = state["gate_records"][-300:]
    save_state(state)

    write_gate(record)

    event("recovery_gate.record_created", {
        "recovery_gate_id": gate_id,
        "status": status,
        "mode": mode,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_gate_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("gate_records", [])
    if not records:
        return None
    return records[-1]


def sanitize_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "recovery_gate_id": item.get("recovery_gate_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "mode": item.get("mode"),
        "recovery_plan_id": item.get("recovery_plan_id"),
        "readiness_level": item.get("readiness_level"),
        "risk_level": item.get("risk_level"),
        "recovery_gate_record_hash": item.get("recovery_gate_record_hash"),
        "local_recovery_token_hash": item.get("local_recovery_token_hash"),
        "local_recovery_token_included": False,
        "gate_executes_recovery": False,
        "gate_executes_rollback": False,
        "gate_deletes_data": False,
        "gate_modifies_target_files": False,
        "gate_runs_git_reset": False,
        "gate_runs_git_force_push": False,
        "gate_executes_shell_commands": False,
        "raw_payload_included": False,
        "blockers": item.get("blockers", [])
    }


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_gate_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("recovery_gate_record_not_found")
    else:
        if not record.get("recovery_gate_id"):
            blockers.append("recovery_gate_id_missing")

        if not record.get("recovery_gate_record_hash"):
            blockers.append("recovery_gate_hash_missing")

        if not record.get("recovery_plan_id"):
            blockers.append("recovery_plan_id_missing")

        if record.get("local_recovery_token_included") is True:
            blockers.append("local_recovery_token_included")

        if record.get("gate_executes_recovery") is True:
            blockers.append("gate_executes_recovery")

        if record.get("gate_executes_rollback") is True:
            blockers.append("gate_executes_rollback")

        if record.get("gate_deletes_data") is True:
            blockers.append("gate_deletes_data")

        if record.get("gate_modifies_target_files") is True:
            blockers.append("gate_modifies_target_files")

        if record.get("gate_runs_git_reset") is True:
            blockers.append("gate_runs_git_reset")

        if record.get("gate_runs_git_force_push") is True:
            blockers.append("gate_runs_git_force_push")

        if record.get("gate_executes_shell_commands") is True:
            blockers.append("gate_executes_shell_commands")

        if record.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if record.get("status") == "blocked":
            warnings.append("recovery_blocked_by_gate")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "063",
        "module": "k_os_agent_recovery_approval_gate_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "recovery_gate_id": record.get("recovery_gate_id") if record else "",
        "gate_status": record.get("status") if record else "",
        "mode": record.get("mode") if record else "",
        "recovery_plan_id": record.get("recovery_plan_id") if record else "",
        "recovery_gate_record_hash": record.get("recovery_gate_record_hash") if record else "",
        "local_recovery_token_included": False,
        "gate_executes_recovery": False,
        "gate_executes_rollback": False,
        "gate_deletes_data": False,
        "gate_modifies_target_files": False,
        "gate_runs_git_reset": False,
        "gate_runs_git_force_push": False,
        "gate_executes_shell_commands": False,
        "raw_payload_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if record and len(blockers) == 0:
        record["validated_at"] = validation["generated_at"]
        record["validated"] = True

    save_state(state)
    write_validation(validation)

    event("recovery_gate.validation_completed", {
        "recovery_gate_id": validation.get("recovery_gate_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def compute_metrics(records: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for item in records:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "gate_record_count": len(records),
        "validation_count": len(validations),
        "approved_count": status_counts.get("approved_for_future_recovery", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "revoked_count": status_counts.get("revoked", 0),
        "recovery_execution_count": 0,
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0,
        "status_counts": status_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    records = [sanitize_record(item) for item in reversed(state.get("gate_records", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(records, validations)

    report = {
        "ok": True,
        "checkpoint": "063",
        "module": "k_os_agent_recovery_approval_gate_core",
        "status": "audit_generated",
        "generated_at": now(),
        "gate_state_path": "local_secrets/k_os_recovery_gate/agent_recovery_gate_state.json",
        "gate_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "gate_executes_recovery": False,
        "gate_executes_rollback": False,
        "gate_deletes_data": False,
        "gate_modifies_target_files": False,
        "gate_runs_git_reset": False,
        "gate_runs_git_force_push": False,
        "gate_executes_shell_commands": False,
        "recovery_plan_available": PLAN_PATH.exists(),
        "readiness_matrix_available": READINESS_MATRIX.exists(),
        "governance_summary_available": GOVERNANCE_SUMMARY.exists(),
        "metrics": metrics,
        "recent_gate_records": records,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_gate": policy.get("required_gates_before_recovery_gate", []),
        "next_checkpoint": policy.get("next_checkpoint", "064 - K-Agent Recovery Dry Run Simulator Core")
    }

    write_report(report)
    event("recovery_gate.audit_generated", {
        "gate_record_count": metrics.get("gate_record_count")
    })
    return report


def write_gate(record: dict[str, Any]) -> None:
    GATE_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Approval Gate Record",
        "",
        "- Recovery Gate ID: " + str(record.get("recovery_gate_id")),
        "- Status: " + str(record.get("status")),
        "- Mode: " + str(record.get("mode")),
        "- Recovery Plan ID: " + str(record.get("recovery_plan_id")),
        "- Readiness level: " + str(record.get("readiness_level")),
        "- Risk level: " + str(record.get("risk_level")),
        "- Gate hash: " + str(record.get("recovery_gate_record_hash")),
        "- Local token hash: " + str(record.get("local_recovery_token_hash")),
        "- Token included: " + str(record.get("local_recovery_token_included")),
        "- Executes recovery: " + str(record.get("gate_executes_recovery")),
        "- Executes rollback: " + str(record.get("gate_executes_rollback")),
        "- Deletes data: " + str(record.get("gate_deletes_data")),
        "- Modifies target files: " + str(record.get("gate_modifies_target_files")),
        "- Runs git reset: " + str(record.get("gate_runs_git_reset")),
        "- Runs git force push: " + str(record.get("gate_runs_git_force_push")),
        "",
        "## Blockers",
        ""
    ]

    if record.get("blockers"):
        for item in record.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    GATE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Gate Validation",
        "",
        "- Recovery Gate ID: " + str(result.get("recovery_gate_id")),
        "- Status: " + str(result.get("status")),
        "- Gate status: " + str(result.get("gate_status")),
        "- Mode: " + str(result.get("mode")),
        "- Recovery Plan ID: " + str(result.get("recovery_plan_id")),
        "- Gate hash: " + str(result.get("recovery_gate_record_hash")),
        "- Token included: " + str(result.get("local_recovery_token_included")),
        "- Executes recovery: " + str(result.get("gate_executes_recovery")),
        "- Executes rollback: " + str(result.get("gate_executes_rollback")),
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
        "# K-OS Agent Recovery Approval Gate Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("gate_state_committed")),
        "- Executes recovery: " + str(report.get("gate_executes_recovery")),
        "- Executes rollback: " + str(report.get("gate_executes_rollback")),
        "- Deletes data: " + str(report.get("gate_deletes_data")),
        "- Modifies target files: " + str(report.get("gate_modifies_target_files")),
        "- Runs git reset: " + str(report.get("gate_runs_git_reset")),
        "- Runs git force push: " + str(report.get("gate_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("gate_executes_shell_commands")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent gate records", ""])

    if report.get("recent_gate_records"):
        for item in report.get("recent_gate_records", [])[:30]:
            lines.append(
                "- " + str(item.get("recovery_gate_id")) +
                " | status=" + str(item.get("status")) +
                " | mode=" + str(item.get("mode")) +
                " | plan=" + str(item.get("recovery_plan_id"))
            )
    else:
        lines.append("- Nenhum registro.")

    lines.extend(["", "## Required gates before recovery gate", ""])

    for gate in report.get("required_gates_before_recovery_gate", []):
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
    parser.add_argument("--mode", choices=["init", "gate", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--gate-mode", default="block_recovery")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "gate":
        result = create_gate(args.gate_mode, args.operator, args.confirmation, args.reason)

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