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

POLICY_PATH = ROOT / "config" / "rollback_sandbox_review" / "k_os_agent_rollback_sandbox_review_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_rollback_sandbox_review"
STATE_PATH = STATE_DIR / "agent_rollback_sandbox_review_state.json"

REPORT_DIR = ROOT / "reports" / "rollback_sandbox_review"
MEMORY_DIR = ROOT / "memory" / "rollback_sandbox_review"

LATEST_JSON = REPORT_DIR / "latest_agent_rollback_sandbox_review_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_rollback_sandbox_review_report.md"
REVIEW_JSON = REPORT_DIR / "latest_rollback_sandbox_operator_review.json"
REVIEW_MD = REPORT_DIR / "latest_rollback_sandbox_operator_review.md"
VALIDATION_JSON = REPORT_DIR / "latest_rollback_sandbox_review_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_rollback_sandbox_review_validation_report.md"
EXECUTIVE_JSON = REPORT_DIR / "latest_rollback_sandbox_executive_summary.json"
EXECUTIVE_MD = REPORT_DIR / "latest_rollback_sandbox_executive_summary.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

SANDBOX_RECORD = ROOT / "reports" / "rollback_sandbox" / "latest_rollback_sandbox_record.json"
SANDBOX_VALIDATION = ROOT / "reports" / "rollback_sandbox" / "latest_rollback_sandbox_validation_report.json"
SANDBOX_REPORT = ROOT / "reports" / "rollback_sandbox" / "latest_agent_rollback_sandbox_report.json"

MANUAL_STUB = ROOT / "reports" / "rollback_manual_stub" / "latest_rollback_manual_stub_record.json"
FINAL_GATE = ROOT / "reports" / "rollback_final_gate" / "latest_rollback_final_gate_record.json"
DRY_RUN_SIM = ROOT / "reports" / "rollback_dry_run" / "latest_rollback_dry_run_simulation.json"
RELEASE_RECORD = ROOT / "reports" / "rollback_release_gate" / "latest_rollback_release_record.json"
ROLLBACK_PLAN = ROOT / "reports" / "rollback_preparation" / "latest_rollback_plan.json"
INCIDENT_RECORD = ROOT / "reports" / "incident_lockdown" / "latest_incident_lockdown_record.json"
FORENSICS_BUNDLE = ROOT / "reports" / "replay_forensics" / "latest_replay_forensics_bundle.json"
LEDGER_RECORD = ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_record.json"


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
        raise RuntimeError("Rollback sandbox review policy not found.")
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
            "review_executes_rollback": False,
            "review_deletes_data": False,
            "review_modifies_target_files": False,
            "reviews": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load rollback sandbox review state.")
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
    data = read_json(SANDBOX_RECORD)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "sandbox_id": "",
        "sandbox_record_hash": "",
        "manual_stub_id": "",
        "blockers": ["sandbox_record_missing"]
    }


def normalize_decision(decision: str) -> str:
    value = (decision or "acknowledge_blocked").strip().lower()
    if value not in {"acknowledge_blocked", "request_changes", "archive_review"}:
        return "acknowledge_blocked"
    return value


def collect_blockers(sandbox: dict[str, Any]) -> list[str]:
    blockers: list[str] = []

    for item in sandbox.get("blockers", []):
        if item not in blockers:
            blockers.append(str(item))

    if sandbox.get("governance_blocks_execution") is True:
        blockers.append("governance_blocks_execution")

    if sandbox.get("sandbox_executes_rollback") is True:
        blockers.append("sandbox_executes_rollback")

    if sandbox.get("sandbox_deletes_data") is True:
        blockers.append("sandbox_deletes_data")

    if sandbox.get("sandbox_modifies_target_files") is True:
        blockers.append("sandbox_modifies_target_files")

    if sandbox.get("sandbox_runs_git_reset") is True:
        blockers.append("sandbox_runs_git_reset")

    if sandbox.get("sandbox_runs_git_force_push") is True:
        blockers.append("sandbox_runs_git_force_push")

    if sandbox.get("sandbox_executes_shell_commands") is True:
        blockers.append("sandbox_executes_shell_commands")

    return sorted(set(blockers))


def gate_check(sandbox: dict[str, Any], operator: str, decision: str, notes: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not decision:
        blockers.append("review_decision_missing")

    if not notes:
        blockers.append("operator_notes_missing")

    if not sandbox.get("sandbox_id"):
        blockers.append("sandbox_record_missing")

    if not sandbox.get("sandbox_record_hash"):
        blockers.append("sandbox_record_hash_missing")

    if not sandbox.get("manual_stub_id"):
        blockers.append("manual_stub_missing")

    if sandbox.get("sandbox_executes_rollback") is True:
        blockers.append("sandbox_executes_rollback")

    if sandbox.get("sandbox_deletes_data") is True:
        blockers.append("sandbox_deletes_data")

    if sandbox.get("sandbox_modifies_target_files") is True:
        blockers.append("sandbox_modifies_target_files")

    if sandbox.get("sandbox_runs_git_reset") is True:
        blockers.append("sandbox_runs_git_reset")

    if sandbox.get("sandbox_runs_git_force_push") is True:
        blockers.append("sandbox_runs_git_force_push")

    if sandbox.get("sandbox_executes_shell_commands") is True:
        blockers.append("sandbox_executes_shell_commands")

    return blockers


def create_review(decision: str, operator: str, notes: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    decision = normalize_decision(decision)
    operator = operator or "operator_k_os"
    sandbox = load_sandbox()

    gate_blockers = gate_check(sandbox, operator, decision, notes)
    sandbox_blockers = collect_blockers(sandbox)
    all_blockers = sorted(set(gate_blockers + sandbox_blockers))

    review_id = "rsr_" + uuid.uuid4().hex[:12]

    if decision == "request_changes":
        status = "changes_requested"
    elif decision == "archive_review":
        status = "archived"
    else:
        status = "review_recorded"

    source_refs = {
        "sandbox_record": source_ref(SANDBOX_RECORD),
        "sandbox_validation": source_ref(SANDBOX_VALIDATION),
        "sandbox_report": source_ref(SANDBOX_REPORT),
        "manual_stub": source_ref(MANUAL_STUB),
        "final_gate": source_ref(FINAL_GATE),
        "dry_run": source_ref(DRY_RUN_SIM),
        "release_record": source_ref(RELEASE_RECORD),
        "rollback_plan": source_ref(ROLLBACK_PLAN),
        "incident_record": source_ref(INCIDENT_RECORD),
        "forensics_bundle": source_ref(FORENSICS_BUNDLE),
        "ledger_record": source_ref(LEDGER_RECORD)
    }

    executive_summary = {
        "sandbox_id": sandbox.get("sandbox_id", ""),
        "sandbox_status": sandbox.get("status", ""),
        "governance_blocks_execution": sandbox.get("governance_blocks_execution", True),
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0,
        "blockers": all_blockers,
        "operator_decision": decision
    }

    review_body = {
        "review_id": review_id,
        "decision": decision,
        "operator": operator,
        "sandbox_id": sandbox.get("sandbox_id", ""),
        "sandbox_hash": sandbox.get("sandbox_record_hash", ""),
        "blockers": all_blockers,
        "executive_summary_hash": stable_hash(executive_summary),
        "source_refs": source_refs
    }

    record = {
        "ok": True,
        "checkpoint": "059",
        "module": "k_os_agent_rollback_sandbox_report_operator_review_core",
        "status": status,
        "review_id": review_id,
        "created_at": now(),
        "decision": decision,
        "operator": operator,
        "operator_notes_hash": stable_hash({"notes": notes}),
        "sandbox_id": sandbox.get("sandbox_id", ""),
        "sandbox_status": sandbox.get("status", ""),
        "sandbox_record_hash": sandbox.get("sandbox_record_hash", ""),
        "manual_stub_id": sandbox.get("manual_stub_id", ""),
        "final_gate_id": sandbox.get("final_gate_id", ""),
        "simulation_id": sandbox.get("simulation_id", ""),
        "rollback_plan_id": sandbox.get("rollback_plan_id", ""),
        "governance_blocks_execution": sandbox.get("governance_blocks_execution", True),
        "review_record_hash": stable_hash(review_body),
        "executive_summary_hash": stable_hash(executive_summary),
        "review_executes_rollback": False,
        "review_deletes_data": False,
        "review_modifies_target_files": False,
        "review_runs_git_reset": False,
        "review_runs_git_force_push": False,
        "review_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "consolidated_blockers": all_blockers,
        "source_refs": source_refs,
        "required_gates_before_operator_review": policy.get("required_gates_before_operator_review", []),
        "next_action": "rollback_governance_summary"
    }

    state.setdefault("reviews", []).append(record)
    state["reviews"] = state["reviews"][-300:]
    save_state(state)

    write_review(record)
    write_executive_summary(executive_summary, record)

    event("rollback_sandbox_review.record_created", {
        "review_id": review_id,
        "decision": decision,
        "status": status,
        "blockers": all_blockers
    })

    return audit_report()


def latest_review_raw() -> dict[str, Any] | None:
    state = ensure_state()
    reviews = state.get("reviews", [])
    if not reviews:
        return None
    return reviews[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_review_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("review_record_not_found")
    else:
        if not record.get("review_id"):
            blockers.append("review_id_missing")

        if not record.get("review_record_hash"):
            blockers.append("review_record_hash_missing")

        if not record.get("sandbox_id"):
            blockers.append("sandbox_id_missing")

        if not record.get("sandbox_record_hash"):
            blockers.append("sandbox_hash_missing")

        if record.get("review_executes_rollback") is True:
            blockers.append("review_executes_rollback")

        if record.get("review_deletes_data") is True:
            blockers.append("review_deletes_data")

        if record.get("review_modifies_target_files") is True:
            blockers.append("review_modifies_target_files")

        if record.get("review_runs_git_reset") is True:
            blockers.append("review_runs_git_reset")

        if record.get("review_runs_git_force_push") is True:
            blockers.append("review_runs_git_force_push")

        if record.get("review_executes_shell_commands") is True:
            blockers.append("review_executes_shell_commands")

        if record.get("release_token_included") is True:
            blockers.append("release_token_included")

        if record.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if record.get("governance_blocks_execution") is True:
            warnings.append("operator_review_confirms_rollback_execution_blocked")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "059",
        "module": "k_os_agent_rollback_sandbox_report_operator_review_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "review_id": record.get("review_id") if record else "",
        "review_status": record.get("status") if record else "",
        "decision": record.get("decision") if record else "",
        "sandbox_id": record.get("sandbox_id") if record else "",
        "review_record_hash": record.get("review_record_hash") if record else "",
        "review_executes_rollback": False,
        "review_deletes_data": False,
        "review_modifies_target_files": False,
        "review_runs_git_reset": False,
        "review_runs_git_force_push": False,
        "review_executes_shell_commands": False,
        "release_token_included": False,
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

    event("rollback_sandbox_review.validation_completed", {
        "review_id": validation.get("review_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_review(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "review_id": item.get("review_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "decision": item.get("decision"),
        "sandbox_id": item.get("sandbox_id"),
        "sandbox_status": item.get("sandbox_status"),
        "review_record_hash": item.get("review_record_hash"),
        "executive_summary_hash": item.get("executive_summary_hash"),
        "governance_blocks_execution": item.get("governance_blocks_execution"),
        "review_executes_rollback": False,
        "review_deletes_data": False,
        "review_modifies_target_files": False,
        "review_runs_git_reset": False,
        "review_runs_git_force_push": False,
        "review_executes_shell_commands": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "consolidated_blockers": item.get("consolidated_blockers", [])
    }


def compute_metrics(reviews: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}

    for item in reviews:
        status = item.get("status", "unknown")
        decision = item.get("decision", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    return {
        "review_count": len(reviews),
        "validation_count": len(validations),
        "review_recorded_count": status_counts.get("review_recorded", 0),
        "changes_requested_count": status_counts.get("changes_requested", 0),
        "archived_count": status_counts.get("archived", 0),
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0,
        "raw_payload_count": 0,
        "status_counts": status_counts,
        "decision_counts": decision_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    reviews = [safe_review(item) for item in reversed(state.get("reviews", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(reviews, validations)

    report = {
        "ok": True,
        "checkpoint": "059",
        "module": "k_os_agent_rollback_sandbox_report_operator_review_core",
        "status": "audit_generated",
        "generated_at": now(),
        "review_state_path": "local_secrets/k_os_rollback_sandbox_review/agent_rollback_sandbox_review_state.json",
        "review_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "review_executes_rollback": False,
        "review_deletes_data": False,
        "review_modifies_target_files": False,
        "review_runs_git_reset": False,
        "review_runs_git_force_push": False,
        "review_executes_shell_commands": False,
        "sandbox_record_available": SANDBOX_RECORD.exists(),
        "manual_stub_available": MANUAL_STUB.exists(),
        "final_gate_available": FINAL_GATE.exists(),
        "dry_run_available": DRY_RUN_SIM.exists(),
        "release_record_available": RELEASE_RECORD.exists(),
        "rollback_plan_available": ROLLBACK_PLAN.exists(),
        "metrics": metrics,
        "recent_reviews": reviews,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_operator_review": policy.get("required_gates_before_operator_review", []),
        "next_checkpoint": policy.get("next_checkpoint", "060 - K-Agent Rollback Governance Summary Core")
    }

    write_report(report)
    event("rollback_sandbox_review.audit_generated", {
        "review_count": metrics.get("review_count")
    })
    return report


def write_executive_summary(summary: dict[str, Any], record: dict[str, Any]) -> None:
    payload = {
        "ok": True,
        "checkpoint": "059",
        "module": "k_os_agent_rollback_sandbox_report_operator_review_core",
        "status": "executive_summary_generated",
        "generated_at": now(),
        "review_id": record.get("review_id"),
        "review_record_hash": record.get("review_record_hash"),
        **summary
    }

    EXECUTIVE_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Sandbox Executive Summary",
        "",
        "- Review ID: " + str(record.get("review_id")),
        "- Decision: " + str(record.get("decision")),
        "- Sandbox ID: " + str(summary.get("sandbox_id")),
        "- Sandbox status: " + str(summary.get("sandbox_status")),
        "- Governance blocks execution: " + str(summary.get("governance_blocks_execution")),
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

    EXECUTIVE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_review(record: dict[str, Any]) -> None:
    REVIEW_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Sandbox Operator Review",
        "",
        "- Review ID: " + str(record.get("review_id")),
        "- Status: " + str(record.get("status")),
        "- Decision: " + str(record.get("decision")),
        "- Sandbox ID: " + str(record.get("sandbox_id")),
        "- Sandbox status: " + str(record.get("sandbox_status")),
        "- Review hash: " + str(record.get("review_record_hash")),
        "- Executive summary hash: " + str(record.get("executive_summary_hash")),
        "- Governance blocks execution: " + str(record.get("governance_blocks_execution")),
        "- Executes rollback: " + str(record.get("review_executes_rollback")),
        "- Deletes data: " + str(record.get("review_deletes_data")),
        "- Modifies target files: " + str(record.get("review_modifies_target_files")),
        "- Runs git reset: " + str(record.get("review_runs_git_reset")),
        "- Runs git force push: " + str(record.get("review_runs_git_force_push")),
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
        "# K-OS Rollback Sandbox Review Validation",
        "",
        "- Review ID: " + str(result.get("review_id")),
        "- Status: " + str(result.get("status")),
        "- Review status: " + str(result.get("review_status")),
        "- Decision: " + str(result.get("decision")),
        "- Sandbox ID: " + str(result.get("sandbox_id")),
        "- Review hash: " + str(result.get("review_record_hash")),
        "- Executes rollback: " + str(result.get("review_executes_rollback")),
        "- Deletes data: " + str(result.get("review_deletes_data")),
        "- Modifies target files: " + str(result.get("review_modifies_target_files")),
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
        "# K-OS Agent Rollback Sandbox Report and Operator Review Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("review_state_committed")),
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
                "- " + str(item.get("review_id")) +
                " | status=" + str(item.get("status")) +
                " | decision=" + str(item.get("decision")) +
                " | sandbox=" + str(item.get("sandbox_id"))
            )
    else:
        lines.append("- Nenhum registro.")

    lines.extend(["", "## Required gates before operator review", ""])

    for gate in report.get("required_gates_before_operator_review", []):
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
    parser.add_argument("--decision", default="acknowledge_blocked")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "review":
        result = create_review(args.decision, args.operator, args.notes)

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