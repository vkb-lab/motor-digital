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

POLICY_PATH = ROOT / "config" / "recovery_governance_summary" / "k_os_agent_recovery_governance_summary_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_recovery_governance_summary"
STATE_PATH = STATE_DIR / "agent_recovery_governance_summary_state.json"

REPORT_DIR = ROOT / "reports" / "recovery_governance_summary"
MEMORY_DIR = ROOT / "memory" / "recovery_governance_summary"

LATEST_JSON = REPORT_DIR / "latest_agent_recovery_governance_summary_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_recovery_governance_summary_report.md"
SUMMARY_JSON = REPORT_DIR / "latest_recovery_governance_summary.json"
SUMMARY_MD = REPORT_DIR / "latest_recovery_governance_summary.md"
VALIDATION_JSON = REPORT_DIR / "latest_recovery_governance_summary_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_recovery_governance_summary_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

INPUTS = [
    {
        "checkpoint": "061",
        "name": "Recovery Readiness Matrix Core",
        "report": ROOT / "reports" / "recovery_readiness_matrix" / "latest_agent_recovery_readiness_matrix_report.json",
        "artifact": ROOT / "reports" / "recovery_readiness_matrix" / "latest_recovery_readiness_matrix.json"
    },
    {
        "checkpoint": "062",
        "name": "Recovery Plan Builder Core",
        "report": ROOT / "reports" / "recovery_plan_builder" / "latest_agent_recovery_plan_builder_report.json",
        "artifact": ROOT / "reports" / "recovery_plan_builder" / "latest_recovery_plan.json"
    },
    {
        "checkpoint": "063",
        "name": "Recovery Approval Gate Core",
        "report": ROOT / "reports" / "recovery_gate" / "latest_agent_recovery_gate_report.json",
        "artifact": ROOT / "reports" / "recovery_gate" / "latest_recovery_gate_record.json"
    },
    {
        "checkpoint": "064",
        "name": "Recovery Dry Run Simulator Core",
        "report": ROOT / "reports" / "recovery_dry_run" / "latest_agent_recovery_dry_run_report.json",
        "artifact": ROOT / "reports" / "recovery_dry_run" / "latest_recovery_dry_run_simulation.json"
    },
    {
        "checkpoint": "065",
        "name": "Recovery Final Gate Core",
        "report": ROOT / "reports" / "recovery_final_gate" / "latest_agent_recovery_final_gate_report.json",
        "artifact": ROOT / "reports" / "recovery_final_gate" / "latest_recovery_final_gate_record.json"
    },
    {
        "checkpoint": "066",
        "name": "Recovery Manual Execution Stub Core",
        "report": ROOT / "reports" / "recovery_manual_stub" / "latest_agent_recovery_manual_stub_report.json",
        "artifact": ROOT / "reports" / "recovery_manual_stub" / "latest_recovery_manual_stub_record.json"
    },
    {
        "checkpoint": "067",
        "name": "Recovery Controlled Execution Sandbox Core",
        "report": ROOT / "reports" / "recovery_controlled_sandbox" / "latest_agent_recovery_controlled_sandbox_report.json",
        "artifact": ROOT / "reports" / "recovery_controlled_sandbox" / "latest_recovery_controlled_sandbox_record.json"
    },
    {
        "checkpoint": "068",
        "name": "Recovery Sandbox Operator Review Core",
        "report": ROOT / "reports" / "recovery_sandbox_review" / "latest_agent_recovery_sandbox_review_report.json",
        "artifact": ROOT / "reports" / "recovery_sandbox_review" / "latest_recovery_sandbox_operator_review.json"
    }
]


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
        raise RuntimeError("Recovery governance summary policy not found.")
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
            "summary_executes_recovery": False,
            "summary_executes_rollback": False,
            "summaries": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load recovery governance summary state.")
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


def flag_true(data: dict[str, Any], keys: list[str]) -> bool:
    for key in keys:
        if data.get(key) is True:
            return True
    return False


def collect_chain() -> list[dict[str, Any]]:
    chain = []

    for item in INPUTS:
        report = read_json(item["report"]) or {}
        artifact = read_json(item["artifact"]) or {}

        report_available = bool(report) and not report.get("_read_error")
        artifact_available = bool(artifact) and not artifact.get("_read_error")

        destructive_keys = [
            "executes_recovery",
            "executes_rollback",
            "deletes_data",
            "modifies_target_files",
            "runs_git_reset",
            "runs_git_force_push",
            "executes_shell_commands",
            "summary_executes_recovery",
            "summary_executes_rollback",
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
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        report_metrics = report.get("metrics", {}) if isinstance(report.get("metrics", {}), dict) else {}
        artifact_blockers = artifact.get("blockers", []) if isinstance(artifact.get("blockers", []), list) else []
        report_blockers = report.get("blockers", []) if isinstance(report.get("blockers", []), list) else []

        chain.append({
            "checkpoint": item["checkpoint"],
            "name": item["name"],
            "report_available": report_available,
            "artifact_available": artifact_available,
            "report_path": rel(item["report"]),
            "artifact_path": rel(item["artifact"]),
            "report_status": report.get("status", "missing") if report_available else "missing",
            "artifact_status": artifact.get("status", "missing") if artifact_available else "missing",
            "report_ok": report.get("ok", None) if report_available else None,
            "artifact_ok": artifact.get("ok", None) if artifact_available else None,
            "report_hash": stable_hash(report) if report_available else "",
            "artifact_hash": stable_hash(artifact) if artifact_available else "",
            "destructive_flag_present": flag_true(report, destructive_keys) or flag_true(artifact, destructive_keys),
            "report_metrics": report_metrics,
            "blockers": report_blockers + artifact_blockers,
            "source_refs": {
                "report": source_ref(item["report"]),
                "artifact": source_ref(item["artifact"])
            }
        })

    return chain


def aggregate_metrics(chain: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "checkpoint_count": len(chain),
        "available_report_count": 0,
        "available_artifact_count": 0,
        "missing_report_count": 0,
        "missing_artifact_count": 0,
        "destructive_flag_count": 0,
        "recovery_execution_count": 0,
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0,
        "raw_payload_count": 0
    }

    for item in chain:
        if item.get("report_available"):
            totals["available_report_count"] += 1
        else:
            totals["missing_report_count"] += 1

        if item.get("artifact_available"):
            totals["available_artifact_count"] += 1
        else:
            totals["missing_artifact_count"] += 1

        if item.get("destructive_flag_present"):
            totals["destructive_flag_count"] += 1

        metrics = item.get("report_metrics", {})

        aliases = {
            "recovery_execution_count": ["recovery_execution_count"],
            "rollback_execution_count": ["rollback_execution_count"],
            "data_delete_count": ["data_delete_count"],
            "target_file_modify_count": ["target_file_modify_count", "file_modify_count"],
            "git_reset_count": ["git_reset_count"],
            "git_force_push_count": ["git_force_push_count"],
            "shell_execution_count": ["shell_execution_count"],
            "raw_payload_count": ["raw_payload_count"]
        }

        for target, keys in aliases.items():
            for key in keys:
                value = metrics.get(key, 0)
                try:
                    totals[target] += int(value)
                except Exception:
                    pass

    return totals


def collect_blockers(chain: list[dict[str, Any]], totals: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = []

    for item in chain:
        if not item.get("report_available"):
            blockers.append({"checkpoint": item.get("checkpoint"), "blocker": "report_missing"})

        if not item.get("artifact_available"):
            blockers.append({"checkpoint": item.get("checkpoint"), "blocker": "artifact_missing"})

        if item.get("destructive_flag_present"):
            blockers.append({"checkpoint": item.get("checkpoint"), "blocker": "destructive_flag_present"})

        for blocker in item.get("blockers", []):
            blockers.append({"checkpoint": item.get("checkpoint"), "blocker": str(blocker)})

    if totals.get("recovery_execution_count", 0) != 0:
        blockers.append({"checkpoint": "aggregate", "blocker": "recovery_execution_count_not_zero"})

    if totals.get("rollback_execution_count", 0) != 0:
        blockers.append({"checkpoint": "aggregate", "blocker": "rollback_execution_count_not_zero"})

    if totals.get("git_reset_count", 0) != 0:
        blockers.append({"checkpoint": "aggregate", "blocker": "git_reset_count_not_zero"})

    if totals.get("git_force_push_count", 0) != 0:
        blockers.append({"checkpoint": "aggregate", "blocker": "git_force_push_count_not_zero"})

    if totals.get("shell_execution_count", 0) != 0:
        blockers.append({"checkpoint": "aggregate", "blocker": "shell_execution_count_not_zero"})

    return blockers


def create_summary(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    summary_id = "rgs2_" + uuid.uuid4().hex[:12]
    chain = collect_chain()
    totals = aggregate_metrics(chain)
    blockers = collect_blockers(chain, totals)

    no_recovery = totals["recovery_execution_count"] == 0
    no_rollback = totals["rollback_execution_count"] == 0
    no_delete = totals["data_delete_count"] == 0
    no_modify = totals["target_file_modify_count"] == 0
    no_reset = totals["git_reset_count"] == 0
    no_force = totals["git_force_push_count"] == 0
    no_shell = totals["shell_execution_count"] == 0

    safety_ok = all([no_recovery, no_rollback, no_delete, no_modify, no_reset, no_force, no_shell])
    evidence_ok = totals["missing_report_count"] == 0 and totals["missing_artifact_count"] == 0

    summary_body = {
        "summary_id": summary_id,
        "covered_checkpoints": policy.get("covered_checkpoints", []),
        "chain_hashes": [
            {
                "checkpoint": item.get("checkpoint"),
                "report_hash": item.get("report_hash"),
                "artifact_hash": item.get("artifact_hash")
            }
            for item in chain
        ],
        "totals": totals,
        "safety_ok": safety_ok,
        "evidence_ok": evidence_ok
    }

    status = "closed_safe" if safety_ok and evidence_ok else "closed_with_review_required"

    summary = {
        "ok": True,
        "checkpoint": "069",
        "module": "k_os_agent_recovery_governance_summary_core",
        "status": status,
        "summary_id": summary_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "recovery_governance_summary_061_068",
        "covered_checkpoints": policy.get("covered_checkpoints", []),
        "chain": chain,
        "totals": totals,
        "consolidated_blockers": blockers,
        "recovery_governance_summary_hash": stable_hash(summary_body),
        "evidence_chain_complete": evidence_ok,
        "no_recovery_executed": no_recovery,
        "no_rollback_executed": no_rollback,
        "no_data_deleted": no_delete,
        "no_target_files_modified": no_modify,
        "no_git_reset_executed": no_reset,
        "no_git_force_push_executed": no_force,
        "no_shell_executed": no_shell,
        "summary_executes_recovery": False,
        "summary_executes_rollback": False,
        "summary_deletes_data": False,
        "summary_modifies_target_files": False,
        "summary_runs_git_reset": False,
        "summary_runs_git_force_push": False,
        "summary_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_governance_summary": policy.get("required_gates_before_recovery_governance_summary", []),
        "next_checkpoint": policy.get("next_checkpoint", "070 - K-Agent Recovery Layer Closure Core")
    }

    state.setdefault("summaries", []).append(summary)
    state["summaries"] = state["summaries"][-300:]
    save_state(state)

    write_summary(summary)

    event("recovery_governance_summary.created", {
        "summary_id": summary_id,
        "status": status,
        "safety_ok": safety_ok,
        "evidence_ok": evidence_ok,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_summary_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("summaries", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    summary = latest_summary_raw()
    blockers = []
    warnings = []

    if not summary:
        blockers.append("recovery_governance_summary_not_found")
    else:
        required = [
            ("summary_id", "summary_id_missing"),
            ("recovery_governance_summary_hash", "summary_hash_missing")
        ]

        for key, blocker in required:
            if not summary.get(key):
                blockers.append(blocker)

        totals = summary.get("totals", {})

        zero_required = [
            ("recovery_execution_count", "recovery_execution_count_not_zero"),
            ("rollback_execution_count", "rollback_execution_count_not_zero"),
            ("data_delete_count", "data_delete_count_not_zero"),
            ("target_file_modify_count", "target_file_modify_count_not_zero"),
            ("git_reset_count", "git_reset_count_not_zero"),
            ("git_force_push_count", "git_force_push_count_not_zero"),
            ("shell_execution_count", "shell_execution_count_not_zero")
        ]

        for key, blocker in zero_required:
            if int(totals.get(key, 0) or 0) != 0:
                blockers.append(blocker)

        destructive_keys = [
            "summary_executes_recovery",
            "summary_executes_rollback",
            "summary_deletes_data",
            "summary_modifies_target_files",
            "summary_runs_git_reset",
            "summary_runs_git_force_push",
            "summary_executes_shell_commands",
            "raw_payload_included",
            "local_recovery_token_included"
        ]

        for key in destructive_keys:
            if summary.get(key) is True:
                blockers.append(key)

        if not summary.get("evidence_chain_complete"):
            warnings.append("evidence_chain_incomplete_or_review_required")

        if summary.get("consolidated_blockers"):
            warnings.append("summary_contains_non_destructive_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "069",
        "module": "k_os_agent_recovery_governance_summary_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "summary_id": summary.get("summary_id") if summary else "",
        "summary_status": summary.get("status") if summary else "",
        "recovery_governance_summary_hash": summary.get("recovery_governance_summary_hash") if summary else "",
        "no_recovery_executed": summary.get("no_recovery_executed") if summary else False,
        "no_rollback_executed": summary.get("no_rollback_executed") if summary else False,
        "no_data_deleted": summary.get("no_data_deleted") if summary else False,
        "no_target_files_modified": summary.get("no_target_files_modified") if summary else False,
        "no_git_reset_executed": summary.get("no_git_reset_executed") if summary else False,
        "no_git_force_push_executed": summary.get("no_git_force_push_executed") if summary else False,
        "no_shell_executed": summary.get("no_shell_executed") if summary else False,
        "summary_executes_recovery": False,
        "summary_executes_rollback": False,
        "summary_deletes_data": False,
        "summary_modifies_target_files": False,
        "summary_runs_git_reset": False,
        "summary_runs_git_force_push": False,
        "summary_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if summary and len(blockers) == 0:
        summary["validated_at"] = validation["generated_at"]
        summary["validated"] = True

    save_state(state)
    write_validation(validation)

    event("recovery_governance_summary.validation_completed", {
        "summary_id": validation.get("summary_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": item.get("summary_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "covered_checkpoints": item.get("covered_checkpoints"),
        "recovery_governance_summary_hash": item.get("recovery_governance_summary_hash"),
        "evidence_chain_complete": item.get("evidence_chain_complete"),
        "no_recovery_executed": item.get("no_recovery_executed"),
        "no_rollback_executed": item.get("no_rollback_executed"),
        "no_data_deleted": item.get("no_data_deleted"),
        "no_target_files_modified": item.get("no_target_files_modified"),
        "no_git_reset_executed": item.get("no_git_reset_executed"),
        "no_git_force_push_executed": item.get("no_git_force_push_executed"),
        "no_shell_executed": item.get("no_shell_executed"),
        "summary_executes_recovery": False,
        "summary_executes_rollback": False,
        "summary_deletes_data": False,
        "summary_modifies_target_files": False,
        "summary_runs_git_reset": False,
        "summary_runs_git_force_push": False,
        "summary_executes_shell_commands": False,
        "blocker_count": len(item.get("consolidated_blockers", []))
    }


def compute_metrics(summaries: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary_count": len(summaries),
        "validation_count": len(validations),
        "closed_safe_count": len([x for x in summaries if x.get("status") == "closed_safe"]),
        "closed_with_review_required_count": len([x for x in summaries if x.get("status") == "closed_with_review_required"]),
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

    summaries = [safe_summary(item) for item in reversed(state.get("summaries", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(summaries, validations)

    report = {
        "ok": True,
        "checkpoint": "069",
        "module": "k_os_agent_recovery_governance_summary_core",
        "status": "audit_generated",
        "generated_at": now(),
        "summary_state_path": "local_secrets/k_os_recovery_governance_summary/agent_recovery_governance_summary_state.json",
        "summary_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "summary_executes_recovery": False,
        "summary_executes_rollback": False,
        "summary_deletes_data": False,
        "summary_modifies_target_files": False,
        "summary_runs_git_reset": False,
        "summary_runs_git_force_push": False,
        "summary_executes_shell_commands": False,
        "covered_checkpoints": policy.get("covered_checkpoints", []),
        "input_availability": [source_ref(item["report"]) for item in INPUTS],
        "metrics": metrics,
        "recent_summaries": summaries,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_governance_summary": policy.get("required_gates_before_recovery_governance_summary", []),
        "next_checkpoint": policy.get("next_checkpoint", "070 - K-Agent Recovery Layer Closure Core")
    }

    write_report(report)
    event("recovery_governance_summary.audit_generated", {
        "summary_count": metrics.get("summary_count")
    })
    return report


def write_summary(summary: dict[str, Any]) -> None:
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Governance Summary",
        "",
        "- Summary ID: " + str(summary.get("summary_id")),
        "- Status: " + str(summary.get("status")),
        "- Hash: " + str(summary.get("recovery_governance_summary_hash")),
        "- Covered checkpoints: " + ", ".join(summary.get("covered_checkpoints", [])),
        "- Evidence chain complete: " + str(summary.get("evidence_chain_complete")),
        "- No recovery executed: " + str(summary.get("no_recovery_executed")),
        "- No rollback executed: " + str(summary.get("no_rollback_executed")),
        "- No data deleted: " + str(summary.get("no_data_deleted")),
        "- No target files modified: " + str(summary.get("no_target_files_modified")),
        "- No git reset executed: " + str(summary.get("no_git_reset_executed")),
        "- No force push executed: " + str(summary.get("no_git_force_push_executed")),
        "- No shell executed: " + str(summary.get("no_shell_executed")),
        "",
        "## Totals",
        ""
    ]

    for key, value in summary.get("totals", {}).items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Evidence chain", ""])

    for item in summary.get("chain", []):
        lines.append(
            "- " + str(item.get("checkpoint")) +
            " | " + str(item.get("name")) +
            " | report=" + str(item.get("report_available")) +
            " | artifact=" + str(item.get("artifact_available")) +
            " | status=" + str(item.get("artifact_status"))
        )

    lines.extend(["", "## Consolidated blockers", ""])

    if summary.get("consolidated_blockers"):
        for item in summary.get("consolidated_blockers", []):
            lines.append("- " + str(item.get("checkpoint")) + ": " + str(item.get("blocker")))
    else:
        lines.append("- Nenhum blocker.")

    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Governance Summary Validation",
        "",
        "- Summary ID: " + str(result.get("summary_id")),
        "- Status: " + str(result.get("status")),
        "- Summary status: " + str(result.get("summary_status")),
        "- Hash: " + str(result.get("recovery_governance_summary_hash")),
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
        "# K-OS Agent Recovery Governance Summary Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("summary_state_committed")),
        "- Executes recovery: " + str(report.get("summary_executes_recovery")),
        "- Executes rollback: " + str(report.get("summary_executes_rollback")),
        "- Deletes data: " + str(report.get("summary_deletes_data")),
        "- Modifies target files: " + str(report.get("summary_modifies_target_files")),
        "- Runs git reset: " + str(report.get("summary_runs_git_reset")),
        "- Runs git force push: " + str(report.get("summary_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("summary_executes_shell_commands")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent summaries", ""])

    if report.get("recent_summaries"):
        for item in report.get("recent_summaries", [])[:30]:
            lines.append(
                "- " + str(item.get("summary_id")) +
                " | status=" + str(item.get("status")) +
                " | evidence=" + str(item.get("evidence_chain_complete")) +
                " | blockers=" + str(item.get("blocker_count"))
            )
    else:
        lines.append("- Nenhum resumo.")

    lines.extend(["", "## Required gates before recovery governance summary", ""])

    for gate in report.get("required_gates_before_recovery_governance_summary", []):
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
    parser.add_argument("--mode", choices=["init", "summarize", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "summarize":
        result = create_summary(args.operator, args.reason)

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