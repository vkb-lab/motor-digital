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

POLICY_PATH = ROOT / "config" / "resilience_scenario_planner" / "k_os_agent_resilience_scenario_planner_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_resilience_scenario_planner"
STATE_PATH = STATE_DIR / "agent_resilience_scenario_planner_state.json"

REPORT_DIR = ROOT / "reports" / "resilience_scenario_planner"
MEMORY_DIR = ROOT / "memory" / "resilience_scenario_planner"

LATEST_JSON = REPORT_DIR / "latest_agent_resilience_scenario_planner_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_resilience_scenario_planner_report.md"
PLAN_JSON = REPORT_DIR / "latest_resilience_scenario_plan.json"
PLAN_MD = REPORT_DIR / "latest_resilience_scenario_plan.md"
VALIDATION_JSON = REPORT_DIR / "latest_resilience_scenario_planner_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_resilience_scenario_planner_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

READINESS_MATRIX = ROOT / "reports" / "resilience_readiness" / "latest_resilience_readiness_matrix.json"
READINESS_REPORT = ROOT / "reports" / "resilience_readiness" / "latest_agent_resilience_readiness_report.json"
READINESS_VALIDATION = ROOT / "reports" / "resilience_readiness" / "latest_resilience_readiness_validation_report.json"
RECOVERY_LAYER_CLOSURE = ROOT / "reports" / "recovery_layer_closure" / "latest_recovery_layer_closure.json"
RECOVERY_GOVERNANCE_SUMMARY = ROOT / "reports" / "recovery_governance_summary" / "latest_recovery_governance_summary.json"


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
        raise RuntimeError("Resilience scenario planner policy not found.")
    return data


def ensure_state() -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not STATE_PATH.exists():
        state = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "planner_executes_recovery": False,
            "planner_executes_rollback": False,
            "plans": [],
            "validations": []
        }
        write_json(STATE_PATH, state)

    data = read_json(STATE_PATH)
    if not data:
        raise RuntimeError("Could not load resilience scenario planner state.")
    return data


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


def scenario_template(category: str, priority: int) -> dict[str, Any]:
    labels = {
        "agent_runtime_failure": "Falha de runtime de agente",
        "memory_integrity_risk": "Risco de integridade de memoria",
        "security_firewall_block": "Bloqueio do security firewall",
        "dashboard_unavailable": "Cockpit Streamlit indisponivel",
        "external_api_unavailable": "API externa indisponivel",
        "git_sync_conflict": "Conflito de sincronizacao Git",
        "operator_misconfiguration": "Configuracao incorreta do operador",
        "report_generation_failure": "Falha de geracao de relatorio"
    }

    return {
        "scenario_id": "rsp_" + uuid.uuid4().hex[:10],
        "category": category,
        "title": labels.get(category, category),
        "priority": priority,
        "severity": "high" if priority <= 3 else "medium" if priority <= 6 else "low",
        "trigger_signals": [
            "missing_expected_report",
            "validation_warning",
            "operator_reported_issue",
            "audit_metric_anomaly"
        ],
        "safe_response_steps": [
            "pause_automation_queue",
            "collect_sanitized_evidence",
            "run_local_validation",
            "open_operator_review",
            "prepare_non_destructive_action_plan"
        ],
        "blocked_response_steps": [
            "execute_recovery_now",
            "execute_rollback_now",
            "delete_files",
            "git_reset_hard",
            "git_force_push",
            "execute_shell_command"
        ],
        "requires_operator_review": True,
        "executes_recovery": False,
        "executes_rollback": False,
        "deletes_data": False,
        "modifies_target_files": False,
        "runs_git_reset": False,
        "runs_git_force_push": False,
        "executes_shell_commands": False
    }


def create_plan(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    readiness = read_json(READINESS_MATRIX) or {}
    closure = read_json(RECOVERY_LAYER_CLOSURE) or {}
    governance = read_json(RECOVERY_GOVERNANCE_SUMMARY) or {}

    blockers = []

    if not readiness.get("readiness_hash"):
        blockers.append("resilience_readiness_missing")

    if not closure.get("recovery_layer_closure_hash"):
        blockers.append("recovery_layer_closure_missing")

    if not governance.get("recovery_governance_summary_hash"):
        blockers.append("recovery_governance_summary_missing")

    destructive_zero = (
        closure.get("no_recovery_executed") is True and
        closure.get("no_rollback_executed") is True and
        closure.get("no_data_deleted") is True and
        closure.get("no_target_files_modified") is True and
        closure.get("no_git_reset_executed") is True and
        closure.get("no_git_force_push_executed") is True and
        closure.get("no_shell_executed") is True
    )

    if not destructive_zero:
        blockers.append("destructive_zero_not_confirmed")

    readiness_status = readiness.get("status", "")
    if readiness_status not in ["resilience_ready", "resilience_ready_with_review"]:
        blockers.append("resilience_readiness_not_ready")

    scenario_categories = policy.get("scenario_categories", [])
    scenarios = []
    for index, category in enumerate(scenario_categories, start=1):
        scenarios.append(scenario_template(str(category), index))

    plan_id = "rspf_" + uuid.uuid4().hex[:12]

    if not scenarios:
        status = "planner_blocked"
        blockers.append("scenario_categories_missing")
    elif blockers:
        status = "scenarios_review_required"
    else:
        status = "scenarios_planned"

    plan_body = {
        "plan_id": plan_id,
        "readiness_hash": readiness.get("readiness_hash", ""),
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash", ""),
        "recovery_governance_summary_hash": governance.get("recovery_governance_summary_hash", ""),
        "scenario_count": len(scenarios),
        "scenario_hashes": [stable_hash(item) for item in scenarios]
    }

    plan = {
        "ok": True,
        "checkpoint": "072",
        "module": "k_os_agent_resilience_scenario_planner_core",
        "status": status,
        "plan_id": plan_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "resilience_scenario_planner",
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "readiness_status": readiness_status,
        "readiness_hash": readiness.get("readiness_hash", ""),
        "readiness_percent": readiness.get("readiness_percent", 0),
        "recovery_layer_closure_id": closure.get("recovery_layer_closure_id", ""),
        "recovery_layer_closure_status": closure.get("status", ""),
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash", ""),
        "recovery_governance_summary_hash": governance.get("recovery_governance_summary_hash", ""),
        "destructive_zero_confirmed": destructive_zero,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "blockers": sorted(set(blockers)),
        "scenario_plan_hash": stable_hash(plan_body),
        "planner_executes_recovery": False,
        "planner_executes_rollback": False,
        "planner_deletes_data": False,
        "planner_modifies_target_files": False,
        "planner_runs_git_reset": False,
        "planner_runs_git_force_push": False,
        "planner_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "source_refs": {
            "resilience_readiness": source_ref(READINESS_MATRIX),
            "resilience_readiness_report": source_ref(READINESS_REPORT),
            "resilience_readiness_validation": source_ref(READINESS_VALIDATION),
            "recovery_layer_closure": source_ref(RECOVERY_LAYER_CLOSURE),
            "recovery_governance_summary": source_ref(RECOVERY_GOVERNANCE_SUMMARY)
        },
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "073 - K-Agent Resilience Drill Designer Core")
    }

    state.setdefault("plans", []).append(plan)
    state["plans"] = state["plans"][-300:]
    save_state(state)

    write_plan(plan)

    event("resilience_scenario_planner.plan_created", {
        "plan_id": plan_id,
        "status": status,
        "scenario_count": len(scenarios),
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_plan_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("plans", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    plan = latest_plan_raw()
    blockers = []
    warnings = []

    if not plan:
        blockers.append("resilience_scenario_plan_not_found")
    else:
        required = [
            ("plan_id", "plan_id_missing"),
            ("scenario_plan_hash", "scenario_plan_hash_missing"),
            ("readiness_hash", "readiness_hash_missing")
        ]

        for key, blocker in required:
            if not plan.get(key):
                blockers.append(blocker)

        if int(plan.get("scenario_count", 0) or 0) <= 0:
            blockers.append("scenario_count_zero")

        destructive_keys = [
            "planner_executes_recovery",
            "planner_executes_rollback",
            "planner_deletes_data",
            "planner_modifies_target_files",
            "planner_runs_git_reset",
            "planner_runs_git_force_push",
            "planner_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if plan.get(key) is True:
                blockers.append(key)

        for scenario in plan.get("scenarios", []):
            for key in [
                "executes_recovery",
                "executes_rollback",
                "deletes_data",
                "modifies_target_files",
                "runs_git_reset",
                "runs_git_force_push",
                "executes_shell_commands"
            ]:
                if scenario.get(key) is True:
                    blockers.append("scenario_" + key)

        if plan.get("status") != "scenarios_planned":
            warnings.append("scenario_plan_requires_operator_review")

        if plan.get("blockers"):
            warnings.append("scenario_plan_contains_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "072",
        "module": "k_os_agent_resilience_scenario_planner_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "plan_id": plan.get("plan_id") if plan else "",
        "plan_status": plan.get("status") if plan else "",
        "scenario_plan_hash": plan.get("scenario_plan_hash") if plan else "",
        "scenario_count": plan.get("scenario_count") if plan else 0,
        "planner_executes_recovery": False,
        "planner_executes_rollback": False,
        "planner_deletes_data": False,
        "planner_modifies_target_files": False,
        "planner_runs_git_reset": False,
        "planner_runs_git_force_push": False,
        "planner_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if plan and len(blockers) == 0:
        plan["validated_at"] = validation["generated_at"]
        plan["validated"] = True

    save_state(state)
    write_validation(validation)

    event("resilience_scenario_planner.validation_completed", {
        "plan_id": validation.get("plan_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_plan(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan_id": item.get("plan_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "readiness_status": item.get("readiness_status"),
        "readiness_percent": item.get("readiness_percent"),
        "scenario_count": item.get("scenario_count"),
        "scenario_plan_hash": item.get("scenario_plan_hash"),
        "destructive_zero_confirmed": item.get("destructive_zero_confirmed"),
        "planner_executes_recovery": False,
        "planner_executes_rollback": False,
        "planner_deletes_data": False,
        "planner_modifies_target_files": False,
        "planner_runs_git_reset": False,
        "planner_runs_git_force_push": False,
        "planner_executes_shell_commands": False,
        "blocker_count": len(item.get("blockers", []))
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    plans = [safe_plan(item) for item in reversed(state.get("plans", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]

    metrics = {
        "plan_count": len(plans),
        "validation_count": len(validations),
        "scenarios_planned_count": len([x for x in plans if x.get("status") == "scenarios_planned"]),
        "scenarios_review_required_count": len([x for x in plans if x.get("status") == "scenarios_review_required"]),
        "planner_blocked_count": len([x for x in plans if x.get("status") == "planner_blocked"]),
        "recovery_execution_count": 0,
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0
    }

    report = {
        "ok": True,
        "checkpoint": "072",
        "module": "k_os_agent_resilience_scenario_planner_core",
        "status": "audit_generated",
        "generated_at": now(),
        "state_path": "local_secrets/k_os_resilience_scenario_planner/agent_resilience_scenario_planner_state.json",
        "state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "planner_executes_recovery": False,
        "planner_executes_rollback": False,
        "planner_deletes_data": False,
        "planner_modifies_target_files": False,
        "planner_runs_git_reset": False,
        "planner_runs_git_force_push": False,
        "planner_executes_shell_commands": False,
        "metrics": metrics,
        "recent_plans": plans,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "073 - K-Agent Resilience Drill Designer Core")
    }

    write_report(report)
    event("resilience_scenario_planner.audit_generated", {
        "plan_count": metrics.get("plan_count")
    })
    return report


def write_plan(plan: dict[str, Any]) -> None:
    PLAN_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Scenario Plan",
        "",
        "- Plan ID: " + str(plan.get("plan_id")),
        "- Status: " + str(plan.get("status")),
        "- Scenario count: " + str(plan.get("scenario_count")),
        "- Hash: " + str(plan.get("scenario_plan_hash")),
        "- Readiness status: " + str(plan.get("readiness_status")),
        "- Readiness percent: " + str(plan.get("readiness_percent")),
        "- Destructive zero confirmed: " + str(plan.get("destructive_zero_confirmed")),
        "- Executes recovery: False",
        "- Executes rollback: False",
        "- Executes shell: False",
        "",
        "## Scenarios",
        ""
    ]

    for item in plan.get("scenarios", []):
        lines.append(
            "- " + str(item.get("scenario_id")) +
            " | " + str(item.get("category")) +
            " | severity=" + str(item.get("severity")) +
            " | review=" + str(item.get("requires_operator_review"))
        )

    lines.extend(["", "## Blockers", ""])

    if plan.get("blockers"):
        for item in plan.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    PLAN_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Scenario Planner Validation",
        "",
        "- Plan ID: " + str(result.get("plan_id")),
        "- Status: " + str(result.get("status")),
        "- Plan status: " + str(result.get("plan_status")),
        "- Scenario count: " + str(result.get("scenario_count")),
        "- Hash: " + str(result.get("scenario_plan_hash")),
        "- Executes recovery: False",
        "- Executes rollback: False",
        "- Executes shell: False",
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
        "# K-OS Agent Resilience Scenario Planner Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("state_committed")),
        "- Executes recovery: False",
        "- Executes rollback: False",
        "- Deletes data: False",
        "- Modifies target files: False",
        "- Runs git reset: False",
        "- Runs git force push: False",
        "- Executes shell commands: False",
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent plans", ""])

    if report.get("recent_plans"):
        for item in report.get("recent_plans", [])[:30]:
            lines.append(
                "- " + str(item.get("plan_id")) +
                " | status=" + str(item.get("status")) +
                " | scenarios=" + str(item.get("scenario_count")) +
                " | blockers=" + str(item.get("blocker_count"))
            )
    else:
        lines.append("- Nenhum plano.")

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
    parser.add_argument("--mode", choices=["init", "plan", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()
    elif args.mode == "plan":
        result = create_plan(args.operator, args.reason)
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