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

POLICY_PATH = ROOT / "config" / "resilience_drill_operator_review" / "k_os_agent_resilience_drill_operator_review_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_resilience_drill_operator_review"
STATE_PATH = STATE_DIR / "agent_resilience_drill_operator_review_state.json"

REPORT_DIR = ROOT / "reports" / "resilience_drill_operator_review"
MEMORY_DIR = ROOT / "memory" / "resilience_drill_operator_review"

LATEST_JSON = REPORT_DIR / "latest_agent_resilience_drill_operator_review_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_resilience_drill_operator_review_report.md"
REVIEW_JSON = REPORT_DIR / "latest_resilience_drill_operator_review.json"
REVIEW_MD = REPORT_DIR / "latest_resilience_drill_operator_review.md"
VALIDATION_JSON = REPORT_DIR / "latest_resilience_drill_operator_review_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_resilience_drill_operator_review_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

DRY_RUN = ROOT / "reports" / "resilience_drill_dry_run" / "latest_resilience_drill_dry_run.json"
DRY_RUN_REPORT = ROOT / "reports" / "resilience_drill_dry_run" / "latest_agent_resilience_drill_dry_run_report.json"
DRY_RUN_VALIDATION = ROOT / "reports" / "resilience_drill_dry_run" / "latest_resilience_drill_dry_run_validation_report.json"
DRILL_DESIGN = ROOT / "reports" / "resilience_drill_designer" / "latest_resilience_drill_design.json"
SCENARIO_PLAN = ROOT / "reports" / "resilience_scenario_planner" / "latest_resilience_scenario_plan.json"
READINESS_MATRIX = ROOT / "reports" / "resilience_readiness" / "latest_resilience_readiness_matrix.json"


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
        raise RuntimeError("Resilience drill operator review policy not found.")
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
            "operator_review_executes_drill": False,
            "operator_review_executes_recovery": False,
            "operator_review_executes_rollback": False,
            "reviews": [],
            "validations": []
        }
        write_json(STATE_PATH, state)

    data = read_json(STATE_PATH)
    if not data:
        raise RuntimeError("Could not load resilience drill operator review state.")
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


def review_dimension(name: str, ok: bool, evidence: str, blocker: str = "", followup: str = "") -> dict[str, Any]:
    return {
        "dimension": name,
        "ok": ok,
        "evidence": evidence,
        "blocker": "" if ok else blocker,
        "followup": followup
    }


def detect_destructive_flags(payload: dict[str, Any], prefix: str) -> list[str]:
    flags = []
    keys = [
        "executes_drill",
        "executes_recovery",
        "executes_rollback",
        "deletes_data",
        "modifies_target_files",
        "runs_git_reset",
        "runs_git_force_push",
        "executes_shell_commands",
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

    for key in keys:
        if payload.get(key) is True:
            flags.append(prefix + "_" + key)

    return flags


def create_review(operator: str, decision: str, notes: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    dry_run = read_json(DRY_RUN) or {}
    design = read_json(DRILL_DESIGN) or {}
    scenario_plan = read_json(SCENARIO_PLAN) or {}
    readiness = read_json(READINESS_MATRIX) or {}

    blockers = []
    warnings = []
    followups = []

    if not dry_run.get("drill_dry_run_hash"):
        blockers.append("resilience_drill_dry_run_missing")

    if not design.get("drill_design_hash"):
        blockers.append("resilience_drill_design_missing")

    if not scenario_plan.get("scenario_plan_hash"):
        blockers.append("resilience_scenario_plan_missing")

    if not readiness.get("readiness_hash"):
        warnings.append("resilience_readiness_missing")

    blockers.extend(detect_destructive_flags(dry_run, "dry_run"))
    blockers.extend(detect_destructive_flags(design, "design"))

    for simulated_drill in dry_run.get("simulated_drills", []):
        blockers.extend(detect_destructive_flags(simulated_drill, "simulated_drill"))
        if simulated_drill.get("executed") is True:
            blockers.append("simulated_drill_executed_true")

        for step in simulated_drill.get("steps", []):
            blockers.extend(detect_destructive_flags(step, "simulated_step"))
            if step.get("executed") is True:
                blockers.append("simulated_step_executed_true")
            if step.get("destructive") is True:
                blockers.append("simulated_step_destructive_true")

    if dry_run.get("status") != "dry_run_completed_safe":
        warnings.append("dry_run_requires_review")
        followups.append("review_dry_run_status_before_future_drill")

    if dry_run.get("blockers"):
        warnings.append("dry_run_contains_blockers")
        followups.append("resolve_or_accept_dry_run_blockers_before_evidence_pack")

    accepted_decisions = ["reviewed", "reviewed_with_followup", "blocked"]
    decision = decision if decision in accepted_decisions else "reviewed_with_followup"

    if decision == "blocked":
        status = "operator_review_blocked"
    elif blockers:
        status = "operator_review_blocked"
    elif warnings or followups or decision == "reviewed_with_followup":
        status = "operator_review_requires_followup"
    else:
        status = "operator_review_recorded"

    dimensions = [
        review_dimension(
            "dry_run_available",
            bool(dry_run.get("drill_dry_run_hash")),
            rel(DRY_RUN),
            "dry_run_missing"
        ),
        review_dimension(
            "dry_run_non_destructive",
            len(detect_destructive_flags(dry_run, "dry_run")) == 0,
            rel(DRY_RUN),
            "dry_run_destructive_flag_detected"
        ),
        review_dimension(
            "drill_design_available",
            bool(design.get("drill_design_hash")),
            rel(DRILL_DESIGN),
            "drill_design_missing"
        ),
        review_dimension(
            "scenario_plan_available",
            bool(scenario_plan.get("scenario_plan_hash")),
            rel(SCENARIO_PLAN),
            "scenario_plan_missing"
        ),
        review_dimension(
            "evidence_chain_available",
            bool(dry_run.get("drill_dry_run_hash")) and bool(design.get("drill_design_hash")) and bool(scenario_plan.get("scenario_plan_hash")),
            "dry_run + design + scenario_plan",
            "evidence_chain_incomplete"
        ),
        review_dimension(
            "operator_followup_captured",
            True,
            "operator_review_record",
            "",
            "followups_recorded"
        ),
        review_dimension(
            "next_checkpoint_ready",
            len(blockers) == 0,
            "075_to_076_route",
            "operator_review_blocked"
        )
    ]

    review_id = "rdor_" + uuid.uuid4().hex[:12]

    review_body = {
        "review_id": review_id,
        "dry_run_hash": dry_run.get("drill_dry_run_hash", ""),
        "design_hash": design.get("drill_design_hash", ""),
        "scenario_plan_hash": scenario_plan.get("scenario_plan_hash", ""),
        "decision": decision,
        "dimension_hashes": [stable_hash(item) for item in dimensions],
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "followups": sorted(set(followups))
    }

    review = {
        "ok": True,
        "checkpoint": "075",
        "module": "k_os_agent_resilience_drill_operator_review_core",
        "status": status,
        "review_id": review_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "decision": decision,
        "reason": reason or "resilience_drill_operator_review",
        "notes_hash": stable_hash({"notes": notes or "operator_review_recorded"}),
        "notes_included": False,
        "drill_dry_run_id": dry_run.get("dry_run_id", ""),
        "drill_dry_run_status": dry_run.get("status", ""),
        "drill_dry_run_hash": dry_run.get("drill_dry_run_hash", ""),
        "drill_design_id": design.get("design_id", ""),
        "drill_design_status": design.get("status", ""),
        "drill_design_hash": design.get("drill_design_hash", ""),
        "scenario_plan_id": scenario_plan.get("plan_id", ""),
        "scenario_plan_status": scenario_plan.get("status", ""),
        "scenario_plan_hash": scenario_plan.get("scenario_plan_hash", ""),
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "readiness_status": readiness.get("status", ""),
        "readiness_hash": readiness.get("readiness_hash", ""),
        "review_dimensions": dimensions,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "followups": sorted(set(followups)),
        "operator_review_hash": stable_hash(review_body),
        "operator_review_executes_drill": False,
        "operator_review_executes_recovery": False,
        "operator_review_executes_rollback": False,
        "operator_review_deletes_data": False,
        "operator_review_modifies_target_files": False,
        "operator_review_runs_git_reset": False,
        "operator_review_runs_git_force_push": False,
        "operator_review_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "source_refs": {
            "drill_dry_run": source_ref(DRY_RUN),
            "drill_dry_run_report": source_ref(DRY_RUN_REPORT),
            "drill_dry_run_validation": source_ref(DRY_RUN_VALIDATION),
            "drill_design": source_ref(DRILL_DESIGN),
            "scenario_plan": source_ref(SCENARIO_PLAN),
            "readiness_matrix": source_ref(READINESS_MATRIX)
        },
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "076 - K-Agent Resilience Drill Evidence Pack Core")
    }

    state.setdefault("reviews", []).append(review)
    state["reviews"] = state["reviews"][-300:]
    save_state(state)

    write_review(review)

    event("resilience_drill_operator_review.created", {
        "review_id": review_id,
        "status": status,
        "decision": decision,
        "blocker_count": len(blockers),
        "warning_count": len(warnings)
    })

    return audit_report()


def latest_review_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("reviews", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    review = latest_review_raw()
    blockers = []
    warnings = []

    if not review:
        blockers.append("resilience_drill_operator_review_not_found")
    else:
        required = [
            ("review_id", "review_id_missing"),
            ("operator_review_hash", "operator_review_hash_missing"),
            ("drill_dry_run_hash", "drill_dry_run_hash_missing")
        ]

        for key, blocker in required:
            if not review.get(key):
                blockers.append(blocker)

        destructive_keys = [
            "operator_review_executes_drill",
            "operator_review_executes_recovery",
            "operator_review_executes_rollback",
            "operator_review_deletes_data",
            "operator_review_modifies_target_files",
            "operator_review_runs_git_reset",
            "operator_review_runs_git_force_push",
            "operator_review_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if review.get(key) is True:
                blockers.append(key)

        if review.get("notes_included") is True:
            blockers.append("raw_operator_notes_included")

        if review.get("status") != "operator_review_recorded":
            warnings.append("operator_review_requires_followup")

        if review.get("blockers"):
            warnings.append("operator_review_contains_blockers")

        if review.get("warnings"):
            warnings.append("operator_review_contains_warnings")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "075",
        "module": "k_os_agent_resilience_drill_operator_review_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "review_id": review.get("review_id") if review else "",
        "review_status": review.get("status") if review else "",
        "decision": review.get("decision") if review else "",
        "operator_review_hash": review.get("operator_review_hash") if review else "",
        "drill_dry_run_hash": review.get("drill_dry_run_hash") if review else "",
        "operator_review_executes_drill": False,
        "operator_review_executes_recovery": False,
        "operator_review_executes_rollback": False,
        "operator_review_deletes_data": False,
        "operator_review_modifies_target_files": False,
        "operator_review_runs_git_reset": False,
        "operator_review_runs_git_force_push": False,
        "operator_review_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if review and len(blockers) == 0:
        review["validated_at"] = validation["generated_at"]
        review["validated"] = True

    save_state(state)
    write_validation(validation)

    event("resilience_drill_operator_review.validation_completed", {
        "review_id": validation.get("review_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_review(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "review_id": item.get("review_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "decision": item.get("decision"),
        "drill_dry_run_status": item.get("drill_dry_run_status"),
        "drill_design_status": item.get("drill_design_status"),
        "operator_review_hash": item.get("operator_review_hash"),
        "operator_review_executes_drill": False,
        "operator_review_executes_recovery": False,
        "operator_review_executes_rollback": False,
        "operator_review_deletes_data": False,
        "operator_review_modifies_target_files": False,
        "operator_review_runs_git_reset": False,
        "operator_review_runs_git_force_push": False,
        "operator_review_executes_shell_commands": False,
        "blocker_count": len(item.get("blockers", [])),
        "warning_count": len(item.get("warnings", [])),
        "followup_count": len(item.get("followups", []))
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    reviews = [safe_review(item) for item in reversed(state.get("reviews", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]

    metrics = {
        "review_count": len(reviews),
        "validation_count": len(validations),
        "operator_review_recorded_count": len([x for x in reviews if x.get("status") == "operator_review_recorded"]),
        "operator_review_requires_followup_count": len([x for x in reviews if x.get("status") == "operator_review_requires_followup"]),
        "operator_review_blocked_count": len([x for x in reviews if x.get("status") == "operator_review_blocked"]),
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
        "checkpoint": "075",
        "module": "k_os_agent_resilience_drill_operator_review_core",
        "status": "audit_generated",
        "generated_at": now(),
        "state_path": "local_secrets/k_os_resilience_drill_operator_review/agent_resilience_drill_operator_review_state.json",
        "state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "operator_review_executes_drill": False,
        "operator_review_executes_recovery": False,
        "operator_review_executes_rollback": False,
        "operator_review_deletes_data": False,
        "operator_review_modifies_target_files": False,
        "operator_review_runs_git_reset": False,
        "operator_review_runs_git_force_push": False,
        "operator_review_executes_shell_commands": False,
        "metrics": metrics,
        "recent_reviews": reviews,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "076 - K-Agent Resilience Drill Evidence Pack Core")
    }

    write_report(report)
    event("resilience_drill_operator_review.audit_generated", {
        "review_count": metrics.get("review_count")
    })
    return report


def write_review(review: dict[str, Any]) -> None:
    REVIEW_JSON.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Drill Operator Review",
        "",
        "- Review ID: " + str(review.get("review_id")),
        "- Status: " + str(review.get("status")),
        "- Decision: " + str(review.get("decision")),
        "- Hash: " + str(review.get("operator_review_hash")),
        "- Dry run status: " + str(review.get("drill_dry_run_status")),
        "- Drill design status: " + str(review.get("drill_design_status")),
        "- Executes drill: False",
        "- Executes recovery: False",
        "- Executes rollback: False",
        "- Executes shell: False",
        "",
        "## Dimensions",
        ""
    ]

    for item in review.get("review_dimensions", []):
        lines.append(
            "- " + str(item.get("dimension")) +
            " | ok=" + str(item.get("ok")) +
            " | evidence=" + str(item.get("evidence"))
        )

    lines.extend(["", "## Blockers", ""])

    if review.get("blockers"):
        for item in review.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    lines.extend(["", "## Warnings", ""])

    if review.get("warnings"):
        for item in review.get("warnings", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum warning.")

    lines.extend(["", "## Followups", ""])

    if review.get("followups"):
        for item in review.get("followups", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum followup.")

    REVIEW_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Drill Operator Review Validation",
        "",
        "- Review ID: " + str(result.get("review_id")),
        "- Status: " + str(result.get("status")),
        "- Review status: " + str(result.get("review_status")),
        "- Decision: " + str(result.get("decision")),
        "- Hash: " + str(result.get("operator_review_hash")),
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
        "# K-OS Agent Resilience Drill Operator Review Core",
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

    lines.extend(["", "## Recent reviews", ""])

    if report.get("recent_reviews"):
        for item in report.get("recent_reviews", [])[:30]:
            lines.append(
                "- " + str(item.get("review_id")) +
                " | status=" + str(item.get("status")) +
                " | decision=" + str(item.get("decision")) +
                " | blockers=" + str(item.get("blocker_count")) +
                " | warnings=" + str(item.get("warning_count"))
            )
    else:
        lines.append("- Nenhuma revisao.")

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
    parser.add_argument("--mode", choices=["init", "review", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--decision", default="reviewed_with_followup")
    parser.add_argument("--notes", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()
    elif args.mode == "review":
        result = create_review(args.operator, args.decision, args.notes, args.reason)
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