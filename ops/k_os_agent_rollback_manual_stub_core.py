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

POLICY_PATH = ROOT / "config" / "rollback_manual_stub" / "k_os_agent_rollback_manual_stub_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_rollback_manual_stub"
STATE_PATH = STATE_DIR / "agent_rollback_manual_stub_state.json"

REPORT_DIR = ROOT / "reports" / "rollback_manual_stub"
MEMORY_DIR = ROOT / "memory" / "rollback_manual_stub"

LATEST_JSON = REPORT_DIR / "latest_agent_rollback_manual_stub_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_rollback_manual_stub_report.md"
STUB_JSON = REPORT_DIR / "latest_rollback_manual_stub_record.json"
STUB_MD = REPORT_DIR / "latest_rollback_manual_stub_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_rollback_manual_stub_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_rollback_manual_stub_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

FINAL_GATE = ROOT / "reports" / "rollback_final_gate" / "latest_rollback_final_gate_record.json"
FINAL_GATE_VALIDATION = ROOT / "reports" / "rollback_final_gate" / "latest_rollback_final_gate_validation_report.json"
FINAL_GATE_REPORT = ROOT / "reports" / "rollback_final_gate" / "latest_agent_rollback_final_gate_report.json"

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
        raise RuntimeError("Rollback Manual Stub policy not found.")
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
            "manual_stub_executes_rollback": False,
            "manual_stub_deletes_data": False,
            "manual_stub_modifies_files": False,
            "stub_records": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load rollback manual stub state.")
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


def load_final_gate() -> dict[str, Any]:
    data = read_json(FINAL_GATE)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "final_gate_id": "",
        "final_gate_record_hash": "",
        "simulation_id": "",
        "rollback_dry_run_hash": "",
        "release_id": "",
        "rollback_plan_id": "",
        "execution_evidence_hash": "",
        "blockers": ["rollback_final_gate_missing"]
    }


def normalize_mode(mode: str) -> str:
    value = (mode or "block_intent").strip().lower()
    if value not in {"record_intent", "block_intent", "revoke_intent"}:
        return "block_intent"
    return value


def gate_check(final_gate: dict[str, Any], mode: str, operator: str, intent: str, reason: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not intent:
        blockers.append("operator_intent_missing")

    if not reason:
        blockers.append("reason_missing")

    if not final_gate.get("final_gate_id"):
        blockers.append("rollback_final_gate_missing")

    if not final_gate.get("final_gate_record_hash"):
        blockers.append("final_gate_hash_missing")

    if not final_gate.get("simulation_id"):
        blockers.append("simulation_id_missing")

    if not final_gate.get("rollback_dry_run_hash"):
        blockers.append("rollback_dry_run_hash_missing")

    if not final_gate.get("release_id"):
        blockers.append("release_id_missing")

    if not final_gate.get("rollback_plan_id"):
        blockers.append("rollback_plan_id_missing")

    if not final_gate.get("execution_evidence_hash"):
        blockers.append("execution_evidence_hash_missing")

    if final_gate.get("final_gate_executes_rollback") is True:
        blockers.append("final_gate_executes_rollback")

    if final_gate.get("final_gate_deletes_data") is True:
        blockers.append("final_gate_deletes_data")

    if final_gate.get("final_gate_modifies_files") is True:
        blockers.append("final_gate_modifies_files")

    if final_gate.get("final_gate_runs_git_reset") is True:
        blockers.append("final_gate_runs_git_reset")

    if final_gate.get("final_gate_runs_git_force_push") is True:
        blockers.append("final_gate_runs_git_force_push")

    if final_gate.get("release_token_included") is True:
        blockers.append("release_token_included")

    if final_gate.get("raw_payload_included") is True:
        blockers.append("raw_payload_included")

    if mode == "record_intent":
        if final_gate.get("status") != "approved_for_future_manual_execution":
            blockers.append("final_gate_not_approved_for_manual_execution")

    return blockers


def create_stub(mode: str, operator: str, intent: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    mode = normalize_mode(mode)
    operator = operator or "operator_k_os"
    final_gate = load_final_gate()

    blockers = gate_check(final_gate, mode, operator, intent, reason)
    stub_id = "rms_" + uuid.uuid4().hex[:12]

    if mode == "revoke_intent":
        status = "intent_revoked"
    elif mode == "record_intent" and len(blockers) == 0:
        status = "intent_recorded_blocked"
        blockers.append("manual_stub_does_not_execute_rollback")
    else:
        status = "intent_blocked"
        if "manual_stub_blocks_execution" not in blockers:
            blockers.append("manual_stub_blocks_execution")

    source_refs = {
        "rollback_final_gate": source_ref(FINAL_GATE),
        "rollback_final_gate_validation": source_ref(FINAL_GATE_VALIDATION),
        "rollback_final_gate_report": source_ref(FINAL_GATE_REPORT),
        "rollback_dry_run": source_ref(DRY_RUN_SIM),
        "release_record": source_ref(RELEASE_RECORD),
        "rollback_plan": source_ref(ROLLBACK_PLAN),
        "incident_record": source_ref(INCIDENT_RECORD),
        "forensics_bundle": source_ref(FORENSICS_BUNDLE),
        "ledger_record": source_ref(LEDGER_RECORD)
    }

    intent_hash = stable_hash({
        "operator": operator,
        "intent": intent,
        "reason": reason,
        "mode": mode
    })

    stub_body = {
        "stub_id": stub_id,
        "mode": mode,
        "status": status,
        "operator": operator,
        "operator_intent_hash": intent_hash,
        "final_gate_id": final_gate.get("final_gate_id", ""),
        "final_gate_record_hash": final_gate.get("final_gate_record_hash", ""),
        "simulation_id": final_gate.get("simulation_id", ""),
        "rollback_dry_run_hash": final_gate.get("rollback_dry_run_hash", ""),
        "release_id": final_gate.get("release_id", ""),
        "rollback_plan_id": final_gate.get("rollback_plan_id", ""),
        "execution_evidence_hash": final_gate.get("execution_evidence_hash", ""),
        "source_refs": source_refs
    }

    record = {
        "ok": True,
        "checkpoint": "057",
        "module": "k_os_agent_rollback_manual_execution_stub_core",
        "status": status,
        "manual_stub_id": stub_id,
        "created_at": now(),
        "mode": mode,
        "operator": operator,
        "reason": reason or "rollback_manual_execution_stub",
        "operator_intent_hash": intent_hash,
        "final_gate_id": final_gate.get("final_gate_id", ""),
        "final_gate_status": final_gate.get("status", ""),
        "final_gate_record_hash": final_gate.get("final_gate_record_hash", ""),
        "simulation_id": final_gate.get("simulation_id", ""),
        "rollback_dry_run_hash": final_gate.get("rollback_dry_run_hash", ""),
        "release_id": final_gate.get("release_id", ""),
        "rollback_plan_id": final_gate.get("rollback_plan_id", ""),
        "incident_id": final_gate.get("incident_id", ""),
        "quarantine_id": final_gate.get("quarantine_id", ""),
        "execution_evidence_hash": final_gate.get("execution_evidence_hash", ""),
        "manual_stub_record_hash": stable_hash(stub_body),
        "manual_stub_executes_rollback": False,
        "manual_stub_deletes_data": False,
        "manual_stub_modifies_files": False,
        "manual_stub_runs_git_reset": False,
        "manual_stub_runs_git_force_push": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "source_refs": source_refs,
        "blockers": blockers,
        "required_gates_before_manual_stub": policy.get("required_gates_before_manual_stub", []),
        "next_action": "rollback_controlled_execution_sandbox" if status == "intent_recorded_blocked" else "rollback_execution_remains_blocked"
    }

    state.setdefault("stub_records", []).append(record)
    state["stub_records"] = state["stub_records"][-300:]
    save_state(state)

    write_stub(record)

    event("rollback_manual_stub.record_created", {
        "manual_stub_id": stub_id,
        "mode": mode,
        "status": status,
        "blockers": blockers
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
        blockers.append("manual_stub_record_not_found")
    else:
        if not record.get("manual_stub_id"):
            blockers.append("manual_stub_id_missing")

        if not record.get("manual_stub_record_hash"):
            blockers.append("manual_stub_record_hash_missing")

        if not record.get("final_gate_id"):
            blockers.append("final_gate_id_missing")

        if not record.get("final_gate_record_hash"):
            blockers.append("final_gate_hash_missing")

        if record.get("manual_stub_executes_rollback") is True:
            blockers.append("manual_stub_executes_rollback")

        if record.get("manual_stub_deletes_data") is True:
            blockers.append("manual_stub_deletes_data")

        if record.get("manual_stub_modifies_files") is True:
            blockers.append("manual_stub_modifies_files")

        if record.get("manual_stub_runs_git_reset") is True:
            blockers.append("manual_stub_runs_git_reset")

        if record.get("manual_stub_runs_git_force_push") is True:
            blockers.append("manual_stub_runs_git_force_push")

        if record.get("release_token_included") is True:
            blockers.append("release_token_included")

        if record.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        warnings.append("manual_stub_never_executes_rollback")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "057",
        "module": "k_os_agent_rollback_manual_execution_stub_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "manual_stub_id": record.get("manual_stub_id") if record else "",
        "manual_stub_status": record.get("status") if record else "",
        "final_gate_id": record.get("final_gate_id") if record else "",
        "manual_stub_record_hash": record.get("manual_stub_record_hash") if record else "",
        "manual_stub_executes_rollback": False,
        "manual_stub_deletes_data": False,
        "manual_stub_modifies_files": False,
        "manual_stub_runs_git_reset": False,
        "manual_stub_runs_git_force_push": False,
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

    event("rollback_manual_stub.validation_completed", {
        "manual_stub_id": validation.get("manual_stub_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def sanitize_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "manual_stub_id": item.get("manual_stub_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "mode": item.get("mode"),
        "final_gate_id": item.get("final_gate_id"),
        "final_gate_status": item.get("final_gate_status"),
        "simulation_id": item.get("simulation_id"),
        "rollback_plan_id": item.get("rollback_plan_id"),
        "manual_stub_record_hash": item.get("manual_stub_record_hash"),
        "manual_stub_executes_rollback": False,
        "manual_stub_deletes_data": False,
        "manual_stub_modifies_files": False,
        "manual_stub_runs_git_reset": False,
        "manual_stub_runs_git_force_push": False,
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
        "manual_stub_record_count": len(records),
        "validation_count": len(validations),
        "intent_recorded_blocked_count": status_counts.get("intent_recorded_blocked", 0),
        "intent_blocked_count": status_counts.get("intent_blocked", 0),
        "intent_revoked_count": status_counts.get("intent_revoked", 0),
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

    records = [sanitize_record(item) for item in reversed(state.get("stub_records", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(records, validations)

    report = {
        "ok": True,
        "checkpoint": "057",
        "module": "k_os_agent_rollback_manual_execution_stub_core",
        "status": "audit_generated",
        "generated_at": now(),
        "manual_stub_state_path": "local_secrets/k_os_rollback_manual_stub/agent_rollback_manual_stub_state.json",
        "manual_stub_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "manual_stub_executes_rollback": False,
        "manual_stub_deletes_data": False,
        "manual_stub_modifies_files": False,
        "manual_stub_runs_git_reset": False,
        "manual_stub_runs_git_force_push": False,
        "rollback_final_gate_available": FINAL_GATE.exists(),
        "rollback_final_gate_validation_available": FINAL_GATE_VALIDATION.exists(),
        "rollback_dry_run_available": DRY_RUN_SIM.exists(),
        "release_record_available": RELEASE_RECORD.exists(),
        "rollback_plan_available": ROLLBACK_PLAN.exists(),
        "incident_record_available": INCIDENT_RECORD.exists(),
        "forensics_bundle_available": FORENSICS_BUNDLE.exists(),
        "ledger_record_available": LEDGER_RECORD.exists(),
        "metrics": metrics,
        "recent_manual_stub_records": records,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_manual_stub": policy.get("required_gates_before_manual_stub", []),
        "next_checkpoint": policy.get("next_checkpoint", "058 - K-Agent Rollback Controlled Execution Sandbox Core")
    }

    write_report(report)
    event("rollback_manual_stub.audit_generated", {
        "manual_stub_record_count": metrics.get("manual_stub_record_count")
    })
    return report


def write_stub(record: dict[str, Any]) -> None:
    STUB_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Manual Execution Stub Record",
        "",
        "- Manual Stub ID: " + str(record.get("manual_stub_id")),
        "- Status: " + str(record.get("status")),
        "- Mode: " + str(record.get("mode")),
        "- Final Gate ID: " + str(record.get("final_gate_id")),
        "- Final Gate Status: " + str(record.get("final_gate_status")),
        "- Simulation ID: " + str(record.get("simulation_id")),
        "- Rollback Plan ID: " + str(record.get("rollback_plan_id")),
        "- Stub hash: " + str(record.get("manual_stub_record_hash")),
        "- Executes rollback: " + str(record.get("manual_stub_executes_rollback")),
        "- Deletes data: " + str(record.get("manual_stub_deletes_data")),
        "- Modifies files: " + str(record.get("manual_stub_modifies_files")),
        "- Runs git reset: " + str(record.get("manual_stub_runs_git_reset")),
        "- Runs git force push: " + str(record.get("manual_stub_runs_git_force_push")),
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
        "# K-OS Rollback Manual Execution Stub Validation",
        "",
        "- Manual Stub ID: " + str(result.get("manual_stub_id")),
        "- Status: " + str(result.get("status")),
        "- Stub status: " + str(result.get("manual_stub_status")),
        "- Final Gate ID: " + str(result.get("final_gate_id")),
        "- Stub hash: " + str(result.get("manual_stub_record_hash")),
        "- Executes rollback: " + str(result.get("manual_stub_executes_rollback")),
        "- Deletes data: " + str(result.get("manual_stub_deletes_data")),
        "- Modifies files: " + str(result.get("manual_stub_modifies_files")),
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
        "# K-OS Agent Rollback Manual Execution Stub Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("manual_stub_state_committed")),
        "- Executes rollback: " + str(report.get("manual_stub_executes_rollback")),
        "- Deletes data: " + str(report.get("manual_stub_deletes_data")),
        "- Modifies files: " + str(report.get("manual_stub_modifies_files")),
        "- Runs git reset: " + str(report.get("manual_stub_runs_git_reset")),
        "- Runs git force push: " + str(report.get("manual_stub_runs_git_force_push")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent manual stub records", ""])

    if report.get("recent_manual_stub_records"):
        for item in report.get("recent_manual_stub_records", [])[:30]:
            lines.append(
                "- " + str(item.get("manual_stub_id")) +
                " | status=" + str(item.get("status")) +
                " | mode=" + str(item.get("mode")) +
                " | final_gate=" + str(item.get("final_gate_id"))
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
    parser.add_argument("--stub-mode", default="block_intent")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--intent", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "stub":
        result = create_stub(args.stub_mode, args.operator, args.intent, args.reason)

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