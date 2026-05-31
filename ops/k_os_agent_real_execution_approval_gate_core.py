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

POLICY_PATH = ROOT / "config" / "real_execution_gate" / "k_os_agent_real_execution_approval_gate_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_real_execution_gate"
STATE_PATH = STATE_DIR / "agent_real_execution_approval_gate_state.json"

REPORT_DIR = ROOT / "reports" / "real_execution_gate"
MEMORY_DIR = ROOT / "memory" / "real_execution_gate"

LATEST_JSON = REPORT_DIR / "latest_agent_real_execution_approval_gate_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_real_execution_approval_gate_report.md"
DECISION_JSON = REPORT_DIR / "latest_real_execution_approval_decision.json"
DECISION_MD = REPORT_DIR / "latest_real_execution_approval_decision.md"
VALIDATION_JSON = REPORT_DIR / "latest_real_execution_approval_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_real_execution_approval_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

DRY_RUN_RESULT = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_result.json"
DRY_RUN_VALIDATION = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_validation_report.json"
DRY_RUN_REPORT = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_executor_report.json"
PROMPT_PACKAGE_REPORT = ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_package.json"
EXECUTION_PLAN_REPORT = ROOT / "reports" / "prompt_assembly" / "latest_agent_execution_plan.json"
AGENT_QUEUE_REPORT = ROOT / "reports" / "agent_queue" / "latest_agent_orchestration_queue_report.json"
AGENT_RUNTIME_REPORT = ROOT / "reports" / "agent_runtime" / "latest_agent_runtime_supervisor_report.json"
COMMAND_CENTER_REPORT = ROOT / "reports" / "command_center" / "latest_command_center_action_router_report.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
        raise RuntimeError("Real Execution Approval Gate policy not found.")
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
            "external_publish_enabled": False,
            "real_execution_performed_by_gate": False,
            "decisions": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load approval gate state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def load_dry_run_result() -> dict[str, Any]:
    data = read_json(DRY_RUN_RESULT)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "dry_run_id": "",
        "agent_id": "k_atlas_engineer",
        "task_id": "manual_real_execution_gate_task",
        "action_id": "cockpit_audit",
        "evidence_hash": "",
        "dry_run": True,
        "real_execution_performed": False,
        "side_effects_performed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": ["dry_run_result_missing"]
    }


def load_dry_run_validation() -> dict[str, Any]:
    data = read_json(DRY_RUN_VALIDATION)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "dry_run_id": "",
        "evidence_hash": "",
        "blockers": ["dry_run_validation_missing"]
    }


def dry_run_gate_check(dry_run: dict[str, Any], validation: dict[str, Any]) -> list[str]:
    blockers = []

    if not dry_run.get("dry_run_id"):
        blockers.append("dry_run_result_missing")

    if dry_run.get("dry_run") is not True:
        blockers.append("dry_run_flag_missing")

    if dry_run.get("real_execution_performed") is True:
        blockers.append("real_execution_already_performed")

    if dry_run.get("side_effects_performed") is True:
        blockers.append("side_effects_already_performed")

    if dry_run.get("external_send_performed") is True:
        blockers.append("external_send_already_performed")

    if dry_run.get("external_publish_performed") is True:
        blockers.append("external_publish_already_performed")

    if not dry_run.get("evidence_hash"):
        blockers.append("dry_run_evidence_hash_missing")

    if validation.get("ok") is not True:
        blockers.append("dry_run_validation_not_ok")

    if validation.get("status") not in {"validated"}:
        blockers.append("dry_run_validation_status_not_validated")

    if validation.get("dry_run_id") and dry_run.get("dry_run_id") and validation.get("dry_run_id") != dry_run.get("dry_run_id"):
        blockers.append("dry_run_validation_id_mismatch")

    return blockers


def create_decision(decision: str, operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    decision_norm = (decision or "block").strip().lower()
    if decision_norm not in {"approve", "block", "revoke"}:
        decision_norm = "block"

    if not operator:
        operator = "operator_k_os"

    dry_run = load_dry_run_result()
    validation = load_dry_run_validation()
    blockers = dry_run_gate_check(dry_run, validation)

    decision_id = "appr_" + uuid.uuid4().hex[:12]
    approval_token_plain = ""
    approval_token_hash = ""

    status = "blocked"

    if decision_norm == "approve":
        if blockers:
            status = "blocked"
        else:
            status = "approved_for_real_execution"
            approval_token_plain = "kos_approval_" + secrets.token_urlsafe(32)
            approval_token_hash = token_hash(approval_token_plain)

    elif decision_norm == "revoke":
        status = "revoked"

    else:
        status = "blocked"
        if not blockers:
            blockers.append("operator_blocked")

    local_record = {
        "decision_id": decision_id,
        "created_at": now(),
        "decision": decision_norm,
        "status": status,
        "operator": operator,
        "reason": reason or "operator_decision",
        "dry_run_id": dry_run.get("dry_run_id", ""),
        "agent_id": dry_run.get("agent_id", ""),
        "task_id": dry_run.get("task_id", ""),
        "action_id": dry_run.get("action_id", ""),
        "dry_run_evidence_hash": dry_run.get("evidence_hash", ""),
        "approval_token": approval_token_plain,
        "approval_token_hash": approval_token_hash,
        "approval_token_stored_local_only": True,
        "real_execution_performed_by_gate": False,
        "side_effects_performed_by_gate": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": blockers
    }

    public_decision = sanitize_decision(local_record)

    state.setdefault("decisions", []).append(local_record)
    state["decisions"] = state["decisions"][-300:]
    save_state(state)

    write_decision(public_decision)

    event("real_execution_gate.decision_created", {
        "decision_id": decision_id,
        "decision": decision_norm,
        "status": status,
        "dry_run_id": dry_run.get("dry_run_id", ""),
        "approval_token_hash": approval_token_hash,
        "blockers": blockers
    })

    return audit_report()


def sanitize_decision(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": item.get("status") == "approved_for_real_execution",
        "checkpoint": "047",
        "module": "k_os_agent_real_execution_approval_gate_core",
        "status": item.get("status"),
        "decision_id": item.get("decision_id"),
        "created_at": item.get("created_at"),
        "decision": item.get("decision"),
        "operator": item.get("operator"),
        "reason": item.get("reason"),
        "dry_run_id": item.get("dry_run_id"),
        "agent_id": item.get("agent_id"),
        "task_id": item.get("task_id"),
        "action_id": item.get("action_id"),
        "dry_run_evidence_hash": item.get("dry_run_evidence_hash"),
        "approval_token_hash": item.get("approval_token_hash"),
        "approval_token_included": False,
        "approval_token_stored_local_only": True,
        "real_execution_performed_by_gate": False,
        "side_effects_performed_by_gate": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": item.get("blockers", []),
        "next_action": "safe_execution_router" if item.get("status") == "approved_for_real_execution" else "resolve_or_review"
    }


def latest_local_decision() -> dict[str, Any] | None:
    state = ensure_state()
    items = state.get("decisions", [])
    if not items:
        return None
    return items[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    decision = latest_local_decision()
    blockers = []
    warnings = []

    if not decision:
        blockers.append("approval_decision_not_found")
    else:
        if not decision.get("decision_id"):
            blockers.append("decision_id_missing")

        if decision.get("status") == "approved_for_real_execution":
            if not decision.get("approval_token"):
                blockers.append("local_approval_token_missing")

            if not decision.get("approval_token_hash"):
                blockers.append("approval_token_hash_missing")

            if not decision.get("dry_run_id"):
                blockers.append("dry_run_id_missing")

            if not decision.get("dry_run_evidence_hash"):
                blockers.append("dry_run_evidence_hash_missing")

            if decision.get("real_execution_performed_by_gate") is True:
                blockers.append("real_execution_performed_by_gate")

            if decision.get("side_effects_performed_by_gate") is True:
                blockers.append("side_effects_performed_by_gate")

        if decision.get("approval_token") and decision.get("approval_token_hash"):
            if token_hash(decision.get("approval_token")) != decision.get("approval_token_hash"):
                blockers.append("approval_token_hash_mismatch")

        if decision.get("status") == "blocked":
            warnings.append("latest_decision_blocked")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "047",
        "module": "k_os_agent_real_execution_approval_gate_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "decision_id": decision.get("decision_id") if decision else "",
        "decision_status": decision.get("status") if decision else "",
        "dry_run_id": decision.get("dry_run_id") if decision else "",
        "agent_id": decision.get("agent_id") if decision else "",
        "task_id": decision.get("task_id") if decision else "",
        "action_id": decision.get("action_id") if decision else "",
        "approval_token_hash": decision.get("approval_token_hash") if decision else "",
        "approval_token_included": False,
        "real_execution_performed_by_gate": False,
        "side_effects_performed_by_gate": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if decision and len(blockers) == 0:
        decision["validated_at"] = validation["generated_at"]
        decision["validated"] = True

    save_state(state)
    write_validation(validation)

    event("real_execution_gate.validation_completed", {
        "decision_id": validation.get("decision_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def compute_metrics(decisions: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    agent_counts: dict[str, int] = {}

    for item in decisions:
        status = item.get("status", "unknown")
        agent = item.get("agent_id", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        agent_counts[agent] = agent_counts.get(agent, 0) + 1

    return {
        "decision_count": len(decisions),
        "validation_count": len(validations),
        "approved_count": status_counts.get("approved_for_real_execution", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "revoked_count": status_counts.get("revoked", 0),
        "real_execution_performed_count": 0,
        "side_effect_count": 0,
        "external_send_count": 0,
        "external_publish_count": 0,
        "status_counts": status_counts,
        "agent_counts": agent_counts
    }


def safe_decision_for_report(item: dict[str, Any]) -> dict[str, Any]:
    return sanitize_decision(item)


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    decisions = [safe_decision_for_report(item) for item in reversed(state.get("decisions", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(decisions, validations)

    report = {
        "ok": True,
        "checkpoint": "047",
        "module": "k_os_agent_real_execution_approval_gate_core",
        "status": "audit_generated",
        "generated_at": now(),
        "approval_gate_state_path": "local_secrets/k_os_real_execution_gate/agent_real_execution_approval_gate_state.json",
        "approval_gate_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "real_execution_performed_by_gate": False,
        "side_effects_performed_by_gate": False,
        "approval_token_stored_local_only": True,
        "approval_token_hash_only_in_reports": True,
        "dry_run_result_available": DRY_RUN_RESULT.exists(),
        "dry_run_validation_available": DRY_RUN_VALIDATION.exists(),
        "dry_run_report_available": DRY_RUN_REPORT.exists(),
        "prompt_package_report_available": PROMPT_PACKAGE_REPORT.exists(),
        "execution_plan_report_available": EXECUTION_PLAN_REPORT.exists(),
        "agent_queue_report_available": AGENT_QUEUE_REPORT.exists(),
        "agent_runtime_report_available": AGENT_RUNTIME_REPORT.exists(),
        "command_center_report_available": COMMAND_CENTER_REPORT.exists(),
        "metrics": metrics,
        "recent_decisions": decisions,
        "recent_validations": validations,
        "required_gates_before_execution_token": policy.get("required_gates_before_execution_token", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "048 - K-Agent Safe Execution Router Core")
    }

    write_report(report)
    event("real_execution_gate.audit_generated", {
        "decision_count": metrics.get("decision_count")
    })
    return report


def write_decision(decision: dict[str, Any]) -> None:
    DECISION_JSON.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Real Execution Approval Decision",
        "",
        "- Decision ID: " + str(decision.get("decision_id")),
        "- Status: " + str(decision.get("status")),
        "- OK: " + str(decision.get("ok")),
        "- Decision: " + str(decision.get("decision")),
        "- Operator: " + str(decision.get("operator")),
        "- Agent: " + str(decision.get("agent_id")),
        "- Task: " + str(decision.get("task_id")),
        "- Action: " + str(decision.get("action_id")),
        "- Dry Run ID: " + str(decision.get("dry_run_id")),
        "- Evidence hash: " + str(decision.get("dry_run_evidence_hash")),
        "- Approval token hash: " + str(decision.get("approval_token_hash")),
        "- Approval token included: " + str(decision.get("approval_token_included")),
        "- Real execution performed by gate: " + str(decision.get("real_execution_performed_by_gate")),
        "- Side effects performed by gate: " + str(decision.get("side_effects_performed_by_gate")),
        "",
        "## Blockers",
        ""
    ]

    if decision.get("blockers"):
        for item in decision.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    DECISION_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Real Execution Approval Validation Report",
        "",
        "- Decision ID: " + str(result.get("decision_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Decision status: " + str(result.get("decision_status")),
        "- Dry Run ID: " + str(result.get("dry_run_id")),
        "- Agent: " + str(result.get("agent_id")),
        "- Task: " + str(result.get("task_id")),
        "- Action: " + str(result.get("action_id")),
        "- Approval token hash: " + str(result.get("approval_token_hash")),
        "- Approval token included: " + str(result.get("approval_token_included")),
        "- Real execution performed by gate: " + str(result.get("real_execution_performed_by_gate")),
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
        "# K-OS Agent Real Execution Approval Gate Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("approval_gate_state_committed")),
        "- Real execution performed by gate: " + str(report.get("real_execution_performed_by_gate")),
        "- Side effects performed by gate: " + str(report.get("side_effects_performed_by_gate")),
        "- Approval token stored local only: " + str(report.get("approval_token_stored_local_only")),
        "- Approval token hash only in reports: " + str(report.get("approval_token_hash_only_in_reports")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent decisions", ""])

    if report.get("recent_decisions"):
        for item in report.get("recent_decisions", [])[:30]:
            lines.append(
                "- " + str(item.get("decision_id")) +
                " | status=" + str(item.get("status")) +
                " | decision=" + str(item.get("decision")) +
                " | agent=" + str(item.get("agent_id")) +
                " | dry_run=" + str(item.get("dry_run_id"))
            )
    else:
        lines.append("- Nenhuma decisao registrada.")

    lines.extend(["", "## Required gates before execution token", ""])

    for gate in report.get("required_gates_before_execution_token", []):
        lines.append("- " + str(gate))

    lines.extend(["", "## Blocked actions", ""])

    for item in report.get("blocked_actions", []):
        lines.append("- " + str(item))

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
    parser.add_argument("--mode", choices=["init", "approve", "block", "revoke", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "approve":
        result = create_decision("approve", args.operator, args.reason)

    elif args.mode == "block":
        result = create_decision("block", args.operator, args.reason)

    elif args.mode == "revoke":
        result = create_decision("revoke", args.operator, args.reason)

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