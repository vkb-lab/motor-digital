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

POLICY_PATH = ROOT / "config" / "replay_forensics" / "k_os_agent_replay_forensics_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_replay_forensics"
STATE_PATH = STATE_DIR / "agent_replay_forensics_state.json"

REPORT_DIR = ROOT / "reports" / "replay_forensics"
MEMORY_DIR = ROOT / "memory" / "replay_forensics"

LATEST_JSON = REPORT_DIR / "latest_agent_replay_forensics_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_replay_forensics_report.md"
BUNDLE_JSON = REPORT_DIR / "latest_replay_forensics_bundle.json"
BUNDLE_MD = REPORT_DIR / "latest_replay_forensics_bundle.md"
VALIDATION_JSON = REPORT_DIR / "latest_replay_forensics_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_replay_forensics_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

LEDGER_RECORD = ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_record.json"
LEDGER_VALIDATION = ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_validation_report.json"
LEDGER_REPORT = ROOT / "reports" / "execution_result_ledger" / "latest_agent_execution_result_ledger_report.json"

ALLOWLISTED_EXECUTION = ROOT / "reports" / "allowlisted_action_executor" / "latest_allowlisted_action_execution.json"
ALLOWLISTED_VALIDATION = ROOT / "reports" / "allowlisted_action_executor" / "latest_allowlisted_action_execution_validation_report.json"
SAFE_ROUTE = ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route.json"
SAFE_ROUTE_VALIDATION = ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route_validation_report.json"
APPROVAL_DECISION = ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_decision.json"
APPROVAL_VALIDATION = ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_validation_report.json"
DRY_RUN_RESULT = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_result.json"
DRY_RUN_VALIDATION = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_validation_report.json"
PROMPT_PACKAGE = ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_package.json"
EXECUTION_PLAN = ROOT / "reports" / "prompt_assembly" / "latest_agent_execution_plan.json"
CONTEXT_PACKET = ROOT / "reports" / "context_injection" / "latest_agent_context_packet.json"


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
        raise RuntimeError("Replay Forensics policy not found.")
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
            "read_only_viewer": True,
            "replay_executes_actions": False,
            "bundles": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load replay forensics state.")
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
        "hash": stable_hash(data),
        "top_level_keys": list(data.keys())[:40]
    }


def load_ledger_record() -> dict[str, Any]:
    data = read_json(LEDGER_RECORD)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "ledger_record_id": "",
        "ledger_record_hash": "",
        "chain_hash": "",
        "execution_id": "",
        "execution_evidence_hash": "",
        "approval_token_included": False,
        "raw_payload_included": False,
        "blockers": ["ledger_record_missing"]
    }


def load_ledger_validation() -> dict[str, Any]:
    data = read_json(LEDGER_VALIDATION)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "ledger_record_id": "",
        "blockers": ["ledger_validation_missing"]
    }


def safe_extract(data: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: data.get(key, "") for key in keys}


def build_timeline() -> list[dict[str, Any]]:
    prompt = read_json(PROMPT_PACKAGE) or {}
    dry_run = read_json(DRY_RUN_RESULT) or {}
    approval = read_json(APPROVAL_DECISION) or {}
    route = read_json(SAFE_ROUTE) or {}
    execution = read_json(ALLOWLISTED_EXECUTION) or {}
    ledger = read_json(LEDGER_RECORD) or {}

    timeline = [
        {
            "order": 1,
            "stage": "prompt_package",
            "source": rel(PROMPT_PACKAGE),
            "available": PROMPT_PACKAGE.exists(),
            "status": prompt.get("status", "missing"),
            "id": prompt.get("prompt_package_id", ""),
            "hash": prompt.get("prompt_package_hash", ""),
            "summary": safe_extract(prompt, ["agent_id", "task_id", "action_id", "objective"])
        },
        {
            "order": 2,
            "stage": "dry_run_result",
            "source": rel(DRY_RUN_RESULT),
            "available": DRY_RUN_RESULT.exists(),
            "status": dry_run.get("status", "missing"),
            "id": dry_run.get("dry_run_id", ""),
            "hash": dry_run.get("evidence_hash", ""),
            "summary": safe_extract(dry_run, ["agent_id", "task_id", "action_id", "simulated_step_count"])
        },
        {
            "order": 3,
            "stage": "approval_decision",
            "source": rel(APPROVAL_DECISION),
            "available": APPROVAL_DECISION.exists(),
            "status": approval.get("status", "missing"),
            "id": approval.get("decision_id", ""),
            "hash": approval.get("approval_token_hash", ""),
            "summary": {
                "decision": approval.get("decision", ""),
                "operator": approval.get("operator", ""),
                "approval_token_included": False
            }
        },
        {
            "order": 4,
            "stage": "safe_route",
            "source": rel(SAFE_ROUTE),
            "available": SAFE_ROUTE.exists(),
            "status": route.get("status", "missing"),
            "id": route.get("route_id", ""),
            "hash": route.get("route_hash", ""),
            "summary": safe_extract(route, ["agent_id", "task_id", "action_id", "route_target"])
        },
        {
            "order": 5,
            "stage": "allowlisted_execution",
            "source": rel(ALLOWLISTED_EXECUTION),
            "available": ALLOWLISTED_EXECUTION.exists(),
            "status": execution.get("status", "missing"),
            "id": execution.get("execution_id", ""),
            "hash": execution.get("execution_evidence_hash", ""),
            "summary": {
                "executed_action": execution.get("executed_action", ""),
                "arbitrary_command_executed": False,
                "shell_command_executed": False,
                "external_send_performed": False,
                "external_publish_performed": False
            }
        },
        {
            "order": 6,
            "stage": "execution_result_ledger",
            "source": rel(LEDGER_RECORD),
            "available": LEDGER_RECORD.exists(),
            "status": ledger.get("status", "missing"),
            "id": ledger.get("ledger_record_id", ""),
            "hash": ledger.get("ledger_record_hash", ""),
            "summary": {
                "execution_id": ledger.get("execution_id", ""),
                "chain_hash": ledger.get("chain_hash", ""),
                "raw_payload_included": False,
                "approval_token_included": False
            }
        }
    ]

    return timeline


def bundle_gate_check(ledger: dict[str, Any], validation: dict[str, Any]) -> list[str]:
    blockers = []

    if not ledger.get("ledger_record_id"):
        blockers.append("ledger_record_missing")

    if ledger.get("status") not in {"recorded", "validated"}:
        blockers.append("ledger_record_status_invalid")

    if validation.get("ok") is not True:
        blockers.append("ledger_validation_not_ok")

    if validation.get("status") != "validated":
        blockers.append("ledger_validation_status_not_validated")

    if not ledger.get("ledger_record_hash"):
        blockers.append("ledger_record_hash_missing")

    if not ledger.get("chain_hash"):
        blockers.append("chain_hash_missing")

    if not ledger.get("execution_evidence_hash"):
        blockers.append("execution_evidence_hash_missing")

    if ledger.get("approval_token_included") is True:
        blockers.append("approval_token_included")

    if ledger.get("raw_payload_included") is True:
        blockers.append("raw_payload_included")

    if ledger.get("external_send_performed") is True:
        blockers.append("external_send_performed")

    if ledger.get("external_publish_performed") is True:
        blockers.append("external_publish_performed")

    return blockers


def create_bundle(reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    ledger = load_ledger_record()
    validation = load_ledger_validation()
    blockers = bundle_gate_check(ledger, validation)

    timeline = build_timeline()

    source_refs = {
        "context_packet": source_ref(CONTEXT_PACKET),
        "prompt_package": source_ref(PROMPT_PACKAGE),
        "execution_plan": source_ref(EXECUTION_PLAN),
        "dry_run_result": source_ref(DRY_RUN_RESULT),
        "dry_run_validation": source_ref(DRY_RUN_VALIDATION),
        "approval_decision": source_ref(APPROVAL_DECISION),
        "approval_validation": source_ref(APPROVAL_VALIDATION),
        "safe_route": source_ref(SAFE_ROUTE),
        "safe_route_validation": source_ref(SAFE_ROUTE_VALIDATION),
        "allowlisted_execution": source_ref(ALLOWLISTED_EXECUTION),
        "allowlisted_validation": source_ref(ALLOWLISTED_VALIDATION),
        "ledger_record": source_ref(LEDGER_RECORD),
        "ledger_validation": source_ref(LEDGER_VALIDATION),
        "ledger_report": source_ref(LEDGER_REPORT)
    }

    bundle_id = "for_" + uuid.uuid4().hex[:12]

    bundle_body = {
        "ledger_record_hash": ledger.get("ledger_record_hash", ""),
        "chain_hash": ledger.get("chain_hash", ""),
        "execution_evidence_hash": ledger.get("execution_evidence_hash", ""),
        "timeline": timeline,
        "source_refs": source_refs
    }

    bundle = {
        "ok": len(blockers) == 0,
        "checkpoint": "051",
        "module": "k_os_agent_replay_forensics_viewer_core",
        "status": "bundle_created" if len(blockers) == 0 else "blocked",
        "forensics_bundle_id": bundle_id,
        "created_at": now(),
        "reason": reason or "replay_forensics_bundle_created",
        "ledger_record_id": ledger.get("ledger_record_id", ""),
        "execution_id": ledger.get("execution_id", ""),
        "executed_action": ledger.get("executed_action", ""),
        "ledger_record_hash": ledger.get("ledger_record_hash", ""),
        "chain_hash": ledger.get("chain_hash", ""),
        "execution_evidence_hash": ledger.get("execution_evidence_hash", ""),
        "timeline_count": len(timeline),
        "timeline": timeline,
        "source_refs": source_refs,
        "forensics_bundle_hash": stable_hash(bundle_body),
        "read_only_viewer": True,
        "replay_executes_actions": False,
        "replay_performs_side_effects": False,
        "approval_token_included": False,
        "raw_payload_included": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "blockers": blockers,
        "required_gates_before_forensics_bundle": policy.get("required_gates_before_forensics_bundle", []),
        "next_action": "incident_lockdown_and_quarantine" if len(blockers) == 0 else "resolve_blockers"
    }

    state.setdefault("bundles", []).append(bundle)
    state["bundles"] = state["bundles"][-300:]
    save_state(state)

    write_bundle(bundle)

    event("replay_forensics.bundle_created", {
        "forensics_bundle_id": bundle_id,
        "ledger_record_id": ledger.get("ledger_record_id", ""),
        "ok": bundle.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def latest_bundle_raw() -> dict[str, Any] | None:
    state = ensure_state()
    bundles = state.get("bundles", [])
    if not bundles:
        return None
    return bundles[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    bundle = latest_bundle_raw()
    blockers = []
    warnings = []

    if not bundle:
        blockers.append("forensics_bundle_not_found")
    else:
        if bundle.get("status") != "bundle_created":
            blockers.append("forensics_bundle_not_created")

        if not bundle.get("forensics_bundle_hash"):
            blockers.append("forensics_bundle_hash_missing")

        if not bundle.get("ledger_record_hash"):
            blockers.append("ledger_record_hash_missing")

        if not bundle.get("chain_hash"):
            blockers.append("chain_hash_missing")

        if bundle.get("read_only_viewer") is not True:
            blockers.append("viewer_not_read_only")

        if bundle.get("replay_executes_actions") is True:
            blockers.append("replay_executes_actions")

        if bundle.get("replay_performs_side_effects") is True:
            blockers.append("replay_performs_side_effects")

        if bundle.get("approval_token_included") is True:
            blockers.append("approval_token_included")

        if bundle.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if bundle.get("external_send_enabled") is True:
            blockers.append("external_send_enabled")

        if bundle.get("external_publish_enabled") is True:
            blockers.append("external_publish_enabled")

        if bundle.get("timeline_count", 0) < 6:
            warnings.append("timeline_incomplete")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "051",
        "module": "k_os_agent_replay_forensics_viewer_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "forensics_bundle_id": bundle.get("forensics_bundle_id") if bundle else "",
        "ledger_record_id": bundle.get("ledger_record_id") if bundle else "",
        "execution_id": bundle.get("execution_id") if bundle else "",
        "forensics_bundle_hash": bundle.get("forensics_bundle_hash") if bundle else "",
        "ledger_record_hash": bundle.get("ledger_record_hash") if bundle else "",
        "chain_hash": bundle.get("chain_hash") if bundle else "",
        "read_only_viewer": True,
        "replay_executes_actions": False,
        "replay_performs_side_effects": False,
        "approval_token_included": False,
        "raw_payload_included": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if bundle and len(blockers) == 0:
        bundle["status"] = "validated"
        bundle["validated_at"] = validation["generated_at"]

    save_state(state)
    write_validation(validation)

    event("replay_forensics.validation_completed", {
        "forensics_bundle_id": validation.get("forensics_bundle_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_bundle_for_report(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "forensics_bundle_id": item.get("forensics_bundle_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "ledger_record_id": item.get("ledger_record_id"),
        "execution_id": item.get("execution_id"),
        "executed_action": item.get("executed_action"),
        "forensics_bundle_hash": item.get("forensics_bundle_hash"),
        "ledger_record_hash": item.get("ledger_record_hash"),
        "chain_hash": item.get("chain_hash"),
        "timeline_count": item.get("timeline_count", 0),
        "read_only_viewer": True,
        "replay_executes_actions": False,
        "replay_performs_side_effects": False,
        "approval_token_included": False,
        "raw_payload_included": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "blockers": item.get("blockers", [])
    }


def compute_metrics(bundles: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}

    for item in bundles:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "forensics_bundle_count": len(bundles),
        "validation_count": len(validations),
        "bundle_created_count": status_counts.get("bundle_created", 0),
        "validated_count": status_counts.get("validated", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "replay_execution_count": 0,
        "side_effect_count": 0,
        "approval_token_in_report_count": 0,
        "raw_payload_bundle_count": 0,
        "status_counts": status_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    bundles = [safe_bundle_for_report(item) for item in reversed(state.get("bundles", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(bundles, validations)

    report = {
        "ok": True,
        "checkpoint": "051",
        "module": "k_os_agent_replay_forensics_viewer_core",
        "status": "audit_generated",
        "generated_at": now(),
        "forensics_state_path": "local_secrets/k_os_replay_forensics/agent_replay_forensics_state.json",
        "forensics_state_committed": False,
        "read_only_viewer": True,
        "replay_executes_actions": False,
        "replay_performs_side_effects": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "raw_payload_storage_allowed": False,
        "approval_token_storage_in_reports_allowed": False,
        "ledger_record_available": LEDGER_RECORD.exists(),
        "ledger_validation_available": LEDGER_VALIDATION.exists(),
        "allowlisted_execution_available": ALLOWLISTED_EXECUTION.exists(),
        "safe_route_available": SAFE_ROUTE.exists(),
        "approval_decision_available": APPROVAL_DECISION.exists(),
        "dry_run_result_available": DRY_RUN_RESULT.exists(),
        "prompt_package_available": PROMPT_PACKAGE.exists(),
        "metrics": metrics,
        "recent_bundles": bundles,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_forensics_bundle": policy.get("required_gates_before_forensics_bundle", []),
        "next_checkpoint": policy.get("next_checkpoint", "052 - K-Agent Incident Lockdown and Quarantine Core")
    }

    write_report(report)
    event("replay_forensics.audit_generated", {
        "forensics_bundle_count": metrics.get("forensics_bundle_count")
    })
    return report


def write_bundle(bundle: dict[str, Any]) -> None:
    BUNDLE_JSON.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Replay and Forensics Bundle",
        "",
        "- Bundle ID: " + str(bundle.get("forensics_bundle_id")),
        "- Status: " + str(bundle.get("status")),
        "- OK: " + str(bundle.get("ok")),
        "- Ledger Record ID: " + str(bundle.get("ledger_record_id")),
        "- Execution ID: " + str(bundle.get("execution_id")),
        "- Executed action: " + str(bundle.get("executed_action")),
        "- Bundle hash: " + str(bundle.get("forensics_bundle_hash")),
        "- Ledger record hash: " + str(bundle.get("ledger_record_hash")),
        "- Chain hash: " + str(bundle.get("chain_hash")),
        "- Read only viewer: " + str(bundle.get("read_only_viewer")),
        "- Replay executes actions: " + str(bundle.get("replay_executes_actions")),
        "- Approval token included: " + str(bundle.get("approval_token_included")),
        "- Raw payload included: " + str(bundle.get("raw_payload_included")),
        "",
        "## Timeline",
        ""
    ]

    for item in bundle.get("timeline", []):
        lines.append(
            "- " + str(item.get("order")) +
            " | " + str(item.get("stage")) +
            " | status=" + str(item.get("status")) +
            " | id=" + str(item.get("id"))
        )

    lines.extend(["", "## Blockers", ""])

    if bundle.get("blockers"):
        for item in bundle.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    BUNDLE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Replay Forensics Validation",
        "",
        "- Bundle ID: " + str(result.get("forensics_bundle_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Ledger Record ID: " + str(result.get("ledger_record_id")),
        "- Execution ID: " + str(result.get("execution_id")),
        "- Bundle hash: " + str(result.get("forensics_bundle_hash")),
        "- Read only viewer: " + str(result.get("read_only_viewer")),
        "- Replay executes actions: " + str(result.get("replay_executes_actions")),
        "- Approval token included: " + str(result.get("approval_token_included")),
        "- Raw payload included: " + str(result.get("raw_payload_included")),
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
        "# K-OS Agent Replay and Forensics Viewer Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("forensics_state_committed")),
        "- Read only viewer: " + str(report.get("read_only_viewer")),
        "- Replay executes actions: " + str(report.get("replay_executes_actions")),
        "- Raw payload storage allowed: " + str(report.get("raw_payload_storage_allowed")),
        "- Approval token storage in reports allowed: " + str(report.get("approval_token_storage_in_reports_allowed")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent bundles", ""])

    if report.get("recent_bundles"):
        for item in report.get("recent_bundles", [])[:30]:
            lines.append(
                "- " + str(item.get("forensics_bundle_id")) +
                " | status=" + str(item.get("status")) +
                " | ledger=" + str(item.get("ledger_record_id")) +
                " | execution=" + str(item.get("execution_id"))
            )
    else:
        lines.append("- Nenhum bundle registrado.")

    lines.extend(["", "## Required gates before forensics bundle", ""])

    for gate in report.get("required_gates_before_forensics_bundle", []):
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
    parser.add_argument("--mode", choices=["init", "bundle", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "bundle":
        result = create_bundle(args.reason)

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