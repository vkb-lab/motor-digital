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

POLICY_PATH = ROOT / "config" / "recovery_manual_stub" / "k_os_agent_recovery_manual_stub_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_recovery_manual_stub"
STATE_PATH = STATE_DIR / "agent_recovery_manual_stub_state.json"

REPORT_DIR = ROOT / "reports" / "recovery_manual_stub"
MEMORY_DIR = ROOT / "memory" / "recovery_manual_stub"

LATEST_JSON = REPORT_DIR / "latest_agent_recovery_manual_stub_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_recovery_manual_stub_report.md"
STUB_JSON = REPORT_DIR / "latest_recovery_manual_stub_record.json"
STUB_MD = REPORT_DIR / "latest_recovery_manual_stub_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_recovery_manual_stub_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_recovery_manual_stub_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

FINAL_GATE = ROOT / "reports" / "recovery_final_gate" / "latest_recovery_final_gate_record.json"
FINAL_GATE_VALIDATION = ROOT / "reports" / "recovery_final_gate" / "latest_recovery_final_gate_validation_report.json"
FINAL_GATE_REPORT = ROOT / "reports" / "recovery_final_gate" / "latest_agent_recovery_final_gate_report.json"

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
        raise RuntimeError("Recovery manual stub policy not found.")
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
            "stub_executes_recovery": False,
            "stub_executes_rollback": False,
            "stub_records": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load recovery manual stub state.")
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


def load_artifact(path: Path, fallback_status: str, fallback_blocker: str) -> dict[str, Any]:
    data = read_json(path)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": fallback_status,
        "blockers": [fallback_blocker]
    }


def normalize_mode(mode: str) -> str:
    value = (mode or "record_blocked_intent").strip().lower()
    if value not in {"record_blocked_intent", "request_future_manual_execution", "revoke_manual_intent"}:
        return "record_blocked_intent"
    return value


def collect_blockers(final_gate: dict[str, Any], dry_run: dict[str, Any], gate: dict[str, Any], plan: dict[str, Any], readiness: dict[str, Any], mode: str, operator: str, reason: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not reason:
        blockers.append("reason_missing")

    if not final_gate.get("recovery_final_gate_id"):
        blockers.append("recovery_final_gate_missing")

    if not final_gate.get("recovery_final_gate_hash"):
        blockers.append("recovery_final_gate_hash_missing")

    if not dry_run.get("simulation_id"):
        blockers.append("recovery_dry_run_missing")

    if not gate.get("recovery_gate_id"):
        blockers.append("recovery_gate_missing")

    if not plan.get("recovery_plan_id"):
        blockers.append("recovery_plan_missing")

    if not readiness.get("matrix_id"):
        blockers.append("readiness_matrix_missing")

    destructive_checks = [
        ("final_gate_executes_recovery", final_gate),
        ("final_gate_executes_rollback", final_gate),
        ("final_gate_deletes_data", final_gate),
        ("final_gate_modifies_target_files", final_gate),
        ("final_gate_runs_git_reset", final_gate),
        ("final_gate_runs_git_force_push", final_gate),
        ("final_gate_executes_shell_commands", final_gate),
        ("dry_run_executes_recovery", dry_run),
        ("dry_run_executes_rollback", dry_run),
        ("dry_run_deletes_data", dry_run),
        ("dry_run_modifies_target_files", dry_run),
        ("dry_run_runs_git_reset", dry_run),
        ("dry_run_runs_git_force_push", dry_run),
        ("dry_run_executes_shell_commands", dry_run),
        ("gate_executes_recovery", gate),
        ("gate_executes_rollback", gate),
        ("gate_deletes_data", gate),
        ("gate_modifies_target_files", gate),
        ("gate_runs_git_reset", gate),
        ("gate_runs_git_force_push", gate),
        ("gate_executes_shell_commands", gate),
        ("plan_executes_recovery", plan),
        ("plan_executes_rollback", plan),
        ("plan_deletes_data", plan),
        ("plan_modifies_target_files", plan),
        ("plan_runs_git_reset", plan),
        ("plan_runs_git_force_push", plan),
        ("plan_executes_shell_commands", plan),
        ("readiness_executes_recovery", readiness),
        ("readiness_executes_rollback", readiness)
    ]

    for key, source in destructive_checks:
        if source.get(key) is True:
            blockers.append(key)

    if mode == "request_future_manual_execution":
        if final_gate.get("status") != "approved_for_future_manual_stub":
            blockers.append("recovery_final_gate_not_approved")

        if dry_run.get("status") != "simulation_completed_safe":
            blockers.append("recovery_dry_run_not_safe")

        if gate.get("status") != "approved_for_future_recovery":
            blockers.append("recovery_gate_not_approved")

        if plan.get("status") != "plan_prepared_review_required":
            blockers.append("recovery_plan_not_prepared")

        if readiness.get("readiness_level") != "controlled_ready":
            blockers.append("readiness_not_controlled_ready")

    for source in [final_gate, dry_run, gate, plan, readiness]:
        for item in source.get("blockers", []):
            text = str(item)
            if text not in blockers:
                blockers.append(text)

    return sorted(set(blockers))


def create_stub(mode: str, operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    mode = normalize_mode(mode)
    operator = operator or "operator_k_os"

    final_gate = load_artifact(FINAL_GATE, "missing", "recovery_final_gate_missing")
    dry_run = load_artifact(DRY_RUN, "missing", "recovery_dry_run_missing")
    gate = load_artifact(RECOVERY_GATE, "missing", "recovery_gate_missing")
    plan = load_artifact(RECOVERY_PLAN, "missing", "recovery_plan_missing")
    readiness = load_artifact(READINESS_MATRIX, "missing", "readiness_matrix_missing")
    governance = load_artifact(GOVERNANCE_SUMMARY, "missing", "governance_summary_missing")

    blockers = collect_blockers(final_gate, dry_run, gate, plan, readiness, mode, operator, reason)
    stub_id = "rms_" + uuid.uuid4().hex[:12]

    if mode == "request_future_manual_execution" and len(blockers) == 0:
        status = "intent_recorded_for_future_review"
    elif mode == "revoke_manual_intent":
        status = "intent_revoked"
    else:
        status = "intent_blocked"
        if "operator_manual_stub_blocks_recovery" not in blockers:
            blockers.append("operator_manual_stub_blocks_recovery")

    source_refs = {
        "recovery_final_gate": source_ref(FINAL_GATE),
        "recovery_final_gate_validation": source_ref(FINAL_GATE_VALIDATION),
        "recovery_final_gate_report": source_ref(FINAL_GATE_REPORT),
        "recovery_dry_run": source_ref(DRY_RUN),
        "recovery_gate": source_ref(RECOVERY_GATE),
        "recovery_plan": source_ref(RECOVERY_PLAN),
        "readiness_matrix": source_ref(READINESS_MATRIX),
        "governance_summary": source_ref(GOVERNANCE_SUMMARY)
    }

    stub_body = {
        "stub_id": stub_id,
        "mode": mode,
        "status": status,
        "operator": operator,
        "final_gate_id": final_gate.get("recovery_final_gate_id", ""),
        "dry_run_id": dry_run.get("simulation_id", ""),
        "recovery_gate_id": gate.get("recovery_gate_id", ""),
        "recovery_plan_id": plan.get("recovery_plan_id", ""),
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "source_refs": source_refs
    }

    record = {
        "ok": True,
        "checkpoint": "066",
        "module": "k_os_agent_recovery_manual_execution_stub_core",
        "status": status,
        "recovery_manual_stub_id": stub_id,
        "created_at": now(),
        "mode": mode,
        "operator": operator,
        "reason": reason or "recovery_manual_execution_stub",
        "recovery_final_gate_id": final_gate.get("recovery_final_gate_id", ""),
        "recovery_final_gate_status": final_gate.get("status", ""),
        "recovery_final_gate_hash": final_gate.get("recovery_final_gate_hash", ""),
        "recovery_dry_run_id": dry_run.get("simulation_id", ""),
        "recovery_dry_run_status": dry_run.get("status", ""),
        "recovery_dry_run_hash": dry_run.get("dry_run_simulation_hash", ""),
        "recovery_gate_id": gate.get("recovery_gate_id", ""),
        "recovery_gate_status": gate.get("status", ""),
        "recovery_plan_id": plan.get("recovery_plan_id", ""),
        "recovery_plan_status": plan.get("status", ""),
        "recovery_plan_hash": plan.get("recovery_plan_hash", ""),
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "readiness_matrix_hash": readiness.get("readiness_matrix_hash", ""),
        "readiness_level": readiness.get("readiness_level", ""),
        "risk_level": readiness.get("risk_level", ""),
        "governance_summary_id": governance.get("summary_id", ""),
        "governance_summary_hash": governance.get("rollback_governance_summary_hash", ""),
        "recovery_manual_stub_hash": stable_hash(stub_body),
        "stub_executes_recovery": False,
        "stub_executes_rollback": False,
        "stub_deletes_data": False,
        "stub_modifies_target_files": False,
        "stub_runs_git_reset": False,
        "stub_runs_git_force_push": False,
        "stub_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "source_refs": source_refs,
        "blockers": blockers,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_manual_stub": policy.get("required_gates_before_manual_stub", []),
        "next_action": "recovery_controlled_execution_sandbox" if status == "intent_recorded_for_future_review" else "recovery_remains_blocked"
    }

    state.setdefault("stub_records", []).append(record)
    state["stub_records"] = state["stub_records"][-300:]
    save_state(state)

    write_stub(record)

    event("recovery_manual_stub.record_created", {
        "recovery_manual_stub_id": stub_id,
        "status": status,
        "mode": mode,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_stub_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("stub_records", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_stub_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("recovery_manual_stub_record_not_found")
    else:
        required = [
            ("recovery_manual_stub_id", "recovery_manual_stub_id_missing"),
            ("recovery_manual_stub_hash", "recovery_manual_stub_hash_missing"),
            ("recovery_final_gate_id", "recovery_final_gate_id_missing"),
            ("recovery_dry_run_id", "recovery_dry_run_id_missing"),
            ("recovery_plan_id", "recovery_plan_id_missing")
        ]

        for key, blocker in required:
            if not record.get(key):
                blockers.append(blocker)

        destructive_keys = [
            "stub_executes_recovery",
            "stub_executes_rollback",
            "stub_deletes_data",
            "stub_modifies_target_files",
            "stub_runs_git_reset",
            "stub_runs_git_force_push",
            "stub_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if record.get(key) is True:
                blockers.append(key)

        if record.get("status") == "intent_blocked":
            warnings.append("recovery_intent_blocked_by_manual_stub")

        if record.get("blockers"):
            warnings.append("manual_stub_contains_non_destructive_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "066",
        "module": "k_os_agent_recovery_manual_execution_stub_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "recovery_manual_stub_id": record.get("recovery_manual_stub_id") if record else "",
        "manual_stub_status": record.get("status") if record else "",
        "mode": record.get("mode") if record else "",
        "recovery_final_gate_id": record.get("recovery_final_gate_id") if record else "",
        "recovery_dry_run_id": record.get("recovery_dry_run_id") if record else "",
        "recovery_plan_id": record.get("recovery_plan_id") if record else "",
        "recovery_manual_stub_hash": record.get("recovery_manual_stub_hash") if record else "",
        "stub_executes_recovery": False,
        "stub_executes_rollback": False,
        "stub_deletes_data": False,
        "stub_modifies_target_files": False,
        "stub_runs_git_reset": False,
        "stub_runs_git_force_push": False,
        "stub_executes_shell_commands": False,
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

    event("recovery_manual_stub.validation_completed", {
        "recovery_manual_stub_id": validation.get("recovery_manual_stub_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "recovery_manual_stub_id": item.get("recovery_manual_stub_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "mode": item.get("mode"),
        "recovery_final_gate_status": item.get("recovery_final_gate_status"),
        "recovery_dry_run_status": item.get("recovery_dry_run_status"),
        "recovery_gate_status": item.get("recovery_gate_status"),
        "recovery_plan_id": item.get("recovery_plan_id"),
        "readiness_level": item.get("readiness_level"),
        "risk_level": item.get("risk_level"),
        "recovery_manual_stub_hash": item.get("recovery_manual_stub_hash"),
        "stub_executes_recovery": False,
        "stub_executes_rollback": False,
        "stub_deletes_data": False,
        "stub_modifies_target_files": False,
        "stub_runs_git_reset": False,
        "stub_runs_git_force_push": False,
        "stub_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blocker_count": len(item.get("blockers", []))
    }


def compute_metrics(records: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for item in records:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "manual_stub_record_count": len(records),
        "validation_count": len(validations),
        "intent_recorded_for_future_review_count": status_counts.get("intent_recorded_for_future_review", 0),
        "intent_blocked_count": status_counts.get("intent_blocked", 0),
        "intent_revoked_count": status_counts.get("intent_revoked", 0),
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

    records = [safe_record(item) for item in reversed(state.get("stub_records", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(records, validations)

    report = {
        "ok": True,
        "checkpoint": "066",
        "module": "k_os_agent_recovery_manual_execution_stub_core",
        "status": "audit_generated",
        "generated_at": now(),
        "stub_state_path": "local_secrets/k_os_recovery_manual_stub/agent_recovery_manual_stub_state.json",
        "stub_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "stub_executes_recovery": False,
        "stub_executes_rollback": False,
        "stub_deletes_data": False,
        "stub_modifies_target_files": False,
        "stub_runs_git_reset": False,
        "stub_runs_git_force_push": False,
        "stub_executes_shell_commands": False,
        "recovery_final_gate_available": FINAL_GATE.exists(),
        "recovery_dry_run_available": DRY_RUN.exists(),
        "recovery_gate_available": RECOVERY_GATE.exists(),
        "recovery_plan_available": RECOVERY_PLAN.exists(),
        "readiness_matrix_available": READINESS_MATRIX.exists(),
        "governance_summary_available": GOVERNANCE_SUMMARY.exists(),
        "metrics": metrics,
        "recent_stub_records": records,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_manual_stub": policy.get("required_gates_before_manual_stub", []),
        "next_checkpoint": policy.get("next_checkpoint", "067 - K-Agent Recovery Controlled Execution Sandbox Core")
    }

    write_report(report)
    event("recovery_manual_stub.audit_generated", {
        "manual_stub_record_count": metrics.get("manual_stub_record_count")
    })
    return report


def write_stub(record: dict[str, Any]) -> None:
    STUB_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Manual Execution Stub Record",
        "",
        "- Recovery Manual Stub ID: " + str(record.get("recovery_manual_stub_id")),
        "- Status: " + str(record.get("status")),
        "- Mode: " + str(record.get("mode")),
        "- Recovery Final Gate status: " + str(record.get("recovery_final_gate_status")),
        "- Recovery Dry Run status: " + str(record.get("recovery_dry_run_status")),
        "- Recovery Gate status: " + str(record.get("recovery_gate_status")),
        "- Recovery Plan ID: " + str(record.get("recovery_plan_id")),
        "- Readiness level: " + str(record.get("readiness_level")),
        "- Risk level: " + str(record.get("risk_level")),
        "- Stub hash: " + str(record.get("recovery_manual_stub_hash")),
        "- Executes recovery: " + str(record.get("stub_executes_recovery")),
        "- Executes rollback: " + str(record.get("stub_executes_rollback")),
        "- Deletes data: " + str(record.get("stub_deletes_data")),
        "- Modifies target files: " + str(record.get("stub_modifies_target_files")),
        "- Runs git reset: " + str(record.get("stub_runs_git_reset")),
        "- Runs git force push: " + str(record.get("stub_runs_git_force_push")),
        "- Executes shell: " + str(record.get("stub_executes_shell_commands")),
        "",
        "## Blockers",
        ""
    ]

    if record.get("blockers"):
        for item in record.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    STUB_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Manual Stub Validation",
        "",
        "- Recovery Manual Stub ID: " + str(result.get("recovery_manual_stub_id")),
        "- Status: " + str(result.get("status")),
        "- Manual stub status: " + str(result.get("manual_stub_status")),
        "- Mode: " + str(result.get("mode")),
        "- Recovery Final Gate ID: " + str(result.get("recovery_final_gate_id")),
        "- Recovery Dry Run ID: " + str(result.get("recovery_dry_run_id")),
        "- Recovery Plan ID: " + str(result.get("recovery_plan_id")),
        "- Stub hash: " + str(result.get("recovery_manual_stub_hash")),
        "- Executes recovery: " + str(result.get("stub_executes_recovery")),
        "- Executes rollback: " + str(result.get("stub_executes_rollback")),
        "- Deletes data: " + str(result.get("stub_deletes_data")),
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
        "# K-OS Agent Recovery Manual Execution Stub Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("stub_state_committed")),
        "- Executes recovery: " + str(report.get("stub_executes_recovery")),
        "- Executes rollback: " + str(report.get("stub_executes_rollback")),
        "- Deletes data: " + str(report.get("stub_deletes_data")),
        "- Modifies target files: " + str(report.get("stub_modifies_target_files")),
        "- Runs git reset: " + str(report.get("stub_runs_git_reset")),
        "- Runs git force push: " + str(report.get("stub_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("stub_executes_shell_commands")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent manual stub records", ""])

    if report.get("recent_stub_records"):
        for item in report.get("recent_stub_records", [])[:30]:
            lines.append(
                "- " + str(item.get("recovery_manual_stub_id")) +
                " | status=" + str(item.get("status")) +
                " | mode=" + str(item.get("mode")) +
                " | final_gate=" + str(item.get("recovery_final_gate_status"))
            )
    else:
        lines.append("- Nenhum registro.")

    lines.extend(["", "## Required gates before manual stub", ""])

    for gate in report.get("required_gates_before_manual_stub", []):
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
    parser.add_argument("--mode", choices=["init", "stub", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--stub-mode", default="record_blocked_intent")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "stub":
        result = create_stub(args.stub_mode, args.operator, args.reason)

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