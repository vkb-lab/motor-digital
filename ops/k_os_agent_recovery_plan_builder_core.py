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

POLICY_PATH = ROOT / "config" / "recovery_plan_builder" / "k_os_agent_recovery_plan_builder_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_recovery_plan_builder"
STATE_PATH = STATE_DIR / "agent_recovery_plan_builder_state.json"

REPORT_DIR = ROOT / "reports" / "recovery_plan_builder"
MEMORY_DIR = ROOT / "memory" / "recovery_plan_builder"

LATEST_JSON = REPORT_DIR / "latest_agent_recovery_plan_builder_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_recovery_plan_builder_report.md"
PLAN_JSON = REPORT_DIR / "latest_recovery_plan.json"
PLAN_MD = REPORT_DIR / "latest_recovery_plan.md"
VALIDATION_JSON = REPORT_DIR / "latest_recovery_plan_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_recovery_plan_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

READINESS_MATRIX = ROOT / "reports" / "recovery_readiness_matrix" / "latest_recovery_readiness_matrix.json"
READINESS_VALIDATION = ROOT / "reports" / "recovery_readiness_matrix" / "latest_recovery_readiness_matrix_validation_report.json"
READINESS_REPORT = ROOT / "reports" / "recovery_readiness_matrix" / "latest_agent_recovery_readiness_matrix_report.json"

GOVERNANCE_SUMMARY = ROOT / "reports" / "rollback_governance_summary" / "latest_rollback_governance_summary.json"
SANDBOX_REVIEW = ROOT / "reports" / "rollback_sandbox_review" / "latest_rollback_sandbox_operator_review.json"


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
        raise RuntimeError("Recovery plan builder policy not found.")
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
            "plan_executes_recovery": False,
            "plan_executes_rollback": False,
            "plans": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load recovery plan builder state.")
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


def load_readiness() -> dict[str, Any]:
    data = read_json(READINESS_MATRIX)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "matrix_id": "",
        "readiness_matrix_hash": "",
        "readiness_score": 0,
        "readiness_level": "not_ready",
        "risk_level": "high",
        "consolidated_blockers": ["recovery_readiness_matrix_missing"]
    }


def build_recovery_plan(operator: str, reason: str, scope: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    readiness = load_readiness()
    governance = read_json(GOVERNANCE_SUMMARY) or {}
    review = read_json(SANDBOX_REVIEW) or {}

    plan_id = "rpb_" + uuid.uuid4().hex[:12]
    readiness_level = readiness.get("readiness_level", "not_ready")
    risk_level = readiness.get("risk_level", "high")
    readiness_score = readiness.get("readiness_score", 0)
    matrix_hash = readiness.get("readiness_matrix_hash", "")

    blockers: list[str] = []

    if not readiness.get("matrix_id"):
        blockers.append("readiness_matrix_missing")

    if not matrix_hash:
        blockers.append("readiness_matrix_hash_missing")

    if not governance.get("summary_id"):
        blockers.append("governance_summary_missing")

    if not review.get("review_id"):
        blockers.append("operator_review_missing")

    if readiness_level != "controlled_ready":
        blockers.append("readiness_not_controlled_ready")

    for item in readiness.get("consolidated_blockers", []):
        text = str(item)
        if text not in blockers:
            blockers.append(text)

    source_refs = {
        "readiness_matrix": source_ref(READINESS_MATRIX),
        "readiness_validation": source_ref(READINESS_VALIDATION),
        "readiness_report": source_ref(READINESS_REPORT),
        "governance_summary": source_ref(GOVERNANCE_SUMMARY),
        "sandbox_operator_review": source_ref(SANDBOX_REVIEW)
    }

    plan_steps = [
        {
            "step": 1,
            "name": "preservar_evidencias",
            "description": "Confirmar que evidencias, reports e hashes permanecem intactos.",
            "executes_recovery": False,
            "destructive": False
        },
        {
            "step": 2,
            "name": "confirmar_escopo",
            "description": "Revisar manualmente o escopo do recovery antes de qualquer execucao futura.",
            "executes_recovery": False,
            "destructive": False
        },
        {
            "step": 3,
            "name": "validar_readiness",
            "description": "Validar readiness score, risco e blockers.",
            "executes_recovery": False,
            "destructive": False
        },
        {
            "step": 4,
            "name": "gate_aprovacao",
            "description": "Enviar plano para approval gate do checkpoint 063.",
            "executes_recovery": False,
            "destructive": False
        },
        {
            "step": 5,
            "name": "execucao_futura_manual",
            "description": "Execucao real futura permanece bloqueada ate autorizacao explicita.",
            "executes_recovery": False,
            "destructive": False
        }
    ]

    plan_body = {
        "plan_id": plan_id,
        "scope": scope,
        "readiness_level": readiness_level,
        "risk_level": risk_level,
        "readiness_score": readiness_score,
        "matrix_hash": matrix_hash,
        "plan_steps": plan_steps,
        "source_refs": source_refs
    }

    status = "plan_prepared_review_required" if len(blockers) == 0 else "plan_blocked_review_required"

    plan = {
        "ok": True,
        "checkpoint": "062",
        "module": "k_os_agent_recovery_plan_builder_core",
        "status": status,
        "recovery_plan_id": plan_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "recovery_plan_builder",
        "scope": scope or "controlled_recovery_scope",
        "readiness_matrix_id": readiness.get("matrix_id", ""),
        "readiness_matrix_hash": matrix_hash,
        "readiness_score": readiness_score,
        "readiness_level": readiness_level,
        "risk_level": risk_level,
        "governance_summary_id": governance.get("summary_id", ""),
        "operator_review_id": review.get("review_id", ""),
        "recovery_plan_hash": stable_hash(plan_body),
        "plan_steps": plan_steps,
        "manual_review_checklist": [
            "Confirmar escopo do recovery.",
            "Confirmar readiness matrix.",
            "Confirmar governance summary.",
            "Confirmar blockers.",
            "Confirmar que nenhuma acao destrutiva sera executada neste checkpoint.",
            "Enviar para approval gate 063."
        ],
        "preconditions": [
            "readiness_matrix_validada",
            "governance_summary_disponivel",
            "operator_review_disponivel",
            "approval_gate_063_obrigatorio",
            "execucao_real_bloqueada"
        ],
        "post_recovery_validation_plan": [
            "validar status do repositorio",
            "validar reports de auditoria",
            "validar integridade de evidencias",
            "registrar fechamento humano"
        ],
        "plan_executes_recovery": False,
        "plan_executes_rollback": False,
        "plan_deletes_data": False,
        "plan_modifies_target_files": False,
        "plan_runs_git_reset": False,
        "plan_runs_git_force_push": False,
        "plan_executes_shell_commands": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "raw_payload_included": False,
        "blocked_actions": policy.get("blocked_actions", []),
        "blockers": blockers,
        "source_refs": source_refs,
        "required_gates_before_recovery_plan": policy.get("required_gates_before_recovery_plan", []),
        "next_checkpoint": policy.get("next_checkpoint", "063 - K-Agent Recovery Approval Gate Core")
    }

    state.setdefault("plans", []).append(plan)
    state["plans"] = state["plans"][-300:]
    save_state(state)

    write_plan(plan)

    event("recovery_plan_builder.plan_created", {
        "recovery_plan_id": plan_id,
        "status": status,
        "readiness_level": readiness_level,
        "risk_level": risk_level,
        "blocker_count": len(blockers)
    })

    return audit_report()


def latest_plan_raw() -> dict[str, Any] | None:
    state = ensure_state()
    plans = state.get("plans", [])
    if not plans:
        return None
    return plans[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    plan = latest_plan_raw()
    blockers = []
    warnings = []

    if not plan:
        blockers.append("recovery_plan_not_found")
    else:
        if not plan.get("recovery_plan_id"):
            blockers.append("recovery_plan_id_missing")

        if not plan.get("recovery_plan_hash"):
            blockers.append("recovery_plan_hash_missing")

        if not plan.get("readiness_matrix_id"):
            blockers.append("readiness_matrix_id_missing")

        if not plan.get("readiness_matrix_hash"):
            blockers.append("readiness_matrix_hash_missing")

        if plan.get("plan_executes_recovery") is True:
            blockers.append("plan_executes_recovery")

        if plan.get("plan_executes_rollback") is True:
            blockers.append("plan_executes_rollback")

        if plan.get("plan_deletes_data") is True:
            blockers.append("plan_deletes_data")

        if plan.get("plan_modifies_target_files") is True:
            blockers.append("plan_modifies_target_files")

        if plan.get("plan_runs_git_reset") is True:
            blockers.append("plan_runs_git_reset")

        if plan.get("plan_runs_git_force_push") is True:
            blockers.append("plan_runs_git_force_push")

        if plan.get("plan_executes_shell_commands") is True:
            blockers.append("plan_executes_shell_commands")

        if plan.get("status") == "plan_blocked_review_required":
            warnings.append("recovery_plan_created_but_requires_review")

        if plan.get("readiness_level") != "controlled_ready":
            warnings.append("readiness_not_controlled_ready")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "062",
        "module": "k_os_agent_recovery_plan_builder_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "recovery_plan_id": plan.get("recovery_plan_id") if plan else "",
        "plan_status": plan.get("status") if plan else "",
        "readiness_level": plan.get("readiness_level") if plan else "",
        "risk_level": plan.get("risk_level") if plan else "",
        "recovery_plan_hash": plan.get("recovery_plan_hash") if plan else "",
        "plan_executes_recovery": False,
        "plan_executes_rollback": False,
        "plan_deletes_data": False,
        "plan_modifies_target_files": False,
        "plan_runs_git_reset": False,
        "plan_runs_git_force_push": False,
        "plan_executes_shell_commands": False,
        "raw_payload_included": False,
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

    event("recovery_plan_builder.validation_completed", {
        "recovery_plan_id": validation.get("recovery_plan_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_plan(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "recovery_plan_id": item.get("recovery_plan_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "scope": item.get("scope"),
        "readiness_score": item.get("readiness_score"),
        "readiness_level": item.get("readiness_level"),
        "risk_level": item.get("risk_level"),
        "recovery_plan_hash": item.get("recovery_plan_hash"),
        "plan_executes_recovery": False,
        "plan_executes_rollback": False,
        "plan_deletes_data": False,
        "plan_modifies_target_files": False,
        "plan_runs_git_reset": False,
        "plan_runs_git_force_push": False,
        "plan_executes_shell_commands": False,
        "blocker_count": len(item.get("blockers", []))
    }


def compute_metrics(plans: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for item in plans:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "plan_count": len(plans),
        "validation_count": len(validations),
        "prepared_review_required_count": status_counts.get("plan_prepared_review_required", 0),
        "blocked_review_required_count": status_counts.get("plan_blocked_review_required", 0),
        "recovery_execution_count": 0,
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "target_file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "shell_execution_count": 0,
        "status_counts": status_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    plans = [safe_plan(item) for item in reversed(state.get("plans", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(plans, validations)

    report = {
        "ok": True,
        "checkpoint": "062",
        "module": "k_os_agent_recovery_plan_builder_core",
        "status": "audit_generated",
        "generated_at": now(),
        "plan_state_path": "local_secrets/k_os_recovery_plan_builder/agent_recovery_plan_builder_state.json",
        "plan_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "plan_executes_recovery": False,
        "plan_executes_rollback": False,
        "plan_deletes_data": False,
        "plan_modifies_target_files": False,
        "plan_runs_git_reset": False,
        "plan_runs_git_force_push": False,
        "plan_executes_shell_commands": False,
        "readiness_matrix_available": READINESS_MATRIX.exists(),
        "governance_summary_available": GOVERNANCE_SUMMARY.exists(),
        "operator_review_available": SANDBOX_REVIEW.exists(),
        "metrics": metrics,
        "recent_plans": plans,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_recovery_plan": policy.get("required_gates_before_recovery_plan", []),
        "next_checkpoint": policy.get("next_checkpoint", "063 - K-Agent Recovery Approval Gate Core")
    }

    write_report(report)
    event("recovery_plan_builder.audit_generated", {
        "plan_count": metrics.get("plan_count")
    })
    return report


def write_plan(plan: dict[str, Any]) -> None:
    PLAN_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Recovery Plan",
        "",
        "- Recovery Plan ID: " + str(plan.get("recovery_plan_id")),
        "- Status: " + str(plan.get("status")),
        "- Scope: " + str(plan.get("scope")),
        "- Readiness level: " + str(plan.get("readiness_level")),
        "- Risk level: " + str(plan.get("risk_level")),
        "- Plan hash: " + str(plan.get("recovery_plan_hash")),
        "- Executes recovery: " + str(plan.get("plan_executes_recovery")),
        "- Executes rollback: " + str(plan.get("plan_executes_rollback")),
        "- Deletes data: " + str(plan.get("plan_deletes_data")),
        "- Modifies target files: " + str(plan.get("plan_modifies_target_files")),
        "- Runs git reset: " + str(plan.get("plan_runs_git_reset")),
        "- Runs git force push: " + str(plan.get("plan_runs_git_force_push")),
        "",
        "## Plan steps",
        ""
    ]

    for item in plan.get("plan_steps", []):
        lines.append(
            "- " + str(item.get("step")) +
            " | " + str(item.get("name")) +
            " | executes_recovery=" + str(item.get("executes_recovery")) +
            " | destructive=" + str(item.get("destructive"))
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
        "# K-OS Recovery Plan Validation",
        "",
        "- Recovery Plan ID: " + str(result.get("recovery_plan_id")),
        "- Status: " + str(result.get("status")),
        "- Plan status: " + str(result.get("plan_status")),
        "- Readiness level: " + str(result.get("readiness_level")),
        "- Risk level: " + str(result.get("risk_level")),
        "- Plan hash: " + str(result.get("recovery_plan_hash")),
        "- Executes recovery: " + str(result.get("plan_executes_recovery")),
        "- Executes rollback: " + str(result.get("plan_executes_rollback")),
        "- Deletes data: " + str(result.get("plan_deletes_data")),
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
        "# K-OS Agent Recovery Plan Builder Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("plan_state_committed")),
        "- Executes recovery: " + str(report.get("plan_executes_recovery")),
        "- Executes rollback: " + str(report.get("plan_executes_rollback")),
        "- Deletes data: " + str(report.get("plan_deletes_data")),
        "- Modifies target files: " + str(report.get("plan_modifies_target_files")),
        "- Runs git reset: " + str(report.get("plan_runs_git_reset")),
        "- Runs git force push: " + str(report.get("plan_runs_git_force_push")),
        "- Executes shell commands: " + str(report.get("plan_executes_shell_commands")),
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
                "- " + str(item.get("recovery_plan_id")) +
                " | status=" + str(item.get("status")) +
                " | readiness=" + str(item.get("readiness_level")) +
                " | risk=" + str(item.get("risk_level"))
            )
    else:
        lines.append("- Nenhum plano.")

    lines.extend(["", "## Required gates before recovery plan", ""])

    for gate in report.get("required_gates_before_recovery_plan", []):
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
    parser.add_argument("--scope", default="controlled_recovery_scope")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "build":
        result = build_recovery_plan(args.operator, args.reason, args.scope)

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