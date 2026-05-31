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

POLICY_PATH = ROOT / "config" / "rollback_preparation" / "k_os_agent_rollback_preparation_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_rollback_preparation"
STATE_PATH = STATE_DIR / "agent_rollback_preparation_state.json"

REPORT_DIR = ROOT / "reports" / "rollback_preparation"
MEMORY_DIR = ROOT / "memory" / "rollback_preparation"

LATEST_JSON = REPORT_DIR / "latest_agent_rollback_preparation_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_rollback_preparation_report.md"
PLAN_JSON = REPORT_DIR / "latest_rollback_plan.json"
PLAN_MD = REPORT_DIR / "latest_rollback_plan.md"
VALIDATION_JSON = REPORT_DIR / "latest_rollback_plan_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_rollback_plan_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

INCIDENT_RECORD = ROOT / "reports" / "incident_lockdown" / "latest_incident_lockdown_record.json"
INCIDENT_VALIDATION = ROOT / "reports" / "incident_lockdown" / "latest_incident_lockdown_validation_report.json"
INCIDENT_REPORT = ROOT / "reports" / "incident_lockdown" / "latest_agent_incident_lockdown_report.json"

FORENSICS_BUNDLE = ROOT / "reports" / "replay_forensics" / "latest_replay_forensics_bundle.json"
LEDGER_RECORD = ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_record.json"
ALLOWLISTED_EXECUTION = ROOT / "reports" / "allowlisted_action_executor" / "latest_allowlisted_action_execution.json"
SAFE_ROUTE = ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route.json"
APPROVAL_DECISION = ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_decision.json"
DRY_RUN_RESULT = ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_result.json"


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
        raise RuntimeError("Rollback Preparation policy not found.")
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
            "rollback_executes_changes": False,
            "rollback_deletes_data": False,
            "plans": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load rollback preparation state.")
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


def load_incident() -> dict[str, Any]:
    data = read_json(INCIDENT_RECORD)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "incident_id": "",
        "quarantine_id": "",
        "severity": "",
        "scope": "",
        "forensics_bundle_hash": "",
        "ledger_record_hash": "",
        "execution_evidence_hash": "",
        "blockers": ["incident_record_missing"]
    }


def load_incident_validation() -> dict[str, Any]:
    data = read_json(INCIDENT_VALIDATION)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "incident_id": "",
        "blockers": ["incident_validation_missing"]
    }


def rollback_gate_check(incident: dict[str, Any], validation: dict[str, Any], scope: str, reason: str) -> list[str]:
    blockers: list[str] = []

    if not incident.get("incident_id"):
        blockers.append("incident_record_missing")

    if incident.get("status") not in {"quarantine_active", "under_review"}:
        blockers.append("incident_not_in_quarantine_or_review")

    if validation.get("ok") is not True:
        blockers.append("incident_validation_not_ok")

    if validation.get("status") != "validated":
        blockers.append("incident_validation_status_not_validated")

    if not incident.get("quarantine_id"):
        blockers.append("quarantine_id_missing")

    if not incident.get("forensics_bundle_hash"):
        blockers.append("forensics_bundle_hash_missing")

    if not incident.get("ledger_record_hash"):
        blockers.append("ledger_record_hash_missing")

    if not incident.get("execution_evidence_hash"):
        blockers.append("execution_evidence_hash_missing")

    if incident.get("new_agent_actions_blocked") is not True:
        blockers.append("new_agent_actions_not_blocked")

    if incident.get("real_execution_blocked") is not True:
        blockers.append("real_execution_not_blocked")

    if not scope:
        blockers.append("rollback_scope_missing")

    if not reason:
        blockers.append("rollback_reason_missing")

    if incident.get("approval_token_included") is True:
        blockers.append("approval_token_included")

    if incident.get("raw_payload_included") is True:
        blockers.append("raw_payload_included")

    return blockers


def create_plan(scope: str, reason: str, operator: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    incident = load_incident()
    validation = load_incident_validation()
    scope = scope or incident.get("scope") or "agent_execution_chain"
    operator = operator or "operator_k_os"

    blockers = rollback_gate_check(incident, validation, scope, reason)

    plan_id = "rbp_" + uuid.uuid4().hex[:12]

    source_refs = {
        "incident_record": source_ref(INCIDENT_RECORD),
        "incident_validation": source_ref(INCIDENT_VALIDATION),
        "incident_report": source_ref(INCIDENT_REPORT),
        "forensics_bundle": source_ref(FORENSICS_BUNDLE),
        "ledger_record": source_ref(LEDGER_RECORD),
        "allowlisted_execution": source_ref(ALLOWLISTED_EXECUTION),
        "safe_route": source_ref(SAFE_ROUTE),
        "approval_decision": source_ref(APPROVAL_DECISION),
        "dry_run_result": source_ref(DRY_RUN_RESULT)
    }

    plan_body = {
        "incident_id": incident.get("incident_id", ""),
        "quarantine_id": incident.get("quarantine_id", ""),
        "scope": scope,
        "forensics_bundle_hash": incident.get("forensics_bundle_hash", ""),
        "ledger_record_hash": incident.get("ledger_record_hash", ""),
        "execution_evidence_hash": incident.get("execution_evidence_hash", ""),
        "source_refs": source_refs
    }

    rollback_steps = [
        {
            "step": 1,
            "name": "preservar_evidencias",
            "description": "Manter incident, forensics, ledger e execution evidence intactos.",
            "executes_changes": False
        },
        {
            "step": 2,
            "name": "confirmar_escopo",
            "description": "Confirmar manualmente o escopo do rollback antes de qualquer ação real.",
            "executes_changes": False
        },
        {
            "step": 3,
            "name": "definir_ponto_restauracao",
            "description": "Selecionar commit/estado anterior somente após revisão humana.",
            "executes_changes": False
        },
        {
            "step": 4,
            "name": "preparar_execucao_futura",
            "description": "Encaminhar para gate de aprovação e release do rollback.",
            "executes_changes": False
        }
    ]

    plan = {
        "ok": len(blockers) == 0,
        "checkpoint": "053",
        "module": "k_os_agent_rollback_preparation_core",
        "status": "prepared" if len(blockers) == 0 else "blocked",
        "rollback_plan_id": plan_id,
        "created_at": now(),
        "operator": operator,
        "reason": reason or "rollback_preparation",
        "incident_id": incident.get("incident_id", ""),
        "quarantine_id": incident.get("quarantine_id", ""),
        "severity": incident.get("severity", ""),
        "rollback_scope": scope,
        "forensics_bundle_id": incident.get("forensics_bundle_id", ""),
        "forensics_bundle_hash": incident.get("forensics_bundle_hash", ""),
        "ledger_record_id": incident.get("ledger_record_id", ""),
        "ledger_record_hash": incident.get("ledger_record_hash", ""),
        "chain_hash": incident.get("chain_hash", ""),
        "execution_id": incident.get("execution_id", ""),
        "execution_evidence_hash": incident.get("execution_evidence_hash", ""),
        "rollback_plan_hash": stable_hash(plan_body),
        "candidate_restore_points": [
            {
                "type": "git_commit_reference",
                "description": "Selecionar manualmente um commit anterior ao incidente, sem executar reset automático.",
                "auto_selected": False,
                "executes_changes": False
            }
        ],
        "rollback_steps": rollback_steps,
        "manual_review_checklist": [
            "Confirmar incidente e severidade.",
            "Confirmar escopo do rollback.",
            "Confirmar evidências preservadas.",
            "Confirmar ponto de restauração.",
            "Confirmar plano de validação pós-rollback.",
            "Aprovação humana obrigatória antes de execução real."
        ],
        "blocked_destructive_actions": policy.get("blocked_actions", []),
        "execution_preconditions": [
            "rollback approval gate validado",
            "rollback release autorizado",
            "security scan limpo",
            "backup/evidência preservados",
            "operador humano aprovado"
        ],
        "post_rollback_validation": [
            "validar Git status",
            "validar módulos críticos",
            "validar ledger",
            "validar cockpit",
            "registrar relatório final"
        ],
        "rollback_executes_changes": False,
        "rollback_deletes_data": False,
        "rollback_modifies_files": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "approval_token_included": False,
        "raw_payload_included": False,
        "release_requires_human_review": True,
        "source_refs": source_refs,
        "blockers": blockers,
        "required_gates_before_rollback_plan": policy.get("required_gates_before_rollback_plan", []),
        "next_action": "rollback_approval_and_release_gate" if len(blockers) == 0 else "resolve_rollback_plan_blockers"
    }

    state.setdefault("plans", []).append(plan)
    state["plans"] = state["plans"][-300:]
    save_state(state)

    write_plan(plan)

    event("rollback_preparation.plan_created", {
        "rollback_plan_id": plan_id,
        "incident_id": incident.get("incident_id", ""),
        "ok": plan.get("ok"),
        "blockers": blockers
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
        blockers.append("rollback_plan_not_found")
    else:
        if plan.get("status") != "prepared":
            blockers.append("rollback_plan_not_prepared")

        if not plan.get("rollback_plan_id"):
            blockers.append("rollback_plan_id_missing")

        if not plan.get("rollback_plan_hash"):
            blockers.append("rollback_plan_hash_missing")

        if not plan.get("incident_id"):
            blockers.append("incident_id_missing")

        if not plan.get("quarantine_id"):
            blockers.append("quarantine_id_missing")

        if not plan.get("execution_evidence_hash"):
            blockers.append("execution_evidence_hash_missing")

        if plan.get("rollback_executes_changes") is True:
            blockers.append("rollback_executes_changes")

        if plan.get("rollback_deletes_data") is True:
            blockers.append("rollback_deletes_data")

        if plan.get("rollback_modifies_files") is True:
            blockers.append("rollback_modifies_files")

        if plan.get("approval_token_included") is True:
            blockers.append("approval_token_included")

        if plan.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if plan.get("severity") == "SEV1":
            warnings.append("sev1_requires_immediate_operator_review")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "053",
        "module": "k_os_agent_rollback_preparation_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "rollback_plan_id": plan.get("rollback_plan_id") if plan else "",
        "incident_id": plan.get("incident_id") if plan else "",
        "quarantine_id": plan.get("quarantine_id") if plan else "",
        "rollback_plan_hash": plan.get("rollback_plan_hash") if plan else "",
        "rollback_executes_changes": False,
        "rollback_deletes_data": False,
        "rollback_modifies_files": False,
        "approval_token_included": False,
        "raw_payload_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if plan and len(blockers) == 0:
        plan["status"] = "validated"
        plan["validated_at"] = validation["generated_at"]

    save_state(state)
    write_validation(validation)

    event("rollback_preparation.validation_completed", {
        "rollback_plan_id": validation.get("rollback_plan_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_plan_for_report(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "rollback_plan_id": item.get("rollback_plan_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "incident_id": item.get("incident_id"),
        "quarantine_id": item.get("quarantine_id"),
        "severity": item.get("severity"),
        "rollback_scope": item.get("rollback_scope"),
        "rollback_plan_hash": item.get("rollback_plan_hash"),
        "execution_evidence_hash": item.get("execution_evidence_hash"),
        "rollback_executes_changes": False,
        "rollback_deletes_data": False,
        "rollback_modifies_files": False,
        "approval_token_included": False,
        "raw_payload_included": False,
        "blockers": item.get("blockers", [])
    }


def compute_metrics(plans: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for item in plans:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "rollback_plan_count": len(plans),
        "validation_count": len(validations),
        "prepared_count": status_counts.get("prepared", 0),
        "validated_count": status_counts.get("validated", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "file_modify_count": 0,
        "raw_payload_plan_count": 0,
        "status_counts": status_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    plans = [safe_plan_for_report(item) for item in reversed(state.get("plans", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(plans, validations)

    report = {
        "ok": True,
        "checkpoint": "053",
        "module": "k_os_agent_rollback_preparation_core",
        "status": "audit_generated",
        "generated_at": now(),
        "rollback_state_path": "local_secrets/k_os_rollback_preparation/agent_rollback_preparation_state.json",
        "rollback_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "rollback_executes_changes": False,
        "rollback_deletes_data": False,
        "rollback_modifies_files": False,
        "human_approval_required_for_execution": True,
        "incident_record_available": INCIDENT_RECORD.exists(),
        "incident_validation_available": INCIDENT_VALIDATION.exists(),
        "forensics_bundle_available": FORENSICS_BUNDLE.exists(),
        "ledger_record_available": LEDGER_RECORD.exists(),
        "metrics": metrics,
        "recent_plans": plans,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_rollback_plan": policy.get("required_gates_before_rollback_plan", []),
        "next_checkpoint": policy.get("next_checkpoint", "054 - K-Agent Rollback Approval and Release Gate Core")
    }

    write_report(report)
    event("rollback_preparation.audit_generated", {
        "rollback_plan_count": metrics.get("rollback_plan_count")
    })
    return report


def write_plan(plan: dict[str, Any]) -> None:
    PLAN_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Preparation Plan",
        "",
        "- Rollback Plan ID: " + str(plan.get("rollback_plan_id")),
        "- Status: " + str(plan.get("status")),
        "- OK: " + str(plan.get("ok")),
        "- Incident ID: " + str(plan.get("incident_id")),
        "- Quarantine ID: " + str(plan.get("quarantine_id")),
        "- Severity: " + str(plan.get("severity")),
        "- Scope: " + str(plan.get("rollback_scope")),
        "- Plan hash: " + str(plan.get("rollback_plan_hash")),
        "- Rollback executes changes: " + str(plan.get("rollback_executes_changes")),
        "- Rollback deletes data: " + str(plan.get("rollback_deletes_data")),
        "- Rollback modifies files: " + str(plan.get("rollback_modifies_files")),
        "- Human review required: " + str(plan.get("release_requires_human_review")),
        "",
        "## Steps",
        ""
    ]

    for item in plan.get("rollback_steps", []):
        lines.append(
            "- " + str(item.get("step")) +
            " | " + str(item.get("name")) +
            " | executes_changes=" + str(item.get("executes_changes"))
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
        "# K-OS Rollback Preparation Validation",
        "",
        "- Rollback Plan ID: " + str(result.get("rollback_plan_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Incident ID: " + str(result.get("incident_id")),
        "- Quarantine ID: " + str(result.get("quarantine_id")),
        "- Plan hash: " + str(result.get("rollback_plan_hash")),
        "- Rollback executes changes: " + str(result.get("rollback_executes_changes")),
        "- Rollback deletes data: " + str(result.get("rollback_deletes_data")),
        "- Rollback modifies files: " + str(result.get("rollback_modifies_files")),
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
        "# K-OS Agent Rollback Preparation Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("rollback_state_committed")),
        "- Rollback executes changes: " + str(report.get("rollback_executes_changes")),
        "- Rollback deletes data: " + str(report.get("rollback_deletes_data")),
        "- Rollback modifies files: " + str(report.get("rollback_modifies_files")),
        "- Human approval required for execution: " + str(report.get("human_approval_required_for_execution")),
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
                "- " + str(item.get("rollback_plan_id")) +
                " | status=" + str(item.get("status")) +
                " | incident=" + str(item.get("incident_id")) +
                " | scope=" + str(item.get("rollback_scope"))
            )
    else:
        lines.append("- Nenhum plano registrado.")

    lines.extend(["", "## Required gates before rollback plan", ""])

    for gate in report.get("required_gates_before_rollback_plan", []):
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
    parser.add_argument("--mode", choices=["init", "prepare", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--scope", default="agent_execution_chain")
    parser.add_argument("--reason", default="")
    parser.add_argument("--operator", default="operator_k_os")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "prepare":
        result = create_plan(args.scope, args.reason, args.operator)

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