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

POLICY_PATH = ROOT / "config" / "resilience_readiness" / "k_os_agent_resilience_readiness_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_resilience_readiness"
STATE_PATH = STATE_DIR / "agent_resilience_readiness_state.json"

REPORT_DIR = ROOT / "reports" / "resilience_readiness"
MEMORY_DIR = ROOT / "memory" / "resilience_readiness"

LATEST_JSON = REPORT_DIR / "latest_agent_resilience_readiness_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_resilience_readiness_report.md"
MATRIX_JSON = REPORT_DIR / "latest_resilience_readiness_matrix.json"
MATRIX_MD = REPORT_DIR / "latest_resilience_readiness_matrix.md"
VALIDATION_JSON = REPORT_DIR / "latest_resilience_readiness_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_resilience_readiness_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

RECOVERY_LAYER_CLOSURE = ROOT / "reports" / "recovery_layer_closure" / "latest_recovery_layer_closure.json"
RECOVERY_LAYER_CLOSURE_REPORT = ROOT / "reports" / "recovery_layer_closure" / "latest_agent_recovery_layer_closure_report.json"
RECOVERY_LAYER_CLOSURE_VALIDATION = ROOT / "reports" / "recovery_layer_closure" / "latest_recovery_layer_closure_validation_report.json"
RECOVERY_GOVERNANCE_SUMMARY = ROOT / "reports" / "recovery_governance_summary" / "latest_recovery_governance_summary.json"
RECOVERY_SANDBOX_REVIEW = ROOT / "reports" / "recovery_sandbox_review" / "latest_recovery_sandbox_operator_review.json"
SECURITY_FIREWALL = ROOT / "ops" / "k_os_security_firewall.py"


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
        raise RuntimeError("Resilience readiness policy not found.")
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
            "readiness_executes_recovery": False,
            "readiness_executes_rollback": False,
            "matrices": [],
            "validations": []
        }
        write_json(STATE_PATH, state)

    data = read_json(STATE_PATH)
    if not data:
        raise RuntimeError("Could not load resilience readiness state.")
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


def score_item(name: str, ok: bool, weight: int, evidence: str, blocker: str = "") -> dict[str, Any]:
    return {
        "dimension": name,
        "ok": ok,
        "weight": weight,
        "score": weight if ok else 0,
        "evidence": evidence,
        "blocker": "" if ok else blocker
    }


def create_matrix(operator: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    closure = read_json(RECOVERY_LAYER_CLOSURE) or {}
    closure_report = read_json(RECOVERY_LAYER_CLOSURE_REPORT) or {}
    closure_validation = read_json(RECOVERY_LAYER_CLOSURE_VALIDATION) or {}
    governance = read_json(RECOVERY_GOVERNANCE_SUMMARY) or {}
    sandbox_review = read_json(RECOVERY_SANDBOX_REVIEW) or {}

    dimensions = []

    dimensions.append(score_item(
        "recovery_layer_closed",
        bool(closure.get("recovery_layer_closure_hash")) and str(closure.get("status", "")).startswith("layer_closed"),
        20,
        rel(RECOVERY_LAYER_CLOSURE),
        "recovery_layer_closure_missing_or_not_closed"
    ))

    dimensions.append(score_item(
        "evidence_chain_complete",
        bool(closure.get("evidence_core_complete")),
        15,
        rel(RECOVERY_LAYER_CLOSURE),
        "evidence_core_chain_incomplete"
    ))

    dimensions.append(score_item(
        "governance_summary_available",
        bool(governance.get("recovery_governance_summary_hash")),
        15,
        rel(RECOVERY_GOVERNANCE_SUMMARY),
        "recovery_governance_summary_missing"
    ))

    destructive_zero = (
        closure.get("no_recovery_executed") is True and
        closure.get("no_rollback_executed") is True and
        closure.get("no_data_deleted") is True and
        closure.get("no_target_files_modified") is True and
        closure.get("no_git_reset_executed") is True and
        closure.get("no_git_force_push_executed") is True and
        closure.get("no_shell_executed") is True
    )

    dimensions.append(score_item(
        "destructive_zero_confirmed",
        destructive_zero,
        20,
        rel(RECOVERY_LAYER_CLOSURE),
        "destructive_zero_not_confirmed"
    ))

    dimensions.append(score_item(
        "operator_review_available",
        bool(sandbox_review.get("recovery_sandbox_review_hash")),
        10,
        rel(RECOVERY_SANDBOX_REVIEW),
        "operator_review_missing"
    ))

    dimensions.append(score_item(
        "local_state_isolated",
        True,
        5,
        "local_secrets/k_os_resilience_readiness",
        ""
    ))

    dimensions.append(score_item(
        "security_firewall_available",
        SECURITY_FIREWALL.exists(),
        10,
        rel(SECURITY_FIREWALL),
        "security_firewall_missing"
    ))

    dimensions.append(score_item(
        "next_layer_ready",
        bool(closure_validation.get("ok")) and destructive_zero,
        5,
        rel(RECOVERY_LAYER_CLOSURE_VALIDATION),
        "next_layer_not_ready"
    ))

    score = sum(int(item["score"]) for item in dimensions)
    max_score = sum(int(item["weight"]) for item in dimensions)
    percent = round((score / max_score) * 100, 2) if max_score else 0

    blockers = [item["blocker"] for item in dimensions if item.get("blocker")]

    if percent >= 90 and not blockers:
        status = "resilience_ready"
    elif percent >= 70:
        status = "resilience_ready_with_review"
    else:
        status = "resilience_blocked"

    matrix_id = "rrm_" + uuid.uuid4().hex[:12]

    matrix_body = {
        "matrix_id": matrix_id,
        "score": score,
        "max_score": max_score,
        "percent": percent,
        "dimensions": dimensions,
        "closure_hash": closure.get("recovery_layer_closure_hash", ""),
        "governance_hash": governance.get("recovery_governance_summary_hash", "")
    }

    matrix = {
        "ok": True,
        "checkpoint": "071",
        "module": "k_os_agent_resilience_readiness_core",
        "status": status,
        "matrix_id": matrix_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "resilience_readiness_after_recovery_layer_closure",
        "score": score,
        "max_score": max_score,
        "readiness_percent": percent,
        "readiness_level": "high" if percent >= 90 else "medium" if percent >= 70 else "low",
        "dimensions": dimensions,
        "blockers": blockers,
        "recovery_layer_closure_id": closure.get("recovery_layer_closure_id", ""),
        "recovery_layer_closure_status": closure.get("status", ""),
        "recovery_layer_closure_hash": closure.get("recovery_layer_closure_hash", ""),
        "recovery_governance_summary_hash": governance.get("recovery_governance_summary_hash", ""),
        "sandbox_operator_review_hash": sandbox_review.get("recovery_sandbox_review_hash", ""),
        "evidence_core_complete": bool(closure.get("evidence_core_complete")),
        "destructive_zero_confirmed": destructive_zero,
        "readiness_hash": stable_hash(matrix_body),
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
        "local_recovery_token_included": False,
        "source_refs": {
            "recovery_layer_closure": source_ref(RECOVERY_LAYER_CLOSURE),
            "recovery_layer_closure_report": source_ref(RECOVERY_LAYER_CLOSURE_REPORT),
            "recovery_layer_closure_validation": source_ref(RECOVERY_LAYER_CLOSURE_VALIDATION),
            "recovery_governance_summary": source_ref(RECOVERY_GOVERNANCE_SUMMARY),
            "recovery_sandbox_review": source_ref(RECOVERY_SANDBOX_REVIEW)
        },
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "072 - K-Agent Resilience Scenario Planner Core")
    }

    state.setdefault("matrices", []).append(matrix)
    state["matrices"] = state["matrices"][-300:]
    save_state(state)

    write_matrix(matrix)

    event("resilience_readiness.matrix_created", {
        "matrix_id": matrix_id,
        "status": status,
        "score": score,
        "max_score": max_score,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_matrix_raw() -> dict[str, Any] | None:
    state = ensure_state()
    records = state.get("matrices", [])
    if not records:
        return None
    return records[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    matrix = latest_matrix_raw()
    blockers = []
    warnings = []

    if not matrix:
        blockers.append("resilience_readiness_matrix_not_found")
    else:
        required = [
            ("matrix_id", "matrix_id_missing"),
            ("readiness_hash", "readiness_hash_missing"),
            ("recovery_layer_closure_hash", "recovery_layer_closure_hash_missing")
        ]

        for key, blocker in required:
            if not matrix.get(key):
                blockers.append(blocker)

        destructive_keys = [
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

        for key in destructive_keys:
            if matrix.get(key) is True:
                blockers.append(key)

        if matrix.get("status") != "resilience_ready":
            warnings.append("resilience_requires_operator_review")

        if matrix.get("blockers"):
            warnings.append("readiness_contains_blockers")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "071",
        "module": "k_os_agent_resilience_readiness_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "matrix_id": matrix.get("matrix_id") if matrix else "",
        "matrix_status": matrix.get("status") if matrix else "",
        "readiness_hash": matrix.get("readiness_hash") if matrix else "",
        "readiness_percent": matrix.get("readiness_percent") if matrix else 0,
        "readiness_executes_recovery": False,
        "readiness_executes_rollback": False,
        "readiness_deletes_data": False,
        "readiness_modifies_target_files": False,
        "readiness_runs_git_reset": False,
        "readiness_runs_git_force_push": False,
        "readiness_executes_shell_commands": False,
        "raw_payload_included": False,
        "local_recovery_token_included": False,
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

    event("resilience_readiness.validation_completed", {
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
        "score": item.get("score"),
        "max_score": item.get("max_score"),
        "readiness_percent": item.get("readiness_percent"),
        "readiness_level": item.get("readiness_level"),
        "readiness_hash": item.get("readiness_hash"),
        "recovery_layer_closure_status": item.get("recovery_layer_closure_status"),
        "destructive_zero_confirmed": item.get("destructive_zero_confirmed"),
        "readiness_executes_recovery": False,
        "readiness_executes_rollback": False,
        "readiness_deletes_data": False,
        "readiness_modifies_target_files": False,
        "readiness_runs_git_reset": False,
        "readiness_runs_git_force_push": False,
        "readiness_executes_shell_commands": False,
        "blocker_count": len(item.get("blockers", []))
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    matrices = [safe_matrix(item) for item in reversed(state.get("matrices", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]

    metrics = {
        "matrix_count": len(matrices),
        "validation_count": len(validations),
        "resilience_ready_count": len([x for x in matrices if x.get("status") == "resilience_ready"]),
        "resilience_ready_with_review_count": len([x for x in matrices if x.get("status") == "resilience_ready_with_review"]),
        "resilience_blocked_count": len([x for x in matrices if x.get("status") == "resilience_blocked"]),
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
        "checkpoint": "071",
        "module": "k_os_agent_resilience_readiness_core",
        "status": "audit_generated",
        "generated_at": now(),
        "state_path": "local_secrets/k_os_resilience_readiness/agent_resilience_readiness_state.json",
        "state_committed": False,
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
        "metrics": metrics,
        "recent_matrices": matrices,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "072 - K-Agent Resilience Scenario Planner Core")
    }

    write_report(report)
    event("resilience_readiness.audit_generated", {
        "matrix_count": metrics.get("matrix_count")
    })
    return report


def write_matrix(matrix: dict[str, Any]) -> None:
    MATRIX_JSON.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Readiness Matrix",
        "",
        "- Matrix ID: " + str(matrix.get("matrix_id")),
        "- Status: " + str(matrix.get("status")),
        "- Score: " + str(matrix.get("score")) + "/" + str(matrix.get("max_score")),
        "- Percent: " + str(matrix.get("readiness_percent")),
        "- Level: " + str(matrix.get("readiness_level")),
        "- Hash: " + str(matrix.get("readiness_hash")),
        "- Recovery layer closure: " + str(matrix.get("recovery_layer_closure_status")),
        "- Destructive zero confirmed: " + str(matrix.get("destructive_zero_confirmed")),
        "- Executes recovery: False",
        "- Executes rollback: False",
        "- Executes shell: False",
        "",
        "## Dimensions",
        ""
    ]

    for item in matrix.get("dimensions", []):
        lines.append(
            "- " + str(item.get("dimension")) +
            " | ok=" + str(item.get("ok")) +
            " | score=" + str(item.get("score")) +
            "/" + str(item.get("weight"))
        )

    lines.extend(["", "## Blockers", ""])

    if matrix.get("blockers"):
        for item in matrix.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    MATRIX_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Resilience Readiness Validation",
        "",
        "- Matrix ID: " + str(result.get("matrix_id")),
        "- Status: " + str(result.get("status")),
        "- Matrix status: " + str(result.get("matrix_status")),
        "- Readiness percent: " + str(result.get("readiness_percent")),
        "- Hash: " + str(result.get("readiness_hash")),
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
        "# K-OS Agent Resilience Readiness Core",
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

    lines.extend(["", "## Recent matrices", ""])

    if report.get("recent_matrices"):
        for item in report.get("recent_matrices", [])[:30]:
            lines.append(
                "- " + str(item.get("matrix_id")) +
                " | status=" + str(item.get("status")) +
                " | percent=" + str(item.get("readiness_percent")) +
                " | blockers=" + str(item.get("blocker_count"))
            )
    else:
        lines.append("- Nenhuma matriz.")

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
    parser.add_argument("--mode", choices=["init", "assess", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()
    elif args.mode == "assess":
        result = create_matrix(args.operator, args.reason)
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