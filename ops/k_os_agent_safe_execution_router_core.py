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

POLICY_PATH = ROOT / "config" / "safe_execution_router" / "k_os_agent_safe_execution_router_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_safe_execution_router"
STATE_PATH = STATE_DIR / "agent_safe_execution_router_state.json"

REPORT_DIR = ROOT / "reports" / "safe_execution_router"
MEMORY_DIR = ROOT / "memory" / "safe_execution_router"

LATEST_JSON = REPORT_DIR / "latest_agent_safe_execution_router_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_safe_execution_router_report.md"
ROUTE_JSON = REPORT_DIR / "latest_safe_execution_route.json"
ROUTE_MD = REPORT_DIR / "latest_safe_execution_route.md"
VALIDATION_JSON = REPORT_DIR / "latest_safe_execution_route_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_safe_execution_route_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

APPROVAL_DECISION = ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_decision.json"
APPROVAL_VALIDATION = ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_validation_report.json"
APPROVAL_STATE = ROOT / "local_secrets" / "k_os_real_execution_gate" / "agent_real_execution_approval_gate_state.json"

DRY_RUN_RESULT = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_result.json"
PROMPT_PACKAGE = ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_package.json"
EXECUTION_PLAN = ROOT / "reports" / "prompt_assembly" / "latest_agent_execution_plan.json"
PERMISSION_MATRIX = ROOT / "config" / "governance" / "k_os_agent_permission_matrix.json"

COMMAND_CENTER_REPORT = ROOT / "reports" / "command_center" / "latest_command_center_action_router_report.json"
AGENT_RUNTIME_REPORT = ROOT / "reports" / "agent_runtime" / "latest_agent_runtime_supervisor_report.json"
AGENT_QUEUE_REPORT = ROOT / "reports" / "agent_queue" / "latest_agent_orchestration_queue_report.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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
        raise RuntimeError("Safe Execution Router policy not found.")
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
            "router_performs_real_execution": False,
            "routes": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load safe execution router state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def latest_approval_from_local_state() -> dict[str, Any]:
    state = read_json(APPROVAL_STATE) or {}
    decisions = state.get("decisions", [])
    if decisions:
        return decisions[-1]
    return {}


def load_approval_decision() -> dict[str, Any]:
    data = read_json(APPROVAL_DECISION)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "decision_id": "",
        "dry_run_id": "",
        "approval_token_hash": "",
        "blockers": ["approval_decision_missing"]
    }


def load_approval_validation() -> dict[str, Any]:
    data = read_json(APPROVAL_VALIDATION)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "decision_id": "",
        "approval_token_hash": "",
        "blockers": ["approval_validation_missing"]
    }


def load_dry_run_result() -> dict[str, Any]:
    data = read_json(DRY_RUN_RESULT)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "dry_run_id": "",
        "agent_id": "k_atlas_engineer",
        "task_id": "manual_safe_route_task",
        "action_id": "cockpit_audit",
        "evidence_hash": "",
        "real_execution_performed": False,
        "side_effects_performed": False
    }


def pick_route_target(requested_target: str, action_id: str) -> str:
    policy = load_policy()
    allowed = set(policy.get("allowed_route_targets", []))

    requested = (requested_target or "").strip()

    if requested in allowed:
        return requested

    if action_id in allowed:
        return action_id

    if action_id == "cockpit_audit":
        return "cockpit_audit"

    return "safe_internal_noop"


def route_gate_check(target: str, approval: dict[str, Any], validation: dict[str, Any], dry_run: dict[str, Any]) -> list[str]:
    policy = load_policy()
    allowed = set(policy.get("allowed_route_targets", []))
    blocked_targets = set(policy.get("blocked_route_targets", []))
    blockers: list[str] = []

    if target not in allowed:
        blockers.append("route_target_not_allowlisted")

    if target in blocked_targets:
        blockers.append("route_target_explicitly_blocked")

    if not approval.get("decision_id"):
        blockers.append("approval_decision_missing")

    if approval.get("status") != "approved_for_real_execution":
        blockers.append("approval_decision_not_approved")

    if not approval.get("approval_token_hash"):
        blockers.append("approval_token_hash_missing")

    if validation.get("ok") is not True:
        blockers.append("approval_validation_not_ok")

    if validation.get("status") != "validated":
        blockers.append("approval_validation_status_not_validated")

    if approval.get("approval_token_hash") and validation.get("approval_token_hash"):
        if approval.get("approval_token_hash") != validation.get("approval_token_hash"):
            blockers.append("approval_token_hash_mismatch")

    if not dry_run.get("dry_run_id"):
        blockers.append("dry_run_result_missing")

    if not dry_run.get("evidence_hash"):
        blockers.append("dry_run_evidence_hash_missing")

    if dry_run.get("real_execution_performed") is True:
        blockers.append("dry_run_already_performed_real_execution")

    if dry_run.get("side_effects_performed") is True:
        blockers.append("dry_run_already_performed_side_effects")

    if target.startswith("external_"):
        blockers.append("external_route_blocked")

    return blockers


def permission_summary(agent_id: str, target: str) -> dict[str, Any]:
    matrix = read_json(PERMISSION_MATRIX) or {}

    return {
        "permission_matrix_available": PERMISSION_MATRIX.exists(),
        "agent_id": agent_id,
        "route_target": target,
        "allowlist_only": True,
        "external_send_allowed": False,
        "external_publish_allowed": False,
        "real_side_effect_allowed_by_router": False,
        "matrix_hash": stable_hash(matrix) if matrix else "",
        "checked": True
    }


def create_route(target: str, operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()

    approval = load_approval_decision()
    validation = load_approval_validation()
    local_approval = latest_approval_from_local_state()
    dry_run = load_dry_run_result()

    agent_id = dry_run.get("agent_id") or approval.get("agent_id") or "k_atlas_engineer"
    task_id = dry_run.get("task_id") or approval.get("task_id") or "manual_safe_route_task"
    action_id = dry_run.get("action_id") or approval.get("action_id") or "cockpit_audit"

    route_target = pick_route_target(target, action_id)
    blockers = route_gate_check(route_target, approval, validation, dry_run)

    local_token_present = bool(local_approval.get("approval_token"))
    if approval.get("status") == "approved_for_real_execution" and not local_token_present:
        blockers.append("local_approval_token_missing")

    route_id = "route_" + uuid.uuid4().hex[:12]

    route_body = {
        "route_id": route_id,
        "agent_id": agent_id,
        "task_id": task_id,
        "action_id": action_id,
        "route_target": route_target,
        "approval_token_hash": approval.get("approval_token_hash", ""),
        "dry_run_evidence_hash": dry_run.get("evidence_hash", ""),
        "permission": permission_summary(agent_id, route_target)
    }

    route = {
        "ok": len(blockers) == 0,
        "checkpoint": "048",
        "module": "k_os_agent_safe_execution_router_core",
        "status": "ready_for_allowlisted_executor" if len(blockers) == 0 else "blocked",
        "route_id": route_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "safe_execution_route_created",
        "agent_id": agent_id,
        "task_id": task_id,
        "action_id": action_id,
        "route_target": route_target,
        "decision_id": approval.get("decision_id", ""),
        "approval_status": approval.get("status", ""),
        "approval_token_hash": approval.get("approval_token_hash", ""),
        "approval_token_included": False,
        "local_approval_token_present": local_token_present,
        "dry_run_id": dry_run.get("dry_run_id", ""),
        "dry_run_evidence_hash": dry_run.get("evidence_hash", ""),
        "route_hash": stable_hash(route_body),
        "permission_check": route_body["permission"],
        "router_performs_real_execution": False,
        "side_effects_performed_by_router": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": blockers,
        "next_action": "allowlisted_action_executor" if len(blockers) == 0 else "resolve_blockers"
    }

    state.setdefault("routes", []).append(route)
    state["routes"] = state["routes"][-300:]
    save_state(state)

    write_route(route)

    event("safe_execution_router.route_created", {
        "route_id": route_id,
        "route_target": route_target,
        "ok": route.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def latest_route_raw() -> dict[str, Any] | None:
    state = ensure_state()
    routes = state.get("routes", [])
    if not routes:
        return None
    return routes[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    route = latest_route_raw()
    blockers = []
    warnings = []

    if not route:
        blockers.append("route_not_found")
    else:
        if not route.get("route_id"):
            blockers.append("route_id_missing")

        if route.get("status") != "ready_for_allowlisted_executor":
            blockers.append("route_not_ready_for_allowlisted_executor")

        if not route.get("route_hash"):
            blockers.append("route_hash_missing")

        if not route.get("approval_token_hash"):
            blockers.append("approval_token_hash_missing")

        if route.get("approval_token_included") is True:
            blockers.append("approval_token_leaked_to_report")

        if route.get("router_performs_real_execution") is True:
            blockers.append("router_performed_real_execution")

        if route.get("side_effects_performed_by_router") is True:
            blockers.append("router_performed_side_effect")

        if route.get("external_send_performed") is True:
            blockers.append("external_send_performed")

        if route.get("external_publish_performed") is True:
            blockers.append("external_publish_performed")

        if route.get("route_target") == "safe_internal_noop":
            warnings.append("route_target_is_noop")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "048",
        "module": "k_os_agent_safe_execution_router_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "route_id": route.get("route_id") if route else "",
        "route_target": route.get("route_target") if route else "",
        "agent_id": route.get("agent_id") if route else "",
        "task_id": route.get("task_id") if route else "",
        "action_id": route.get("action_id") if route else "",
        "route_hash": route.get("route_hash") if route else "",
        "approval_token_hash": route.get("approval_token_hash") if route else "",
        "approval_token_included": False,
        "router_performs_real_execution": False,
        "side_effects_performed_by_router": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if route and len(blockers) == 0:
        route["validated_at"] = validation["generated_at"]
        route["validated"] = True

    save_state(state)
    write_validation(validation)

    event("safe_execution_router.validation_completed", {
        "route_id": validation.get("route_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_route_for_report(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "route_id": item.get("route_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "agent_id": item.get("agent_id"),
        "task_id": item.get("task_id"),
        "action_id": item.get("action_id"),
        "route_target": item.get("route_target"),
        "decision_id": item.get("decision_id"),
        "dry_run_id": item.get("dry_run_id"),
        "route_hash": item.get("route_hash"),
        "approval_token_hash": item.get("approval_token_hash"),
        "approval_token_included": False,
        "router_performs_real_execution": False,
        "side_effects_performed_by_router": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "blockers": item.get("blockers", [])
    }


def compute_metrics(routes: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}

    for item in routes:
        status = item.get("status", "unknown")
        target = item.get("route_target", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1

    return {
        "route_count": len(routes),
        "validation_count": len(validations),
        "ready_route_count": status_counts.get("ready_for_allowlisted_executor", 0),
        "blocked_route_count": status_counts.get("blocked", 0),
        "real_execution_by_router_count": 0,
        "side_effect_by_router_count": 0,
        "external_send_count": 0,
        "external_publish_count": 0,
        "status_counts": status_counts,
        "target_counts": target_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    routes = [safe_route_for_report(item) for item in reversed(state.get("routes", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(routes, validations)

    report = {
        "ok": True,
        "checkpoint": "048",
        "module": "k_os_agent_safe_execution_router_core",
        "status": "audit_generated",
        "generated_at": now(),
        "router_state_path": "local_secrets/k_os_safe_execution_router/agent_safe_execution_router_state.json",
        "router_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "router_performs_real_execution": False,
        "side_effects_performed_by_router": False,
        "allowlist_only": True,
        "approval_decision_available": APPROVAL_DECISION.exists(),
        "approval_validation_available": APPROVAL_VALIDATION.exists(),
        "approval_state_available_local_only": APPROVAL_STATE.exists(),
        "dry_run_result_available": DRY_RUN_RESULT.exists(),
        "prompt_package_available": PROMPT_PACKAGE.exists(),
        "execution_plan_available": EXECUTION_PLAN.exists(),
        "permission_matrix_available": PERMISSION_MATRIX.exists(),
        "command_center_report_available": COMMAND_CENTER_REPORT.exists(),
        "agent_runtime_report_available": AGENT_RUNTIME_REPORT.exists(),
        "agent_queue_report_available": AGENT_QUEUE_REPORT.exists(),
        "metrics": metrics,
        "recent_routes": routes,
        "recent_validations": validations,
        "allowed_route_targets": policy.get("allowed_route_targets", []),
        "blocked_route_targets": policy.get("blocked_route_targets", []),
        "required_gates_before_safe_route": policy.get("required_gates_before_safe_route", []),
        "blocked_actions": policy.get("blocked_route_targets", []),
        "next_checkpoint": policy.get("next_checkpoint", "049 - K-Agent Allowlisted Action Executor Core")
    }

    write_report(report)
    event("safe_execution_router.audit_generated", {
        "route_count": metrics.get("route_count")
    })
    return report


def write_route(route: dict[str, Any]) -> None:
    ROUTE_JSON.write_text(json.dumps(route, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Safe Execution Route",
        "",
        "- Route ID: " + str(route.get("route_id")),
        "- Status: " + str(route.get("status")),
        "- OK: " + str(route.get("ok")),
        "- Agent: " + str(route.get("agent_id")),
        "- Task: " + str(route.get("task_id")),
        "- Action: " + str(route.get("action_id")),
        "- Route target: " + str(route.get("route_target")),
        "- Decision ID: " + str(route.get("decision_id")),
        "- Dry Run ID: " + str(route.get("dry_run_id")),
        "- Route hash: " + str(route.get("route_hash")),
        "- Approval token included: " + str(route.get("approval_token_included")),
        "- Router performs real execution: " + str(route.get("router_performs_real_execution")),
        "- Side effects performed by router: " + str(route.get("side_effects_performed_by_router")),
        "- External publish performed: " + str(route.get("external_publish_performed")),
        "",
        "## Blockers",
        ""
    ]

    if route.get("blockers"):
        for item in route.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    ROUTE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Safe Execution Route Validation Report",
        "",
        "- Route ID: " + str(result.get("route_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Route target: " + str(result.get("route_target")),
        "- Agent: " + str(result.get("agent_id")),
        "- Task: " + str(result.get("task_id")),
        "- Action: " + str(result.get("action_id")),
        "- Route hash: " + str(result.get("route_hash")),
        "- Approval token included: " + str(result.get("approval_token_included")),
        "- Router performs real execution: " + str(result.get("router_performs_real_execution")),
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
        "# K-OS Agent Safe Execution Router Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("router_state_committed")),
        "- Allowlist only: " + str(report.get("allowlist_only")),
        "- Router performs real execution: " + str(report.get("router_performs_real_execution")),
        "- Side effects performed by router: " + str(report.get("side_effects_performed_by_router")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent routes", ""])

    if report.get("recent_routes"):
        for item in report.get("recent_routes", [])[:30]:
            lines.append(
                "- " + str(item.get("route_id")) +
                " | status=" + str(item.get("status")) +
                " | target=" + str(item.get("route_target")) +
                " | agent=" + str(item.get("agent_id"))
            )
    else:
        lines.append("- Nenhuma rota registrada.")

    lines.extend(["", "## Allowed route targets", ""])

    for item in report.get("allowed_route_targets", []):
        lines.append("- " + str(item))

    lines.extend(["", "## Required gates before safe route", ""])

    for gate in report.get("required_gates_before_safe_route", []):
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
    parser.add_argument("--mode", choices=["init", "route", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--target", default="")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "route":
        result = create_route(args.target, args.operator, args.reason)

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