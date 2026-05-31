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

POLICY_PATH = ROOT / "config" / "rollback_release_gate" / "k_os_agent_rollback_release_gate_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_rollback_release_gate"
STATE_PATH = STATE_DIR / "agent_rollback_release_gate_state.json"

REPORT_DIR = ROOT / "reports" / "rollback_release_gate"
MEMORY_DIR = ROOT / "memory" / "rollback_release_gate"

LATEST_JSON = REPORT_DIR / "latest_agent_rollback_release_gate_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_rollback_release_gate_report.md"
RELEASE_JSON = REPORT_DIR / "latest_rollback_release_record.json"
RELEASE_MD = REPORT_DIR / "latest_rollback_release_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_rollback_release_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_rollback_release_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

ROLLBACK_PLAN = ROOT / "reports" / "rollback_preparation" / "latest_rollback_plan.json"
ROLLBACK_VALIDATION = ROOT / "reports" / "rollback_preparation" / "latest_rollback_plan_validation_report.json"
ROLLBACK_REPORT = ROOT / "reports" / "rollback_preparation" / "latest_agent_rollback_preparation_report.json"

INCIDENT_RECORD = ROOT / "reports" / "incident_lockdown" / "latest_incident_lockdown_record.json"
FORENSICS_BUNDLE = ROOT / "reports" / "replay_forensics" / "latest_replay_forensics_bundle.json"
LEDGER_RECORD = ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_record.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
        raise RuntimeError("Rollback Release Gate policy not found.")
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
            "release_gate_executes_rollback": False,
            "release_gate_deletes_data": False,
            "release_records": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load rollback release gate state.")
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
    data = read_json(ROLLBACK_PLAN)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "rollback_plan_id": "",
        "rollback_plan_hash": "",
        "incident_id": "",
        "quarantine_id": "",
        "execution_evidence_hash": "",
        "blockers": ["rollback_plan_missing"]
    }


def load_plan_validation() -> dict[str, Any]:
    data = read_json(ROLLBACK_VALIDATION)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "rollback_plan_id": "",
        "blockers": ["rollback_plan_validation_missing"]
    }


def gate_check(plan: dict[str, Any], validation: dict[str, Any], decision: str, operator: str, reason: str) -> list[str]:
    blockers: list[str] = []

    if not operator:
        blockers.append("operator_missing")

    if not reason:
        blockers.append("release_reason_missing")

    if not plan.get("rollback_plan_id"):
        blockers.append("rollback_plan_missing")

    if not plan.get("rollback_plan_hash"):
        blockers.append("rollback_plan_hash_missing")

    if not plan.get("incident_id"):
        blockers.append("incident_id_missing")

    if not plan.get("quarantine_id"):
        blockers.append("quarantine_id_missing")

    if not plan.get("execution_evidence_hash"):
        blockers.append("execution_evidence_hash_missing")

    if plan.get("rollback_executes_changes") is True:
        blockers.append("rollback_plan_executes_changes")

    if plan.get("rollback_deletes_data") is True:
        blockers.append("rollback_plan_deletes_data")

    if plan.get("rollback_modifies_files") is True:
        blockers.append("rollback_plan_modifies_files")

    if plan.get("approval_token_included") is True:
        blockers.append("approval_token_included")

    if plan.get("raw_payload_included") is True:
        blockers.append("raw_payload_included")

    if decision == "approve_future_rollback":
        if plan.get("status") not in {"prepared", "validated"}:
            blockers.append("rollback_plan_not_prepared_or_validated")

        if validation.get("ok") is not True:
            blockers.append("rollback_plan_validation_not_ok")

        if validation.get("status") != "validated":
            blockers.append("rollback_plan_validation_status_not_validated")

    return blockers


def normalize_decision(decision: str) -> str:
    value = (decision or "block_future_rollback").strip().lower()
    if value not in {"approve_future_rollback", "block_future_rollback", "revoke_future_rollback"}:
        return "block_future_rollback"
    return value


def create_release(decision: str, operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    decision = normalize_decision(decision)
    operator = operator or "operator_k_os"

    plan = load_plan()
    validation = load_plan_validation()
    blockers = gate_check(plan, validation, decision, operator, reason)

    release_id = "rbg_" + uuid.uuid4().hex[:12]
    local_token = ""
    local_token_hash = ""

    if decision == "approve_future_rollback" and len(blockers) == 0:
        status = "approved_for_future_rollback"
        local_token = "kos_rollback_release_" + secrets.token_urlsafe(32)
        local_token_hash = token_hash(local_token)
    elif decision == "revoke_future_rollback":
        status = "revoked"
    else:
        status = "blocked"
        if decision == "block_future_rollback" and "operator_blocked_release" not in blockers:
            blockers.append("operator_blocked_release")

    source_refs = {
        "rollback_plan": source_ref(ROLLBACK_PLAN),
        "rollback_validation": source_ref(ROLLBACK_VALIDATION),
        "rollback_report": source_ref(ROLLBACK_REPORT),
        "incident_record": source_ref(INCIDENT_RECORD),
        "forensics_bundle": source_ref(FORENSICS_BUNDLE),
        "ledger_record": source_ref(LEDGER_RECORD)
    }

    release_body = {
        "release_id": release_id,
        "decision": decision,
        "status": status,
        "operator": operator,
        "rollback_plan_id": plan.get("rollback_plan_id", ""),
        "rollback_plan_hash": plan.get("rollback_plan_hash", ""),
        "incident_id": plan.get("incident_id", ""),
        "quarantine_id": plan.get("quarantine_id", ""),
        "execution_evidence_hash": plan.get("execution_evidence_hash", ""),
        "source_refs": source_refs
    }

    local_record = {
        "release_id": release_id,
        "created_at": now(),
        "decision": decision,
        "status": status,
        "operator": operator,
        "reason": reason or "rollback_release_gate_decision",
        "rollback_plan_id": plan.get("rollback_plan_id", ""),
        "rollback_plan_hash": plan.get("rollback_plan_hash", ""),
        "incident_id": plan.get("incident_id", ""),
        "quarantine_id": plan.get("quarantine_id", ""),
        "execution_evidence_hash": plan.get("execution_evidence_hash", ""),
        "release_record_hash": stable_hash(release_body),
        "local_release_token": local_token,
        "local_release_token_hash": local_token_hash,
        "local_release_token_stored_local_only": True,
        "release_token_included": False,
        "release_gate_executes_rollback": False,
        "release_gate_deletes_data": False,
        "release_gate_modifies_files": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "source_refs": source_refs,
        "blockers": blockers,
        "required_gates_before_future_rollback_release": policy.get("required_gates_before_future_rollback_release", []),
        "next_action": "rollback_dry_run_simulator" if status == "approved_for_future_rollback" else "rollback_remains_blocked"
    }

    state.setdefault("release_records", []).append(local_record)
    state["release_records"] = state["release_records"][-300:]
    save_state(state)

    write_release(sanitize_release(local_record))

    event("rollback_release_gate.record_created", {
        "release_id": release_id,
        "decision": decision,
        "status": status,
        "ok": status in {"approved_for_future_rollback", "blocked", "revoked"},
        "blockers": blockers
    })

    return audit_report()


def sanitize_release(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": item.get("status") in {"approved_for_future_rollback", "blocked", "revoked"},
        "checkpoint": "054",
        "module": "k_os_agent_rollback_approval_release_gate_core",
        "status": item.get("status"),
        "release_id": item.get("release_id"),
        "created_at": item.get("created_at"),
        "decision": item.get("decision"),
        "operator": item.get("operator"),
        "reason": item.get("reason"),
        "rollback_plan_id": item.get("rollback_plan_id"),
        "rollback_plan_hash": item.get("rollback_plan_hash"),
        "incident_id": item.get("incident_id"),
        "quarantine_id": item.get("quarantine_id"),
        "execution_evidence_hash": item.get("execution_evidence_hash"),
        "release_record_hash": item.get("release_record_hash"),
        "local_release_token_hash": item.get("local_release_token_hash"),
        "release_token_included": False,
        "local_release_token_stored_local_only": True,
        "release_gate_executes_rollback": False,
        "release_gate_deletes_data": False,
        "release_gate_modifies_files": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "blockers": item.get("blockers", []),
        "next_action": item.get("next_action")
    }


def latest_release_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("release_records", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_release_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("release_record_not_found")
    else:
        if not record.get("release_id"):
            blockers.append("release_id_missing")

        if not record.get("release_record_hash"):
            blockers.append("release_record_hash_missing")

        if not record.get("rollback_plan_id"):
            blockers.append("rollback_plan_id_missing")

        if not record.get("rollback_plan_hash"):
            blockers.append("rollback_plan_hash_missing")

        if record.get("release_token_included") is True:
            blockers.append("release_token_included")

        if record.get("release_gate_executes_rollback") is True:
            blockers.append("release_gate_executes_rollback")

        if record.get("release_gate_deletes_data") is True:
            blockers.append("release_gate_deletes_data")

        if record.get("release_gate_modifies_files") is True:
            blockers.append("release_gate_modifies_files")

        if record.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if record.get("status") == "blocked":
            warnings.append("rollback_release_blocked_by_gate")

        if record.get("status") == "approved_for_future_rollback" and not record.get("local_release_token_hash"):
            blockers.append("local_release_token_hash_missing")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "054",
        "module": "k_os_agent_rollback_approval_release_gate_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "release_id": record.get("release_id") if record else "",
        "release_status": record.get("status") if record else "",
        "decision": record.get("decision") if record else "",
        "rollback_plan_id": record.get("rollback_plan_id") if record else "",
        "release_record_hash": record.get("release_record_hash") if record else "",
        "local_release_token_hash": record.get("local_release_token_hash") if record else "",
        "release_token_included": False,
        "release_gate_executes_rollback": False,
        "release_gate_deletes_data": False,
        "release_gate_modifies_files": False,
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

    event("rollback_release_gate.validation_completed", {
        "release_id": validation.get("release_id"),
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
        "release_record_count": len(records),
        "validation_count": len(validations),
        "approved_count": status_counts.get("approved_for_future_rollback", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "revoked_count": status_counts.get("revoked", 0),
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "file_modify_count": 0,
        "raw_payload_record_count": 0,
        "status_counts": status_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    records = [sanitize_release(item) for item in reversed(state.get("release_records", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(records, validations)

    report = {
        "ok": True,
        "checkpoint": "054",
        "module": "k_os_agent_rollback_approval_release_gate_core",
        "status": "audit_generated",
        "generated_at": now(),
        "release_state_path": "local_secrets/k_os_rollback_release_gate/agent_rollback_release_gate_state.json",
        "release_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "release_gate_executes_rollback": False,
        "release_gate_deletes_data": False,
        "release_gate_modifies_files": False,
        "human_operator_required": True,
        "rollback_plan_available": ROLLBACK_PLAN.exists(),
        "rollback_validation_available": ROLLBACK_VALIDATION.exists(),
        "incident_record_available": INCIDENT_RECORD.exists(),
        "forensics_bundle_available": FORENSICS_BUNDLE.exists(),
        "ledger_record_available": LEDGER_RECORD.exists(),
        "metrics": metrics,
        "recent_release_records": records,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_future_rollback_release": policy.get("required_gates_before_future_rollback_release", []),
        "next_checkpoint": policy.get("next_checkpoint", "055 - K-Agent Rollback Dry Run Simulator Core")
    }

    write_report(report)
    event("rollback_release_gate.audit_generated", {
        "release_record_count": metrics.get("release_record_count")
    })
    return report


def write_release(record: dict[str, Any]) -> None:
    RELEASE_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Release Gate Record",
        "",
        "- Release ID: " + str(record.get("release_id")),
        "- Status: " + str(record.get("status")),
        "- OK: " + str(record.get("ok")),
        "- Decision: " + str(record.get("decision")),
        "- Rollback Plan ID: " + str(record.get("rollback_plan_id")),
        "- Incident ID: " + str(record.get("incident_id")),
        "- Quarantine ID: " + str(record.get("quarantine_id")),
        "- Release hash: " + str(record.get("release_record_hash")),
        "- Local release token hash: " + str(record.get("local_release_token_hash")),
        "- Release token included: " + str(record.get("release_token_included")),
        "- Executes rollback: " + str(record.get("release_gate_executes_rollback")),
        "- Deletes data: " + str(record.get("release_gate_deletes_data")),
        "- Modifies files: " + str(record.get("release_gate_modifies_files")),
        "",
        "## Blockers",
        ""
    ]

    if record.get("blockers"):
        for item in record.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    RELEASE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Release Gate Validation",
        "",
        "- Release ID: " + str(result.get("release_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Release status: " + str(result.get("release_status")),
        "- Decision: " + str(result.get("decision")),
        "- Rollback Plan ID: " + str(result.get("rollback_plan_id")),
        "- Release hash: " + str(result.get("release_record_hash")),
        "- Release token included: " + str(result.get("release_token_included")),
        "- Executes rollback: " + str(result.get("release_gate_executes_rollback")),
        "- Deletes data: " + str(result.get("release_gate_deletes_data")),
        "- Modifies files: " + str(result.get("release_gate_modifies_files")),
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
        "# K-OS Agent Rollback Approval and Release Gate Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("release_state_committed")),
        "- Executes rollback: " + str(report.get("release_gate_executes_rollback")),
        "- Deletes data: " + str(report.get("release_gate_deletes_data")),
        "- Modifies files: " + str(report.get("release_gate_modifies_files")),
        "- Human operator required: " + str(report.get("human_operator_required")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent release records", ""])

    if report.get("recent_release_records"):
        for item in report.get("recent_release_records", [])[:30]:
            lines.append(
                "- " + str(item.get("release_id")) +
                " | status=" + str(item.get("status")) +
                " | decision=" + str(item.get("decision")) +
                " | plan=" + str(item.get("rollback_plan_id"))
            )
    else:
        lines.append("- Nenhum registro.")

    lines.extend(["", "## Required gates before future rollback release", ""])

    for gate in report.get("required_gates_before_future_rollback_release", []):
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
    parser.add_argument("--decision", default="block_future_rollback")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "decide":
        result = create_release(args.decision, args.operator, args.reason)

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