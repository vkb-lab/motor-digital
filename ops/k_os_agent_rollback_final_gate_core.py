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

POLICY_PATH = ROOT / "config" / "rollback_final_gate" / "k_os_agent_rollback_final_gate_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_rollback_final_gate"
STATE_PATH = STATE_DIR / "agent_rollback_final_gate_state.json"

REPORT_DIR = ROOT / "reports" / "rollback_final_gate"
MEMORY_DIR = ROOT / "memory" / "rollback_final_gate"

LATEST_JSON = REPORT_DIR / "latest_agent_rollback_final_gate_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_rollback_final_gate_report.md"
GATE_JSON = REPORT_DIR / "latest_rollback_final_gate_record.json"
GATE_MD = REPORT_DIR / "latest_rollback_final_gate_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_rollback_final_gate_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_rollback_final_gate_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

DRY_RUN_SIM = ROOT / "reports" / "rollback_dry_run" / "latest_rollback_dry_run_simulation.json"
DRY_RUN_VALIDATION = ROOT / "reports" / "rollback_dry_run" / "latest_rollback_dry_run_validation_report.json"
DRY_RUN_REPORT = ROOT / "reports" / "rollback_dry_run" / "latest_agent_rollback_dry_run_report.json"

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
        raise RuntimeError("Rollback Final Gate policy not found.")
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
            "final_gate_executes_rollback": False,
            "final_gate_deletes_data": False,
            "final_gate_modifies_files": False,
            "gate_records": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load rollback final gate state.")
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


def load_dry_run() -> dict[str, Any]:
    data = read_json(DRY_RUN_SIM)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "simulation_id": "",
        "rollback_dry_run_hash": "",
        "release_id": "",
        "rollback_plan_id": "",
        "execution_evidence_hash": "",
        "blockers": ["rollback_dry_run_missing"]
    }


def gate_check(dry_run: dict[str, Any], decision: str, operator: str, confirmation: str, reason: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not reason:
        blockers.append("reason_missing")

    if not confirmation:
        blockers.append("operator_confirmation_missing")

    if not dry_run.get("simulation_id"):
        blockers.append("rollback_dry_run_missing")

    if not dry_run.get("rollback_dry_run_hash"):
        blockers.append("rollback_dry_run_hash_missing")

    if not dry_run.get("release_id"):
        blockers.append("release_id_missing")

    if not dry_run.get("rollback_plan_id"):
        blockers.append("rollback_plan_id_missing")

    if not dry_run.get("execution_evidence_hash"):
        blockers.append("execution_evidence_hash_missing")

    if dry_run.get("dry_run_executes_rollback") is True:
        blockers.append("dry_run_executes_rollback")

    if dry_run.get("dry_run_deletes_data") is True:
        blockers.append("dry_run_deletes_data")

    if dry_run.get("dry_run_modifies_files") is True:
        blockers.append("dry_run_modifies_files")

    if dry_run.get("dry_run_runs_git_reset") is True:
        blockers.append("dry_run_runs_git_reset")

    if dry_run.get("dry_run_runs_git_force_push") is True:
        blockers.append("dry_run_runs_git_force_push")

    if dry_run.get("release_token_included") is True:
        blockers.append("release_token_included")

    if dry_run.get("raw_payload_included") is True:
        blockers.append("raw_payload_included")

    if decision == "approve_future_manual_execution":
        if dry_run.get("status") != "simulated":
            blockers.append("dry_run_not_fully_simulated_for_approval")

    return blockers


def normalize_decision(decision: str) -> str:
    value = (decision or "block_execution").strip().lower()
    if value not in {"block_execution", "approve_future_manual_execution", "revoke_execution"}:
        return "block_execution"
    return value


def create_gate(decision: str, operator: str, confirmation: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    decision = normalize_decision(decision)
    operator = operator or "operator_k_os"
    dry_run = load_dry_run()

    blockers = gate_check(dry_run, decision, operator, confirmation, reason)

    gate_id = "rfg_" + uuid.uuid4().hex[:12]

    if decision == "approve_future_manual_execution" and len(blockers) == 0:
        status = "approved_for_future_manual_execution"
    elif decision == "revoke_execution":
        status = "revoked"
    else:
        status = "blocked"
        if "operator_blocked_final_execution" not in blockers:
            blockers.append("operator_blocked_final_execution")

    source_refs = {
        "rollback_dry_run": source_ref(DRY_RUN_SIM),
        "rollback_dry_run_validation": source_ref(DRY_RUN_VALIDATION),
        "rollback_dry_run_report": source_ref(DRY_RUN_REPORT),
        "release_record": source_ref(RELEASE_RECORD),
        "rollback_plan": source_ref(ROLLBACK_PLAN),
        "incident_record": source_ref(INCIDENT_RECORD),
        "forensics_bundle": source_ref(FORENSICS_BUNDLE),
        "ledger_record": source_ref(LEDGER_RECORD)
    }

    gate_body = {
        "gate_id": gate_id,
        "decision": decision,
        "status": status,
        "operator": operator,
        "confirmation_hash": stable_hash({"confirmation": confirmation}),
        "simulation_id": dry_run.get("simulation_id", ""),
        "rollback_dry_run_hash": dry_run.get("rollback_dry_run_hash", ""),
        "release_id": dry_run.get("release_id", ""),
        "rollback_plan_id": dry_run.get("rollback_plan_id", ""),
        "execution_evidence_hash": dry_run.get("execution_evidence_hash", ""),
        "source_refs": source_refs
    }

    record = {
        "ok": True,
        "checkpoint": "056",
        "module": "k_os_agent_rollback_execution_final_gate_core",
        "status": status,
        "final_gate_id": gate_id,
        "created_at": now(),
        "decision": decision,
        "operator": operator,
        "reason": reason or "rollback_final_gate_decision",
        "operator_confirmation_hash": stable_hash({"confirmation": confirmation}),
        "simulation_id": dry_run.get("simulation_id", ""),
        "rollback_dry_run_hash": dry_run.get("rollback_dry_run_hash", ""),
        "release_id": dry_run.get("release_id", ""),
        "release_status": dry_run.get("release_status", ""),
        "rollback_plan_id": dry_run.get("rollback_plan_id", ""),
        "incident_id": dry_run.get("incident_id", ""),
        "quarantine_id": dry_run.get("quarantine_id", ""),
        "execution_evidence_hash": dry_run.get("execution_evidence_hash", ""),
        "final_gate_record_hash": stable_hash(gate_body),
        "final_gate_executes_rollback": False,
        "final_gate_deletes_data": False,
        "final_gate_modifies_files": False,
        "final_gate_runs_git_reset": False,
        "final_gate_runs_git_force_push": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "source_refs": source_refs,
        "blockers": blockers,
        "required_gates_before_any_future_execution": policy.get("required_gates_before_any_future_execution", []),
        "next_action": "rollback_manual_execution_stub" if status == "approved_for_future_manual_execution" else "rollback_execution_blocked"
    }

    state.setdefault("gate_records", []).append(record)
    state["gate_records"] = state["gate_records"][-300:]
    save_state(state)

    write_gate(record)

    event("rollback_final_gate.record_created", {
        "final_gate_id": gate_id,
        "decision": decision,
        "status": status,
        "blockers": blockers
    })

    return audit_report()


def latest_gate_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("gate_records", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_gate_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("final_gate_record_not_found")
    else:
        if not record.get("final_gate_id"):
            blockers.append("final_gate_id_missing")

        if not record.get("final_gate_record_hash"):
            blockers.append("final_gate_record_hash_missing")

        if not record.get("simulation_id"):
            blockers.append("simulation_id_missing")

        if not record.get("rollback_dry_run_hash"):
            blockers.append("rollback_dry_run_hash_missing")

        if record.get("final_gate_executes_rollback") is True:
            blockers.append("final_gate_executes_rollback")

        if record.get("final_gate_deletes_data") is True:
            blockers.append("final_gate_deletes_data")

        if record.get("final_gate_modifies_files") is True:
            blockers.append("final_gate_modifies_files")

        if record.get("final_gate_runs_git_reset") is True:
            blockers.append("final_gate_runs_git_reset")

        if record.get("final_gate_runs_git_force_push") is True:
            blockers.append("final_gate_runs_git_force_push")

        if record.get("release_token_included") is True:
            blockers.append("release_token_included")

        if record.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if record.get("status") == "blocked":
            warnings.append("rollback_execution_blocked_by_final_gate")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "056",
        "module": "k_os_agent_rollback_execution_final_gate_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "final_gate_id": record.get("final_gate_id") if record else "",
        "final_gate_status": record.get("status") if record else "",
        "decision": record.get("decision") if record else "",
        "simulation_id": record.get("simulation_id") if record else "",
        "rollback_dry_run_hash": record.get("rollback_dry_run_hash") if record else "",
        "final_gate_record_hash": record.get("final_gate_record_hash") if record else "",
        "final_gate_executes_rollback": False,
        "final_gate_deletes_data": False,
        "final_gate_modifies_files": False,
        "final_gate_runs_git_reset": False,
        "final_gate_runs_git_force_push": False,
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

    event("rollback_final_gate.validation_completed", {
        "final_gate_id": validation.get("final_gate_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def sanitize_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "final_gate_id": item.get("final_gate_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "decision": item.get("decision"),
        "simulation_id": item.get("simulation_id"),
        "rollback_plan_id": item.get("rollback_plan_id"),
        "release_id": item.get("release_id"),
        "final_gate_record_hash": item.get("final_gate_record_hash"),
        "rollback_dry_run_hash": item.get("rollback_dry_run_hash"),
        "final_gate_executes_rollback": False,
        "final_gate_deletes_data": False,
        "final_gate_modifies_files": False,
        "final_gate_runs_git_reset": False,
        "final_gate_runs_git_force_push": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "blockers": item.get("blockers", [])
    }


def compute_metrics(records: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for item in records:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "final_gate_record_count": len(records),
        "validation_count": len(validations),
        "approved_count": status_counts.get("approved_for_future_manual_execution", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "revoked_count": status_counts.get("revoked", 0),
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "raw_payload_count": 0,
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
        "checkpoint": "056",
        "module": "k_os_agent_rollback_execution_final_gate_core",
        "status": "audit_generated",
        "generated_at": now(),
        "final_gate_state_path": "local_secrets/k_os_rollback_final_gate/agent_rollback_final_gate_state.json",
        "final_gate_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "final_gate_executes_rollback": False,
        "final_gate_deletes_data": False,
        "final_gate_modifies_files": False,
        "final_gate_runs_git_reset": False,
        "final_gate_runs_git_force_push": False,
        "rollback_dry_run_available": DRY_RUN_SIM.exists(),
        "rollback_dry_run_validation_available": DRY_RUN_VALIDATION.exists(),
        "release_record_available": RELEASE_RECORD.exists(),
        "rollback_plan_available": ROLLBACK_PLAN.exists(),
        "incident_record_available": INCIDENT_RECORD.exists(),
        "forensics_bundle_available": FORENSICS_BUNDLE.exists(),
        "ledger_record_available": LEDGER_RECORD.exists(),
        "metrics": metrics,
        "recent_final_gate_records": records,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_any_future_execution": policy.get("required_gates_before_any_future_execution", []),
        "next_checkpoint": policy.get("next_checkpoint", "057 - K-Agent Rollback Manual Execution Stub Core")
    }

    write_report(report)
    event("rollback_final_gate.audit_generated", {
        "final_gate_record_count": metrics.get("final_gate_record_count")
    })
    return report


def write_gate(record: dict[str, Any]) -> None:
    GATE_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Execution Final Gate Record",
        "",
        "- Final Gate ID: " + str(record.get("final_gate_id")),
        "- Status: " + str(record.get("status")),
        "- Decision: " + str(record.get("decision")),
        "- Simulation ID: " + str(record.get("simulation_id")),
        "- Release ID: " + str(record.get("release_id")),
        "- Rollback Plan ID: " + str(record.get("rollback_plan_id")),
        "- Gate hash: " + str(record.get("final_gate_record_hash")),
        "- Executes rollback: " + str(record.get("final_gate_executes_rollback")),
        "- Deletes data: " + str(record.get("final_gate_deletes_data")),
        "- Modifies files: " + str(record.get("final_gate_modifies_files")),
        "- Runs git reset: " + str(record.get("final_gate_runs_git_reset")),
        "- Runs git force push: " + str(record.get("final_gate_runs_git_force_push")),
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
        "# K-OS Rollback Execution Final Gate Validation",
        "",
        "- Final Gate ID: " + str(result.get("final_gate_id")),
        "- Status: " + str(result.get("status")),
        "- Gate status: " + str(result.get("final_gate_status")),
        "- Decision: " + str(result.get("decision")),
        "- Simulation ID: " + str(result.get("simulation_id")),
        "- Gate hash: " + str(result.get("final_gate_record_hash")),
        "- Executes rollback: " + str(result.get("final_gate_executes_rollback")),
        "- Deletes data: " + str(result.get("final_gate_deletes_data")),
        "- Modifies files: " + str(result.get("final_gate_modifies_files")),
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
        "# K-OS Agent Rollback Execution Final Gate Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("final_gate_state_committed")),
        "- Executes rollback: " + str(report.get("final_gate_executes_rollback")),
        "- Deletes data: " + str(report.get("final_gate_deletes_data")),
        "- Modifies files: " + str(report.get("final_gate_modifies_files")),
        "- Runs git reset: " + str(report.get("final_gate_runs_git_reset")),
        "- Runs git force push: " + str(report.get("final_gate_runs_git_force_push")),
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
                "- " + str(item.get("final_gate_id")) +
                " | status=" + str(item.get("status")) +
                " | decision=" + str(item.get("decision")) +
                " | simulation=" + str(item.get("simulation_id"))
            )
    else:
        lines.append("- Nenhum registro.")

    lines.extend(["", "## Required gates before any future execution", ""])

    for gate in report.get("required_gates_before_any_future_execution", []):
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
    parser.add_argument("--mode", choices=["init", "decide", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--decision", default="block_execution")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "decide":
        result = create_gate(args.decision, args.operator, args.confirmation, args.reason)

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