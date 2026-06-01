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

POLICY_PATH = ROOT / "config" / "recovery_layer_closure" / "k_os_agent_recovery_layer_closure_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_recovery_layer_closure"
STATE_PATH = STATE_DIR / "agent_recovery_layer_closure_state.json"

REPORT_DIR = ROOT / "reports" / "recovery_layer_closure"
MEMORY_DIR = ROOT / "memory" / "recovery_layer_closure"

LATEST_JSON = REPORT_DIR / "latest_agent_recovery_layer_closure_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_recovery_layer_closure_report.md"
CLOSURE_JSON = REPORT_DIR / "latest_recovery_layer_closure.json"
CLOSURE_MD = REPORT_DIR / "latest_recovery_layer_closure.md"
VALIDATION_JSON = REPORT_DIR / "latest_recovery_layer_closure_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_recovery_layer_closure_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

INPUTS = [
    {
        "checkpoint": "061",
        "name": "Recovery Readiness Matrix Core",
        "report": ROOT / "reports" / "recovery_readiness_matrix" / "latest_agent_recovery_readiness_matrix_report.json",
        "artifact": ROOT / "reports" / "recovery_readiness_matrix" / "latest_recovery_readiness_matrix.json",
        "closure": ROOT / "reports" / "recovery_readiness_matrix" / "k_os_061_closure_report.json"
    },
    {
        "checkpoint": "062",
        "name": "Recovery Plan Builder Core",
        "report": ROOT / "reports" / "recovery_plan_builder" / "latest_agent_recovery_plan_builder_report.json",
        "artifact": ROOT / "reports" / "recovery_plan_builder" / "latest_recovery_plan.json",
        "closure": ROOT / "reports" / "recovery_plan_builder" / "k_os_062_closure_report.json"
    },
    {
        "checkpoint": "063",
        "name": "Recovery Approval Gate Core",
        "report": ROOT / "reports" / "recovery_gate" / "latest_agent_recovery_gate_report.json",
        "artifact": ROOT / "reports" / "recovery_gate" / "latest_recovery_gate_record.json",
        "closure": ROOT / "reports" / "recovery_gate" / "k_os_063_closure_report.json"
    },
    {
        "checkpoint": "064",
        "name": "Recovery Dry Run Simulator Core",
        "report": ROOT / "reports" / "recovery_dry_run" / "latest_agent_recovery_dry_run_report.json",
        "artifact": ROOT / "reports" / "recovery_dry_run" / "latest_recovery_dry_run_simulation.json",
        "closure": ROOT / "reports" / "recovery_dry_run" / "k_os_064_closure_report.json"
    },
    {
        "checkpoint": "065",
        "name": "Recovery Final Gate Core",
        "report": ROOT / "reports" / "recovery_final_gate" / "latest_agent_recovery_final_gate_report.json",
        "artifact": ROOT / "reports" / "recovery_final_gate" / "latest_recovery_final_gate_record.json",
        "closure": ROOT / "reports" / "recovery_final_gate" / "k_os_065_closure_report.json"
    },
    {
        "checkpoint": "066",
        "name": "Recovery Manual Execution Stub Core",
        "report": ROOT / "reports" / "recovery_manual_stub" / "latest_agent_recovery_manual_stub_report.json",
        "artifact": ROOT / "reports" / "recovery_manual_stub" / "latest_recovery_manual_stub_record.json",
        "closure": ROOT / "reports" / "recovery_manual_stub" / "k_os_066_closure_report.json"
    },
    {
        "checkpoint": "067",
        "name": "Recovery Controlled Execution Sandbox Core",
        "report": ROOT / "reports" / "recovery_controlled_sandbox" / "latest_agent_recovery_controlled_sandbox_report.json",
        "artifact": ROOT / "reports" / "recovery_controlled_sandbox" / "latest_recovery_controlled_sandbox_record.json",
        "closure": ROOT / "reports" / "recovery_controlled_sandbox" / "k_os_067_closure_report.json"
    },
    {
        "checkpoint": "068",
        "name": "Recovery Sandbox Operator Review Core",
        "report": ROOT / "reports" / "recovery_sandbox_review" / "latest_agent_recovery_sandbox_review_report.json",
        "artifact": ROOT / "reports" / "recovery_sandbox_review" / "latest_recovery_sandbox_operator_review.json",
        "closure": ROOT / "reports" / "recovery_sandbox_review" / "k_os_068_closure_report.json"
    },
    {
        "checkpoint": "069",
        "name": "Recovery Governance Summary Core",
        "report": ROOT / "reports" / "recovery_governance_summary" / "latest_agent_recovery_governance_summary_report.json",
        "artifact": ROOT / "reports" / "recovery_governance_summary" / "latest_recovery_governance_summary.json",
        "closure": ROOT / "reports" / "recovery_governance_summary" / "k_os_069_closure_report.json"
    }
]

GOVERNANCE_SUMMARY = ROOT / "reports" / "recovery_governance_summary" / "latest_recovery_governance_summary.json"


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
        raise RuntimeError("Recovery layer closure policy not found.")
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
            "closure_executes_recovery": False,
            "closure_executes_rollback": False,
            "closures": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load recovery layer closure state.")
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


def has_true(data: dict[str, Any], keys: list[str]) -> bool:
    for key in keys:
        if data.get(key) is True:
            return True
    return False


def metric_int(metrics: dict[str, Any], key: str) -> int:
    try:
        return int(metrics.get(key, 0) or 0)
    except Exception:
        return 0


def collect_evidence_chain() -> list[dict[str, Any]]:
    destructive_keys = [
        "executes_recovery",
        "executes_rollback",
        "deletes_data",
        "modifies_target_files",
        "runs_git_reset",
        "runs_git_force_push",
        "executes_shell_commands",
        "readiness_executes_recovery",
        "readiness_executes_rollback",
        "plan_executes_recovery",
        "plan_executes_rollback",
        "gate_executes_recovery",
        "gate_executes_rollback",
        "dry_run_executes_recovery",
        "dry_run_executes_rollback",
        "final_gate_executes_recovery",
        "final_gate_executes_rollback",
        "stub_executes_recovery",
        "stub_executes_rollback",
        "sandbox_executes_recovery",
        "sandbox_executes_rollback",
        "review_executes_recovery",
        "review_executes_rollback",
        "summary_executes_recovery",
        "summary_executes_rollback",
        "closure_executes_recovery",
        "closure_executes_rollback",
        "deletes_data",
        "modifies_target_files",
        "runs_git_reset",
        "runs_git_force_push",
        "executes_shell_commands",
        "raw_payload_included",
        "local_recovery_token_included"
    ]

    chain = []

    for item in INPUTS:
        report = read_json(item["report"]) or {}
        artifact = read_json(item["artifact"]) or {}
        closure = read_json(item["closure"]) or {}

        report_available = bool(report) and not report.get("_read_error")
        artifact_available = bool(artifact) and not artifact.get("_read_error")
        closure_available = bool(closure) and not closure.get("_read_error")

        metrics = report.get("metrics", {}) if isinstance(report.get("metrics", {}), dict) else {}

        checkpoint_record = {
            "checkpoint": item["checkpoint"],
            "name": item["name"],
            "report_available": report_available,
            "artifact_available": artifact_available,
            "closure_available": closure_available,
            "report_path": rel(item["report"]),
            "artifact_path": rel(item["artifact"]),
            "closure_path": rel(item["closure"]),
            "report_status": report.get("status", "missing") if report_available else "missing",
            "artifact_status": artifact.get("status", "missing") if artifact_available else "missing",
            "closure_status": closure.get("status", "missing") if closure_available else "missing",
            "report_hash": stable_hash(report) if report_available else "",
            "artifact_hash": stable_hash(artifact) if artifact_available else "",
            "closure_hash": stable_hash(closure) if closure_available else "",
            "destructive_flag_present": (
                has_true(report, destructive_keys) or
                has_true(artifact, destructive_keys) or
                has_true(closure, destructive_keys)
            ),
            "metrics": {
                "recovery_execution_count": metric_int(metrics, "recovery_execution_count"),
                "rollback_execution_count": metric_int(metrics, "rollback_execution_count"),
                "data_delete_count": metric_int(metrics, "data_delete_count"),
                "target_file_modify_count": metric_int(metrics, "target_file_modify_count"),
                "git_reset_count": metric_int(metrics, "git_reset_count"),
                "git_force_push_count": metric_int(metrics, "git_force_push_count"),
                "shell_execution_count": metric_int(metrics, "shell_execution_count")
            },
            "source_refs": {
                "report": source_ref(item["report"]),
                "artifact": source_ref(item["artifact"]),
                "closure": source_ref(item["closure"])
            }
        }

        chain.append(checkpoint_record)

    return chain


def aggregate_totals(chain: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "checkpoint_count": len(chain),
        "report_available_count": 0,
        "artifact_available_count": 0,
        "closure_available_count": 0,
        "missing_report_count": 0,
        "missing_artifact_count": 0,
        "missing_closure_count": 0,
        "destructive_flag_count": 0,
        "recovery_execution_count": 0,
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0
    }

    for item in chain:
        if item.get("report_available"):
            totals["report_available_count"] += 1
        else:
            totals["missing_report_count"] += 1

        if item.get("artifact_available"):
            totals["artifact_available_count"] += 1
        else:
            totals["missing_artifact_count"] += 1

        if item.get("closure_available"):
            totals["closure_available_count"] += 1
        else:
            totals["missing_closure_count"] += 1

        if item.get("destructive_flag_present"):
            totals["destructive_flag_count"] += 1

        metrics = item.get("metrics", {})
        for key in [
            "recovery_execution_count",
            "rollback_execution_count",
            "data_delete_count",
            "target_file_modify_count",
            "git_reset_count",
            "git_force_push_count",
            "shell_execution_count"
        ]:
            totals[key] += metric_int(metrics, key)

    return totals


def collect_blockers(chain: list[dict[str, Any]], totals: dict[str, Any], governance: dict[str, Any]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []

    if not governance:
        blockers.append({"checkpoint": "069", "blocker": "recovery_governance_summary_missing"})
    elif not governance.get("recovery_governance_summary_hash"):
        blockers.append({"checkpoint": "069", "blocker": "recovery_governance_summary_hash_missing"})

    for item in chain:
        checkpoint = str(item.get("checkpoint"))

        if not item.get("report_available"):
            blockers.append({"checkpoint": checkpoint, "blocker": "report_missing"})

        if not item.get("artifact_available"):
            blockers.append({"checkpoint": checkpoint, "blocker": "artifact_missing"})

        if not item.get("closure_available"):
            blockers.append({"checkpoint": checkpoint, "blocker": "closure_report_missing"})

        if item.get("destructive_flag_present"):
            blockers.append({"checkpoint": checkpoint, "blocker": "destructive_flag_present"})

    zero_required = [
        "recovery_execution_count",
        "rollback_execution_count",
        "data_delete_count",
        "target_file_modify_count",
        "git_reset_count",
        "git_force_push_count",
        "shell_execution_count"
    ]

    for key in zero_required:
        if int(totals.get(key, 0) or 0) != 0:
            blockers.append({"checkpoint": "aggregate", "blocker": key + "_not_zero"})

    return blockers


def create_closure(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    closure_id = "rlc_" + uuid.uuid4().hex[:12]
    governance = read_json(GOVERNANCE_SUMMARY) or {}
    chain = collect_evidence_chain()
    totals = aggregate_totals(chain)
    blockers = collect_blockers(chain, totals, governance)

    destructive_zero = (
        totals["recovery_execution_count"] == 0 and
        totals["rollback_execution_count"] == 0 and
        totals["data_delete_count"] == 0 and
        totals["target_file_modify_count"] == 0 and
        totals["git_reset_count"] == 0 and
        totals["git_force_push_count"] == 0 and
        totals["shell_execution_count"] == 0 and
        totals["destructive_flag_count"] == 0
    )

    evidence_core_complete = (
        totals["missing_report_count"] == 0 and
        totals["missing_artifact_count"] == 0 and
        bool(governance.get("recovery_governance_summary_hash"))
    )

    evidence_closure_complete = totals["missing_closure_count"] == 0

    if destructive_zero and evidence_core_complete and evidence_closure_complete:
        status = "layer_closed_safe"
    elif destructive_zero and evidence_core_complete:
        status = "layer_closed_with_review_required"
    else:
        status = "layer_blocked"

    closure_body = {
        "closure_id": closure_id,
        "covered_checkpoints": policy.get("covered_checkpoints", []),
        "chain_hashes": [
            {
                "checkpoint": item.get("checkpoint"),
                "report_hash": item.get("report_hash"),
                "artifact_hash": item.get("artifact_hash"),
                "closure_hash": item.get("closure_hash")
            }
            for item in chain
        ],
        "governance_summary_hash": governance.get("recovery_governance_summary_hash", ""),
        "totals": totals,
        "destructive_zero": destructive_zero,
        "evidence_core_complete": evidence_core_complete,
        "evidence_closure_complete": evidence_closure_complete
    }

    closure = {
        "ok": True,
        "checkpoint": "070",
        "module": "k_os_agent_recovery_layer_closure_core",
        "status": status,
        "recovery_layer_closure_id": closure_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "recovery_layer_closure_061_069",
        "covered_checkpoints": policy.get("covered_checkpoints", []),
        "recovery_governance_summary_available": bool(governance),
        "recovery_governance_summary_id": governance.get("summary_id", ""),
        "recovery_governance_summary_hash": governance.get("recovery_governance_summary_hash", ""),
        "evidence_chain": chain,
        "totals": totals,
        "consolidated_blockers": blockers,
        "recovery_layer_closure_hash": stable_hash(closure_body),
        "destructive_zero": destructive_zero,
        "evidence_core_complete": evidence_core_complete,
        "evidence_closure_complete": evidence_closure_complete,
        "no_recovery_executed": totals["recovery_execution_count"] == 0,
        "no_rollback_executed": totals["rollback_execution_count"] == 0,
        "no_data_deleted": totals["data_delete_count"] == 0,
        "no_target_files_modified": totals["target_file_modify_count"] == 0,
        "no_git_reset_executed": totals["git_reset_count"] == 0,
        "no_git_force_push_executed": totals["git_force_push_count"] == 0,
        "no_shell_executed": totals["shell_execution_count"] == 0,
        "closure_executes_recovery": False,
        "closure_executes_rollback": False,
        "closure_deletes_data": False,
        "closure_modifies_target_files": False,
        "closure_runs_git_reset": False,
        "closure_runs_git_force_push": False,
        "closure_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_layer_closure": policy.get("required_gates_before_recovery_layer_closure", []),
        "next_checkpoint": policy.get("next_checkpoint", "071 - K-Agent Resilience Readiness Core")
    }

    state.setdefault("closures", []).append(closure)
    state["closures"] = state["closures"][-300:]
    save_state(state)

    write_closure(closure)

    event("recovery_layer_closure.created", {
        "recovery_layer_closure_id": closure_id,
        "status": status,
        "destructive_zero": destructive_zero,
        "evidence_core_complete": evidence_core_complete,
        "evidence_closure_complete": evidence_closure_complete,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_closure_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("closures", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    closure = latest_closure_raw()
    blockers: list[str] = []
    warnings: list[str] = []

    if not closure:
        blockers.append("recovery_layer_closure_not_found")
    else:
        required = [
            ("recovery_layer_closure_id", "recovery_layer_closure_id_missing"),
            ("recovery_layer_closure_hash", "recovery_layer_closure_hash_missing"),
            ("recovery_governance_summary_hash", "recovery_governance_summary_hash_missing")
        ]

        for key, blocker in required:
            if not closure.get(key):
                blockers.append(blocker)

        totals = closure.get("totals", {})

        zero_required = [
            ("recovery_execution_count", "recovery_execution_count_not_zero"),
            ("rollback_execution_count", "rollback_execution_count_not_zero"),
            ("data_delete_count", "data_delete_count_not_zero"),
            ("target_file_modify_count", "target_file_modify_count_not_zero"),
            ("git_reset_count", "git_reset_count_not_zero"),
            ("git_force_push_count", "git_force_push_count_not_zero"),
            ("shell_execution_count", "shell_execution_count_not_zero"),
            ("destructive_flag_count", "destructive_flag_count_not_zero")
        ]

        for key, blocker in zero_required:
            if int(totals.get(key, 0) or 0) != 0:
                blockers.append(blocker)

        destructive_keys = [
            "closure_executes_recovery",
            "closure_executes_rollback",
            "closure_deletes_data",
            "closure_modifies_target_files",
            "closure_runs_git_reset",
            "closure_runs_git_force_push",
            "closure_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if closure.get(key) is True:
                blockers.append(key)

        if not closure.get("evidence_core_complete"):
            warnings.append("core_evidence_chain_incomplete")

        if not closure.get("evidence_closure_complete"):
            warnings.append("closure_reports_incomplete_but_layer_can_continue_with_review")

        if closure.get("consolidated_blockers"):
            warnings.append("layer_closure_contains_non_destructive_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "070",
        "module": "k_os_agent_recovery_layer_closure_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "recovery_layer_closure_id": closure.get("recovery_layer_closure_id") if closure else "",
        "layer_status": closure.get("status") if closure else "",
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash") if closure else "",
        "recovery_governance_summary_hash": closure.get("recovery_governance_summary_hash") if closure else "",
        "no_recovery_executed": closure.get("no_recovery_executed") if closure else False,
        "no_rollback_executed": closure.get("no_rollback_executed") if closure else False,
        "no_data_deleted": closure.get("no_data_deleted") if closure else False,
        "no_target_files_modified": closure.get("no_target_files_modified") if closure else False,
        "no_git_reset_executed": closure.get("no_git_reset_executed") if closure else False,
        "no_git_force_push_executed": closure.get("no_git_force_push_executed") if closure else False,
        "no_shell_executed": closure.get("no_shell_executed") if closure else False,
        "closure_executes_recovery": False,
        "closure_executes_rollback": False,
        "closure_deletes_data": False,
        "closure_modifies_target_files": False,
        "closure_runs_git_reset": False,
        "closure_runs_git_force_push": False,
        "closure_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if closure and len(blockers) == 0:
        closure["validated_at"] = validation["generated_at"]
        closure["validated"] = True

    save_state(state)
    write_validation(validation)

    event("recovery_layer_closure.validation_completed", {
        "recovery_layer_closure_id": validation.get("recovery_layer_closure_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_closure(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "recovery_layer_closure_id": item.get("recovery_layer_closure_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "covered_checkpoints": item.get("covered_checkpoints"),
        "recovery_layer_closure_hash": item.get("recovery_layer_closure_hash"),
        "recovery_governance_summary_hash": item.get("recovery_governance_summary_hash"),
        "destructive_zero": item.get("destructive_zero"),
        "evidence_core_complete": item.get("evidence_core_complete"),
        "evidence_closure_complete": item.get("evidence_closure_complete"),
        "no_recovery_executed": item.get("no_recovery_executed"),
        "no_rollback_executed": item.get("no_rollback_executed"),
        "no_data_deleted": item.get("no_data_deleted"),
        "no_target_files_modified": item.get("no_target_files_modified"),
        "no_git_reset_executed": item.get("no_git_reset_executed"),
        "no_git_force_push_executed": item.get("no_git_force_push_executed"),
        "no_shell_executed": item.get("no_shell_executed"),
        "closure_executes_recovery": False,
        "closure_executes_rollback": False,
        "closure_deletes_data": False,
        "closure_modifies_target_files": False,
        "closure_runs_git_reset": False,
        "closure_runs_git_force_push": False,
        "closure_executes_shell_commands": False,
        "blocker_count": len(item.get("consolidated_blockers", []))
    }


def compute_metrics(closures: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "closure_count": len(closures),
        "validation_count": len(validations),
        "layer_closed_safe_count": len([x for x in closures if x.get("status") == "layer_closed_safe"]),
        "layer_closed_with_review_required_count": len([x for x in closures if x.get("status") == "layer_closed_with_review_required"]),
        "layer_blocked_count": len([x for x in closures if x.get("status") == "layer_blocked"]),
        "recovery_execution_count": 0,
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    closures = [safe_closure(item) for item in reversed(state.get("closures", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(closures, validations)

    report = {
        "ok": True,
        "checkpoint": "070",
        "module": "k_os_agent_recovery_layer_closure_core",
        "status": "audit_generated",
        "generated_at": now(),
        "closure_state_path": "local_secrets/k_os_recovery_layer_closure/agent_recovery_layer_closure_state.json",
        "closure_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "closure_executes_recovery": False,
        "closure_executes_rollback": False,
        "closure_deletes_data": False,
        "closure_modifies_target_files": False,
        "closure_runs_git_reset": False,
        "closure_runs_git_force_push": False,
        "closure_executes_shell_commands": False,
        "covered_checkpoints": policy.get("covered_checkpoints", []),
        "metrics": metrics,
        "recent_closures": closures,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_layer_closure": policy.get("required_gates_before_recovery_layer_closure", []),
        "next_checkpoint": policy.get("next_checkpoint", "071 - K-Agent Resilience Readiness Core")
    }

    write_report(report)
    event("recovery_layer_closure.audit_generated", {
        "closure_count": metrics.get("closure_count")
    })
    return report


def write_closure(closure: dict[str, Any]) -> None:
    CLOSURE_JSON.write_text(json.dumps(closure, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Layer Closure",
        "",
        "- Closure ID: " + str(closure.get("recovery_layer_closure_id")),
        "- Status: " + str(closure.get("status")),
        "- Hash: " + str(closure.get("recovery_layer_closure_hash")),
        "- Governance summary hash: " + str(closure.get("recovery_governance_summary_hash")),
        "- Covered checkpoints: " + ", ".join(closure.get("covered_checkpoints", [])),
        "- Destructive zero: " + str(closure.get("destructive_zero")),
        "- Evidence core complete: " + str(closure.get("evidence_core_complete")),
        "- Evidence closure complete: " + str(closure.get("evidence_closure_complete")),
        "- No recovery executed: " + str(closure.get("no_recovery_executed")),
        "- No rollback executed: " + str(closure.get("no_rollback_executed")),
        "- No data deleted: " + str(closure.get("no_data_deleted")),
        "- No target files modified: " + str(closure.get("no_target_files_modified")),
        "- No git reset executed: " + str(closure.get("no_git_reset_executed")),
        "- No force push executed: " + str(closure.get("no_git_force_push_executed")),
        "- No shell executed: " + str(closure.get("no_shell_executed")),
        "",
        "## Totals",
        ""
    ]

    for key, value in closure.get("totals", {}).items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Evidence chain", ""])

    for item in closure.get("evidence_chain", []):
        lines.append(
            "- " + str(item.get("checkpoint")) +
            " | " + str(item.get("name")) +
            " | report=" + str(item.get("report_available")) +
            " | artifact=" + str(item.get("artifact_available")) +
            " | closure=" + str(item.get("closure_available"))
        )

    lines.extend(["", "## Consolidated blockers", ""])

    if closure.get("consolidated_blockers"):
        for item in closure.get("consolidated_blockers", []):
            lines.append("- " + str(item.get("checkpoint")) + ": " + str(item.get("blocker")))
    else:
        lines.append("- Nenhum blocker.")

    CLOSURE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Layer Closure Validation",
        "",
        "- Closure ID: " + str(result.get("recovery_layer_closure_id")),
        "- Status: " + str(result.get("status")),
        "- Layer status: " + str(result.get("layer_status")),
        "- Hash: " + str(result.get("recovery_layer_closure_hash")),
        "- No recovery executed: " + str(result.get("no_recovery_executed")),
        "- No rollback executed: " + str(result.get("no_rollback_executed")),
        "- No data deleted: " + str(result.get("no_data_deleted")),
        "- No target files modified: " + str(result.get("no_target_files_modified")),
        "- No git reset executed: " + str(result.get("no_git_reset_executed")),
        "- No force push executed: " + str(result.get("no_git_force_push_executed")),
        "- No shell executed: " + str(result.get("no_shell_executed")),
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
        "# K-OS Agent Recovery Layer Closure Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("closure_state_committed")),
        "- Executes recovery: " + str(report.get("closure_executes_recovery")),
        "- Executes rollback: " + str(report.get("closure_executes_rollback")),
        "- Deletes data: " + str(report.get("closure_deletes_data")),
        "- Modifies target files: " + str(report.get("closure_modifies_target_files")),
        "- Runs git reset: " + str(report.get("closure_runs_git_reset")),
        "- Runs git force push: " + str(report.get("closure_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("closure_executes_shell_commands")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent closures", ""])

    if report.get("recent_closures"):
        for item in report.get("recent_closures", [])[:30]:
            lines.append(
                "- " + str(item.get("recovery_layer_closure_id")) +
                " | status=" + str(item.get("status")) +
                " | destructive_zero=" + str(item.get("destructive_zero")) +
                " | blockers=" + str(item.get("blocker_count"))
            )
    else:
        lines.append("- Nenhum fechamento.")

    lines.extend(["", "## Required gates before recovery layer closure", ""])

    for gate in report.get("required_gates_before_recovery_layer_closure", []):
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
    parser.add_argument("--mode", choices=["init", "close", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "close":
        result = create_closure(args.operator, args.reason)

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