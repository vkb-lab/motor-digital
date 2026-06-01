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

POLICY_PATH = ROOT / "config" / "recovery_readiness_matrix" / "k_os_agent_recovery_readiness_matrix_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_recovery_readiness_matrix"
STATE_PATH = STATE_DIR / "agent_recovery_readiness_matrix_state.json"

REPORT_DIR = ROOT / "reports" / "recovery_readiness_matrix"
MEMORY_DIR = ROOT / "memory" / "recovery_readiness_matrix"

LATEST_JSON = REPORT_DIR / "latest_agent_recovery_readiness_matrix_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_recovery_readiness_matrix_report.md"
MATRIX_JSON = REPORT_DIR / "latest_recovery_readiness_matrix.json"
MATRIX_MD = REPORT_DIR / "latest_recovery_readiness_matrix.md"
VALIDATION_JSON = REPORT_DIR / "latest_recovery_readiness_matrix_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_recovery_readiness_matrix_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

GOVERNANCE_SUMMARY = ROOT / "reports" / "rollback_governance_summary" / "latest_rollback_governance_summary.json"
GOVERNANCE_VALIDATION = ROOT / "reports" / "rollback_governance_summary" / "latest_rollback_governance_summary_validation_report.json"
GOVERNANCE_REPORT = ROOT / "reports" / "rollback_governance_summary" / "latest_agent_rollback_governance_summary_report.json"

SANDBOX_REVIEW = ROOT / "reports" / "rollback_sandbox_review" / "latest_rollback_sandbox_operator_review.json"
SANDBOX_SUMMARY = ROOT / "reports" / "rollback_sandbox_review" / "latest_rollback_sandbox_executive_summary.json"
SANDBOX_RECORD = ROOT / "reports" / "rollback_sandbox" / "latest_rollback_sandbox_record.json"
MANUAL_STUB = ROOT / "reports" / "rollback_manual_stub" / "latest_rollback_manual_stub_record.json"
FINAL_GATE = ROOT / "reports" / "rollback_final_gate" / "latest_rollback_final_gate_record.json"
DRY_RUN = ROOT / "reports" / "rollback_dry_run" / "latest_rollback_dry_run_simulation.json"
RELEASE_RECORD = ROOT / "reports" / "rollback_release_gate" / "latest_rollback_release_record.json"
ROLLBACK_PLAN = ROOT / "reports" / "rollback_preparation" / "latest_rollback_plan.json"


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
        raise RuntimeError("Recovery readiness matrix policy not found.")
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
            "readiness_executes_recovery": False,
            "readiness_executes_rollback": False,
            "matrices": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load recovery readiness matrix state.")
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


def load_governance_summary() -> dict[str, Any]:
    data = read_json(GOVERNANCE_SUMMARY)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "summary_id": "",
        "rollback_governance_summary_hash": "",
        "consolidated_blockers": ["rollback_governance_summary_missing"]
    }


def score_dimension(name: str, ok: bool, weight: int, blockers: list[str]) -> dict[str, Any]:
    score = weight if ok else 0
    return {
        "dimension": name,
        "ok": ok,
        "weight": weight,
        "score": score,
        "blockers": blockers
    }


def build_matrix(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    governance = load_governance_summary()
    sandbox_review = read_json(SANDBOX_REVIEW) or {}
    sandbox_summary = read_json(SANDBOX_SUMMARY) or {}

    totals = governance.get("totals", {}) if isinstance(governance.get("totals", {}), dict) else {}
    consolidated_blockers = governance.get("consolidated_blockers", [])

    governance_available = bool(governance.get("summary_id")) and bool(governance.get("rollback_governance_summary_hash"))
    operator_review_available = bool(sandbox_review.get("review_id"))
    sandbox_summary_available = bool(sandbox_summary.get("review_id")) or bool(sandbox_summary.get("sandbox_id"))

    no_real_rollback = bool(governance.get("no_real_rollback_executed", False))
    no_data_deleted = bool(governance.get("no_data_deleted", False))
    no_files_modified = bool(governance.get("no_target_files_modified", False))
    no_git_reset = bool(governance.get("no_git_reset_executed", False))
    no_force_push = bool(governance.get("no_git_force_push_executed", False))
    no_shell = bool(governance.get("no_shell_execution", False))

    missing_reports = int(totals.get("missing_report_count", 0) or 0)
    evidence_complete = missing_reports == 0 and governance_available

    matrix_id = "rrm_" + uuid.uuid4().hex[:12]

    dimensions = [
        score_dimension(
            "governance_chain",
            governance_available and missing_reports == 0,
            20,
            [] if governance_available and missing_reports == 0 else ["governance_chain_incomplete"]
        ),
        score_dimension(
            "evidence_integrity",
            evidence_complete,
            15,
            [] if evidence_complete else ["evidence_chain_incomplete"]
        ),
        score_dimension(
            "operator_review",
            operator_review_available and sandbox_summary_available,
            15,
            [] if operator_review_available and sandbox_summary_available else ["operator_review_missing"]
        ),
        score_dimension(
            "rollback_safety",
            no_real_rollback and no_git_reset and no_force_push,
            20,
            [] if no_real_rollback and no_git_reset and no_force_push else ["rollback_safety_not_clean"]
        ),
        score_dimension(
            "sandbox_safety",
            no_shell,
            10,
            [] if no_shell else ["sandbox_shell_execution_detected"]
        ),
        score_dimension(
            "auditability",
            bool(governance.get("rollback_governance_summary_hash")),
            10,
            [] if governance.get("rollback_governance_summary_hash") else ["summary_hash_missing"]
        ),
        score_dimension(
            "data_protection",
            no_data_deleted and no_files_modified,
            5,
            [] if no_data_deleted and no_files_modified else ["data_or_file_change_detected"]
        ),
        score_dimension(
            "execution_blocking",
            True,
            5,
            []
        )
    ]

    readiness_score = sum(item["score"] for item in dimensions)
    max_score = sum(item["weight"] for item in dimensions)

    if readiness_score >= 90 and not consolidated_blockers:
        readiness_level = "controlled_ready"
    elif readiness_score >= 70:
        readiness_level = "review_required"
    elif readiness_score >= 50:
        readiness_level = "limited_ready"
    else:
        readiness_level = "not_ready"

    risk_level = "low" if readiness_level == "controlled_ready" else "medium" if readiness_level == "review_required" else "high"

    source_refs = {
        "governance_summary": source_ref(GOVERNANCE_SUMMARY),
        "governance_validation": source_ref(GOVERNANCE_VALIDATION),
        "governance_report": source_ref(GOVERNANCE_REPORT),
        "sandbox_review": source_ref(SANDBOX_REVIEW),
        "sandbox_summary": source_ref(SANDBOX_SUMMARY),
        "sandbox_record": source_ref(SANDBOX_RECORD),
        "manual_stub": source_ref(MANUAL_STUB),
        "final_gate": source_ref(FINAL_GATE),
        "dry_run": source_ref(DRY_RUN),
        "release_record": source_ref(RELEASE_RECORD),
        "rollback_plan": source_ref(ROLLBACK_PLAN)
    }

    matrix_body = {
        "matrix_id": matrix_id,
        "readiness_score": readiness_score,
        "max_score": max_score,
        "readiness_level": readiness_level,
        "risk_level": risk_level,
        "dimensions": dimensions,
        "source_refs": source_refs
    }

    matrix = {
        "ok": True,
        "checkpoint": "061",
        "module": "k_os_agent_recovery_readiness_matrix_core",
        "status": "matrix_generated",
        "matrix_id": matrix_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "recovery_readiness_matrix",
        "readiness_score": readiness_score,
        "max_score": max_score,
        "readiness_percent": round((readiness_score / max_score) * 100, 2) if max_score else 0,
        "readiness_level": readiness_level,
        "risk_level": risk_level,
        "dimensions": dimensions,
        "governance_summary_id": governance.get("summary_id", ""),
        "governance_summary_hash": governance.get("rollback_governance_summary_hash", ""),
        "evidence_chain_complete": evidence_complete,
        "operator_review_available": operator_review_available,
        "sandbox_summary_available": sandbox_summary_available,
        "no_real_rollback_executed": no_real_rollback,
        "no_data_deleted": no_data_deleted,
        "no_target_files_modified": no_files_modified,
        "no_git_reset_executed": no_git_reset,
        "no_git_force_push_executed": no_force_push,
        "no_shell_execution": no_shell,
        "readiness_matrix_hash": stable_hash(matrix_body),
        "readiness_executes_recovery": False,
        "readiness_executes_rollback": False,
        "readiness_deletes_data": False,
        "readiness_modifies_target_files": False,
        "readiness_runs_git_reset": False,
        "readiness_runs_git_force_push": False,
        "readiness_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "consolidated_blockers": consolidated_blockers,
        "source_refs": source_refs,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_readiness": policy.get("required_gates_before_recovery_readiness", []),
        "next_checkpoint": policy.get("next_checkpoint", "062 - K-Agent Recovery Plan Builder Core")
    }

    state.setdefault("matrices", []).append(matrix)
    state["matrices"] = state["matrices"][-300:]
    save_state(state)

    write_matrix(matrix)

    event("recovery_readiness_matrix.created", {
        "matrix_id": matrix_id,
        "readiness_score": readiness_score,
        "readiness_level": readiness_level,
        "risk_level": risk_level
    })

    return audit_report()


def latest_matrix_raw() -> dict[str, Any] | None:
    state = ensure_state()
    matrices = state.get("matrices", [])
    if not matrices:
        return None
    return matrices[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    matrix = latest_matrix_raw()
    blockers = []
    warnings = []

    if not matrix:
        blockers.append("readiness_matrix_not_found")
    else:
        if not matrix.get("matrix_id"):
            blockers.append("matrix_id_missing")

        if not matrix.get("readiness_matrix_hash"):
            blockers.append("readiness_matrix_hash_missing")

        if matrix.get("readiness_score", 0) <= 0:
            blockers.append("readiness_score_missing")

        if matrix.get("readiness_executes_recovery") is True:
            blockers.append("readiness_executes_recovery")

        if matrix.get("readiness_executes_rollback") is True:
            blockers.append("readiness_executes_rollback")

        if matrix.get("readiness_deletes_data") is True:
            blockers.append("readiness_deletes_data")

        if matrix.get("readiness_modifies_target_files") is True:
            blockers.append("readiness_modifies_target_files")

        if matrix.get("readiness_runs_git_reset") is True:
            blockers.append("readiness_runs_git_reset")

        if matrix.get("readiness_runs_git_force_push") is True:
            blockers.append("readiness_runs_git_force_push")

        if matrix.get("readiness_executes_shell_commands") is True:
            blockers.append("readiness_executes_shell_commands")

        if matrix.get("readiness_level") != "controlled_ready":
            warnings.append("recovery_readiness_requires_operator_review")

        if matrix.get("consolidated_blockers"):
            warnings.append("non_destructive_governance_blockers_present")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "061",
        "module": "k_os_agent_recovery_readiness_matrix_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "matrix_id": matrix.get("matrix_id") if matrix else "",
        "readiness_score": matrix.get("readiness_score") if matrix else 0,
        "readiness_level": matrix.get("readiness_level") if matrix else "",
        "risk_level": matrix.get("risk_level") if matrix else "",
        "readiness_matrix_hash": matrix.get("readiness_matrix_hash") if matrix else "",
        "readiness_executes_recovery": False,
        "readiness_executes_rollback": False,
        "readiness_deletes_data": False,
        "readiness_modifies_target_files": False,
        "readiness_runs_git_reset": False,
        "readiness_runs_git_force_push": False,
        "readiness_executes_shell_commands": False,
        "raw_payload_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if matrix and len(blockers) == 0:
        matrix["validated_at"] = validation["generated_at"]
        matrix["validated"] = True

    save_state(state)
    write_validation(validation)

    event("recovery_readiness_matrix.validation_completed", {
        "matrix_id": validation.get("matrix_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_matrix(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "matrix_id": item.get("matrix_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "readiness_score": item.get("readiness_score"),
        "max_score": item.get("max_score"),
        "readiness_percent": item.get("readiness_percent"),
        "readiness_level": item.get("readiness_level"),
        "risk_level": item.get("risk_level"),
        "readiness_matrix_hash": item.get("readiness_matrix_hash"),
        "evidence_chain_complete": item.get("evidence_chain_complete"),
        "operator_review_available": item.get("operator_review_available"),
        "readiness_executes_recovery": False,
        "readiness_executes_rollback": False,
        "readiness_deletes_data": False,
        "readiness_modifies_target_files": False,
        "readiness_runs_git_reset": False,
        "readiness_runs_git_force_push": False,
        "readiness_executes_shell_commands": False,
        "blocker_count": len(item.get("consolidated_blockers", []))
    }


def compute_metrics(matrices: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    level_counts: dict[str, int] = {}
    for item in matrices:
        level = item.get("readiness_level", "unknown")
        level_counts[level] = level_counts.get(level, 0) + 1

    return {
        "matrix_count": len(matrices),
        "validation_count": len(validations),
        "controlled_ready_count": level_counts.get("controlled_ready", 0),
        "review_required_count": level_counts.get("review_required", 0),
        "limited_ready_count": level_counts.get("limited_ready", 0),
        "not_ready_count": level_counts.get("not_ready", 0),
        "recovery_execution_count": 0,
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0,
        "level_counts": level_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    matrices = [safe_matrix(item) for item in reversed(state.get("matrices", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(matrices, validations)

    report = {
        "ok": True,
        "checkpoint": "061",
        "module": "k_os_agent_recovery_readiness_matrix_core",
        "status": "audit_generated",
        "generated_at": now(),
        "readiness_state_path": "local_secrets/k_os_recovery_readiness_matrix/agent_recovery_readiness_matrix_state.json",
        "readiness_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "readiness_executes_recovery": False,
        "readiness_executes_rollback": False,
        "readiness_deletes_data": False,
        "readiness_modifies_target_files": False,
        "readiness_runs_git_reset": False,
        "readiness_runs_git_force_push": False,
        "readiness_executes_shell_commands": False,
        "readiness_dimensions": policy.get("readiness_dimensions", []),
        "governance_summary_available": GOVERNANCE_SUMMARY.exists(),
        "sandbox_review_available": SANDBOX_REVIEW.exists(),
        "metrics": metrics,
        "recent_matrices": matrices,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_readiness": policy.get("required_gates_before_recovery_readiness", []),
        "next_checkpoint": policy.get("next_checkpoint", "062 - K-Agent Recovery Plan Builder Core")
    }

    write_report(report)
    event("recovery_readiness_matrix.audit_generated", {
        "matrix_count": metrics.get("matrix_count")
    })
    return report


def write_matrix(matrix: dict[str, Any]) -> None:
    MATRIX_JSON.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Readiness Matrix",
        "",
        "- Matrix ID: " + str(matrix.get("matrix_id")),
        "- Status: " + str(matrix.get("status")),
        "- Readiness score: " + str(matrix.get("readiness_score")) + "/" + str(matrix.get("max_score")),
        "- Readiness percent: " + str(matrix.get("readiness_percent")),
        "- Readiness level: " + str(matrix.get("readiness_level")),
        "- Risk level: " + str(matrix.get("risk_level")),
        "- Matrix hash: " + str(matrix.get("readiness_matrix_hash")),
        "- Executes recovery: " + str(matrix.get("readiness_executes_recovery")),
        "- Executes rollback: " + str(matrix.get("readiness_executes_rollback")),
        "- Deletes data: " + str(matrix.get("readiness_deletes_data")),
        "- Modifies target files: " + str(matrix.get("readiness_modifies_target_files")),
        "- Runs git reset: " + str(matrix.get("readiness_runs_git_reset")),
        "- Runs git force push: " + str(matrix.get("readiness_runs_git_force_push")),
        "",
        "## Dimensions",
        ""
    ]

    for item in matrix.get("dimensions", []):
        lines.append(
            "- " + str(item.get("dimension")) +
            " | score=" + str(item.get("score")) +
            "/" + str(item.get("weight")) +
            " | ok=" + str(item.get("ok"))
        )

    lines.extend(["", "## Consolidated blockers", ""])

    if matrix.get("consolidated_blockers"):
        for item in matrix.get("consolidated_blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    MATRIX_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Readiness Matrix Validation",
        "",
        "- Matrix ID: " + str(result.get("matrix_id")),
        "- Status: " + str(result.get("status")),
        "- Readiness score: " + str(result.get("readiness_score")),
        "- Readiness level: " + str(result.get("readiness_level")),
        "- Risk level: " + str(result.get("risk_level")),
        "- Matrix hash: " + str(result.get("readiness_matrix_hash")),
        "- Executes recovery: " + str(result.get("readiness_executes_recovery")),
        "- Executes rollback: " + str(result.get("readiness_executes_rollback")),
        "- Deletes data: " + str(result.get("readiness_deletes_data")),
        "- Modifies target files: " + str(result.get("readiness_modifies_target_files")),
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
        "# K-OS Agent Recovery Readiness Matrix Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("readiness_state_committed")),
        "- Executes recovery: " + str(report.get("readiness_executes_recovery")),
        "- Executes rollback: " + str(report.get("readiness_executes_rollback")),
        "- Deletes data: " + str(report.get("readiness_deletes_data")),
        "- Modifies target files: " + str(report.get("readiness_modifies_target_files")),
        "- Runs git reset: " + str(report.get("readiness_runs_git_reset")),
        "- Runs git force push: " + str(report.get("readiness_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("readiness_executes_shell_commands")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent matrices", ""])

    if report.get("recent_matrices"):
        for item in report.get("recent_matrices", [])[:30]:
            lines.append(
                "- " + str(item.get("matrix_id")) +
                " | score=" + str(item.get("readiness_score")) +
                " | level=" + str(item.get("readiness_level")) +
                " | risk=" + str(item.get("risk_level"))
            )
    else:
        lines.append("- Nenhuma matriz.")

    lines.extend(["", "## Required gates before recovery readiness", ""])

    for gate in report.get("required_gates_before_recovery_readiness", []):
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
    parser.add_argument("--mode", choices=["init", "build", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "build":
        result = build_matrix(args.operator, args.reason)

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