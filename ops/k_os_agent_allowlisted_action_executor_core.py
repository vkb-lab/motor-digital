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

POLICY_PATH = ROOT / "config" / "allowlisted_action_executor" / "k_os_agent_allowlisted_action_executor_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_allowlisted_action_executor"
STATE_PATH = STATE_DIR / "agent_allowlisted_action_executor_state.json"

REPORT_DIR = ROOT / "reports" / "allowlisted_action_executor"
MEMORY_DIR = ROOT / "memory" / "allowlisted_action_executor"

LATEST_JSON = REPORT_DIR / "latest_agent_allowlisted_action_executor_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_allowlisted_action_executor_report.md"
EXECUTION_JSON = REPORT_DIR / "latest_allowlisted_action_execution.json"
EXECUTION_MD = REPORT_DIR / "latest_allowlisted_action_execution.md"
VALIDATION_JSON = REPORT_DIR / "latest_allowlisted_action_execution_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_allowlisted_action_execution_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

SAFE_ROUTE = ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route.json"
SAFE_ROUTE_VALIDATION = ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route_validation_report.json"
SAFE_ROUTER_REPORT = ROOT / "reports" / "safe_execution_router" / "latest_agent_safe_execution_router_report.json"

APPROVAL_DECISION = ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_decision.json"
DRY_RUN_RESULT = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_result.json"
PROMPT_PACKAGE = ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_package.json"
EXECUTION_PLAN = ROOT / "reports" / "prompt_assembly" / "latest_agent_execution_plan.json"

SECURITY_REPORT = ROOT / "reports" / "security" / "latest_security_firewall_report.json"
COCKPIT_REPORT = ROOT / "reports" / "cockpit" / "latest_executive_cockpit_report.json"
ANALYTICS_REPORT = ROOT / "reports" / "analytics" / "latest_analytics_executive_metrics_report.json"
MEMORY_BUS_REPORT = ROOT / "reports" / "memory_bus" / "latest_memory_event_bus_report.json"
CONTEXT_API_REPORT = ROOT / "reports" / "context_api" / "latest_context_retrieval_api_report.json"
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
        raise RuntimeError("Allowlisted Action Executor policy not found.")
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
            "arbitrary_command_execution_allowed": False,
            "executions": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load allowlisted executor state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def load_safe_route() -> dict[str, Any]:
    data = read_json(SAFE_ROUTE)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "route_id": "",
        "route_target": "safe_internal_noop",
        "agent_id": "k_atlas_engineer",
        "task_id": "manual_allowlisted_execution_task",
        "action_id": "safe_internal_noop",
        "route_hash": "",
        "approval_token_hash": "",
        "dry_run_evidence_hash": "",
        "blockers": ["safe_route_missing"]
    }


def load_safe_route_validation() -> dict[str, Any]:
    data = read_json(SAFE_ROUTE_VALIDATION)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "route_id": "",
        "route_target": "",
        "blockers": ["safe_route_validation_missing"]
    }


def report_summary(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if not data or data.get("_read_error"):
        return {
            "available": False,
            "path": str(path).replace(str(ROOT) + "\\", "").replace(str(ROOT) + "/", ""),
            "status": "missing",
            "hash": ""
        }

    keys = list(data.keys())
    safe = {
        "available": True,
        "path": str(path).replace(str(ROOT) + "\\", "").replace(str(ROOT) + "/", ""),
        "status": data.get("status", "available"),
        "ok": data.get("ok", None),
        "checkpoint": data.get("checkpoint", ""),
        "module": data.get("module", ""),
        "generated_at": data.get("generated_at", ""),
        "hash": stable_hash(data),
        "top_level_keys": keys[:30]
    }
    return safe


def allowed_action_catalog() -> dict[str, Any]:
    return load_policy().get("allowed_actions", {})


def is_action_allowed(action: str) -> bool:
    return action in allowed_action_catalog()


def action_evidence(action: str) -> dict[str, Any]:
    if action == "safe_internal_noop":
        return {
            "action_result": "noop_completed",
            "side_effect_performed": False,
            "summary": "Ação interna nula executada para validação segura."
        }

    if action == "cockpit_audit":
        return {
            "action_result": "cockpit_audit_recorded",
            "side_effect_performed": False,
            "source_report": report_summary(COCKPIT_REPORT)
        }

    if action == "analytics_audit":
        return {
            "action_result": "analytics_audit_recorded",
            "side_effect_performed": False,
            "source_report": report_summary(ANALYTICS_REPORT)
        }

    if action == "security_scan_staged":
        return {
            "action_result": "security_scan_evidence_recorded",
            "side_effect_performed": False,
            "source_report": report_summary(SECURITY_REPORT)
        }

    if action == "memory_bus_audit":
        return {
            "action_result": "memory_bus_audit_recorded",
            "side_effect_performed": False,
            "source_report": report_summary(MEMORY_BUS_REPORT)
        }

    if action == "context_api_audit":
        return {
            "action_result": "context_api_audit_recorded",
            "side_effect_performed": False,
            "source_report": report_summary(CONTEXT_API_REPORT)
        }

    if action == "agent_runtime_audit":
        return {
            "action_result": "agent_runtime_audit_recorded",
            "side_effect_performed": False,
            "source_report": report_summary(AGENT_RUNTIME_REPORT)
        }

    if action == "agent_queue_audit":
        return {
            "action_result": "agent_queue_audit_recorded",
            "side_effect_performed": False,
            "source_report": report_summary(AGENT_QUEUE_REPORT)
        }

    return {
        "action_result": "blocked_unknown_action",
        "side_effect_performed": False
    }


def gate_check(route: dict[str, Any], validation: dict[str, Any], requested_action: str) -> tuple[str, list[str]]:
    blockers: list[str] = []

    route_action = route.get("route_target") or route.get("action_id") or "safe_internal_noop"
    action = requested_action.strip() if requested_action else route_action

    if not is_action_allowed(action):
        blockers.append("action_not_allowlisted")

    if route.get("route_id") == "":
        blockers.append("safe_route_missing")

    if route.get("status") != "ready_for_allowlisted_executor":
        blockers.append("safe_route_not_ready")

    if route.get("approval_token_included") is True:
        blockers.append("approval_token_leaked")

    if not route.get("approval_token_hash"):
        blockers.append("approval_token_hash_missing")

    if not route.get("dry_run_evidence_hash"):
        blockers.append("dry_run_evidence_hash_missing")

    if route.get("router_performs_real_execution") is True:
        blockers.append("router_already_performed_real_execution")

    if route.get("side_effects_performed_by_router") is True:
        blockers.append("router_already_performed_side_effect")

    if validation.get("ok") is not True:
        blockers.append("safe_route_validation_not_ok")

    if validation.get("status") != "validated":
        blockers.append("safe_route_validation_status_not_validated")

    if validation.get("route_id") and route.get("route_id") and validation.get("route_id") != route.get("route_id"):
        blockers.append("safe_route_validation_id_mismatch")

    if action.startswith("external_"):
        blockers.append("external_action_blocked")

    blocked_names = {
        "run_arbitrary_command",
        "execute_shell",
        "send_external_message",
        "publish_external_content",
        "call_external_provider",
        "delete_file",
        "delete_memory",
        "export_secret",
        "export_raw_memory",
        "charge_payment",
        "send_customer_message"
    }

    if action in blocked_names:
        blockers.append("action_explicitly_blocked")

    return action, blockers


def execute_action(action: str, operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    route = load_safe_route()
    validation = load_safe_route_validation()

    final_action, blockers = gate_check(route, validation, action)

    pre_evidence = {
        "created_at": now(),
        "route_id": route.get("route_id", ""),
        "route_hash": route.get("route_hash", ""),
        "approval_token_hash": route.get("approval_token_hash", ""),
        "dry_run_evidence_hash": route.get("dry_run_evidence_hash", ""),
        "action": final_action,
        "allowlisted": is_action_allowed(final_action),
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "arbitrary_command_execution_allowed": False,
        "shell_command_execution_allowed": False
    }

    action_result = {}
    if not blockers:
        action_result = action_evidence(final_action)

    execution_id = "exec_" + uuid.uuid4().hex[:12]

    post_evidence = {
        "created_at": now(),
        "execution_id": execution_id,
        "action": final_action,
        "action_result": action_result.get("action_result", "blocked"),
        "side_effect_performed": action_result.get("side_effect_performed", False),
        "external_send_performed": False,
        "external_publish_performed": False,
        "arbitrary_command_executed": False,
        "shell_command_executed": False
    }

    execution_body = {
        "pre_evidence": pre_evidence,
        "post_evidence": post_evidence,
        "action_result": action_result,
        "blockers": blockers
    }

    execution = {
        "ok": len(blockers) == 0,
        "checkpoint": "049",
        "module": "k_os_agent_allowlisted_action_executor_core",
        "status": "executed" if len(blockers) == 0 else "blocked",
        "execution_id": execution_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "allowlisted_action_execution",
        "agent_id": route.get("agent_id", "k_atlas_engineer"),
        "task_id": route.get("task_id", "manual_allowlisted_execution_task"),
        "action_id": route.get("action_id", final_action),
        "route_id": route.get("route_id", ""),
        "route_target": route.get("route_target", ""),
        "executed_action": final_action,
        "action_type": allowed_action_catalog().get(final_action, {}).get("type", "unknown"),
        "route_hash": route.get("route_hash", ""),
        "approval_token_hash": route.get("approval_token_hash", ""),
        "approval_token_included": False,
        "dry_run_evidence_hash": route.get("dry_run_evidence_hash", ""),
        "pre_execution_evidence_hash": stable_hash(pre_evidence),
        "post_execution_evidence_hash": stable_hash(post_evidence),
        "execution_evidence_hash": stable_hash(execution_body),
        "arbitrary_command_executed": False,
        "shell_command_executed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "external_provider_called": False,
        "side_effect_performed": action_result.get("side_effect_performed", False) if not blockers else False,
        "action_result": action_result,
        "blockers": blockers,
        "required_gates_before_action_execution": policy.get("required_gates_before_action_execution", []),
        "next_action": "execution_result_ledger" if len(blockers) == 0 else "resolve_blockers"
    }

    state.setdefault("executions", []).append(execution)
    state["executions"] = state["executions"][-300:]
    save_state(state)

    write_execution(execution)

    event("allowlisted_action_executor.execution_completed", {
        "execution_id": execution_id,
        "executed_action": final_action,
        "ok": execution.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def latest_execution_raw() -> dict[str, Any] | None:
    state = ensure_state()
    executions = state.get("executions", [])
    if not executions:
        return None
    return executions[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    execution = latest_execution_raw()
    blockers = []
    warnings = []

    if not execution:
        blockers.append("execution_not_found")
    else:
        if execution.get("status") != "executed":
            blockers.append("execution_not_completed")

        if not execution.get("execution_evidence_hash"):
            blockers.append("execution_evidence_hash_missing")

        if not execution.get("pre_execution_evidence_hash"):
            blockers.append("pre_execution_evidence_hash_missing")

        if not execution.get("post_execution_evidence_hash"):
            blockers.append("post_execution_evidence_hash_missing")

        if execution.get("approval_token_included") is True:
            blockers.append("approval_token_leaked")

        if execution.get("arbitrary_command_executed") is True:
            blockers.append("arbitrary_command_executed")

        if execution.get("shell_command_executed") is True:
            blockers.append("shell_command_executed")

        if execution.get("external_send_performed") is True:
            blockers.append("external_send_performed")

        if execution.get("external_publish_performed") is True:
            blockers.append("external_publish_performed")

        if execution.get("external_provider_called") is True:
            blockers.append("external_provider_called")

        if not is_action_allowed(execution.get("executed_action", "")):
            blockers.append("executed_action_not_allowlisted")

        if execution.get("side_effect_performed") is True:
            warnings.append("allowlisted_action_reported_side_effect")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "049",
        "module": "k_os_agent_allowlisted_action_executor_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "execution_id": execution.get("execution_id") if execution else "",
        "executed_action": execution.get("executed_action") if execution else "",
        "route_id": execution.get("route_id") if execution else "",
        "agent_id": execution.get("agent_id") if execution else "",
        "task_id": execution.get("task_id") if execution else "",
        "execution_evidence_hash": execution.get("execution_evidence_hash") if execution else "",
        "approval_token_included": False,
        "arbitrary_command_executed": False,
        "shell_command_executed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "external_provider_called": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if execution and len(blockers) == 0:
        execution["validated_at"] = validation["generated_at"]
        execution["validated"] = True

    save_state(state)
    write_validation(validation)

    event("allowlisted_action_executor.validation_completed", {
        "execution_id": validation.get("execution_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_execution_for_report(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "execution_id": item.get("execution_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "agent_id": item.get("agent_id"),
        "task_id": item.get("task_id"),
        "action_id": item.get("action_id"),
        "route_id": item.get("route_id"),
        "executed_action": item.get("executed_action"),
        "action_type": item.get("action_type"),
        "execution_evidence_hash": item.get("execution_evidence_hash"),
        "approval_token_hash": item.get("approval_token_hash"),
        "approval_token_included": False,
        "arbitrary_command_executed": False,
        "shell_command_executed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "external_provider_called": False,
        "side_effect_performed": item.get("side_effect_performed", False),
        "blockers": item.get("blockers", [])
    }


def compute_metrics(executions: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}

    for item in executions:
        status = item.get("status", "unknown")
        action = item.get("executed_action", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        action_counts[action] = action_counts.get(action, 0) + 1

    return {
        "execution_count": len(executions),
        "validation_count": len(validations),
        "executed_count": status_counts.get("executed", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "arbitrary_command_count": 0,
        "shell_command_count": 0,
        "external_send_count": 0,
        "external_publish_count": 0,
        "external_provider_call_count": 0,
        "status_counts": status_counts,
        "action_counts": action_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    executions = [safe_execution_for_report(item) for item in reversed(state.get("executions", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(executions, validations)

    report = {
        "ok": True,
        "checkpoint": "049",
        "module": "k_os_agent_allowlisted_action_executor_core",
        "status": "audit_generated",
        "generated_at": now(),
        "executor_state_path": "local_secrets/k_os_allowlisted_action_executor/agent_allowlisted_action_executor_state.json",
        "executor_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "arbitrary_command_execution_allowed": False,
        "shell_command_execution_allowed": False,
        "external_provider_call_allowed": False,
        "allowlist_only": True,
        "safe_route_available": SAFE_ROUTE.exists(),
        "safe_route_validation_available": SAFE_ROUTE_VALIDATION.exists(),
        "safe_router_report_available": SAFE_ROUTER_REPORT.exists(),
        "approval_decision_available": APPROVAL_DECISION.exists(),
        "dry_run_result_available": DRY_RUN_RESULT.exists(),
        "prompt_package_available": PROMPT_PACKAGE.exists(),
        "execution_plan_available": EXECUTION_PLAN.exists(),
        "metrics": metrics,
        "recent_executions": executions,
        "recent_validations": validations,
        "allowed_actions": list(policy.get("allowed_actions", {}).keys()),
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_action_execution": policy.get("required_gates_before_action_execution", []),
        "next_checkpoint": policy.get("next_checkpoint", "050 - K-Agent Execution Result Ledger Core")
    }

    write_report(report)
    event("allowlisted_action_executor.audit_generated", {
        "execution_count": metrics.get("execution_count")
    })
    return report


def write_execution(execution: dict[str, Any]) -> None:
    EXECUTION_JSON.write_text(json.dumps(execution, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Allowlisted Action Execution",
        "",
        "- Execution ID: " + str(execution.get("execution_id")),
        "- Status: " + str(execution.get("status")),
        "- OK: " + str(execution.get("ok")),
        "- Agent: " + str(execution.get("agent_id")),
        "- Task: " + str(execution.get("task_id")),
        "- Route ID: " + str(execution.get("route_id")),
        "- Executed action: " + str(execution.get("executed_action")),
        "- Action type: " + str(execution.get("action_type")),
        "- Evidence hash: " + str(execution.get("execution_evidence_hash")),
        "- Approval token included: " + str(execution.get("approval_token_included")),
        "- Arbitrary command executed: " + str(execution.get("arbitrary_command_executed")),
        "- Shell command executed: " + str(execution.get("shell_command_executed")),
        "- External publish performed: " + str(execution.get("external_publish_performed")),
        "- Side effect performed: " + str(execution.get("side_effect_performed")),
        "",
        "## Blockers",
        ""
    ]

    if execution.get("blockers"):
        for item in execution.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    EXECUTION_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Allowlisted Action Execution Validation",
        "",
        "- Execution ID: " + str(result.get("execution_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Executed action: " + str(result.get("executed_action")),
        "- Route ID: " + str(result.get("route_id")),
        "- Evidence hash: " + str(result.get("execution_evidence_hash")),
        "- Approval token included: " + str(result.get("approval_token_included")),
        "- Arbitrary command executed: " + str(result.get("arbitrary_command_executed")),
        "- Shell command executed: " + str(result.get("shell_command_executed")),
        "- External publish performed: " + str(result.get("external_publish_performed")),
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
        "# K-OS Agent Allowlisted Action Executor Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("executor_state_committed")),
        "- Allowlist only: " + str(report.get("allowlist_only")),
        "- Arbitrary command allowed: " + str(report.get("arbitrary_command_execution_allowed")),
        "- Shell command allowed: " + str(report.get("shell_command_execution_allowed")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent executions", ""])

    if report.get("recent_executions"):
        for item in report.get("recent_executions", [])[:30]:
            lines.append(
                "- " + str(item.get("execution_id")) +
                " | status=" + str(item.get("status")) +
                " | action=" + str(item.get("executed_action")) +
                " | agent=" + str(item.get("agent_id"))
            )
    else:
        lines.append("- Nenhuma execução registrada.")

    lines.extend(["", "## Allowed actions", ""])

    for item in report.get("allowed_actions", []):
        lines.append("- " + str(item))

    lines.extend(["", "## Required gates before action execution", ""])

    for gate in report.get("required_gates_before_action_execution", []):
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
    parser.add_argument("--mode", choices=["init", "execute", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--action", default="")
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "execute":
        result = execute_action(args.action, args.operator, args.reason)

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