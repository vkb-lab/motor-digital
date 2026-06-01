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

POLICY_PATH = ROOT / "config" / "rollback_governance_summary" / "k_os_agent_rollback_governance_summary_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_rollback_governance_summary"
STATE_PATH = STATE_DIR / "agent_rollback_governance_summary_state.json"

REPORT_DIR = ROOT / "reports" / "rollback_governance_summary"
MEMORY_DIR = ROOT / "memory" / "rollback_governance_summary"

LATEST_JSON = REPORT_DIR / "latest_agent_rollback_governance_summary_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_rollback_governance_summary_report.md"
SUMMARY_JSON = REPORT_DIR / "latest_rollback_governance_summary.json"
SUMMARY_MD = REPORT_DIR / "latest_rollback_governance_summary.md"
VALIDATION_JSON = REPORT_DIR / "latest_rollback_governance_summary_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_rollback_governance_summary_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

INPUTS = [
    {
        "checkpoint": "053",
        "name": "Rollback Preparation Core",
        "path": ROOT / "reports" / "rollback_preparation" / "latest_agent_rollback_preparation_report.json",
        "artifact": ROOT / "reports" / "rollback_preparation" / "latest_rollback_plan.json"
    },
    {
        "checkpoint": "054",
        "name": "Rollback Approval and Release Gate Core",
        "path": ROOT / "reports" / "rollback_release_gate" / "latest_agent_rollback_release_gate_report.json",
        "artifact": ROOT / "reports" / "rollback_release_gate" / "latest_rollback_release_record.json"
    },
    {
        "checkpoint": "055",
        "name": "Rollback Dry Run Simulator Core",
        "path": ROOT / "reports" / "rollback_dry_run" / "latest_agent_rollback_dry_run_report.json",
        "artifact": ROOT / "reports" / "rollback_dry_run" / "latest_rollback_dry_run_simulation.json"
    },
    {
        "checkpoint": "056",
        "name": "Rollback Execution Final Gate Core",
        "path": ROOT / "reports" / "rollback_final_gate" / "latest_agent_rollback_final_gate_report.json",
        "artifact": ROOT / "reports" / "rollback_final_gate" / "latest_rollback_final_gate_record.json"
    },
    {
        "checkpoint": "057",
        "name": "Rollback Manual Execution Stub Core",
        "path": ROOT / "reports" / "rollback_manual_stub" / "latest_agent_rollback_manual_stub_report.json",
        "artifact": ROOT / "reports" / "rollback_manual_stub" / "latest_rollback_manual_stub_record.json"
    },
    {
        "checkpoint": "058",
        "name": "Rollback Controlled Execution Sandbox Core",
        "path": ROOT / "reports" / "rollback_sandbox" / "latest_agent_rollback_sandbox_report.json",
        "artifact": ROOT / "reports" / "rollback_sandbox" / "latest_rollback_sandbox_record.json"
    },
    {
        "checkpoint": "059",
        "name": "Rollback Sandbox Report and Operator Review Core",
        "path": ROOT / "reports" / "rollback_sandbox_review" / "latest_agent_rollback_sandbox_review_report.json",
        "artifact": ROOT / "reports" / "rollback_sandbox_review" / "latest_rollback_sandbox_operator_review.json"
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
        raise RuntimeError("Rollback governance summary policy not found.")
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
            "summary_executes_rollback": False,
            "summary_deletes_data": False,
            "summary_modifies_target_files": False,
            "summaries": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load rollback governance summary state.")
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
        "generated_at": data.get("generated_at", data.get("created_at", "")),
        "hash": stable_hash(data)
    }


def metric_value(report: dict[str, Any], key: str) -> int:
    metrics = report.get("metrics", {})
    value = metrics.get(key, 0)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except Exception:
        return 0


def execution_flags(report: dict[str, Any]) -> dict[str, bool]:
    keys = [
        "rollback_executes_changes",
        "release_gate_executes_rollback",
        "dry_run_executes_rollback",
        "final_gate_executes_rollback",
        "manual_stub_executes_rollback",
        "sandbox_executes_rollback",
        "review_executes_rollback",
        "summary_executes_rollback",
        "rollback_deletes_data",
        "release_gate_deletes_data",
        "dry_run_deletes_data",
        "final_gate_deletes_data",
        "manual_stub_deletes_data",
        "sandbox_deletes_data",
        "review_deletes_data",
        "summary_deletes_data",
        "rollback_modifies_files",
        "release_gate_modifies_files",
        "dry_run_modifies_files",
        "final_gate_modifies_files",
        "manual_stub_modifies_files",
        "sandbox_modifies_target_files",
        "review_modifies_target_files",
        "summary_modifies_target_files",
        "dry_run_runs_git_reset",
        "final_gate_runs_git_reset",
        "manual_stub_runs_git_reset",
        "sandbox_runs_git_reset",
        "review_runs_git_reset",
        "summary_runs_git_reset",
        "dry_run_runs_git_force_push",
        "final_gate_runs_git_force_push",
        "manual_stub_runs_git_force_push",
        "sandbox_runs_git_force_push",
        "review_runs_git_force_push",
        "summary_runs_git_force_push",
        "sandbox_executes_shell_commands",
        "review_executes_shell_commands",
        "summary_executes_shell_commands"
    ]

    return {key: bool(report.get(key, False)) for key in keys if key in report}


def collect_chain() -> list[dict[str, Any]]:
    chain = []

    for item in INPUTS:
        report = read_json(item["path"]) or {}
        artifact = read_json(item["artifact"]) or {}

        available = bool(report) and not report.get("_read_error")
        artifact_available = bool(artifact) and not artifact.get("_read_error")

        flags = execution_flags(report)

        chain.append({
            "checkpoint": item["checkpoint"],
            "name": item["name"],
            "report_available": available,
            "artifact_available": artifact_available,
            "report_path": rel(item["path"]),
            "artifact_path": rel(item["artifact"]),
            "report_status": report.get("status", "missing") if available else "missing",
            "artifact_status": artifact.get("status", "missing") if artifact_available else "missing",
            "report_ok": report.get("ok", None) if available else None,
            "artifact_ok": artifact.get("ok", None) if artifact_available else None,
            "report_hash": stable_hash(report) if available else "",
            "artifact_hash": stable_hash(artifact) if artifact_available else "",
            "execution_flags": flags,
            "metrics": report.get("metrics", {}) if available else {},
            "source_refs": {
                "report": source_ref(item["path"]),
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
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "file_modify_count": 0,
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

        metrics = item.get("metrics", {})

        for key in [
            "rollback_execution_count",
            "data_delete_count",
            "target_file_modify_count",
            "file_modify_count",
            "git_reset_count",
            "git_force_push_count",
            "shell_execution_count",
            "raw_payload_count"
        ]:
            value = metrics.get(key, 0)
            try:
                totals[key] += int(value)
            except Exception:
                pass

    return totals


def collect_blockers(chain: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blockers = []

    for item in chain:
        if not item.get("report_available"):
            blockers.append({
                "checkpoint": item.get("checkpoint"),
                "blocker": "report_missing"
            })

        if not item.get("artifact_available"):
            blockers.append({
                "checkpoint": item.get("checkpoint"),
                "blocker": "artifact_missing"
            })

        metrics = item.get("metrics", {})
        status_counts = metrics.get("status_counts", {})
        if isinstance(status_counts, dict):
            if int(status_counts.get("blocked", 0) or 0) > 0:
                blockers.append({
                    "checkpoint": item.get("checkpoint"),
                    "blocker": "blocked_status_present"
                })

        flags = item.get("execution_flags", {})
        for key, value in flags.items():
            if value is True:
                blockers.append({
                    "checkpoint": item.get("checkpoint"),
                    "blocker": key
                })

    return blockers


def create_summary(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    summary_id = "rgs_" + uuid.uuid4().hex[:12]
    chain = collect_chain()
    totals = aggregate_metrics(chain)
    blockers = collect_blockers(chain)

    no_real_rollback = (
        totals["rollback_execution_count"] == 0 and
        totals["data_delete_count"] == 0 and
        totals["target_file_modify_count"] == 0 and
        totals["file_modify_count"] == 0 and
        totals["git_reset_count"] == 0 and
        totals["git_force_push_count"] == 0 and
        totals["shell_execution_count"] == 0
    )

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
        "no_real_rollback": no_real_rollback
    }

    status = "closed_safe" if no_real_rollback and totals["missing_report_count"] == 0 else "closed_with_blockers"

    summary = {
        "ok": True,
        "checkpoint": "060",
        "module": "k_os_agent_rollback_governance_summary_core",
        "status": status,
        "summary_id": summary_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "rollback_governance_summary",
        "covered_checkpoints": policy.get("covered_checkpoints", []),
        "chain": chain,
        "totals": totals,
        "consolidated_blockers": blockers,
        "rollback_governance_summary_hash": stable_hash(summary_body),
        "no_real_rollback_executed": no_real_rollback,
        "no_data_deleted": totals["data_delete_count"] == 0,
        "no_target_files_modified": totals["target_file_modify_count"] == 0 and totals["file_modify_count"] == 0,
        "no_git_reset_executed": totals["git_reset_count"] == 0,
        "no_git_force_push_executed": totals["git_force_push_count"] == 0,
        "no_shell_execution": totals["shell_execution_count"] == 0,
        "summary_executes_rollback": False,
        "summary_deletes_data": False,
        "summary_modifies_target_files": False,
        "summary_runs_git_reset": False,
        "summary_runs_git_force_push": False,
        "summary_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_governance_summary": policy.get("required_gates_before_governance_summary", []),
        "next_checkpoint": policy.get("next_checkpoint", "061 - K-Agent Recovery Readiness Matrix Core")
    }

    state.setdefault("summaries", []).append(summary)
    state["summaries"] = state["summaries"][-300:]
    save_state(state)

    write_summary(summary)

    event("rollback_governance_summary.created", {
        "summary_id": summary_id,
        "status": status,
        "no_real_rollback_executed": no_real_rollback,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_summary_raw() -> dict[str, Any] | None:
    state = ensure_state()
    summaries = state.get("summaries", [])
    if not summaries:
        return None
    return summaries[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    summary = latest_summary_raw()
    blockers = []
    warnings = []

    if not summary:
        blockers.append("governance_summary_not_found")
    else:
        if not summary.get("summary_id"):
            blockers.append("summary_id_missing")

        if not summary.get("rollback_governance_summary_hash"):
            blockers.append("summary_hash_missing")

        totals = summary.get("totals", {})

        if int(totals.get("missing_report_count", 0) or 0) > 0:
            blockers.append("missing_report_count_not_zero")

        if int(totals.get("rollback_execution_count", 0) or 0) != 0:
            blockers.append("rollback_execution_count_not_zero")

        if int(totals.get("data_delete_count", 0) or 0) != 0:
            blockers.append("data_delete_count_not_zero")

        if int(totals.get("target_file_modify_count", 0) or 0) != 0:
            blockers.append("target_file_modify_count_not_zero")

        if int(totals.get("git_reset_count", 0) or 0) != 0:
            blockers.append("git_reset_count_not_zero")

        if int(totals.get("git_force_push_count", 0) or 0) != 0:
            blockers.append("git_force_push_count_not_zero")

        if int(totals.get("shell_execution_count", 0) or 0) != 0:
            blockers.append("shell_execution_count_not_zero")

        if summary.get("summary_executes_rollback") is True:
            blockers.append("summary_executes_rollback")

        if summary.get("summary_deletes_data") is True:
            blockers.append("summary_deletes_data")

        if summary.get("summary_modifies_target_files") is True:
            blockers.append("summary_modifies_target_files")

        if summary.get("summary_runs_git_reset") is True:
            blockers.append("summary_runs_git_reset")

        if summary.get("summary_runs_git_force_push") is True:
            blockers.append("summary_runs_git_force_push")

        if summary.get("summary_executes_shell_commands") is True:
            blockers.append("summary_executes_shell_commands")

        if summary.get("consolidated_blockers"):
            warnings.append("governance_summary_contains_non_destructive_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "060",
        "module": "k_os_agent_rollback_governance_summary_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "summary_id": summary.get("summary_id") if summary else "",
        "summary_status": summary.get("status") if summary else "",
        "rollback_governance_summary_hash": summary.get("rollback_governance_summary_hash") if summary else "",
        "no_real_rollback_executed": summary.get("no_real_rollback_executed") if summary else False,
        "no_data_deleted": summary.get("no_data_deleted") if summary else False,
        "no_target_files_modified": summary.get("no_target_files_modified") if summary else False,
        "no_git_reset_executed": summary.get("no_git_reset_executed") if summary else False,
        "no_git_force_push_executed": summary.get("no_git_force_push_executed") if summary else False,
        "no_shell_execution": summary.get("no_shell_execution") if summary else False,
        "summary_executes_rollback": False,
        "summary_deletes_data": False,
        "summary_modifies_target_files": False,
        "summary_runs_git_reset": False,
        "summary_runs_git_force_push": False,
        "summary_executes_shell_commands": False,
        "release_token_included": False,
        "raw_payload_included": False,
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

    event("rollback_governance_summary.validation_completed", {
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
        "rollback_governance_summary_hash": item.get("rollback_governance_summary_hash"),
        "covered_checkpoints": item.get("covered_checkpoints"),
        "totals": item.get("totals"),
        "no_real_rollback_executed": item.get("no_real_rollback_executed"),
        "no_data_deleted": item.get("no_data_deleted"),
        "no_target_files_modified": item.get("no_target_files_modified"),
        "no_git_reset_executed": item.get("no_git_reset_executed"),
        "no_git_force_push_executed": item.get("no_git_force_push_executed"),
        "no_shell_execution": item.get("no_shell_execution"),
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
        "closed_with_blockers_count": len([x for x in summaries if x.get("status") == "closed_with_blockers"]),
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0,
        "raw_payload_count": 0
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    summaries = [safe_summary(item) for item in reversed(state.get("summaries", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(summaries, validations)

    report = {
        "ok": True,
        "checkpoint": "060",
        "module": "k_os_agent_rollback_governance_summary_core",
        "status": "audit_generated",
        "generated_at": now(),
        "summary_state_path": "local_secrets/k_os_rollback_governance_summary/agent_rollback_governance_summary_state.json",
        "summary_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "summary_executes_rollback": False,
        "summary_deletes_data": False,
        "summary_modifies_target_files": False,
        "summary_runs_git_reset": False,
        "summary_runs_git_force_push": False,
        "summary_executes_shell_commands": False,
        "covered_checkpoints": policy.get("covered_checkpoints", []),
        "input_availability": [source_ref(item["path"]) for item in INPUTS],
        "metrics": metrics,
        "recent_summaries": summaries,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_governance_summary": policy.get("required_gates_before_governance_summary", []),
        "next_checkpoint": policy.get("next_checkpoint", "061 - K-Agent Recovery Readiness Matrix Core")
    }

    write_report(report)
    event("rollback_governance_summary.audit_generated", {
        "summary_count": metrics.get("summary_count")
    })
    return report


def write_summary(summary: dict[str, Any]) -> None:
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Governance Summary",
        "",
        "- Summary ID: " + str(summary.get("summary_id")),
        "- Status: " + str(summary.get("status")),
        "- Hash: " + str(summary.get("rollback_governance_summary_hash")),
        "- Covered checkpoints: " + ", ".join(summary.get("covered_checkpoints", [])),
        "- No real rollback executed: " + str(summary.get("no_real_rollback_executed")),
        "- No data deleted: " + str(summary.get("no_data_deleted")),
        "- No target files modified: " + str(summary.get("no_target_files_modified")),
        "- No git reset executed: " + str(summary.get("no_git_reset_executed")),
        "- No force push executed: " + str(summary.get("no_git_force_push_executed")),
        "- No shell execution: " + str(summary.get("no_shell_execution")),
        "",
        "## Totals",
        ""
    ]

    for key, value in summary.get("totals", {}).items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Chain", ""])

    for item in summary.get("chain", []):
        lines.append(
            "- " + str(item.get("checkpoint")) +
            " | " + str(item.get("name")) +
            " | report=" + str(item.get("report_available")) +
            " | artifact=" + str(item.get("artifact_available")) +
            " | status=" + str(item.get("report_status"))
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
        "# K-OS Rollback Governance Summary Validation",
        "",
        "- Summary ID: " + str(result.get("summary_id")),
        "- Status: " + str(result.get("status")),
        "- Summary status: " + str(result.get("summary_status")),
        "- Hash: " + str(result.get("rollback_governance_summary_hash")),
        "- No real rollback executed: " + str(result.get("no_real_rollback_executed")),
        "- No data deleted: " + str(result.get("no_data_deleted")),
        "- No target files modified: " + str(result.get("no_target_files_modified")),
        "- No git reset executed: " + str(result.get("no_git_reset_executed")),
        "- No force push executed: " + str(result.get("no_git_force_push_executed")),
        "- No shell execution: " + str(result.get("no_shell_execution")),
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
        "# K-OS Agent Rollback Governance Summary Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("summary_state_committed")),
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
                " | no_rollback=" + str(item.get("no_real_rollback_executed")) +
                " | blockers=" + str(item.get("blocker_count"))
            )
    else:
        lines.append("- Nenhum resumo.")

    lines.extend(["", "## Required gates before governance summary", ""])

    for gate in report.get("required_gates_before_governance_summary", []):
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