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

POLICY_PATH = ROOT / "config" / "resilience_drill_evidence_pack" / "k_os_agent_resilience_drill_evidence_pack_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_resilience_drill_evidence_pack"
STATE_PATH = STATE_DIR / "agent_resilience_drill_evidence_pack_state.json"

REPORT_DIR = ROOT / "reports" / "resilience_drill_evidence_pack"
MEMORY_DIR = ROOT / "memory" / "resilience_drill_evidence_pack"

LATEST_JSON = REPORT_DIR / "latest_agent_resilience_drill_evidence_pack_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_resilience_drill_evidence_pack_report.md"
PACK_JSON = REPORT_DIR / "latest_resilience_drill_evidence_pack.json"
PACK_MD = REPORT_DIR / "latest_resilience_drill_evidence_pack.md"
VALIDATION_JSON = REPORT_DIR / "latest_resilience_drill_evidence_pack_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_resilience_drill_evidence_pack_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

OPERATOR_REVIEW = ROOT / "reports" / "resilience_drill_operator_review" / "latest_resilience_drill_operator_review.json"
OPERATOR_REVIEW_REPORT = ROOT / "reports" / "resilience_drill_operator_review" / "latest_agent_resilience_drill_operator_review_report.json"
OPERATOR_REVIEW_VALIDATION = ROOT / "reports" / "resilience_drill_operator_review" / "latest_resilience_drill_operator_review_validation_report.json"
DRY_RUN = ROOT / "reports" / "resilience_drill_dry_run" / "latest_resilience_drill_dry_run.json"
DRY_RUN_VALIDATION = ROOT / "reports" / "resilience_drill_dry_run" / "latest_resilience_drill_dry_run_validation_report.json"
DRILL_DESIGN = ROOT / "reports" / "resilience_drill_designer" / "latest_resilience_drill_design.json"
DRILL_DESIGN_VALIDATION = ROOT / "reports" / "resilience_drill_designer" / "latest_resilience_drill_designer_validation_report.json"
SCENARIO_PLAN = ROOT / "reports" / "resilience_scenario_planner" / "latest_resilience_scenario_plan.json"
SCENARIO_VALIDATION = ROOT / "reports" / "resilience_scenario_planner" / "latest_resilience_scenario_planner_validation_report.json"
READINESS_MATRIX = ROOT / "reports" / "resilience_readiness" / "latest_resilience_readiness_matrix.json"
READINESS_VALIDATION = ROOT / "reports" / "resilience_readiness" / "latest_resilience_readiness_validation_report.json"
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
        raise RuntimeError("Resilience drill evidence pack policy not found.")
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
            "evidence_pack_executes_drill": False,
            "evidence_pack_executes_recovery": False,
            "evidence_pack_executes_rollback": False,
            "packs": [],
            "validations": []
        }
        write_json(STATE_PATH, state)

    data = read_json(STATE_PATH)
    if not data:
        raise RuntimeError("Could not load resilience drill evidence pack state.")
    return data


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def source_ref(path: Path, required_hash_key: str = "") -> dict[str, Any]:
    data = read_json(path)
    if not data or data.get("_read_error"):
        return {
            "available": False,
            "path": rel(path),
            "status": "missing",
            "ok": False,
            "hash": "",
            "required_hash_key": required_hash_key
        }

    detected_hash = ""
    if required_hash_key:
        detected_hash = str(data.get(required_hash_key, ""))

    if not detected_hash:
        detected_hash = stable_hash(data)

    return {
        "available": True,
        "path": rel(path),
        "checkpoint": data.get("checkpoint", ""),
        "module": data.get("module", ""),
        "status": data.get("status", ""),
        "ok": data.get("ok", None),
        "created_at": data.get("created_at", data.get("generated_at", "")),
        "hash": detected_hash,
        "content_hash": stable_hash(data),
        "required_hash_key": required_hash_key
    }


def destructive_flags(payload: dict[str, Any], prefix: str) -> list[str]:
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
        "operator_review_executes_drill",
        "operator_review_executes_recovery",
        "operator_review_executes_rollback",
        "operator_review_deletes_data",
        "operator_review_modifies_target_files",
        "operator_review_runs_git_reset",
        "operator_review_runs_git_force_push",
        "operator_review_executes_shell_commands",
        "dry_run_executes_drill",
        "dry_run_executes_recovery",
        "dry_run_executes_rollback",
        "dry_run_deletes_data",
        "dry_run_modifies_target_files",
        "dry_run_runs_git_reset",
        "dry_run_runs_git_force_push",
        "dry_run_executes_shell_commands",
        "designer_executes_drill",
        "designer_executes_recovery",
        "designer_executes_rollback",
        "designer_deletes_data",
        "designer_modifies_target_files",
        "designer_runs_git_reset",
        "designer_runs_git_force_push",
        "designer_executes_shell_commands",
        "planner_executes_recovery",
        "planner_executes_rollback",
        "planner_deletes_data",
        "planner_modifies_target_files",
        "planner_runs_git_reset",
        "planner_runs_git_force_push",
        "planner_executes_shell_commands",
        "readiness_executes_recovery",
        "readiness_executes_rollback",
        "readiness_deletes_data",
        "readiness_modifies_target_files",
        "readiness_runs_git_reset",
        "readiness_runs_git_force_push",
        "readiness_executes_shell_commands",
        "raw_payload_included",
        "local_recovery_token_included"
    ]

    for key in keys:
        if payload.get(key) is True:
            flags.append(prefix + "_" + key)

    return flags


def create_evidence_item(name: str, path: Path, hash_key: str, required: bool) -> dict[str, Any]:
    ref = source_ref(path, hash_key)
    status = "available" if ref.get("available") else "missing"
    return {
        "name": name,
        "required": required,
        "status": status,
        "available": ref.get("available"),
        "path": ref.get("path"),
        "checkpoint": ref.get("checkpoint"),
        "module": ref.get("module"),
        "source_status": ref.get("status"),
        "ok": ref.get("ok"),
        "hash": ref.get("hash"),
        "content_hash": ref.get("content_hash"),
        "required_hash_key": hash_key
    }


def create_pack(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    review = read_json(OPERATOR_REVIEW) or {}
    dry_run = read_json(DRY_RUN) or {}
    design = read_json(DRILL_DESIGN) or {}
    scenario = read_json(SCENARIO_PLAN) or {}
    readiness = read_json(READINESS_MATRIX) or {}
    closure = read_json(RECOVERY_LAYER_CLOSURE) or {}

    blockers = []
    warnings = []
    followups = []

    evidence_items = [
        create_evidence_item("operator_review", OPERATOR_REVIEW, "operator_review_hash", True),
        create_evidence_item("operator_review_report", OPERATOR_REVIEW_REPORT, "", False),
        create_evidence_item("operator_review_validation", OPERATOR_REVIEW_VALIDATION, "", True),
        create_evidence_item("drill_dry_run", DRY_RUN, "drill_dry_run_hash", True),
        create_evidence_item("drill_dry_run_validation", DRY_RUN_VALIDATION, "", True),
        create_evidence_item("drill_design", DRILL_DESIGN, "drill_design_hash", True),
        create_evidence_item("drill_design_validation", DRILL_DESIGN_VALIDATION, "", True),
        create_evidence_item("scenario_plan", SCENARIO_PLAN, "scenario_plan_hash", True),
        create_evidence_item("scenario_validation", SCENARIO_VALIDATION, "", True),
        create_evidence_item("readiness_matrix", READINESS_MATRIX, "readiness_hash", True),
        create_evidence_item("readiness_validation", READINESS_VALIDATION, "", True),
        create_evidence_item("recovery_layer_closure", RECOVERY_LAYER_CLOSURE, "recovery_layer_closure_hash", True)
    ]

    for item in evidence_items:
        if item.get("required") and not item.get("available"):
            blockers.append("missing_required_evidence_" + str(item.get("name")))

    for prefix, payload in [
        ("operator_review", review),
        ("dry_run", dry_run),
        ("drill_design", design),
        ("scenario_plan", scenario),
        ("readiness", readiness)
    ]:
        blockers.extend(destructive_flags(payload, prefix))

    for simulated_drill in dry_run.get("simulated_drills", []):
        blockers.extend(destructive_flags(simulated_drill, "simulated_drill"))
        if simulated_drill.get("executed") is True:
            blockers.append("simulated_drill_executed_true")

        for step in simulated_drill.get("steps", []):
            blockers.extend(destructive_flags(step, "simulated_step"))
            if step.get("executed") is True:
                blockers.append("simulated_step_executed_true")
            if step.get("destructive") is True:
                blockers.append("simulated_step_destructive_true")

    if review.get("status") != "operator_review_recorded":
        warnings.append("operator_review_not_clean_recorded")
        followups.append("carry_operator_review_followup_to_governance_summary_077")

    if dry_run.get("status") != "dry_run_completed_safe":
        warnings.append("dry_run_not_clean_safe")
        followups.append("carry_dry_run_followup_to_governance_summary_077")

    if design.get("status") != "drills_designed":
        warnings.append("drill_design_not_clean_designed")
        followups.append("carry_design_followup_to_governance_summary_077")

    if scenario.get("status") != "scenarios_planned":
        warnings.append("scenario_plan_not_clean_planned")
        followups.append("carry_scenario_followup_to_governance_summary_077")

    if closure.get("no_recovery_executed") is not True:
        blockers.append("no_recovery_not_confirmed")

    if closure.get("no_rollback_executed") is not True:
        blockers.append("no_rollback_not_confirmed")

    if closure.get("no_git_reset_executed") is not True:
        blockers.append("no_git_reset_not_confirmed")

    if closure.get("no_git_force_push_executed") is not True:
        blockers.append("no_git_force_push_not_confirmed")

    if closure.get("no_shell_executed") is not True:
        blockers.append("no_shell_not_confirmed")

    pack_id = "rdep_" + uuid.uuid4().hex[:12]

    if blockers:
        status = "evidence_pack_blocked"
    elif warnings or followups:
        status = "evidence_pack_ready_with_followup"
    else:
        status = "evidence_pack_ready"

    evidence_chain_hash = stable_hash({
        "evidence_items": evidence_items,
        "operator_review_hash": review.get("operator_review_hash", ""),
        "drill_dry_run_hash": dry_run.get("drill_dry_run_hash", ""),
        "drill_design_hash": design.get("drill_design_hash", ""),
        "scenario_plan_hash": scenario.get("scenario_plan_hash", ""),
        "readiness_hash": readiness.get("readiness_hash", ""),
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash", "")
    })

    pack_body = {
        "pack_id": pack_id,
        "status": status,
        "evidence_chain_hash": evidence_chain_hash,
        "required_evidence_count": len([x for x in evidence_items if x.get("required")]),
        "available_required_evidence_count": len([x for x in evidence_items if x.get("required") and x.get("available")]),
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "followups": sorted(set(followups))
    }

    pack = {
        "ok": True,
        "checkpoint": "076",
        "module": "k_os_agent_resilience_drill_evidence_pack_core",
        "status": status,
        "pack_id": pack_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "resilience_drill_evidence_pack",
        "operator_review_id": review.get("review_id", ""),
        "operator_review_status": review.get("status", ""),
        "operator_review_hash": review.get("operator_review_hash", ""),
        "drill_dry_run_id": dry_run.get("dry_run_id", ""),
        "drill_dry_run_status": dry_run.get("status", ""),
        "drill_dry_run_hash": dry_run.get("drill_dry_run_hash", ""),
        "drill_design_id": design.get("design_id", ""),
        "drill_design_status": design.get("status", ""),
        "drill_design_hash": design.get("drill_design_hash", ""),
        "scenario_plan_id": scenario.get("plan_id", ""),
        "scenario_plan_status": scenario.get("status", ""),
        "scenario_plan_hash": scenario.get("scenario_plan_hash", ""),
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "readiness_status": readiness.get("status", ""),
        "readiness_hash": readiness.get("readiness_hash", ""),
        "recovery_layer_closure_id": closure.get("recovery_layer_closure_id", ""),
        "recovery_layer_closure_status": closure.get("status", ""),
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash", ""),
        "required_evidence_count": pack_body["required_evidence_count"],
        "available_required_evidence_count": pack_body["available_required_evidence_count"],
        "evidence_complete": pack_body["required_evidence_count"] == pack_body["available_required_evidence_count"],
        "evidence_items": evidence_items,
        "evidence_chain_hash": evidence_chain_hash,
        "evidence_pack_hash": stable_hash(pack_body),
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "followups": sorted(set(followups)),
        "evidence_pack_executes_drill": False,
        "evidence_pack_executes_recovery": False,
        "evidence_pack_executes_rollback": False,
        "evidence_pack_deletes_data": False,
        "evidence_pack_modifies_target_files": False,
        "evidence_pack_runs_git_reset": False,
        "evidence_pack_runs_git_force_push": False,
        "evidence_pack_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "source_refs": {
            "operator_review": source_ref(OPERATOR_REVIEW, "operator_review_hash"),
            "drill_dry_run": source_ref(DRY_RUN, "drill_dry_run_hash"),
            "drill_design": source_ref(DRILL_DESIGN, "drill_design_hash"),
            "scenario_plan": source_ref(SCENARIO_PLAN, "scenario_plan_hash"),
            "readiness_matrix": source_ref(READINESS_MATRIX, "readiness_hash"),
            "recovery_layer_closure": source_ref(RECOVERY_LAYER_CLOSURE, "recovery_layer_closure_hash")
        },
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "077 - K-Agent Resilience Governance Summary Core")
    }

    state.setdefault("packs", []).append(pack)
    state["packs"] = state["packs"][-300:]
    save_state(state)

    write_pack(pack)

    event("resilience_drill_evidence_pack.created", {
        "pack_id": pack_id,
        "status": status,
        "evidence_complete": pack.get("evidence_complete"),
        "blocker_count": len(blockers),
        "warning_count": len(warnings)
    })

    return audit_report()


def latest_pack_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("packs", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    pack = latest_pack_raw()
    blockers = []
    warnings = []

    if not pack:
        blockers.append("resilience_drill_evidence_pack_not_found")
    else:
        required = [
            ("pack_id", "pack_id_missing"),
            ("evidence_pack_hash", "evidence_pack_hash_missing"),
            ("evidence_chain_hash", "evidence_chain_hash_missing"),
            ("operator_review_hash", "operator_review_hash_missing"),
            ("drill_dry_run_hash", "drill_dry_run_hash_missing")
        ]

        for key, blocker in required:
            if not pack.get(key):
                blockers.append(blocker)

        if pack.get("evidence_complete") is not True:
            blockers.append("evidence_chain_incomplete")

        destructive_keys = [
            "evidence_pack_executes_drill",
            "evidence_pack_executes_recovery",
            "evidence_pack_executes_rollback",
            "evidence_pack_deletes_data",
            "evidence_pack_modifies_target_files",
            "evidence_pack_runs_git_reset",
            "evidence_pack_runs_git_force_push",
            "evidence_pack_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if pack.get(key) is True:
                blockers.append(key)

        if pack.get("status") == "evidence_pack_blocked":
            warnings.append("evidence_pack_status_blocked")

        if pack.get("status") == "evidence_pack_ready_with_followup":
            warnings.append("evidence_pack_carries_followup_to_077")

        if pack.get("warnings"):
            warnings.append("evidence_pack_contains_warnings")

        if pack.get("followups"):
            warnings.append("evidence_pack_contains_followups")

        if pack.get("blockers"):
            blockers.extend(pack.get("blockers", []))

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "076",
        "module": "k_os_agent_resilience_drill_evidence_pack_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "pack_id": pack.get("pack_id") if pack else "",
        "pack_status": pack.get("status") if pack else "",
        "evidence_pack_hash": pack.get("evidence_pack_hash") if pack else "",
        "evidence_chain_hash": pack.get("evidence_chain_hash") if pack else "",
        "evidence_complete": pack.get("evidence_complete") if pack else False,
        "evidence_pack_executes_drill": False,
        "evidence_pack_executes_recovery": False,
        "evidence_pack_executes_rollback": False,
        "evidence_pack_deletes_data": False,
        "evidence_pack_modifies_target_files": False,
        "evidence_pack_runs_git_reset": False,
        "evidence_pack_runs_git_force_push": False,
        "evidence_pack_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings))
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if pack and len(blockers) == 0:
        pack["validated_at"] = validation["generated_at"]
        pack["validated"] = True

    save_state(state)
    write_validation(validation)

    event("resilience_drill_evidence_pack.validation_completed", {
        "pack_id": validation.get("pack_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_pack(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "pack_id": item.get("pack_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "evidence_complete": item.get("evidence_complete"),
        "required_evidence_count": item.get("required_evidence_count"),
        "available_required_evidence_count": item.get("available_required_evidence_count"),
        "operator_review_status": item.get("operator_review_status"),
        "drill_dry_run_status": item.get("drill_dry_run_status"),
        "evidence_pack_hash": item.get("evidence_pack_hash"),
        "evidence_chain_hash": item.get("evidence_chain_hash"),
        "evidence_pack_executes_drill": False,
        "evidence_pack_executes_recovery": False,
        "evidence_pack_executes_rollback": False,
        "evidence_pack_deletes_data": False,
        "evidence_pack_modifies_target_files": False,
        "evidence_pack_runs_git_reset": False,
        "evidence_pack_runs_git_force_push": False,
        "evidence_pack_executes_shell_commands": False,
        "blocker_count": len(item.get("blockers", [])),
        "warning_count": len(item.get("warnings", [])),
        "followup_count": len(item.get("followups", []))
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    packs = [safe_pack(item) for item in reversed(state.get("packs", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]

    metrics = {
        "pack_count": len(packs),
        "validation_count": len(validations),
        "evidence_pack_ready_count": len([x for x in packs if x.get("status") == "evidence_pack_ready"]),
        "evidence_pack_ready_with_followup_count": len([x for x in packs if x.get("status") == "evidence_pack_ready_with_followup"]),
        "evidence_pack_blocked_count": len([x for x in packs if x.get("status") == "evidence_pack_blocked"]),
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
        "checkpoint": "076",
        "module": "k_os_agent_resilience_drill_evidence_pack_core",
        "status": "audit_generated",
        "generated_at": now(),
        "state_path": "local_secrets/k_os_resilience_drill_evidence_pack/agent_resilience_drill_evidence_pack_state.json",
        "state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "evidence_pack_executes_drill": False,
        "evidence_pack_executes_recovery": False,
        "evidence_pack_executes_rollback": False,
        "evidence_pack_deletes_data": False,
        "evidence_pack_modifies_target_files": False,
        "evidence_pack_runs_git_reset": False,
        "evidence_pack_runs_git_force_push": False,
        "evidence_pack_executes_shell_commands": False,
        "metrics": metrics,
        "recent_packs": packs,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "077 - K-Agent Resilience Governance Summary Core")
    }

    write_report(report)
    event("resilience_drill_evidence_pack.audit_generated", {
        "pack_count": metrics.get("pack_count")
    })
    return report


def write_pack(pack: dict[str, Any]) -> None:
    PACK_JSON.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Drill Evidence Pack",
        "",
        "- Pack ID: " + str(pack.get("pack_id")),
        "- Status: " + str(pack.get("status")),
        "- Evidence complete: " + str(pack.get("evidence_complete")),
        "- Required evidence: " + str(pack.get("available_required_evidence_count")) + "/" + str(pack.get("required_evidence_count")),
        "- Evidence pack hash: " + str(pack.get("evidence_pack_hash")),
        "- Evidence chain hash: " + str(pack.get("evidence_chain_hash")),
        "- Executes drill: False",
        "- Executes recovery: False",
        "- Executes rollback: False",
        "- Executes shell: False",
        "",
        "## Evidence items",
        ""
    ]

    for item in pack.get("evidence_items", []):
        lines.append(
            "- " + str(item.get("name")) +
            " | required=" + str(item.get("required")) +
            " | available=" + str(item.get("available")) +
            " | status=" + str(item.get("source_status")) +
            " | hash=" + str(item.get("hash"))
        )

    lines.extend(["", "## Blockers", ""])

    if pack.get("blockers"):
        for item in pack.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    lines.extend(["", "## Warnings", ""])

    if pack.get("warnings"):
        for item in pack.get("warnings", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum warning.")

    lines.extend(["", "## Followups", ""])

    if pack.get("followups"):
        for item in pack.get("followups", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum followup.")

    PACK_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Drill Evidence Pack Validation",
        "",
        "- Pack ID: " + str(result.get("pack_id")),
        "- Status: " + str(result.get("status")),
        "- Pack status: " + str(result.get("pack_status")),
        "- Evidence complete: " + str(result.get("evidence_complete")),
        "- Evidence pack hash: " + str(result.get("evidence_pack_hash")),
        "- Evidence chain hash: " + str(result.get("evidence_chain_hash")),
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
        "# K-OS Agent Resilience Drill Evidence Pack Core",
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

    lines.extend(["", "## Recent packs", ""])

    if report.get("recent_packs"):
        for item in report.get("recent_packs", [])[:30]:
            lines.append(
                "- " + str(item.get("pack_id")) +
                " | status=" + str(item.get("status")) +
                " | complete=" + str(item.get("evidence_complete")) +
                " | blockers=" + str(item.get("blocker_count")) +
                " | warnings=" + str(item.get("warning_count"))
            )
    else:
        lines.append("- Nenhum pacote.")

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
    parser.add_argument("--mode", choices=["init", "pack", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()
    elif args.mode == "pack":
        result = create_pack(args.operator, args.reason)
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