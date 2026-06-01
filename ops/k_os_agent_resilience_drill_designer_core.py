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

POLICY_PATH = ROOT / "config" / "resilience_drill_designer" / "k_os_agent_resilience_drill_designer_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_resilience_drill_designer"
STATE_PATH = STATE_DIR / "agent_resilience_drill_designer_state.json"

REPORT_DIR = ROOT / "reports" / "resilience_drill_designer"
MEMORY_DIR = ROOT / "memory" / "resilience_drill_designer"

LATEST_JSON = REPORT_DIR / "latest_agent_resilience_drill_designer_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_resilience_drill_designer_report.md"
DESIGN_JSON = REPORT_DIR / "latest_resilience_drill_design.json"
DESIGN_MD = REPORT_DIR / "latest_resilience_drill_design.md"
VALIDATION_JSON = REPORT_DIR / "latest_resilience_drill_designer_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_resilience_drill_designer_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

SCENARIO_PLAN = ROOT / "reports" / "resilience_scenario_planner" / "latest_resilience_scenario_plan.json"
SCENARIO_REPORT = ROOT / "reports" / "resilience_scenario_planner" / "latest_agent_resilience_scenario_planner_report.json"
SCENARIO_VALIDATION = ROOT / "reports" / "resilience_scenario_planner" / "latest_resilience_scenario_planner_validation_report.json"
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
        raise RuntimeError("Resilience drill designer policy not found.")
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
            "designer_executes_drill": False,
            "designer_executes_recovery": False,
            "designer_executes_rollback": False,
            "designs": [],
            "validations": []
        }
        write_json(STATE_PATH, state)

    data = read_json(STATE_PATH)
    if not data:
        raise RuntimeError("Could not load resilience drill designer state.")
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


def build_drill_from_scenario(scenario: dict[str, Any], index: int) -> dict[str, Any]:
    category = str(scenario.get("category", "unknown"))
    title = str(scenario.get("title", category))
    severity = str(scenario.get("severity", "medium"))

    return {
        "drill_id": "rdd_" + uuid.uuid4().hex[:10],
        "source_scenario_id": scenario.get("scenario_id", ""),
        "category": category,
        "title": "Drill - " + title,
        "priority": index,
        "severity": severity,
        "drill_type": "tabletop" if severity == "high" else "audit_walkthrough",
        "duration_minutes": 30 if severity == "high" else 20,
        "objective": "Validate safe operational response for " + category + " without executing destructive actions.",
        "participants": [
            "operator_k_os",
            "audit_reviewer",
            "technical_owner"
        ],
        "prerequisites": [
            "latest_sanitized_reports_available",
            "operator_present",
            "security_firewall_available",
            "no_live_recovery_execution"
        ],
        "drill_steps": [
            {
                "step": 1,
                "name": "open_scenario_context",
                "description": "Review the source scenario, trigger signals, and safe response expectations.",
                "executes_drill": False,
                "executes_recovery": False,
                "executes_rollback": False,
                "destructive": False
            },
            {
                "step": 2,
                "name": "validate_evidence_chain",
                "description": "Confirm that required reports and hashes are available.",
                "executes_drill": False,
                "executes_recovery": False,
                "executes_rollback": False,
                "destructive": False
            },
            {
                "step": 3,
                "name": "walk_safe_response_steps",
                "description": "Review the non-destructive response flow.",
                "executes_drill": False,
                "executes_recovery": False,
                "executes_rollback": False,
                "destructive": False
            },
            {
                "step": 4,
                "name": "record_operator_findings",
                "description": "Capture operator notes for future dry run.",
                "executes_drill": False,
                "executes_recovery": False,
                "executes_rollback": False,
                "destructive": False
            },
            {
                "step": 5,
                "name": "prepare_dry_run_074",
                "description": "Route the design to checkpoint 074 for safe dry run.",
                "executes_drill": False,
                "executes_recovery": False,
                "executes_rollback": False,
                "destructive": False
            }
        ],
        "expected_evidence": [
            "drill_design_record",
            "operator_review_notes_hash",
            "blocked_actions_confirmed",
            "dry_run_ready_signal"
        ],
        "blocked_steps": [
            "execute_drill_now",
            "execute_recovery_now",
            "execute_rollback_now",
            "delete_files",
            "git_reset_hard",
            "git_force_push",
            "execute_shell_command"
        ],
        "requires_operator_review": True,
        "executes_drill": False,
        "executes_recovery": False,
        "executes_rollback": False,
        "deletes_data": False,
        "modifies_target_files": False,
        "runs_git_reset": False,
        "runs_git_force_push": False,
        "executes_shell_commands": False
    }


def create_design(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    scenario_plan = read_json(SCENARIO_PLAN) or {}
    readiness = read_json(READINESS_MATRIX) or {}
    closure = read_json(RECOVERY_LAYER_CLOSURE) or {}

    blockers = []

    if not scenario_plan.get("scenario_plan_hash"):
        blockers.append("resilience_scenario_plan_missing")

    if not readiness.get("readiness_hash"):
        blockers.append("resilience_readiness_missing")

    if not closure.get("recovery_layer_closure_hash"):
        blockers.append("recovery_layer_closure_missing")

    if scenario_plan.get("planner_executes_recovery") is True:
        blockers.append("scenario_planner_executes_recovery")

    if scenario_plan.get("planner_executes_rollback") is True:
        blockers.append("scenario_planner_executes_rollback")

    if scenario_plan.get("planner_executes_shell_commands") is True:
        blockers.append("scenario_planner_executes_shell_commands")

    if readiness.get("readiness_executes_recovery") is True:
        blockers.append("readiness_executes_recovery")

    if closure.get("no_recovery_executed") is not True:
        blockers.append("no_recovery_not_confirmed")

    if closure.get("no_rollback_executed") is not True:
        blockers.append("no_rollback_not_confirmed")

    scenarios = scenario_plan.get("scenarios", [])
    if not isinstance(scenarios, list):
        scenarios = []

    drills = []
    for index, scenario in enumerate(scenarios, start=1):
        drills.append(build_drill_from_scenario(scenario, index))

    if len(drills) == 0:
        blockers.append("no_scenarios_available_for_drill_design")

    design_id = "rddp_" + uuid.uuid4().hex[:12]

    if len(drills) == 0:
        status = "designer_blocked"
    elif blockers:
        status = "drills_review_required"
    else:
        status = "drills_designed"

    design_body = {
        "design_id": design_id,
        "scenario_plan_hash": scenario_plan.get("scenario_plan_hash", ""),
        "readiness_hash": readiness.get("readiness_hash", ""),
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash", ""),
        "drill_count": len(drills),
        "drill_hashes": [stable_hash(item) for item in drills]
    }

    design = {
        "ok": True,
        "checkpoint": "073",
        "module": "k_os_agent_resilience_drill_designer_core",
        "status": status,
        "design_id": design_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "resilience_drill_designer",
        "scenario_plan_id": scenario_plan.get("plan_id", ""),
        "scenario_plan_status": scenario_plan.get("status", ""),
        "scenario_plan_hash": scenario_plan.get("scenario_plan_hash", ""),
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "readiness_status": readiness.get("status", ""),
        "readiness_hash": readiness.get("readiness_hash", ""),
        "recovery_layer_closure_id": closure.get("recovery_layer_closure_id", ""),
        "recovery_layer_closure_status": closure.get("status", ""),
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash", ""),
        "drill_count": len(drills),
        "drills": drills,
        "blockers": sorted(set(blockers)),
        "drill_design_hash": stable_hash(design_body),
        "designer_executes_drill": False,
        "designer_executes_recovery": False,
        "designer_executes_rollback": False,
        "designer_deletes_data": False,
        "designer_modifies_target_files": False,
        "designer_runs_git_reset": False,
        "designer_runs_git_force_push": False,
        "designer_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "source_refs": {
            "scenario_plan": source_ref(SCENARIO_PLAN),
            "scenario_report": source_ref(SCENARIO_REPORT),
            "scenario_validation": source_ref(SCENARIO_VALIDATION),
            "readiness_matrix": source_ref(READINESS_MATRIX),
            "recovery_layer_closure": source_ref(RECOVERY_LAYER_CLOSURE)
        },
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "074 - K-Agent Resilience Drill Dry Run Core")
    }

    state.setdefault("designs", []).append(design)
    state["designs"] = state["designs"][-300:]
    save_state(state)

    write_design(design)

    event("resilience_drill_designer.design_created", {
        "design_id": design_id,
        "status": status,
        "drill_count": len(drills),
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_design_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("designs", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    design = latest_design_raw()
    blockers = []
    warnings = []

    if not design:
        blockers.append("resilience_drill_design_not_found")
    else:
        required = [
            ("design_id", "design_id_missing"),
            ("drill_design_hash", "drill_design_hash_missing"),
            ("scenario_plan_hash", "scenario_plan_hash_missing")
        ]

        for key, blocker in required:
            if not design.get(key):
                blockers.append(blocker)

        if int(design.get("drill_count", 0) or 0) <= 0:
            blockers.append("drill_count_zero")

        destructive_keys = [
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

        for key in destructive_keys:
            if design.get(key) is True:
                blockers.append(key)

        for drill in design.get("drills", []):
            for key in [
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
                    blockers.append("drill_" + key)

        if design.get("status") != "drills_designed":
            warnings.append("drill_design_requires_operator_review")

        if design.get("blockers"):
            warnings.append("drill_design_contains_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "073",
        "module": "k_os_agent_resilience_drill_designer_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "design_id": design.get("design_id") if design else "",
        "design_status": design.get("status") if design else "",
        "drill_design_hash": design.get("drill_design_hash") if design else "",
        "drill_count": design.get("drill_count") if design else 0,
        "designer_executes_drill": False,
        "designer_executes_recovery": False,
        "designer_executes_rollback": False,
        "designer_deletes_data": False,
        "designer_modifies_target_files": False,
        "designer_runs_git_reset": False,
        "designer_runs_git_force_push": False,
        "designer_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if design and len(blockers) == 0:
        design["validated_at"] = validation["generated_at"]
        design["validated"] = True

    save_state(state)
    write_validation(validation)

    event("resilience_drill_designer.validation_completed", {
        "design_id": validation.get("design_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_design(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "design_id": item.get("design_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "scenario_plan_status": item.get("scenario_plan_status"),
        "readiness_status": item.get("readiness_status"),
        "drill_count": item.get("drill_count"),
        "drill_design_hash": item.get("drill_design_hash"),
        "designer_executes_drill": False,
        "designer_executes_recovery": False,
        "designer_executes_rollback": False,
        "designer_deletes_data": False,
        "designer_modifies_target_files": False,
        "designer_runs_git_reset": False,
        "designer_runs_git_force_push": False,
        "designer_executes_shell_commands": False,
        "blocker_count": len(item.get("blockers", []))
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    designs = [safe_design(item) for item in reversed(state.get("designs", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]

    metrics = {
        "design_count": len(designs),
        "validation_count": len(validations),
        "drills_designed_count": len([x for x in designs if x.get("status") == "drills_designed"]),
        "drills_review_required_count": len([x for x in designs if x.get("status") == "drills_review_required"]),
        "designer_blocked_count": len([x for x in designs if x.get("status") == "designer_blocked"]),
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
        "checkpoint": "073",
        "module": "k_os_agent_resilience_drill_designer_core",
        "status": "audit_generated",
        "generated_at": now(),
        "state_path": "local_secrets/k_os_resilience_drill_designer/agent_resilience_drill_designer_state.json",
        "state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "designer_executes_drill": False,
        "designer_executes_recovery": False,
        "designer_executes_rollback": False,
        "designer_deletes_data": False,
        "designer_modifies_target_files": False,
        "designer_runs_git_reset": False,
        "designer_runs_git_force_push": False,
        "designer_executes_shell_commands": False,
        "metrics": metrics,
        "recent_designs": designs,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "074 - K-Agent Resilience Drill Dry Run Core")
    }

    write_report(report)
    event("resilience_drill_designer.audit_generated", {
        "design_count": metrics.get("design_count")
    })
    return report


def write_design(design: dict[str, Any]) -> None:
    DESIGN_JSON.write_text(json.dumps(design, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Drill Design",
        "",
        "- Design ID: " + str(design.get("design_id")),
        "- Status: " + str(design.get("status")),
        "- Drill count: " + str(design.get("drill_count")),
        "- Hash: " + str(design.get("drill_design_hash")),
        "- Scenario plan status: " + str(design.get("scenario_plan_status")),
        "- Readiness status: " + str(design.get("readiness_status")),
        "- Executes drill: False",
        "- Executes recovery: False",
        "- Executes rollback: False",
        "- Executes shell: False",
        "",
        "## Drills",
        ""
    ]

    for item in design.get("drills", []):
        lines.append(
            "- " + str(item.get("drill_id")) +
            " | " + str(item.get("category")) +
            " | type=" + str(item.get("drill_type")) +
            " | severity=" + str(item.get("severity"))
        )

    lines.extend(["", "## Blockers", ""])

    if design.get("blockers"):
        for item in design.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    DESIGN_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Drill Designer Validation",
        "",
        "- Design ID: " + str(result.get("design_id")),
        "- Status: " + str(result.get("status")),
        "- Design status: " + str(result.get("design_status")),
        "- Drill count: " + str(result.get("drill_count")),
        "- Hash: " + str(result.get("drill_design_hash")),
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
        "# K-OS Agent Resilience Drill Designer Core",
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

    lines.extend(["", "## Recent designs", ""])

    if report.get("recent_designs"):
        for item in report.get("recent_designs", [])[:30]:
            lines.append(
                "- " + str(item.get("design_id")) +
                " | status=" + str(item.get("status")) +
                " | drills=" + str(item.get("drill_count")) +
                " | blockers=" + str(item.get("blocker_count"))
            )
    else:
        lines.append("- Nenhum design.")

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
    parser.add_argument("--mode", choices=["init", "design", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()
    elif args.mode == "design":
        result = create_design(args.operator, args.reason)
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