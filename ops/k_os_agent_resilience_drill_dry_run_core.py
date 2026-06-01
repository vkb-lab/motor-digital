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

POLICY_PATH = ROOT / "config" / "resilience_drill_dry_run" / "k_os_agent_resilience_drill_dry_run_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_resilience_drill_dry_run"
STATE_PATH = STATE_DIR / "agent_resilience_drill_dry_run_state.json"

REPORT_DIR = ROOT / "reports" / "resilience_drill_dry_run"
MEMORY_DIR = ROOT / "memory" / "resilience_drill_dry_run"

LATEST_JSON = REPORT_DIR / "latest_agent_resilience_drill_dry_run_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_resilience_drill_dry_run_report.md"
DRY_RUN_JSON = REPORT_DIR / "latest_resilience_drill_dry_run.json"
DRY_RUN_MD = REPORT_DIR / "latest_resilience_drill_dry_run.md"
VALIDATION_JSON = REPORT_DIR / "latest_resilience_drill_dry_run_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_resilience_drill_dry_run_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

DRILL_DESIGN = ROOT / "reports" / "resilience_drill_designer" / "latest_resilience_drill_design.json"
DRILL_DESIGN_REPORT = ROOT / "reports" / "resilience_drill_designer" / "latest_agent_resilience_drill_designer_report.json"
DRILL_DESIGN_VALIDATION = ROOT / "reports" / "resilience_drill_designer" / "latest_resilience_drill_designer_validation_report.json"
SCENARIO_PLAN = ROOT / "reports" / "resilience_scenario_planner" / "latest_resilience_scenario_plan.json"
READINESS_MATRIX = ROOT / "reports" / "resilience_readiness" / "latest_resilience_readiness_matrix.json"
RECOVERY_LAYER_CLOSURE = ROOT / "reports" / "recovery_layer_closure" / "latest_recovery_layer_closure.json"


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
        raise RuntimeError("Resilience drill dry run policy not found.")
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
            "dry_run_executes_drill": False,
            "dry_run_executes_recovery": False,
            "dry_run_executes_rollback": False,
            "dry_runs": [],
            "validations": []
        }
        write_json(STATE_PATH, state)

    data = read_json(STATE_PATH)
    if not data:
        raise RuntimeError("Could not load resilience drill dry run state.")
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


def simulate_drill(drill: dict[str, Any]) -> dict[str, Any]:
    steps = []
    for step in drill.get("drill_steps", []):
        steps.append({
            "step": step.get("step"),
            "name": step.get("name", ""),
            "description": step.get("description", ""),
            "simulated": True,
            "executed": False,
            "executes_drill": False,
            "executes_recovery": False,
            "executes_rollback": False,
            "deletes_data": False,
            "modifies_target_files": False,
            "runs_git_reset": False,
            "runs_git_force_push": False,
            "executes_shell_commands": False,
            "destructive": False
        })

    if not steps:
        steps = [
            {
                "step": 1,
                "name": "missing_drill_steps_review",
                "description": "Drill has no steps; operator review required.",
                "simulated": True,
                "executed": False,
                "executes_drill": False,
                "executes_recovery": False,
                "executes_rollback": False,
                "deletes_data": False,
                "modifies_target_files": False,
                "runs_git_reset": False,
                "runs_git_force_push": False,
                "executes_shell_commands": False,
                "destructive": False
            }
        ]

    return {
        "drill_id": drill.get("drill_id", ""),
        "category": drill.get("category", ""),
        "title": drill.get("title", ""),
        "severity": drill.get("severity", ""),
        "source_scenario_id": drill.get("source_scenario_id", ""),
        "step_count": len(steps),
        "steps": steps,
        "simulated": True,
        "executed": False,
        "requires_operator_review": True,
        "executes_drill": False,
        "executes_recovery": False,
        "executes_rollback": False,
        "deletes_data": False,
        "modifies_target_files": False,
        "runs_git_reset": False,
        "runs_git_force_push": False,
        "executes_shell_commands": False,
        "simulation_hash": stable_hash({
            "drill_id": drill.get("drill_id", ""),
            "steps": steps
        })
    }


def create_dry_run(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    design = read_json(DRILL_DESIGN) or {}
    scenario_plan = read_json(SCENARIO_PLAN) or {}
    readiness = read_json(READINESS_MATRIX) or {}
    closure = read_json(RECOVERY_LAYER_CLOSURE) or {}

    blockers = []

    if not design.get("drill_design_hash"):
        blockers.append("resilience_drill_design_missing")

    if not scenario_plan.get("scenario_plan_hash"):
        blockers.append("resilience_scenario_plan_missing")

    if not readiness.get("readiness_hash"):
        blockers.append("resilience_readiness_missing")

    if not closure.get("recovery_layer_closure_hash"):
        blockers.append("recovery_layer_closure_missing")

    destructive_design_keys = [
        "designer_executes_drill",
        "designer_executes_recovery",
        "designer_executes_rollback",
        "designer_deletes_data",
        "designer_modifies_target_files",
        "designer_runs_git_reset",
        "designer_runs_git_force_push",
        "designer_executes_shell_commands",
        "raw_payload_included",
        "local_recovery_token_included"
    ]

    for key in destructive_design_keys:
        if design.get(key) is True:
            blockers.append("design_" + key)

    if closure.get("no_recovery_executed") is not True:
        blockers.append("no_recovery_not_confirmed")

    if closure.get("no_rollback_executed") is not True:
        blockers.append("no_rollback_not_confirmed")

    drills = design.get("drills", [])
    if not isinstance(drills, list):
        drills = []

    simulated_drills = []
    for drill in drills:
        simulated_drills.append(simulate_drill(drill))

    if len(simulated_drills) == 0:
        blockers.append("no_drills_available_for_dry_run")

    dry_run_id = "rdrill_" + uuid.uuid4().hex[:12]

    if len(simulated_drills) == 0:
        status = "dry_run_blocked"
    elif blockers:
        status = "dry_run_review_required"
    else:
        status = "dry_run_completed_safe"

    dry_run_body = {
        "dry_run_id": dry_run_id,
        "design_hash": design.get("drill_design_hash", ""),
        "scenario_plan_hash": scenario_plan.get("scenario_plan_hash", ""),
        "readiness_hash": readiness.get("readiness_hash", ""),
        "drill_count": len(simulated_drills),
        "drill_simulation_hashes": [item.get("simulation_hash") for item in simulated_drills]
    }

    record = {
        "ok": True,
        "checkpoint": "074",
        "module": "k_os_agent_resilience_drill_dry_run_core",
        "status": status,
        "dry_run_id": dry_run_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "resilience_drill_dry_run",
        "drill_design_id": design.get("design_id", ""),
        "drill_design_status": design.get("status", ""),
        "drill_design_hash": design.get("drill_design_hash", ""),
        "scenario_plan_id": scenario_plan.get("plan_id", ""),
        "scenario_plan_status": scenario_plan.get("status", ""),
        "scenario_plan_hash": scenario_plan.get("scenario_plan_hash", ""),
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "readiness_status": readiness.get("status", ""),
        "readiness_hash": readiness.get("readiness_hash", ""),
        "recovery_layer_closure_id": closure.get("recovery_layer_closure_id", ""),
        "recovery_layer_closure_status": closure.get("status", ""),
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash", ""),
        "drill_count": len(simulated_drills),
        "simulated_drills": simulated_drills,
        "blockers": sorted(set(blockers)),
        "drill_dry_run_hash": stable_hash(dry_run_body),
        "dry_run_executes_drill": False,
        "dry_run_executes_recovery": False,
        "dry_run_executes_rollback": False,
        "dry_run_deletes_data": False,
        "dry_run_modifies_target_files": False,
        "dry_run_runs_git_reset": False,
        "dry_run_runs_git_force_push": False,
        "dry_run_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "source_refs": {
            "drill_design": source_ref(DRILL_DESIGN),
            "drill_design_report": source_ref(DRILL_DESIGN_REPORT),
            "drill_design_validation": source_ref(DRILL_DESIGN_VALIDATION),
            "scenario_plan": source_ref(SCENARIO_PLAN),
            "readiness_matrix": source_ref(READINESS_MATRIX),
            "recovery_layer_closure": source_ref(RECOVERY_LAYER_CLOSURE)
        },
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "075 - K-Agent Resilience Drill Operator Review Core")
    }

    state.setdefault("dry_runs", []).append(record)
    state["dry_runs"] = state["dry_runs"][-300:]
    save_state(state)

    write_dry_run(record)

    event("resilience_drill_dry_run.created", {
        "dry_run_id": dry_run_id,
        "status": status,
        "drill_count": len(simulated_drills),
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_dry_run_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("dry_runs", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    record = latest_dry_run_raw()
    blockers = []
    warnings = []

    if not record:
        blockers.append("resilience_drill_dry_run_not_found")
    else:
        required = [
            ("dry_run_id", "dry_run_id_missing"),
            ("drill_dry_run_hash", "drill_dry_run_hash_missing"),
            ("drill_design_hash", "drill_design_hash_missing")
        ]

        for key, blocker in required:
            if not record.get(key):
                blockers.append(blocker)

        if int(record.get("drill_count", 0) or 0) <= 0:
            blockers.append("drill_count_zero")

        destructive_keys = [
            "dry_run_executes_drill",
            "dry_run_executes_recovery",
            "dry_run_executes_rollback",
            "dry_run_deletes_data",
            "dry_run_modifies_target_files",
            "dry_run_runs_git_reset",
            "dry_run_runs_git_force_push",
            "dry_run_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if record.get(key) is True:
                blockers.append(key)

        for drill in record.get("simulated_drills", []):
            for key in [
                "executed",
                "executes_drill",
                "executes_recovery",
                "executes_rollback",
                "deletes_data",
                "modifies_target_files",
                "runs_git_reset",
                "runs_git_force_push",
                "executes_shell_commands"
            ]:
                if drill.get(key) is True:
                    blockers.append("simulated_drill_" + key)

            for step in drill.get("steps", []):
                for key in [
                    "executed",
                    "executes_drill",
                    "executes_recovery",
                    "executes_rollback",
                    "deletes_data",
                    "modifies_target_files",
                    "runs_git_reset",
                    "runs_git_force_push",
                    "executes_shell_commands",
                    "destructive"
                ]:
                    if step.get(key) is True:
                        blockers.append("simulated_step_" + key)

        if record.get("status") != "dry_run_completed_safe":
            warnings.append("dry_run_requires_operator_review")

        if record.get("blockers"):
            warnings.append("dry_run_contains_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "074",
        "module": "k_os_agent_resilience_drill_dry_run_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "dry_run_id": record.get("dry_run_id") if record else "",
        "dry_run_status": record.get("status") if record else "",
        "drill_dry_run_hash": record.get("drill_dry_run_hash") if record else "",
        "drill_count": record.get("drill_count") if record else 0,
        "dry_run_executes_drill": False,
        "dry_run_executes_recovery": False,
        "dry_run_executes_rollback": False,
        "dry_run_deletes_data": False,
        "dry_run_modifies_target_files": False,
        "dry_run_runs_git_reset": False,
        "dry_run_runs_git_force_push": False,
        "dry_run_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
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

    event("resilience_drill_dry_run.validation_completed", {
        "dry_run_id": validation.get("dry_run_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_dry_run(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "dry_run_id": item.get("dry_run_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "drill_design_status": item.get("drill_design_status"),
        "scenario_plan_status": item.get("scenario_plan_status"),
        "drill_count": item.get("drill_count"),
        "drill_dry_run_hash": item.get("drill_dry_run_hash"),
        "dry_run_executes_drill": False,
        "dry_run_executes_recovery": False,
        "dry_run_executes_rollback": False,
        "dry_run_deletes_data": False,
        "dry_run_modifies_target_files": False,
        "dry_run_runs_git_reset": False,
        "dry_run_runs_git_force_push": False,
        "dry_run_executes_shell_commands": False,
        "blocker_count": len(item.get("blockers", []))
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    dry_runs = [safe_dry_run(item) for item in reversed(state.get("dry_runs", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]

    metrics = {
        "dry_run_count": len(dry_runs),
        "validation_count": len(validations),
        "dry_run_completed_safe_count": len([x for x in dry_runs if x.get("status") == "dry_run_completed_safe"]),
        "dry_run_review_required_count": len([x for x in dry_runs if x.get("status") == "dry_run_review_required"]),
        "dry_run_blocked_count": len([x for x in dry_runs if x.get("status") == "dry_run_blocked"]),
        "drill_execution_count": 0,
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
        "checkpoint": "074",
        "module": "k_os_agent_resilience_drill_dry_run_core",
        "status": "audit_generated",
        "generated_at": now(),
        "state_path": "local_secrets/k_os_resilience_drill_dry_run/agent_resilience_drill_dry_run_state.json",
        "state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "dry_run_executes_drill": False,
        "dry_run_executes_recovery": False,
        "dry_run_executes_rollback": False,
        "dry_run_deletes_data": False,
        "dry_run_modifies_target_files": False,
        "dry_run_runs_git_reset": False,
        "dry_run_runs_git_force_push": False,
        "dry_run_executes_shell_commands": False,
        "metrics": metrics,
        "recent_dry_runs": dry_runs,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "075 - K-Agent Resilience Drill Operator Review Core")
    }

    write_report(report)
    event("resilience_drill_dry_run.audit_generated", {
        "dry_run_count": metrics.get("dry_run_count")
    })
    return report


def write_dry_run(record: dict[str, Any]) -> None:
    DRY_RUN_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Drill Dry Run",
        "",
        "- Dry Run ID: " + str(record.get("dry_run_id")),
        "- Status: " + str(record.get("status")),
        "- Drill count: " + str(record.get("drill_count")),
        "- Hash: " + str(record.get("drill_dry_run_hash")),
        "- Drill design status: " + str(record.get("drill_design_status")),
        "- Scenario plan status: " + str(record.get("scenario_plan_status")),
        "- Executes drill: False",
        "- Executes recovery: False",
        "- Executes rollback: False",
        "- Executes shell: False",
        "",
        "## Simulated drills",
        ""
    ]

    for item in record.get("simulated_drills", []):
        lines.append(
            "- " + str(item.get("drill_id")) +
            " | " + str(item.get("category")) +
            " | steps=" + str(item.get("step_count")) +
            " | executed=" + str(item.get("executed"))
        )

    lines.extend(["", "## Blockers", ""])

    if record.get("blockers"):
        for item in record.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    DRY_RUN_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Drill Dry Run Validation",
        "",
        "- Dry Run ID: " + str(result.get("dry_run_id")),
        "- Status: " + str(result.get("status")),
        "- Dry run status: " + str(result.get("dry_run_status")),
        "- Drill count: " + str(result.get("drill_count")),
        "- Hash: " + str(result.get("drill_dry_run_hash")),
        "- Executes drill: False",
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
        "# K-OS Agent Resilience Drill Dry Run Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("state_committed")),
        "- Executes drill: False",
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

    lines.extend(["", "## Recent dry runs", ""])

    if report.get("recent_dry_runs"):
        for item in report.get("recent_dry_runs", [])[:30]:
            lines.append(
                "- " + str(item.get("dry_run_id")) +
                " | status=" + str(item.get("status")) +
                " | drills=" + str(item.get("drill_count")) +
                " | blockers=" + str(item.get("blocker_count"))
            )
    else:
        lines.append("- Nenhum dry run.")

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
    parser.add_argument("--mode", choices=["init", "dry-run", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()
    elif args.mode == "dry-run":
        result = create_dry_run(args.operator, args.reason)
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