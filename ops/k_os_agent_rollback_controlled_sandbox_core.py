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

POLICY_PATH = ROOT / "config" / "rollback_sandbox" / "k_os_agent_rollback_sandbox_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_rollback_sandbox"
STATE_PATH = STATE_DIR / "agent_rollback_sandbox_state.json"

REPORT_DIR = ROOT / "reports" / "rollback_sandbox"
MEMORY_DIR = ROOT / "memory" / "rollback_sandbox"

LATEST_JSON = REPORT_DIR / "latest_agent_rollback_sandbox_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_rollback_sandbox_report.md"
SANDBOX_JSON = REPORT_DIR / "latest_rollback_sandbox_record.json"
SANDBOX_MD = REPORT_DIR / "latest_rollback_sandbox_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_rollback_sandbox_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_rollback_sandbox_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

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
        raise RuntimeError("Rollback Sandbox policy not found.")
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
            "sandbox_executes_rollback": False,
            "sandbox_deletes_data": False,
            "sandbox_modifies_target_files": False,
            "sandbox_records": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load rollback sandbox state.")
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


def load_manual_stub() -> dict[str, Any]:
    data = read_json(MANUAL_STUB)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "manual_stub_id": "",
        "manual_stub_record_hash": "",
        "final_gate_id": "",
        "blockers": ["manual_stub_missing"]
    }


def normalize_mode(mode: str) -> str:
    value = (mode or "safe_block").strip().lower()
    if value not in {"safe_block", "simulate_environment", "audit_only"}:
        return "safe_block"
    return value


def gate_check(stub: dict[str, Any], mode: str, operator: str, reason: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not reason:
        blockers.append("reason_missing")

    if not stub.get("manual_stub_id"):
        blockers.append("manual_stub_missing")

    if not stub.get("manual_stub_record_hash"):
        blockers.append("manual_stub_hash_missing")

    if not stub.get("final_gate_id"):
        blockers.append("final_gate_missing")

    if not stub.get("simulation_id"):
        blockers.append("dry_run_simulation_missing")

    if not stub.get("release_id"):
        blockers.append("release_record_missing")

    if not stub.get("rollback_plan_id"):
        blockers.append("rollback_plan_missing")

    if stub.get("manual_stub_executes_rollback") is True:
        blockers.append("manual_stub_executes_rollback")

    if stub.get("manual_stub_deletes_data") is True:
        blockers.append("manual_stub_deletes_data")

    if stub.get("manual_stub_modifies_files") is True:
        blockers.append("manual_stub_modifies_files")

    if stub.get("manual_stub_runs_git_reset") is True:
        blockers.append("manual_stub_runs_git_reset")

    if stub.get("manual_stub_runs_git_force_push") is True:
        blockers.append("manual_stub_runs_git_force_push")

    if stub.get("release_token_included") is True:
        blockers.append("release_token_included")

    if stub.get("raw_payload_included") is True:
        blockers.append("raw_payload_included")

    if mode == "simulate_environment":
        if stub.get("status") not in {"intent_recorded_blocked", "intent_blocked"}:
            blockers.append("manual_stub_not_ready_for_sandbox")

    return blockers


def build_sandbox_checks() -> list[dict[str, Any]]:
    return [
        {
            "check": "git_status_read_only",
            "description": "Somente leitura do status Git. Nenhum comando destrutivo executado.",
            "simulated": True,
            "executes_command": False,
            "destructive": False
        },
        {
            "check": "git_log_read_only",
            "description": "Somente leitura do historico Git. Nenhum reset executado.",
            "simulated": True,
            "executes_command": False,
            "destructive": False
        },
        {
            "check": "policy_read_only",
            "description": "Leitura das policies de rollback e governanca.",
            "simulated": True,
            "executes_command": False,
            "destructive": False
        },
        {
            "check": "evidence_hash_read_only",
            "description": "Referencia aos hashes de evidencia sem expor payload bruto.",
            "simulated": True,
            "executes_command": False,
            "destructive": False
        },
        {
            "check": "destructive_command_filter",
            "description": "Filtro bloqueia git reset, force push, delecao e modificacao de arquivos.",
            "simulated": True,
            "executes_command": False,
            "destructive": False
        }
    ]


def create_sandbox(mode: str, operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    mode = normalize_mode(mode)
    operator = operator or "operator_k_os"
    stub = load_manual_stub()

    blockers = gate_check(stub, mode, operator, reason)
    sandbox_id = "rxb_" + uuid.uuid4().hex[:12]

    governance_blocks_execution = stub.get("status") in {"intent_blocked", "intent_recorded_blocked", "intent_revoked", "missing"}

    if mode == "audit_only":
        status = "sandbox_created"
    elif governance_blocks_execution:
        status = "sandbox_blocked_by_governance"
    elif len(blockers) == 0:
        status = "sandbox_created"
    else:
        status = "blocked"

    source_refs = {
        "manual_stub": source_ref(MANUAL_STUB),
        "final_gate": source_ref(FINAL_GATE),
        "rollback_dry_run": source_ref(DRY_RUN_SIM),
        "release_record": source_ref(RELEASE_RECORD),
        "rollback_plan": source_ref(ROLLBACK_PLAN),
        "incident_record": source_ref(INCIDENT_RECORD),
        "forensics_bundle": source_ref(FORENSICS_BUNDLE),
        "ledger_record": source_ref(LEDGER_RECORD)
    }

    sandbox_checks = build_sandbox_checks()

    sandbox_body = {
        "sandbox_id": sandbox_id,
        "mode": mode,
        "status": status,
        "operator": operator,
        "manual_stub_id": stub.get("manual_stub_id", ""),
        "manual_stub_hash": stub.get("manual_stub_record_hash", ""),
        "final_gate_id": stub.get("final_gate_id", ""),
        "simulation_id": stub.get("simulation_id", ""),
        "release_id": stub.get("release_id", ""),
        "rollback_plan_id": stub.get("rollback_plan_id", ""),
        "checks": sandbox_checks,
        "source_refs": source_refs
    }

    record = {
        "ok": True,
        "checkpoint": "058",
        "module": "k_os_agent_rollback_controlled_execution_sandbox_core",
        "status": status,
        "sandbox_id": sandbox_id,
        "created_at": now(),
        "mode": mode,
        "operator": operator,
        "reason": reason or "rollback_controlled_execution_sandbox",
        "manual_stub_id": stub.get("manual_stub_id", ""),
        "manual_stub_status": stub.get("status", ""),
        "manual_stub_record_hash": stub.get("manual_stub_record_hash", ""),
        "final_gate_id": stub.get("final_gate_id", ""),
        "simulation_id": stub.get("simulation_id", ""),
        "rollback_dry_run_hash": stub.get("rollback_dry_run_hash", ""),
        "release_id": stub.get("release_id", ""),
        "rollback_plan_id": stub.get("rollback_plan_id", ""),
        "incident_id": stub.get("incident_id", ""),
        "quarantine_id": stub.get("quarantine_id", ""),
        "execution_evidence_hash": stub.get("execution_evidence_hash", ""),
        "sandbox_record_hash": stable_hash(sandbox_body),
        "governance_blocks_execution": governance_blocks_execution,
        "sandbox_check_count": len(sandbox_checks),
        "sandbox_checks": sandbox_checks,
        "sandbox_executes_rollback": False,
        "sandbox_deletes_data": False,
        "sandbox_modifies_target_files": False,
        "sandbox_runs_git_reset": False,
        "sandbox_runs_git_force_push": False,
        "sandbox_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "blocked_commands": policy.get("blocked_commands", []),
        "source_refs": source_refs,
        "blockers": blockers,
        "required_gates_before_sandbox": policy.get("required_gates_before_sandbox", []),
        "next_action": "operator_review_sandbox_report"
    }

    state.setdefault("sandbox_records", []).append(record)
    state["sandbox_records"] = state["sandbox_records"][-300:]
    save_state(state)

    write_sandbox(record)

    event("rollback_sandbox.record_created", {
        "sandbox_id": sandbox_id,
        "mode": mode,
        "status": status,
        "governance_blocks_execution": governance_blocks_execution,
        "blockers": blockers
    })

    return audit_report()


def latest_sandbox_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("sandbox_records", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_sandbox_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("sandbox_record_not_found")
    else:
        if not record.get("sandbox_id"):
            blockers.append("sandbox_id_missing")

        if not record.get("sandbox_record_hash"):
            blockers.append("sandbox_record_hash_missing")

        if not record.get("manual_stub_id"):
            blockers.append("manual_stub_id_missing")

        if not record.get("manual_stub_record_hash"):
            blockers.append("manual_stub_hash_missing")

        if record.get("sandbox_executes_rollback") is True:
            blockers.append("sandbox_executes_rollback")

        if record.get("sandbox_deletes_data") is True:
            blockers.append("sandbox_deletes_data")

        if record.get("sandbox_modifies_target_files") is True:
            blockers.append("sandbox_modifies_target_files")

        if record.get("sandbox_runs_git_reset") is True:
            blockers.append("sandbox_runs_git_reset")

        if record.get("sandbox_runs_git_force_push") is True:
            blockers.append("sandbox_runs_git_force_push")

        if record.get("sandbox_executes_shell_commands") is True:
            blockers.append("sandbox_executes_shell_commands")

        if record.get("release_token_included") is True:
            blockers.append("release_token_included")

        if record.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if record.get("governance_blocks_execution") is True:
            warnings.append("sandbox_created_with_governance_execution_block")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "058",
        "module": "k_os_agent_rollback_controlled_execution_sandbox_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "sandbox_id": record.get("sandbox_id") if record else "",
        "sandbox_status": record.get("status") if record else "",
        "sandbox_record_hash": record.get("sandbox_record_hash") if record else "",
        "manual_stub_id": record.get("manual_stub_id") if record else "",
        "governance_blocks_execution": record.get("governance_blocks_execution") if record else False,
        "sandbox_executes_rollback": False,
        "sandbox_deletes_data": False,
        "sandbox_modifies_target_files": False,
        "sandbox_runs_git_reset": False,
        "sandbox_runs_git_force_push": False,
        "sandbox_executes_shell_commands": False,
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

    event("rollback_sandbox.validation_completed", {
        "sandbox_id": validation.get("sandbox_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "sandbox_id": item.get("sandbox_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "mode": item.get("mode"),
        "manual_stub_id": item.get("manual_stub_id"),
        "final_gate_id": item.get("final_gate_id"),
        "simulation_id": item.get("simulation_id"),
        "rollback_plan_id": item.get("rollback_plan_id"),
        "sandbox_record_hash": item.get("sandbox_record_hash"),
        "governance_blocks_execution": item.get("governance_blocks_execution"),
        "sandbox_executes_rollback": False,
        "sandbox_deletes_data": False,
        "sandbox_modifies_target_files": False,
        "sandbox_runs_git_reset": False,
        "sandbox_runs_git_force_push": False,
        "sandbox_executes_shell_commands": False,
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
        "sandbox_record_count": len(records),
        "validation_count": len(validations),
        "sandbox_created_count": status_counts.get("sandbox_created", 0),
        "sandbox_blocked_by_governance_count": status_counts.get("sandbox_blocked_by_governance", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0,
        "raw_payload_count": 0,
        "status_counts": status_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    records = [safe_record(item) for item in reversed(state.get("sandbox_records", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(records, validations)

    report = {
        "ok": True,
        "checkpoint": "058",
        "module": "k_os_agent_rollback_controlled_execution_sandbox_core",
        "status": "audit_generated",
        "generated_at": now(),
        "sandbox_state_path": "local_secrets/k_os_rollback_sandbox/agent_rollback_sandbox_state.json",
        "sandbox_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "sandbox_executes_rollback": False,
        "sandbox_deletes_data": False,
        "sandbox_modifies_target_files": False,
        "sandbox_runs_git_reset": False,
        "sandbox_runs_git_force_push": False,
        "sandbox_executes_shell_commands": False,
        "manual_stub_available": MANUAL_STUB.exists(),
        "final_gate_available": FINAL_GATE.exists(),
        "dry_run_available": DRY_RUN_SIM.exists(),
        "release_record_available": RELEASE_RECORD.exists(),
        "rollback_plan_available": ROLLBACK_PLAN.exists(),
        "incident_record_available": INCIDENT_RECORD.exists(),
        "forensics_bundle_available": FORENSICS_BUNDLE.exists(),
        "ledger_record_available": LEDGER_RECORD.exists(),
        "metrics": metrics,
        "recent_sandbox_records": records,
        "recent_validations": validations,
        "blocked_commands": policy.get("blocked_commands", []),
        "required_gates_before_sandbox": policy.get("required_gates_before_sandbox", []),
        "next_checkpoint": policy.get("next_checkpoint", "059 - K-Agent Rollback Sandbox Report and Operator Review Core")
    }

    write_report(report)
    event("rollback_sandbox.audit_generated", {
        "sandbox_record_count": metrics.get("sandbox_record_count")
    })
    return report


def write_sandbox(record: dict[str, Any]) -> None:
    SANDBOX_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Controlled Execution Sandbox Record",
        "",
        "- Sandbox ID: " + str(record.get("sandbox_id")),
        "- Status: " + str(record.get("status")),
        "- Mode: " + str(record.get("mode")),
        "- Manual Stub ID: " + str(record.get("manual_stub_id")),
        "- Final Gate ID: " + str(record.get("final_gate_id")),
        "- Simulation ID: " + str(record.get("simulation_id")),
        "- Rollback Plan ID: " + str(record.get("rollback_plan_id")),
        "- Sandbox hash: " + str(record.get("sandbox_record_hash")),
        "- Governance blocks execution: " + str(record.get("governance_blocks_execution")),
        "- Executes rollback: " + str(record.get("sandbox_executes_rollback")),
        "- Deletes data: " + str(record.get("sandbox_deletes_data")),
        "- Modifies target files: " + str(record.get("sandbox_modifies_target_files")),
        "- Runs git reset: " + str(record.get("sandbox_runs_git_reset")),
        "- Runs git force push: " + str(record.get("sandbox_runs_git_force_push")),
        "- Executes shell commands: " + str(record.get("sandbox_executes_shell_commands")),
        "",
        "## Sandbox checks",
        ""
    ]

    for item in record.get("sandbox_checks", []):
        lines.append(
            "- " + str(item.get("check")) +
            " | simulated=" + str(item.get("simulated")) +
            " | destructive=" + str(item.get("destructive"))
        )

    lines.extend(["", "## Blockers", ""])

    if record.get("blockers"):
        for item in record.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    SANDBOX_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Sandbox Validation",
        "",
        "- Sandbox ID: " + str(result.get("sandbox_id")),
        "- Status: " + str(result.get("status")),
        "- Sandbox status: " + str(result.get("sandbox_status")),
        "- Sandbox hash: " + str(result.get("sandbox_record_hash")),
        "- Governance blocks execution: " + str(result.get("governance_blocks_execution")),
        "- Executes rollback: " + str(result.get("sandbox_executes_rollback")),
        "- Deletes data: " + str(result.get("sandbox_deletes_data")),
        "- Modifies target files: " + str(result.get("sandbox_modifies_target_files")),
        "- Runs git reset: " + str(result.get("sandbox_runs_git_reset")),
        "- Runs git force push: " + str(result.get("sandbox_runs_git_force_push")),
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
        "# K-OS Agent Rollback Controlled Execution Sandbox Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("sandbox_state_committed")),
        "- Executes rollback: " + str(report.get("sandbox_executes_rollback")),
        "- Deletes data: " + str(report.get("sandbox_deletes_data")),
        "- Modifies target files: " + str(report.get("sandbox_modifies_target_files")),
        "- Runs git reset: " + str(report.get("sandbox_runs_git_reset")),
        "- Runs git force push: " + str(report.get("sandbox_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("sandbox_executes_shell_commands")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent sandbox records", ""])

    if report.get("recent_sandbox_records"):
        for item in report.get("recent_sandbox_records", [])[:30]:
            lines.append(
                "- " + str(item.get("sandbox_id")) +
                " | status=" + str(item.get("status")) +
                " | mode=" + str(item.get("mode")) +
                " | stub=" + str(item.get("manual_stub_id"))
            )
    else:
        lines.append("- Nenhum registro.")

    lines.extend(["", "## Required gates before sandbox", ""])

    for gate in report.get("required_gates_before_sandbox", []):
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
    parser.add_argument("--mode", choices=["init", "sandbox", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--sandbox-mode", default="safe_block")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "sandbox":
        result = create_sandbox(args.sandbox_mode, args.operator, args.reason)

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