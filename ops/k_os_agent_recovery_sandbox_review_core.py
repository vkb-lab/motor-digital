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

POLICY_PATH = ROOT / "config" / "recovery_sandbox_review" / "k_os_agent_recovery_sandbox_review_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_recovery_sandbox_review"
STATE_PATH = STATE_DIR / "agent_recovery_sandbox_review_state.json"

REPORT_DIR = ROOT / "reports" / "recovery_sandbox_review"
MEMORY_DIR = ROOT / "memory" / "recovery_sandbox_review"

LATEST_JSON = REPORT_DIR / "latest_agent_recovery_sandbox_review_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_recovery_sandbox_review_report.md"
REVIEW_JSON = REPORT_DIR / "latest_recovery_sandbox_operator_review.json"
REVIEW_MD = REPORT_DIR / "latest_recovery_sandbox_operator_review.md"
SUMMARY_JSON = REPORT_DIR / "latest_recovery_sandbox_executive_summary.json"
SUMMARY_MD = REPORT_DIR / "latest_recovery_sandbox_executive_summary.md"
VALIDATION_JSON = REPORT_DIR / "latest_recovery_sandbox_review_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_recovery_sandbox_review_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

SANDBOX = ROOT / "reports" / "recovery_controlled_sandbox" / "latest_recovery_controlled_sandbox_record.json"
SANDBOX_VALIDATION = ROOT / "reports" / "recovery_controlled_sandbox" / "latest_recovery_controlled_sandbox_validation_report.json"
SANDBOX_REPORT = ROOT / "reports" / "recovery_controlled_sandbox" / "latest_agent_recovery_controlled_sandbox_report.json"

MANUAL_STUB = ROOT / "reports" / "recovery_manual_stub" / "latest_recovery_manual_stub_record.json"
FINAL_GATE = ROOT / "reports" / "recovery_final_gate" / "latest_recovery_final_gate_record.json"
DRY_RUN = ROOT / "reports" / "recovery_dry_run" / "latest_recovery_dry_run_simulation.json"
RECOVERY_GATE = ROOT / "reports" / "recovery_gate" / "latest_recovery_gate_record.json"
RECOVERY_PLAN = ROOT / "reports" / "recovery_plan_builder" / "latest_recovery_plan.json"
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
        raise RuntimeError("Recovery sandbox review policy not found.")
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
            "review_executes_recovery": False,
            "review_executes_rollback": False,
            "reviews": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load recovery sandbox review state.")
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


def load_sandbox() -> dict[str, Any]:
    data = read_json(SANDBOX)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "recovery_controlled_sandbox_id": "",
        "recovery_controlled_sandbox_hash": "",
        "workspace_manifest_hash": "",
        "blockers": ["recovery_controlled_sandbox_missing"]
    }


def normalize_review_mode(mode: str) -> str:
    value = (mode or "acknowledge_blocked").strip().lower()
    if value not in {"acknowledge_blocked", "request_changes", "archive_review"}:
        return "acknowledge_blocked"
    return value


def collect_blockers(sandbox: dict[str, Any], operator: str, notes: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not notes:
        blockers.append("operator_notes_missing")

    required = [
        ("recovery_controlled_sandbox_id", "recovery_controlled_sandbox_missing"),
        ("recovery_controlled_sandbox_hash", "recovery_controlled_sandbox_hash_missing"),
        ("workspace_manifest_hash", "workspace_manifest_hash_missing"),
        ("recovery_manual_stub_id", "recovery_manual_stub_missing"),
        ("recovery_final_gate_id", "recovery_final_gate_missing"),
        ("recovery_dry_run_id", "recovery_dry_run_missing"),
        ("recovery_plan_id", "recovery_plan_missing")
    ]

    for key, blocker in required:
        if not sandbox.get(key):
            blockers.append(blocker)

    destructive_keys = [
        "sandbox_executes_recovery",
        "sandbox_executes_rollback",
        "sandbox_deletes_data",
        "sandbox_modifies_target_files",
        "sandbox_runs_git_reset",
        "sandbox_runs_git_force_push",
        "sandbox_executes_shell_commands",
        "raw_payload_included",
        "local_recovery_token_included"
    ]

    for key in destructive_keys:
        if sandbox.get(key) is True:
            blockers.append(key)

    if sandbox.get("governance_blocks_execution") is True:
        blockers.append("governance_blocks_execution")

    for item in sandbox.get("blockers", []):
        text = str(item)
        if text not in blockers:
            blockers.append(text)

    return sorted(set(blockers))


def create_review(review_mode: str, operator: str, notes: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    review_mode = normalize_review_mode(review_mode)
    operator = operator or "operator_k_os"
    sandbox = load_sandbox()

    blockers = collect_blockers(sandbox, operator, notes)
    review_id = "rsor_" + uuid.uuid4().hex[:12]

    if review_mode == "request_changes":
        status = "changes_requested"
    elif review_mode == "archive_review":
        status = "archived"
    else:
        status = "review_acknowledged_blocked"

    source_refs = {
        "recovery_controlled_sandbox": source_ref(SANDBOX),
        "recovery_controlled_sandbox_validation": source_ref(SANDBOX_VALIDATION),
        "recovery_controlled_sandbox_report": source_ref(SANDBOX_REPORT),
        "recovery_manual_stub": source_ref(MANUAL_STUB),
        "recovery_final_gate": source_ref(FINAL_GATE),
        "recovery_dry_run": source_ref(DRY_RUN),
        "recovery_gate": source_ref(RECOVERY_GATE),
        "recovery_plan": source_ref(RECOVERY_PLAN),
        "readiness_matrix": source_ref(READINESS_MATRIX),
        "governance_summary": source_ref(GOVERNANCE_SUMMARY)
    }

    executive_summary = {
        "review_id": review_id,
        "sandbox_id": sandbox.get("recovery_controlled_sandbox_id", ""),
        "sandbox_status": sandbox.get("status", ""),
        "workspace_manifest_hash": sandbox.get("workspace_manifest_hash", ""),
        "governance_blocks_execution": sandbox.get("governance_blocks_execution", True),
        "operator_review_mode": review_mode,
        "blockers": blockers,
        "recovery_execution_count": 0,
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0
    }

    review_body = {
        "review_id": review_id,
        "status": status,
        "review_mode": review_mode,
        "operator": operator,
        "notes_hash": stable_hash({"notes": notes}),
        "sandbox_id": sandbox.get("recovery_controlled_sandbox_id", ""),
        "sandbox_hash": sandbox.get("recovery_controlled_sandbox_hash", ""),
        "workspace_manifest_hash": sandbox.get("workspace_manifest_hash", ""),
        "executive_summary_hash": stable_hash(executive_summary),
        "source_refs": source_refs
    }

    record = {
        "ok": True,
        "checkpoint": "068",
        "module": "k_os_agent_recovery_sandbox_operator_review_core",
        "status": status,
        "recovery_sandbox_review_id": review_id,
        "created_at": now(),
        "review_mode": review_mode,
        "operator": operator,
        "operator_notes_hash": stable_hash({"notes": notes}),
        "recovery_controlled_sandbox_id": sandbox.get("recovery_controlled_sandbox_id", ""),
        "recovery_controlled_sandbox_status": sandbox.get("status", ""),
        "recovery_controlled_sandbox_hash": sandbox.get("recovery_controlled_sandbox_hash", ""),
        "workspace_manifest_hash": sandbox.get("workspace_manifest_hash", ""),
        "recovery_manual_stub_id": sandbox.get("recovery_manual_stub_id", ""),
        "recovery_manual_stub_status": sandbox.get("recovery_manual_stub_status", ""),
        "recovery_final_gate_id": sandbox.get("recovery_final_gate_id", ""),
        "recovery_final_gate_status": sandbox.get("recovery_final_gate_status", ""),
        "recovery_dry_run_id": sandbox.get("recovery_dry_run_id", ""),
        "recovery_dry_run_status": sandbox.get("recovery_dry_run_status", ""),
        "recovery_gate_id": sandbox.get("recovery_gate_id", ""),
        "recovery_gate_status": sandbox.get("recovery_gate_status", ""),
        "recovery_plan_id": sandbox.get("recovery_plan_id", ""),
        "readiness_level": sandbox.get("readiness_level", ""),
        "risk_level": sandbox.get("risk_level", ""),
        "governance_blocks_execution": sandbox.get("governance_blocks_execution", True),
        "recovery_sandbox_review_hash": stable_hash(review_body),
        "executive_summary_hash": stable_hash(executive_summary),
        "review_executes_recovery": False,
        "review_executes_rollback": False,
        "review_deletes_data": False,
        "review_modifies_target_files": False,
        "review_runs_git_reset": False,
        "review_runs_git_force_push": False,
        "review_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "consolidated_blockers": blockers,
        "source_refs": source_refs,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_sandbox_review": policy.get("required_gates_before_sandbox_review", []),
        "next_action": "recovery_governance_summary"
    }

    state.setdefault("reviews", []).append(record)
    state["reviews"] = state["reviews"][-300:]
    save_state(state)

    write_review(record)
    write_executive_summary(record, executive_summary)

    event("recovery_sandbox_review.record_created", {
        "recovery_sandbox_review_id": review_id,
        "status": status,
        "review_mode": review_mode,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_review_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("reviews", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_review_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("recovery_sandbox_review_record_not_found")
    else:
        required = [
            ("recovery_sandbox_review_id", "recovery_sandbox_review_id_missing"),
            ("recovery_sandbox_review_hash", "recovery_sandbox_review_hash_missing"),
            ("executive_summary_hash", "executive_summary_hash_missing"),
            ("recovery_controlled_sandbox_id", "recovery_controlled_sandbox_id_missing"),
            ("workspace_manifest_hash", "workspace_manifest_hash_missing")
        ]

        for key, blocker in required:
            if not record.get(key):
                blockers.append(blocker)

        destructive_keys = [
            "review_executes_recovery",
            "review_executes_rollback",
            "review_deletes_data",
            "review_modifies_target_files",
            "review_runs_git_reset",
            "review_runs_git_force_push",
            "review_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if record.get(key) is True:
                blockers.append(key)

        if record.get("governance_blocks_execution") is True:
            warnings.append("operator_review_confirms_governance_block")

        if record.get("consolidated_blockers"):
            warnings.append("review_contains_non_destructive_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "068",
        "module": "k_os_agent_recovery_sandbox_operator_review_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "recovery_sandbox_review_id": record.get("recovery_sandbox_review_id") if record else "",
        "review_status": record.get("status") if record else "",
        "review_mode": record.get("review_mode") if record else "",
        "recovery_controlled_sandbox_id": record.get("recovery_controlled_sandbox_id") if record else "",
        "workspace_manifest_hash": record.get("workspace_manifest_hash") if record else "",
        "recovery_sandbox_review_hash": record.get("recovery_sandbox_review_hash") if record else "",
        "review_executes_recovery": False,
        "review_executes_rollback": False,
        "review_deletes_data": False,
        "review_modifies_target_files": False,
        "review_runs_git_reset": False,
        "review_runs_git_force_push": False,
        "review_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
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

    event("recovery_sandbox_review.validation_completed", {
        "recovery_sandbox_review_id": validation.get("recovery_sandbox_review_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "recovery_sandbox_review_id": item.get("recovery_sandbox_review_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "review_mode": item.get("review_mode"),
        "recovery_controlled_sandbox_status": item.get("recovery_controlled_sandbox_status"),
        "workspace_manifest_hash": item.get("workspace_manifest_hash"),
        "recovery_sandbox_review_hash": item.get("recovery_sandbox_review_hash"),
        "executive_summary_hash": item.get("executive_summary_hash"),
        "governance_blocks_execution": item.get("governance_blocks_execution"),
        "review_executes_recovery": False,
        "review_executes_rollback": False,
        "review_deletes_data": False,
        "review_modifies_target_files": False,
        "review_runs_git_reset": False,
        "review_runs_git_force_push": False,
        "review_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blocker_count": len(item.get("consolidated_blockers", []))
    }


def compute_metrics(records: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for item in records:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "review_record_count": len(records),
        "validation_count": len(validations),
        "review_acknowledged_blocked_count": status_counts.get("review_acknowledged_blocked", 0),
        "changes_requested_count": status_counts.get("changes_requested", 0),
        "archived_count": status_counts.get("archived", 0),
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

    records = [safe_record(item) for item in reversed(state.get("reviews", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(records, validations)

    report = {
        "ok": True,
        "checkpoint": "068",
        "module": "k_os_agent_recovery_sandbox_operator_review_core",
        "status": "audit_generated",
        "generated_at": now(),
        "review_state_path": "local_secrets/k_os_recovery_sandbox_review/agent_recovery_sandbox_review_state.json",
        "review_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "review_executes_recovery": False,
        "review_executes_rollback": False,
        "review_deletes_data": False,
        "review_modifies_target_files": False,
        "review_runs_git_reset": False,
        "review_runs_git_force_push": False,
        "review_executes_shell_commands": False,
        "recovery_controlled_sandbox_available": SANDBOX.exists(),
        "recovery_manual_stub_available": MANUAL_STUB.exists(),
        "recovery_final_gate_available": FINAL_GATE.exists(),
        "recovery_dry_run_available": DRY_RUN.exists(),
        "recovery_gate_available": RECOVERY_GATE.exists(),
        "recovery_plan_available": RECOVERY_PLAN.exists(),
        "metrics": metrics,
        "recent_reviews": records,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_sandbox_review": policy.get("required_gates_before_sandbox_review", []),
        "next_checkpoint": policy.get("next_checkpoint", "069 - K-Agent Recovery Governance Summary Core")
    }

    write_report(report)
    event("recovery_sandbox_review.audit_generated", {
        "review_record_count": metrics.get("review_record_count")
    })
    return report


def write_executive_summary(record: dict[str, Any], summary: dict[str, Any]) -> None:
    payload = {
        "ok": True,
        "checkpoint": "068",
        "module": "k_os_agent_recovery_sandbox_operator_review_core",
        "status": "executive_summary_generated",
        "generated_at": now(),
        "recovery_sandbox_review_id": record.get("recovery_sandbox_review_id"),
        "recovery_sandbox_review_hash": record.get("recovery_sandbox_review_hash"),
        **summary
    }

    SUMMARY_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Sandbox Executive Summary",
        "",
        "- Review ID: " + str(record.get("recovery_sandbox_review_id")),
        "- Review status: " + str(record.get("status")),
        "- Sandbox ID: " + str(summary.get("sandbox_id")),
        "- Sandbox status: " + str(summary.get("sandbox_status")),
        "- Workspace hash: " + str(summary.get("workspace_manifest_hash")),
        "- Governance blocks execution: " + str(summary.get("governance_blocks_execution")),
        "- Recovery execution count: 0",
        "- Rollback execution count: 0",
        "- Data delete count: 0",
        "- Target file modify count: 0",
        "- Git reset count: 0",
        "- Git force push count: 0",
        "- Shell execution count: 0",
        "",
        "## Consolidated blockers",
        ""
    ]

    if summary.get("blockers"):
        for item in summary.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_review(record: dict[str, Any]) -> None:
    REVIEW_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Sandbox Operator Review",
        "",
        "- Review ID: " + str(record.get("recovery_sandbox_review_id")),
        "- Status: " + str(record.get("status")),
        "- Review mode: " + str(record.get("review_mode")),
        "- Sandbox ID: " + str(record.get("recovery_controlled_sandbox_id")),
        "- Sandbox status: " + str(record.get("recovery_controlled_sandbox_status")),
        "- Workspace hash: " + str(record.get("workspace_manifest_hash")),
        "- Review hash: " + str(record.get("recovery_sandbox_review_hash")),
        "- Executive summary hash: " + str(record.get("executive_summary_hash")),
        "- Executes recovery: " + str(record.get("review_executes_recovery")),
        "- Executes rollback: " + str(record.get("review_executes_rollback")),
        "- Deletes data: " + str(record.get("review_deletes_data")),
        "- Modifies target files: " + str(record.get("review_modifies_target_files")),
        "- Runs git reset: " + str(record.get("review_runs_git_reset")),
        "- Runs git force push: " + str(record.get("review_runs_git_force_push")),
        "- Executes shell: " + str(record.get("review_executes_shell_commands")),
        "",
        "## Consolidated blockers",
        ""
    ]

    if record.get("consolidated_blockers"):
        for item in record.get("consolidated_blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    REVIEW_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Sandbox Review Validation",
        "",
        "- Review ID: " + str(result.get("recovery_sandbox_review_id")),
        "- Status: " + str(result.get("status")),
        "- Review status: " + str(result.get("review_status")),
        "- Review mode: " + str(result.get("review_mode")),
        "- Sandbox ID: " + str(result.get("recovery_controlled_sandbox_id")),
        "- Workspace hash: " + str(result.get("workspace_manifest_hash")),
        "- Review hash: " + str(result.get("recovery_sandbox_review_hash")),
        "- Executes recovery: " + str(result.get("review_executes_recovery")),
        "- Executes rollback: " + str(result.get("review_executes_rollback")),
        "- Deletes data: " + str(result.get("review_deletes_data")),
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
        "# K-OS Agent Recovery Sandbox Operator Review Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("review_state_committed")),
        "- Executes recovery: " + str(report.get("review_executes_recovery")),
        "- Executes rollback: " + str(report.get("review_executes_rollback")),
        "- Deletes data: " + str(report.get("review_deletes_data")),
        "- Modifies target files: " + str(report.get("review_modifies_target_files")),
        "- Runs git reset: " + str(report.get("review_runs_git_reset")),
        "- Runs git force push: " + str(report.get("review_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("review_executes_shell_commands")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent reviews", ""])

    if report.get("recent_reviews"):
        for item in report.get("recent_reviews", [])[:30]:
            lines.append(
                "- " + str(item.get("recovery_sandbox_review_id")) +
                " | status=" + str(item.get("status")) +
                " | mode=" + str(item.get("review_mode")) +
                " | blockers=" + str(item.get("blocker_count"))
            )
    else:
        lines.append("- Nenhum registro.")

    lines.extend(["", "## Required gates before sandbox review", ""])

    for gate in report.get("required_gates_before_sandbox_review", []):
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
    parser.add_argument("--mode", choices=["init", "review", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--review-mode", default="acknowledge_blocked")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "review":
        result = create_review(args.review_mode, args.operator, args.notes)

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