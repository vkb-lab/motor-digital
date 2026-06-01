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

POLICY_PATH = ROOT / "config" / "recovery_final_gate" / "k_os_agent_recovery_final_gate_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_recovery_final_gate"
STATE_PATH = STATE_DIR / "agent_recovery_final_gate_state.json"

REPORT_DIR = ROOT / "reports" / "recovery_final_gate"
MEMORY_DIR = ROOT / "memory" / "recovery_final_gate"

LATEST_JSON = REPORT_DIR / "latest_agent_recovery_final_gate_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_recovery_final_gate_report.md"
FINAL_JSON = REPORT_DIR / "latest_recovery_final_gate_record.json"
FINAL_MD = REPORT_DIR / "latest_recovery_final_gate_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_recovery_final_gate_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_recovery_final_gate_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

DRY_RUN = ROOT / "reports" / "recovery_dry_run" / "latest_recovery_dry_run_simulation.json"
DRY_RUN_VALIDATION = ROOT / "reports" / "recovery_dry_run" / "latest_recovery_dry_run_validation_report.json"
DRY_RUN_REPORT = ROOT / "reports" / "recovery_dry_run" / "latest_agent_recovery_dry_run_report.json"

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
        raise RuntimeError("Recovery final gate policy not found.")
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
            "final_gate_executes_recovery": False,
            "final_gate_executes_rollback": False,
            "final_gate_records": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load recovery final gate state.")
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
    value = (mode or "block_execution").strip().lower()
    if value not in {"block_execution", "approve_future_manual_stub", "revoke_execution"}:
        return "block_execution"
    return value


def collect_blockers(dry_run: dict[str, Any], gate: dict[str, Any], plan: dict[str, Any], readiness: dict[str, Any], mode: str, operator: str, reason: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not reason:
        blockers.append("reason_missing")

    if not dry_run.get("simulation_id"):
        blockers.append("recovery_dry_run_missing")

    if not dry_run.get("dry_run_simulation_hash"):
        blockers.append("recovery_dry_run_hash_missing")

    if not gate.get("recovery_gate_id"):
        blockers.append("recovery_gate_missing")

    if not plan.get("recovery_plan_id"):
        blockers.append("recovery_plan_missing")

    if not plan.get("recovery_plan_hash"):
        blockers.append("recovery_plan_hash_missing")

    if not readiness.get("matrix_id"):
        blockers.append("readiness_matrix_missing")

    destructive_checks = [
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

    if mode == "approve_future_manual_stub":
        if gate.get("status") != "approved_for_future_recovery":
            blockers.append("recovery_gate_not_approved")

        if dry_run.get("status") != "simulation_completed_safe":
            blockers.append("dry_run_not_completed_safe")

        if plan.get("status") != "plan_prepared_review_required":
            blockers.append("recovery_plan_not_prepared")

        if readiness.get("readiness_level") != "controlled_ready":
            blockers.append("readiness_not_controlled_ready")

        if dry_run.get("blockers"):
            blockers.append("dry_run_has_blockers")

        if gate.get("blockers"):
            blockers.append("recovery_gate_has_blockers")

        if plan.get("blockers"):
            blockers.append("recovery_plan_has_blockers")

    for source in [dry_run, gate, plan, readiness]:
        for item in source.get("blockers", []):
            text = str(item)
            if text not in blockers:
                blockers.append(text)

    return sorted(set(blockers))


def create_final_gate(mode: str, operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    mode = normalize_mode(mode)
    operator = operator or "operator_k_os"

    dry_run = load_artifact(DRY_RUN, "missing", "recovery_dry_run_missing")
    gate = load_artifact(RECOVERY_GATE, "missing", "recovery_gate_missing")
    plan = load_artifact(RECOVERY_PLAN, "missing", "recovery_plan_missing")
    readiness = load_artifact(READINESS_MATRIX, "missing", "readiness_matrix_missing")
    governance = load_artifact(GOVERNANCE_SUMMARY, "missing", "governance_summary_missing")

    blockers = collect_blockers(dry_run, gate, plan, readiness, mode, operator, reason)
    final_gate_id = "rfg_" + uuid.uuid4().hex[:12]

    if mode == "approve_future_manual_stub" and len(blockers) == 0:
        status = "approved_for_future_manual_stub"
    elif mode == "revoke_execution":
        status = "revoked"
    else:
        status = "blocked"
        if "operator_final_gate_blocks_recovery" not in blockers:
            blockers.append("operator_final_gate_blocks_recovery")

    source_refs = {
        "recovery_dry_run": source_ref(DRY_RUN),
        "recovery_dry_run_validation": source_ref(DRY_RUN_VALIDATION),
        "recovery_dry_run_report": source_ref(DRY_RUN_REPORT),
        "recovery_gate": source_ref(RECOVERY_GATE),
        "recovery_plan": source_ref(RECOVERY_PLAN),
        "readiness_matrix": source_ref(READINESS_MATRIX),
        "governance_summary": source_ref(GOVERNANCE_SUMMARY)
    }

    final_body = {
        "final_gate_id": final_gate_id,
        "mode": mode,
        "status": status,
        "operator": operator,
        "dry_run_id": dry_run.get("simulation_id", ""),
        "dry_run_hash": dry_run.get("dry_run_simulation_hash", ""),
        "recovery_gate_id": gate.get("recovery_gate_id", ""),
        "recovery_plan_id": plan.get("recovery_plan_id", ""),
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "source_refs": source_refs
    }

    record = {
        "ok": True,
        "checkpoint": "065",
        "module": "k_os_agent_recovery_final_gate_core",
        "status": status,
        "recovery_final_gate_id": final_gate_id,
        "created_at": now(),
        "mode": mode,
        "operator": operator,
        "reason": reason or "recovery_final_gate",
        "recovery_dry_run_id": dry_run.get("simulation_id", ""),
        "recovery_dry_run_status": dry_run.get("status", ""),
        "recovery_dry_run_hash": dry_run.get("dry_run_simulation_hash", ""),
        "recovery_gate_id": gate.get("recovery_gate_id", ""),
        "recovery_gate_status": gate.get("status", ""),
        "recovery_gate_hash": gate.get("recovery_gate_record_hash", ""),
        "recovery_plan_id": plan.get("recovery_plan_id", ""),
        "recovery_plan_status": plan.get("status", ""),
        "recovery_plan_hash": plan.get("recovery_plan_hash", ""),
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "readiness_matrix_hash": readiness.get("readiness_matrix_hash", ""),
        "readiness_level": readiness.get("readiness_level", ""),
        "risk_level": readiness.get("risk_level", ""),
        "governance_summary_id": governance.get("summary_id", ""),
        "governance_summary_hash": governance.get("rollback_governance_summary_hash", ""),
        "recovery_final_gate_hash": stable_hash(final_body),
        "final_gate_executes_recovery": False,
        "final_gate_executes_rollback": False,
        "final_gate_deletes_data": False,
        "final_gate_modifies_target_files": False,
        "final_gate_runs_git_reset": False,
        "final_gate_runs_git_force_push": False,
        "final_gate_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "source_refs": source_refs,
        "blockers": blockers,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_final_gate": policy.get("required_gates_before_final_gate", []),
        "next_action": "recovery_manual_execution_stub" if status == "approved_for_future_manual_stub" else "recovery_remains_blocked"
    }

    state.setdefault("final_gate_records", []).append(record)
    state["final_gate_records"] = state["final_gate_records"][-300:]
    save_state(state)

    write_final_gate(record)

    event("recovery_final_gate.record_created", {
        "recovery_final_gate_id": final_gate_id,
        "status": status,
        "mode": mode,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_final_gate_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("final_gate_records", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_final_gate_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("recovery_final_gate_record_not_found")
    else:
        required = [
            ("recovery_final_gate_id", "recovery_final_gate_id_missing"),
            ("recovery_final_gate_hash", "recovery_final_gate_hash_missing"),
            ("recovery_dry_run_id", "recovery_dry_run_id_missing"),
            ("recovery_plan_id", "recovery_plan_id_missing")
        ]

        for key, blocker in required:
            if not record.get(key):
                blockers.append(blocker)

        destructive_keys = [
            "final_gate_executes_recovery",
            "final_gate_executes_rollback",
            "final_gate_deletes_data",
            "final_gate_modifies_target_files",
            "final_gate_runs_git_reset",
            "final_gate_runs_git_force_push",
            "final_gate_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if record.get(key) is True:
                blockers.append(key)

        if record.get("status") == "blocked":
            warnings.append("recovery_blocked_by_final_gate")

        if record.get("blockers"):
            warnings.append("final_gate_contains_non_destructive_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "065",
        "module": "k_os_agent_recovery_final_gate_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "recovery_final_gate_id": record.get("recovery_final_gate_id") if record else "",
        "final_gate_status": record.get("status") if record else "",
        "mode": record.get("mode") if record else "",
        "recovery_dry_run_id": record.get("recovery_dry_run_id") if record else "",
        "recovery_plan_id": record.get("recovery_plan_id") if record else "",
        "recovery_final_gate_hash": record.get("recovery_final_gate_hash") if record else "",
        "final_gate_executes_recovery": False,
        "final_gate_executes_rollback": False,
        "final_gate_deletes_data": False,
        "final_gate_modifies_target_files": False,
        "final_gate_runs_git_reset": False,
        "final_gate_runs_git_force_push": False,
        "final_gate_executes_shell_commands": False,
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

    event("recovery_final_gate.validation_completed", {
        "recovery_final_gate_id": validation.get("recovery_final_gate_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "recovery_final_gate_id": item.get("recovery_final_gate_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "mode": item.get("mode"),
        "recovery_dry_run_id": item.get("recovery_dry_run_id"),
        "recovery_dry_run_status": item.get("recovery_dry_run_status"),
        "recovery_gate_status": item.get("recovery_gate_status"),
        "recovery_plan_id": item.get("recovery_plan_id"),
        "readiness_level": item.get("readiness_level"),
        "risk_level": item.get("risk_level"),
        "recovery_final_gate_hash": item.get("recovery_final_gate_hash"),
        "final_gate_executes_recovery": False,
        "final_gate_executes_rollback": False,
        "final_gate_deletes_data": False,
        "final_gate_modifies_target_files": False,
        "final_gate_runs_git_reset": False,
        "final_gate_runs_git_force_push": False,
        "final_gate_executes_shell_commands": False,
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
        "final_gate_record_count": len(records),
        "validation_count": len(validations),
        "approved_for_future_manual_stub_count": status_counts.get("approved_for_future_manual_stub", 0),
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

    records = [safe_record(item) for item in reversed(state.get("final_gate_records", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(records, validations)

    report = {
        "ok": True,
        "checkpoint": "065",
        "module": "k_os_agent_recovery_final_gate_core",
        "status": "audit_generated",
        "generated_at": now(),
        "final_gate_state_path": "local_secrets/k_os_recovery_final_gate/agent_recovery_final_gate_state.json",
        "final_gate_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "final_gate_executes_recovery": False,
        "final_gate_executes_rollback": False,
        "final_gate_deletes_data": False,
        "final_gate_modifies_target_files": False,
        "final_gate_runs_git_reset": False,
        "final_gate_runs_git_force_push": False,
        "final_gate_executes_shell_commands": False,
        "recovery_dry_run_available": DRY_RUN.exists(),
        "recovery_gate_available": RECOVERY_GATE.exists(),
        "recovery_plan_available": RECOVERY_PLAN.exists(),
        "readiness_matrix_available": READINESS_MATRIX.exists(),
        "governance_summary_available": GOVERNANCE_SUMMARY.exists(),
        "metrics": metrics,
        "recent_final_gate_records": records,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_final_gate": policy.get("required_gates_before_final_gate", []),
        "next_checkpoint": policy.get("next_checkpoint", "066 - K-Agent Recovery Manual Execution Stub Core")
    }

    write_report(report)
    event("recovery_final_gate.audit_generated", {
        "final_gate_record_count": metrics.get("final_gate_record_count")
    })
    return report


def write_final_gate(record: dict[str, Any]) -> None:
    FINAL_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Final Gate Record",
        "",
        "- Recovery Final Gate ID: " + str(record.get("recovery_final_gate_id")),
        "- Status: " + str(record.get("status")),
        "- Mode: " + str(record.get("mode")),
        "- Recovery Dry Run ID: " + str(record.get("recovery_dry_run_id")),
        "- Recovery Dry Run status: " + str(record.get("recovery_dry_run_status")),
        "- Recovery Gate status: " + str(record.get("recovery_gate_status")),
        "- Recovery Plan ID: " + str(record.get("recovery_plan_id")),
        "- Readiness level: " + str(record.get("readiness_level")),
        "- Risk level: " + str(record.get("risk_level")),
        "- Final gate hash: " + str(record.get("recovery_final_gate_hash")),
        "- Executes recovery: " + str(record.get("final_gate_executes_recovery")),
        "- Executes rollback: " + str(record.get("final_gate_executes_rollback")),
        "- Deletes data: " + str(record.get("final_gate_deletes_data")),
        "- Modifies target files: " + str(record.get("final_gate_modifies_target_files")),
        "- Runs git reset: " + str(record.get("final_gate_runs_git_reset")),
        "- Runs git force push: " + str(record.get("final_gate_runs_git_force_push")),
        "- Executes shell: " + str(record.get("final_gate_executes_shell_commands")),
        "",
        "## Blockers",
        ""
    ]

    if record.get("blockers"):
        for item in record.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    FINAL_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Final Gate Validation",
        "",
        "- Recovery Final Gate ID: " + str(result.get("recovery_final_gate_id")),
        "- Status: " + str(result.get("status")),
        "- Final gate status: " + str(result.get("final_gate_status")),
        "- Mode: " + str(result.get("mode")),
        "- Recovery Dry Run ID: " + str(result.get("recovery_dry_run_id")),
        "- Recovery Plan ID: " + str(result.get("recovery_plan_id")),
        "- Final gate hash: " + str(result.get("recovery_final_gate_hash")),
        "- Executes recovery: " + str(result.get("final_gate_executes_recovery")),
        "- Executes rollback: " + str(result.get("final_gate_executes_rollback")),
        "- Deletes data: " + str(result.get("final_gate_deletes_data")),
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
        "# K-OS Agent Recovery Final Gate Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("final_gate_state_committed")),
        "- Executes recovery: " + str(report.get("final_gate_executes_recovery")),
        "- Executes rollback: " + str(report.get("final_gate_executes_rollback")),
        "- Deletes data: " + str(report.get("final_gate_deletes_data")),
        "- Modifies target files: " + str(report.get("final_gate_modifies_target_files")),
        "- Runs git reset: " + str(report.get("final_gate_runs_git_reset")),
        "- Runs git force push: " + str(report.get("final_gate_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("final_gate_executes_shell_commands")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent final gate records", ""])

    if report.get("recent_final_gate_records"):
        for item in report.get("recent_final_gate_records", [])[:30]:
            lines.append(
                "- " + str(item.get("recovery_final_gate_id")) +
                " | status=" + str(item.get("status")) +
                " | mode=" + str(item.get("mode")) +
                " | dry_run=" + str(item.get("recovery_dry_run_status"))
            )
    else:
        lines.append("- Nenhum registro.")

    lines.extend(["", "## Required gates before final gate", ""])

    for gate in report.get("required_gates_before_final_gate", []):
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
    parser.add_argument("--final-mode", default="block_execution")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "gate":
        result = create_final_gate(args.final_mode, args.operator, args.reason)

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