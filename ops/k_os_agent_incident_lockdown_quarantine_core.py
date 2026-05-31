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

POLICY_PATH = ROOT / "config" / "incident_lockdown" / "k_os_agent_incident_lockdown_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_incident_lockdown"
STATE_PATH = STATE_DIR / "agent_incident_lockdown_state.json"

REPORT_DIR = ROOT / "reports" / "incident_lockdown"
MEMORY_DIR = ROOT / "memory" / "incident_lockdown"

LATEST_JSON = REPORT_DIR / "latest_agent_incident_lockdown_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_incident_lockdown_report.md"
INCIDENT_JSON = REPORT_DIR / "latest_incident_lockdown_record.json"
INCIDENT_MD = REPORT_DIR / "latest_incident_lockdown_record.md"
VALIDATION_JSON = REPORT_DIR / "latest_incident_lockdown_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_incident_lockdown_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

FORENSICS_BUNDLE = ROOT / "reports" / "replay_forensics" / "latest_replay_forensics_bundle.json"
FORENSICS_VALIDATION = ROOT / "reports" / "replay_forensics" / "latest_replay_forensics_validation_report.json"
FORENSICS_REPORT = ROOT / "reports" / "replay_forensics" / "latest_agent_replay_forensics_report.json"

LEDGER_RECORD = ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_record.json"
LEDGER_VALIDATION = ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_validation_report.json"
ALLOWLISTED_EXECUTION = ROOT / "reports" / "allowlisted_action_executor" / "latest_allowlisted_action_execution.json"
SAFE_ROUTE = ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route.json"
APPROVAL_DECISION = ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_decision.json"
DRY_RUN_RESULT = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_result.json"
PROMPT_PACKAGE = ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_package.json"


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
        raise RuntimeError("Incident Lockdown policy not found.")
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
            "new_agent_actions_blocked": False,
            "real_execution_blocked": False,
            "incidents": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load incident lockdown state.")
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
            "hash": "",
            "status": "missing"
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


def load_forensics_bundle() -> dict[str, Any]:
    data = read_json(FORENSICS_BUNDLE)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "forensics_bundle_id": "",
        "forensics_bundle_hash": "",
        "ledger_record_id": "",
        "execution_id": "",
        "execution_evidence_hash": "",
        "blockers": ["forensics_bundle_missing"]
    }


def load_forensics_validation() -> dict[str, Any]:
    data = read_json(FORENSICS_VALIDATION)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "forensics_bundle_id": "",
        "blockers": ["forensics_validation_missing"]
    }


def load_ledger_record() -> dict[str, Any]:
    data = read_json(LEDGER_RECORD)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "ledger_record_id": "",
        "execution_id": "",
        "execution_evidence_hash": "",
        "ledger_record_hash": "",
        "chain_hash": "",
        "blockers": ["ledger_record_missing"]
    }


def normalize_severity(value: str) -> str:
    value = (value or "SEV3").strip().upper()
    if value not in {"SEV1", "SEV2", "SEV3", "SEV4"}:
        return "SEV3"
    return value


def gate_check(scope: str, severity: str, reason: str, bundle: dict[str, Any], validation: dict[str, Any], ledger: dict[str, Any]) -> list[str]:
    blockers: list[str] = []

    if not reason:
        blockers.append("incident_reason_missing")

    if not scope:
        blockers.append("incident_scope_missing")

    if not severity:
        blockers.append("incident_severity_missing")

    if not bundle.get("forensics_bundle_id"):
        blockers.append("forensics_bundle_missing")

    if not bundle.get("forensics_bundle_hash"):
        blockers.append("forensics_bundle_hash_missing")

    if validation.get("ok") is not True:
        blockers.append("forensics_validation_not_ok")

    if validation.get("status") != "validated":
        blockers.append("forensics_validation_status_not_validated")

    if not ledger.get("ledger_record_id"):
        blockers.append("ledger_record_missing")

    if not ledger.get("ledger_record_hash"):
        blockers.append("ledger_record_hash_missing")

    if not ledger.get("chain_hash"):
        blockers.append("ledger_chain_hash_missing")

    if not ledger.get("execution_evidence_hash"):
        blockers.append("execution_evidence_hash_missing")

    if bundle.get("approval_token_included") is True:
        blockers.append("approval_token_included")

    if bundle.get("raw_payload_included") is True:
        blockers.append("raw_payload_included")

    return blockers


def create_lockdown(scope: str, severity: str, reason: str, operator: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    severity = normalize_severity(severity)
    scope = scope or "agent_execution_chain"
    operator = operator or "operator_k_os"

    bundle = load_forensics_bundle()
    validation = load_forensics_validation()
    ledger = load_ledger_record()

    blockers = gate_check(scope, severity, reason, bundle, validation, ledger)

    incident_id = "inc_" + uuid.uuid4().hex[:12]
    quarantine_id = "qua_" + uuid.uuid4().hex[:12]

    source_refs = {
        "forensics_bundle": source_ref(FORENSICS_BUNDLE),
        "forensics_validation": source_ref(FORENSICS_VALIDATION),
        "forensics_report": source_ref(FORENSICS_REPORT),
        "ledger_record": source_ref(LEDGER_RECORD),
        "ledger_validation": source_ref(LEDGER_VALIDATION),
        "allowlisted_execution": source_ref(ALLOWLISTED_EXECUTION),
        "safe_route": source_ref(SAFE_ROUTE),
        "approval_decision": source_ref(APPROVAL_DECISION),
        "dry_run_result": source_ref(DRY_RUN_RESULT),
        "prompt_package": source_ref(PROMPT_PACKAGE)
    }

    quarantine_body = {
        "incident_id": incident_id,
        "quarantine_id": quarantine_id,
        "scope": scope,
        "severity": severity,
        "forensics_bundle_hash": bundle.get("forensics_bundle_hash", ""),
        "ledger_record_hash": ledger.get("ledger_record_hash", ""),
        "chain_hash": ledger.get("chain_hash", ""),
        "execution_evidence_hash": ledger.get("execution_evidence_hash", ""),
        "source_refs": source_refs
    }

    lockdown_hash = stable_hash(quarantine_body)

    record = {
        "ok": len(blockers) == 0,
        "checkpoint": "052",
        "module": "k_os_agent_incident_lockdown_quarantine_core",
        "status": "quarantine_active" if len(blockers) == 0 else "blocked",
        "incident_id": incident_id,
        "quarantine_id": quarantine_id,
        "created_at": now(),
        "operator": operator,
        "severity": severity,
        "scope": scope,
        "reason": reason or "incident_lockdown",
        "forensics_bundle_id": bundle.get("forensics_bundle_id", ""),
        "forensics_bundle_hash": bundle.get("forensics_bundle_hash", ""),
        "ledger_record_id": ledger.get("ledger_record_id", ""),
        "ledger_record_hash": ledger.get("ledger_record_hash", ""),
        "chain_hash": ledger.get("chain_hash", ""),
        "execution_id": ledger.get("execution_id", ""),
        "execution_evidence_hash": ledger.get("execution_evidence_hash", ""),
        "lockdown_record_hash": lockdown_hash,
        "quarantine_record_hash": stable_hash({"quarantine_id": quarantine_id, "lockdown_hash": lockdown_hash}),
        "new_agent_actions_blocked": len(blockers) == 0,
        "real_execution_blocked": len(blockers) == 0,
        "external_send_blocked": True,
        "external_publish_blocked": True,
        "external_provider_call_blocked": True,
        "release_requires_human_review": True,
        "rollback_preparation_enabled": True,
        "lockdown_deletes_data": False,
        "quarantine_deletes_data": False,
        "source_refs": source_refs,
        "approval_token_included": False,
        "raw_payload_included": False,
        "blockers": blockers,
        "required_gates_before_lockdown": policy.get("required_gates_before_lockdown", []),
        "next_action": "rollback_preparation" if len(blockers) == 0 else "resolve_lockdown_blockers"
    }

    state.setdefault("incidents", []).append(record)
    state["incidents"] = state["incidents"][-300:]

    if len(blockers) == 0:
        state["new_agent_actions_blocked"] = True
        state["real_execution_blocked"] = True
        state["latest_active_incident_id"] = incident_id
        state["latest_quarantine_id"] = quarantine_id

    save_state(state)
    write_incident(record)

    event("incident_lockdown.quarantine_created", {
        "incident_id": incident_id,
        "quarantine_id": quarantine_id,
        "severity": severity,
        "scope": scope,
        "ok": record.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def latest_incident_raw() -> dict[str, Any] | None:
    state = ensure_state()
    incidents = state.get("incidents", [])
    if not incidents:
        return None
    return incidents[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    incident = latest_incident_raw()
    blockers = []
    warnings = []

    if not incident:
        blockers.append("incident_lockdown_record_not_found")
    else:
        if incident.get("status") != "quarantine_active":
            blockers.append("incident_not_quarantine_active")

        if not incident.get("incident_id"):
            blockers.append("incident_id_missing")

        if not incident.get("quarantine_id"):
            blockers.append("quarantine_id_missing")

        if not incident.get("lockdown_record_hash"):
            blockers.append("lockdown_record_hash_missing")

        if not incident.get("quarantine_record_hash"):
            blockers.append("quarantine_record_hash_missing")

        if not incident.get("forensics_bundle_hash"):
            blockers.append("forensics_bundle_hash_missing")

        if not incident.get("ledger_record_hash"):
            blockers.append("ledger_record_hash_missing")

        if not incident.get("execution_evidence_hash"):
            blockers.append("execution_evidence_hash_missing")

        if incident.get("new_agent_actions_blocked") is not True:
            blockers.append("new_agent_actions_not_blocked")

        if incident.get("real_execution_blocked") is not True:
            blockers.append("real_execution_not_blocked")

        if incident.get("lockdown_deletes_data") is True:
            blockers.append("lockdown_deletes_data")

        if incident.get("quarantine_deletes_data") is True:
            blockers.append("quarantine_deletes_data")

        if incident.get("approval_token_included") is True:
            blockers.append("approval_token_included")

        if incident.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if incident.get("severity") == "SEV1":
            warnings.append("sev1_requires_immediate_operator_review")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "052",
        "module": "k_os_agent_incident_lockdown_quarantine_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "incident_id": incident.get("incident_id") if incident else "",
        "quarantine_id": incident.get("quarantine_id") if incident else "",
        "severity": incident.get("severity") if incident else "",
        "scope": incident.get("scope") if incident else "",
        "lockdown_record_hash": incident.get("lockdown_record_hash") if incident else "",
        "quarantine_record_hash": incident.get("quarantine_record_hash") if incident else "",
        "new_agent_actions_blocked": incident.get("new_agent_actions_blocked") if incident else False,
        "real_execution_blocked": incident.get("real_execution_blocked") if incident else False,
        "approval_token_included": False,
        "raw_payload_included": False,
        "lockdown_deletes_data": False,
        "quarantine_deletes_data": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if incident and len(blockers) == 0:
        incident["validated_at"] = validation["generated_at"]
        incident["validated"] = True

    save_state(state)
    write_validation(validation)

    event("incident_lockdown.validation_completed", {
        "incident_id": validation.get("incident_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_incident_for_report(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "incident_id": item.get("incident_id"),
        "quarantine_id": item.get("quarantine_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "severity": item.get("severity"),
        "scope": item.get("scope"),
        "forensics_bundle_id": item.get("forensics_bundle_id"),
        "ledger_record_id": item.get("ledger_record_id"),
        "execution_id": item.get("execution_id"),
        "lockdown_record_hash": item.get("lockdown_record_hash"),
        "quarantine_record_hash": item.get("quarantine_record_hash"),
        "new_agent_actions_blocked": item.get("new_agent_actions_blocked"),
        "real_execution_blocked": item.get("real_execution_blocked"),
        "release_requires_human_review": True,
        "approval_token_included": False,
        "raw_payload_included": False,
        "lockdown_deletes_data": False,
        "quarantine_deletes_data": False,
        "blockers": item.get("blockers", [])
    }


def compute_metrics(incidents: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}

    for item in incidents:
        status = item.get("status", "unknown")
        severity = item.get("severity", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "incident_count": len(incidents),
        "validation_count": len(validations),
        "active_quarantine_count": status_counts.get("quarantine_active", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "released_count": status_counts.get("released", 0),
        "data_delete_count": 0,
        "raw_payload_incident_count": 0,
        "approval_token_in_report_count": 0,
        "status_counts": status_counts,
        "severity_counts": severity_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    incidents = [safe_incident_for_report(item) for item in reversed(state.get("incidents", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(incidents, validations)

    report = {
        "ok": True,
        "checkpoint": "052",
        "module": "k_os_agent_incident_lockdown_quarantine_core",
        "status": "audit_generated",
        "generated_at": now(),
        "lockdown_state_path": "local_secrets/k_os_incident_lockdown/agent_incident_lockdown_state.json",
        "lockdown_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "lockdown_performs_destructive_action": False,
        "lockdown_deletes_data": False,
        "quarantine_deletes_data": False,
        "new_agent_actions_blocked": state.get("new_agent_actions_blocked", False),
        "real_execution_blocked": state.get("real_execution_blocked", False),
        "human_review_required_to_release": True,
        "rollback_preparation_enabled": True,
        "forensics_bundle_available": FORENSICS_BUNDLE.exists(),
        "forensics_validation_available": FORENSICS_VALIDATION.exists(),
        "ledger_record_available": LEDGER_RECORD.exists(),
        "ledger_validation_available": LEDGER_VALIDATION.exists(),
        "allowlisted_execution_available": ALLOWLISTED_EXECUTION.exists(),
        "safe_route_available": SAFE_ROUTE.exists(),
        "approval_decision_available": APPROVAL_DECISION.exists(),
        "metrics": metrics,
        "recent_incidents": incidents,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_lockdown": policy.get("required_gates_before_lockdown", []),
        "next_checkpoint": policy.get("next_checkpoint", "053 - K-Agent Rollback Preparation Core")
    }

    write_report(report)
    event("incident_lockdown.audit_generated", {
        "incident_count": metrics.get("incident_count"),
        "active_quarantine_count": metrics.get("active_quarantine_count")
    })
    return report


def write_incident(record: dict[str, Any]) -> None:
    INCIDENT_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Incident Lockdown and Quarantine Record",
        "",
        "- Incident ID: " + str(record.get("incident_id")),
        "- Quarantine ID: " + str(record.get("quarantine_id")),
        "- Status: " + str(record.get("status")),
        "- OK: " + str(record.get("ok")),
        "- Severity: " + str(record.get("severity")),
        "- Scope: " + str(record.get("scope")),
        "- Forensics bundle ID: " + str(record.get("forensics_bundle_id")),
        "- Ledger record ID: " + str(record.get("ledger_record_id")),
        "- Execution ID: " + str(record.get("execution_id")),
        "- Lockdown hash: " + str(record.get("lockdown_record_hash")),
        "- Quarantine hash: " + str(record.get("quarantine_record_hash")),
        "- New agent actions blocked: " + str(record.get("new_agent_actions_blocked")),
        "- Real execution blocked: " + str(record.get("real_execution_blocked")),
        "- Release requires human review: " + str(record.get("release_requires_human_review")),
        "- Approval token included: " + str(record.get("approval_token_included")),
        "- Raw payload included: " + str(record.get("raw_payload_included")),
        "- Lockdown deletes data: " + str(record.get("lockdown_deletes_data")),
        "",
        "## Blockers",
        ""
    ]

    if record.get("blockers"):
        for item in record.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    INCIDENT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Incident Lockdown Validation",
        "",
        "- Incident ID: " + str(result.get("incident_id")),
        "- Quarantine ID: " + str(result.get("quarantine_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Severity: " + str(result.get("severity")),
        "- Scope: " + str(result.get("scope")),
        "- New agent actions blocked: " + str(result.get("new_agent_actions_blocked")),
        "- Real execution blocked: " + str(result.get("real_execution_blocked")),
        "- Approval token included: " + str(result.get("approval_token_included")),
        "- Raw payload included: " + str(result.get("raw_payload_included")),
        "- Lockdown deletes data: " + str(result.get("lockdown_deletes_data")),
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
        "# K-OS Agent Incident Lockdown and Quarantine Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("lockdown_state_committed")),
        "- New agent actions blocked: " + str(report.get("new_agent_actions_blocked")),
        "- Real execution blocked: " + str(report.get("real_execution_blocked")),
        "- Lockdown deletes data: " + str(report.get("lockdown_deletes_data")),
        "- Human review required to release: " + str(report.get("human_review_required_to_release")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent incidents", ""])

    if report.get("recent_incidents"):
        for item in report.get("recent_incidents", [])[:30]:
            lines.append(
                "- " + str(item.get("incident_id")) +
                " | quarantine=" + str(item.get("quarantine_id")) +
                " | status=" + str(item.get("status")) +
                " | severity=" + str(item.get("severity"))
            )
    else:
        lines.append("- Nenhum incidente registrado.")

    lines.extend(["", "## Required gates before lockdown", ""])

    for gate in report.get("required_gates_before_lockdown", []):
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
    parser.add_argument("--mode", choices=["init", "lockdown", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--scope", default="agent_execution_chain")
    parser.add_argument("--severity", default="SEV3")
    parser.add_argument("--reason", default="")
    parser.add_argument("--operator", default="operator_k_os")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "lockdown":
        result = create_lockdown(args.scope, args.severity, args.reason, args.operator)

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