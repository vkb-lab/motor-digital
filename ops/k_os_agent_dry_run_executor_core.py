# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "dry_run_executor" / "k_os_agent_dry_run_executor_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_dry_run_executor"
STATE_PATH = STATE_DIR / "agent_dry_run_executor_state.json"

REPORT_DIR = ROOT / "reports" / "dry_run_executor"
MEMORY_DIR = ROOT / "memory" / "dry_run_executor"

LATEST_JSON = REPORT_DIR / "latest_agent_dry_run_executor_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_dry_run_executor_report.md"
RESULT_JSON = REPORT_DIR / "latest_agent_dry_run_result.json"
RESULT_MD = REPORT_DIR / "latest_agent_dry_run_result.md"
VALIDATION_JSON = REPORT_DIR / "latest_agent_dry_run_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_agent_dry_run_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

PROMPT_PACKAGE_REPORT = ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_package.json"
EXECUTION_PLAN_REPORT = ROOT / "reports" / "prompt_assembly" / "latest_agent_execution_plan.json"
PROMPT_ASSEMBLY_REPORT = ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_assembly_report.json"
CONTEXT_INJECTION_REPORT = ROOT / "reports" / "context_injection" / "latest_agent_context_injection_report.json"
AGENT_QUEUE_REPORT = ROOT / "reports" / "agent_queue" / "latest_agent_orchestration_queue_report.json"
AGENT_RUNTIME_REPORT = ROOT / "reports" / "agent_runtime" / "latest_agent_runtime_supervisor_report.json"
COMMAND_CENTER_REPORT = ROOT / "reports" / "command_center" / "latest_command_center_action_router_report.json"

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_\-]{20,}",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"[PRIVATE_KEY_PATTERN_REDACTED]",
    r"api[_-]?key\s*[:=]",
    r"secret\s*[:=]",
    r"token\s*[:=]",
    r"password\s*[:=]"
]


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
        raise RuntimeError("Dry Run Executor policy not found.")
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
            "real_execution_enabled": False,
            "dry_runs": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load Dry Run Executor state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def has_secret_marker(data: Any) -> bool:
    raw = json.dumps(data, ensure_ascii=False)
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, raw, flags=re.IGNORECASE):
            return True
    return False


def has_raw_payload_marker(data: Any) -> bool:
    raw = json.dumps(data, ensure_ascii=False).lower()
    markers = [
        '"raw_payload_included": true',
        '"raw_report_included": true',
        '"raw_payload":',
        '"raw_report":',
        '"api_key":',
        '"password":'
    ]
    return any(marker in raw for marker in markers)


def load_prompt_package() -> dict[str, Any]:
    data = read_json(PROMPT_PACKAGE_REPORT)
    if data and not data.get("_read_error"):
        return data

    return {
        "ok": False,
        "status": "missing",
        "prompt_package_id": "",
        "agent_id": "k_atlas_engineer",
        "task_id": "manual_dry_run_task",
        "action_id": "cockpit_audit",
        "prompt_package_hash": "",
        "execution_plan_id": "",
        "execution_plan_hash": "",
        "blockers": ["prompt_package_missing"],
        "raw_payload_included": False,
        "secret_included": False
    }


def load_execution_plan() -> dict[str, Any]:
    data = read_json(EXECUTION_PLAN_REPORT)
    if data and not data.get("_read_error"):
        return data

    return {
        "plan_id": "",
        "agent_id": "k_atlas_engineer",
        "task_id": "manual_dry_run_task",
        "action_id": "cockpit_audit",
        "objective": "Plano ausente.",
        "dry_run": True,
        "steps": [],
        "blocked_actions": ["execute_without_plan"]
    }


def simulate_step(step: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": step.get("step"),
        "name": step.get("name", "unnamed_step"),
        "description": step.get("description", ""),
        "gate": step.get("gate", ""),
        "simulation_status": "simulated",
        "side_effect_performed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "result": "Dry-run simulation only. No real action executed."
    }


def execute_dry_run(reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    prompt_package = load_prompt_package()
    execution_plan = load_execution_plan()

    blockers = []
    warnings = []

    if not prompt_package.get("prompt_package_id"):
        blockers.append("prompt_package_missing")

    if prompt_package.get("status") not in {"assembled", "validated"}:
        blockers.append("prompt_package_not_validated_or_assembled")

    if not prompt_package.get("prompt_package_hash"):
        blockers.append("prompt_package_hash_missing")

    if not execution_plan.get("plan_id"):
        blockers.append("execution_plan_missing")

    if not execution_plan.get("steps"):
        blockers.append("execution_plan_steps_missing")

    if has_raw_payload_marker(prompt_package) or has_raw_payload_marker(execution_plan):
        blockers.append("raw_payload_marker_detected")

    if has_secret_marker(prompt_package) or has_secret_marker(execution_plan):
        blockers.append("secret_marker_detected")

    if prompt_package.get("external_send_enabled") is True:
        blockers.append("external_send_enabled_on_prompt")

    if prompt_package.get("external_publish_enabled") is True:
        blockers.append("external_publish_enabled_on_prompt")

    simulated_steps = []
    if not blockers:
        for step in execution_plan.get("steps", []):
            simulated_steps.append(simulate_step(step))

    dry_run_id = "dry_" + uuid.uuid4().hex[:12]

    result_body = {
        "prompt_package_hash": prompt_package.get("prompt_package_hash", ""),
        "execution_plan_hash": prompt_package.get("execution_plan_hash", execution_plan.get("plan_id", "")),
        "steps": simulated_steps,
        "blockers": blockers
    }

    result = {
        "ok": len(blockers) == 0,
        "checkpoint": "046",
        "module": "k_os_agent_dry_run_executor_core",
        "status": "dry_run_completed" if len(blockers) == 0 else "blocked",
        "dry_run_id": dry_run_id,
        "generated_at": now(),
        "agent_id": prompt_package.get("agent_id", execution_plan.get("agent_id", "")),
        "task_id": prompt_package.get("task_id", execution_plan.get("task_id", "")),
        "action_id": prompt_package.get("action_id", execution_plan.get("action_id", "")),
        "prompt_package_id": prompt_package.get("prompt_package_id", ""),
        "execution_plan_id": execution_plan.get("plan_id", ""),
        "reason": reason or "dry_run_execution",
        "dry_run": True,
        "real_execution_performed": False,
        "side_effects_performed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "command_center_called": False,
        "simulated_step_count": len(simulated_steps),
        "simulated_steps": simulated_steps,
        "blockers": blockers,
        "warnings": warnings,
        "evidence_hash": stable_hash(result_body),
        "prompt_package_hash": prompt_package.get("prompt_package_hash", ""),
        "execution_plan_hash": prompt_package.get("execution_plan_hash", stable_hash(execution_plan)),
        "required_gates_before_real_execution": policy.get("required_gates_before_real_execution", []),
        "next_action": "operator_review_before_real_execution" if len(blockers) == 0 else "resolve_blockers"
    }

    state.setdefault("dry_runs", []).append(result)
    state["dry_runs"] = state["dry_runs"][-300:]
    save_state(state)

    write_result(result)

    event("dry_run_executor.dry_run_completed", {
        "dry_run_id": dry_run_id,
        "ok": result.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def latest_dry_run_raw() -> dict[str, Any] | None:
    state = ensure_state()
    items = state.get("dry_runs", [])
    if not items:
        return None
    return items[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    result = latest_dry_run_raw()

    blockers = []
    warnings = []

    if not result:
        blockers.append("dry_run_result_not_found")
    else:
        if result.get("dry_run") is not True:
            blockers.append("dry_run_flag_missing")

        if result.get("real_execution_performed") is True:
            blockers.append("real_execution_performed")

        if result.get("side_effects_performed") is True:
            blockers.append("side_effects_performed")

        if result.get("external_send_performed") is True:
            blockers.append("external_send_performed")

        if result.get("external_publish_performed") is True:
            blockers.append("external_publish_performed")

        if not result.get("evidence_hash"):
            blockers.append("evidence_hash_missing")

        if result.get("status") != "dry_run_completed":
            blockers.append("dry_run_not_completed")

        if result.get("simulated_step_count", 0) < 1:
            warnings.append("no_steps_simulated")

        if has_raw_payload_marker(result):
            blockers.append("raw_payload_marker_detected")

        if has_secret_marker(result):
            blockers.append("secret_marker_detected")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "046",
        "module": "k_os_agent_dry_run_executor_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "dry_run_id": result.get("dry_run_id") if result else "",
        "agent_id": result.get("agent_id") if result else "",
        "task_id": result.get("task_id") if result else "",
        "action_id": result.get("action_id") if result else "",
        "evidence_hash": result.get("evidence_hash") if result else "",
        "blockers": blockers,
        "warnings": warnings,
        "dry_run": True,
        "real_execution_performed": False,
        "side_effects_performed": False,
        "external_send_performed": False,
        "external_publish_performed": False
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if result and len(blockers) == 0:
        result["status"] = "ready_for_review"
        result["validated_at"] = validation["generated_at"]
        result["next_action"] = "real_execution_approval_gate"

    save_state(state)
    write_validation(validation)

    event("dry_run_executor.validation_completed", {
        "dry_run_id": validation.get("dry_run_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_dry_run(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "dry_run_id": item.get("dry_run_id"),
        "generated_at": item.get("generated_at"),
        "agent_id": item.get("agent_id"),
        "task_id": item.get("task_id"),
        "action_id": item.get("action_id"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "dry_run": True,
        "real_execution_performed": False,
        "side_effects_performed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "simulated_step_count": item.get("simulated_step_count", 0),
        "evidence_hash": item.get("evidence_hash", ""),
        "prompt_package_hash": item.get("prompt_package_hash", ""),
        "execution_plan_hash": item.get("execution_plan_hash", ""),
        "blockers": item.get("blockers", [])
    }


def compute_metrics(dry_runs: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    agent_counts: dict[str, int] = {}

    for item in dry_runs:
        status = item.get("status", "unknown")
        agent = item.get("agent_id", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        agent_counts[agent] = agent_counts.get(agent, 0) + 1

    return {
        "dry_run_count": len(dry_runs),
        "validation_count": len(validations),
        "completed_count": status_counts.get("dry_run_completed", 0),
        "ready_for_review_count": status_counts.get("ready_for_review", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "real_execution_count": 0,
        "side_effect_count": 0,
        "external_send_count": 0,
        "external_publish_count": 0,
        "status_counts": status_counts,
        "agent_counts": agent_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    dry_runs = [safe_dry_run(item) for item in reversed(state.get("dry_runs", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(dry_runs, validations)

    report = {
        "ok": True,
        "checkpoint": "046",
        "module": "k_os_agent_dry_run_executor_core",
        "status": "audit_generated",
        "generated_at": now(),
        "dry_run_state_path": "local_secrets/k_os_dry_run_executor/agent_dry_run_executor_state.json",
        "dry_run_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "real_execution_enabled": False,
        "side_effects_allowed": False,
        "dry_run_default": True,
        "prompt_package_report_available": PROMPT_PACKAGE_REPORT.exists(),
        "execution_plan_report_available": EXECUTION_PLAN_REPORT.exists(),
        "prompt_assembly_report_available": PROMPT_ASSEMBLY_REPORT.exists(),
        "context_injection_report_available": CONTEXT_INJECTION_REPORT.exists(),
        "agent_queue_report_available": AGENT_QUEUE_REPORT.exists(),
        "agent_runtime_report_available": AGENT_RUNTIME_REPORT.exists(),
        "command_center_report_available": COMMAND_CENTER_REPORT.exists(),
        "metrics": metrics,
        "recent_dry_runs": dry_runs,
        "recent_validations": validations,
        "required_gates_before_real_execution": policy.get("required_gates_before_real_execution", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "047 - K-Agent Real Execution Approval Gate Core")
    }

    write_report(report)
    event("dry_run_executor.audit_generated", {
        "dry_run_count": metrics.get("dry_run_count")
    })
    return report


def write_result(result: dict[str, Any]) -> None:
    RESULT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Dry Run Result",
        "",
        "- Dry Run ID: " + str(result.get("dry_run_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Agent: " + str(result.get("agent_id")),
        "- Task: " + str(result.get("task_id")),
        "- Action: " + str(result.get("action_id")),
        "- Simulated steps: " + str(result.get("simulated_step_count")),
        "- Evidence hash: " + str(result.get("evidence_hash")),
        "- Real execution performed: " + str(result.get("real_execution_performed")),
        "- Side effects performed: " + str(result.get("side_effects_performed")),
        "- External publish performed: " + str(result.get("external_publish_performed")),
        "",
        "## Simulated steps",
        ""
    ]

    if result.get("simulated_steps"):
        for item in result.get("simulated_steps", []):
            lines.append(
                "- " + str(item.get("step")) +
                " | " + str(item.get("name")) +
                " | status=" + str(item.get("simulation_status")) +
                " | gate=" + str(item.get("gate"))
            )
    else:
        lines.append("- Nenhum passo simulado.")

    lines.extend(["", "## Blockers", ""])

    if result.get("blockers"):
        for item in result.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Dry Run Validation Report",
        "",
        "- Dry Run ID: " + str(result.get("dry_run_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Agent: " + str(result.get("agent_id")),
        "- Task: " + str(result.get("task_id")),
        "- Action: " + str(result.get("action_id")),
        "- Evidence hash: " + str(result.get("evidence_hash")),
        "- Real execution performed: " + str(result.get("real_execution_performed")),
        "- Side effects performed: " + str(result.get("side_effects_performed")),
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
        "# K-OS Agent Dry Run Executor Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("dry_run_state_committed")),
        "- Real execution enabled: " + str(report.get("real_execution_enabled")),
        "- Side effects allowed: " + str(report.get("side_effects_allowed")),
        "- Dry-run default: " + str(report.get("dry_run_default")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent dry-runs", ""])

    if report.get("recent_dry_runs"):
        for item in report.get("recent_dry_runs", [])[:30]:
            lines.append(
                "- " + str(item.get("dry_run_id")) +
                " | agent=" + str(item.get("agent_id")) +
                " | task=" + str(item.get("task_id")) +
                " | status=" + str(item.get("status")) +
                " | steps=" + str(item.get("simulated_step_count"))
            )
    else:
        lines.append("- Nenhum dry-run registrado.")

    lines.extend(["", "## Required gates before real execution", ""])

    for gate in report.get("required_gates_before_real_execution", []):
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
    parser.add_argument("--mode", choices=["init", "execute", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "execute":
        result = execute_dry_run(args.reason)

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
