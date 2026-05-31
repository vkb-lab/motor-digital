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

POLICY_PATH = ROOT / "config" / "rollback_dry_run" / "k_os_agent_rollback_dry_run_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_rollback_dry_run"
STATE_PATH = STATE_DIR / "agent_rollback_dry_run_state.json"

REPORT_DIR = ROOT / "reports" / "rollback_dry_run"
MEMORY_DIR = ROOT / "memory" / "rollback_dry_run"

LATEST_JSON = REPORT_DIR / "latest_agent_rollback_dry_run_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_rollback_dry_run_report.md"
SIM_JSON = REPORT_DIR / "latest_rollback_dry_run_simulation.json"
SIM_MD = REPORT_DIR / "latest_rollback_dry_run_simulation.md"
VALIDATION_JSON = REPORT_DIR / "latest_rollback_dry_run_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_rollback_dry_run_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

RELEASE_RECORD = ROOT / "reports" / "rollback_release_gate" / "latest_rollback_release_record.json"
RELEASE_VALIDATION = ROOT / "reports" / "rollback_release_gate" / "latest_rollback_release_validation_report.json"
RELEASE_REPORT = ROOT / "reports" / "rollback_release_gate" / "latest_agent_rollback_release_gate_report.json"

ROLLBACK_PLAN = ROOT / "reports" / "rollback_preparation" / "latest_rollback_plan.json"
ROLLBACK_VALIDATION = ROOT / "reports" / "rollback_preparation" / "latest_rollback_plan_validation_report.json"
INCIDENT_RECORD = ROOT / "reports" / "incident_lockdown" / "latest_incident_lockdown_record.json"
FORENSICS_BUNDLE = ROOT / "reports" / "replay_forensics" / "latest_replay_forensics_bundle.json"
LEDGER_RECORD = ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_record.json"


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
        raise RuntimeError("Rollback Dry Run policy not found.")
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
            "dry_run_executes_rollback": False,
            "dry_run_deletes_data": False,
            "dry_run_modifies_files": False,
            "simulations": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load rollback dry run state.")
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


def load_release() -> dict[str, Any]:
    data = read_json(RELEASE_RECORD)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "release_id": "",
        "decision": "",
        "rollback_plan_id": "",
        "rollback_plan_hash": "",
        "execution_evidence_hash": "",
        "blockers": ["rollback_release_record_missing"]
    }


def load_plan() -> dict[str, Any]:
    data = read_json(ROLLBACK_PLAN)
    if data and not data.get("_read_error"):
        return data
    return {
        "ok": False,
        "status": "missing",
        "rollback_plan_id": "",
        "rollback_plan_hash": "",
        "incident_id": "",
        "quarantine_id": "",
        "execution_evidence_hash": "",
        "blockers": ["rollback_plan_missing"]
    }


def gate_check(release: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    blockers: list[str] = []

    if not release.get("release_id"):
        blockers.append("rollback_release_record_missing")

    if not release.get("release_record_hash"):
        blockers.append("release_record_hash_missing")

    if release.get("release_gate_executes_rollback") is True:
        blockers.append("release_gate_executes_rollback")

    if release.get("release_gate_deletes_data") is True:
        blockers.append("release_gate_deletes_data")

    if release.get("release_gate_modifies_files") is True:
        blockers.append("release_gate_modifies_files")

    if release.get("release_token_included") is True:
        blockers.append("release_token_included")

    if release.get("raw_payload_included") is True:
        blockers.append("raw_payload_included")

    if not plan.get("rollback_plan_id"):
        blockers.append("rollback_plan_missing")

    if not plan.get("rollback_plan_hash"):
        blockers.append("rollback_plan_hash_missing")

    if not plan.get("incident_id"):
        blockers.append("incident_id_missing")

    if not plan.get("quarantine_id"):
        blockers.append("quarantine_id_missing")

    if not plan.get("execution_evidence_hash"):
        blockers.append("execution_evidence_hash_missing")

    if plan.get("rollback_executes_changes") is True:
        blockers.append("rollback_plan_executes_changes")

    if plan.get("rollback_deletes_data") is True:
        blockers.append("rollback_plan_deletes_data")

    if plan.get("rollback_modifies_files") is True:
        blockers.append("rollback_plan_modifies_files")

    return blockers


def create_simulation(reason: str, operator: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    release = load_release()
    plan = load_plan()

    blockers = gate_check(release, plan)

    release_status = release.get("status", "")
    release_decision = release.get("decision", "")

    safe_blocked_by_release_gate = release_status == "blocked" or release_decision == "block_future_rollback"

    simulation_id = "rds_" + uuid.uuid4().hex[:12]

    simulation_steps = [
        {
            "step": 1,
            "name": "validar_gate_de_release",
            "description": "Confirmar se o rollback futuro está aprovado, bloqueado ou revogado.",
            "result": "release_gate_checked",
            "executes_rollback": False
        },
        {
            "step": 2,
            "name": "validar_plano_rollback",
            "description": "Confirmar hash, escopo, incidente e evidências do plano.",
            "result": "rollback_plan_checked",
            "executes_rollback": False
        },
        {
            "step": 3,
            "name": "simular_ponto_restauracao",
            "description": "Simular seleção futura de restore point sem executar git reset.",
            "result": "restore_point_simulated",
            "executes_rollback": False
        },
        {
            "step": 4,
            "name": "simular_validacao_pos_rollback",
            "description": "Simular checks pós-rollback sem alterar arquivos.",
            "result": "post_rollback_validation_simulated",
            "executes_rollback": False
        }
    ]

    status = "simulated_blocked" if safe_blocked_by_release_gate else "simulated"

    source_refs = {
        "release_record": source_ref(RELEASE_RECORD),
        "release_validation": source_ref(RELEASE_VALIDATION),
        "release_report": source_ref(RELEASE_REPORT),
        "rollback_plan": source_ref(ROLLBACK_PLAN),
        "rollback_validation": source_ref(ROLLBACK_VALIDATION),
        "incident_record": source_ref(INCIDENT_RECORD),
        "forensics_bundle": source_ref(FORENSICS_BUNDLE),
        "ledger_record": source_ref(LEDGER_RECORD)
    }

    simulation_body = {
        "simulation_id": simulation_id,
        "release_id": release.get("release_id", ""),
        "release_status": release_status,
        "release_decision": release_decision,
        "rollback_plan_id": plan.get("rollback_plan_id", ""),
        "rollback_plan_hash": plan.get("rollback_plan_hash", ""),
        "execution_evidence_hash": plan.get("execution_evidence_hash", ""),
        "safe_blocked_by_release_gate": safe_blocked_by_release_gate,
        "steps": simulation_steps,
        "source_refs": source_refs
    }

    simulation = {
        "ok": len(blockers) == 0 or safe_blocked_by_release_gate,
        "checkpoint": "055",
        "module": "k_os_agent_rollback_dry_run_simulator_core",
        "status": status if len(blockers) == 0 or safe_blocked_by_release_gate else "blocked",
        "simulation_id": simulation_id,
        "created_at": now(),
        "operator": operator or "operator_k_os",
        "reason": reason or "rollback_dry_run_simulation",
        "release_id": release.get("release_id", ""),
        "release_status": release_status,
        "release_decision": release_decision,
        "safe_blocked_by_release_gate": safe_blocked_by_release_gate,
        "rollback_plan_id": plan.get("rollback_plan_id", ""),
        "rollback_plan_hash": plan.get("rollback_plan_hash", ""),
        "incident_id": plan.get("incident_id", ""),
        "quarantine_id": plan.get("quarantine_id", ""),
        "execution_evidence_hash": plan.get("execution_evidence_hash", ""),
        "simulation_step_count": len(simulation_steps),
        "simulation_steps": simulation_steps,
        "rollback_dry_run_hash": stable_hash(simulation_body),
        "dry_run_executes_rollback": False,
        "dry_run_deletes_data": False,
        "dry_run_modifies_files": False,
        "dry_run_runs_git_reset": False,
        "dry_run_runs_git_force_push": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "approval_token_included": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "source_refs": source_refs,
        "blockers": blockers,
        "required_gates_before_rollback_dry_run": policy.get("required_gates_before_rollback_dry_run", []),
        "next_action": "rollback_execution_final_gate" if len(blockers) == 0 else "rollback_remains_blocked"
    }

    state.setdefault("simulations", []).append(simulation)
    state["simulations"] = state["simulations"][-300:]
    save_state(state)

    write_simulation(simulation)

    event("rollback_dry_run.simulation_created", {
        "simulation_id": simulation_id,
        "status": simulation.get("status"),
        "safe_blocked_by_release_gate": safe_blocked_by_release_gate,
        "ok": simulation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def latest_simulation_raw() -> dict[str, Any] | None:
    state = ensure_state()
    simulations = state.get("simulations", [])
    if not simulations:
        return None
    return simulations[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    simulation = latest_simulation_raw()
    blockers = []
    warnings = []

    if not simulation:
        blockers.append("rollback_dry_run_simulation_not_found")
    else:
        if simulation.get("status") not in {"simulated", "simulated_blocked"}:
            blockers.append("rollback_dry_run_not_simulated")

        if not simulation.get("simulation_id"):
            blockers.append("simulation_id_missing")

        if not simulation.get("rollback_dry_run_hash"):
            blockers.append("rollback_dry_run_hash_missing")

        if simulation.get("dry_run_executes_rollback") is True:
            blockers.append("dry_run_executes_rollback")

        if simulation.get("dry_run_deletes_data") is True:
            blockers.append("dry_run_deletes_data")

        if simulation.get("dry_run_modifies_files") is True:
            blockers.append("dry_run_modifies_files")

        if simulation.get("dry_run_runs_git_reset") is True:
            blockers.append("dry_run_runs_git_reset")

        if simulation.get("dry_run_runs_git_force_push") is True:
            blockers.append("dry_run_runs_git_force_push")

        if simulation.get("external_send_enabled") is True:
            blockers.append("external_send_enabled")

        if simulation.get("external_publish_enabled") is True:
            blockers.append("external_publish_enabled")

        if simulation.get("approval_token_included") is True:
            blockers.append("approval_token_included")

        if simulation.get("release_token_included") is True:
            blockers.append("release_token_included")

        if simulation.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if simulation.get("safe_blocked_by_release_gate") is True:
            warnings.append("rollback_dry_run_safely_blocked_by_release_gate")

    validation = {
        "ok": len(blockers) == 0,
        "checkpoint": "055",
        "module": "k_os_agent_rollback_dry_run_simulator_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "simulation_id": simulation.get("simulation_id") if simulation else "",
        "simulation_status": simulation.get("status") if simulation else "",
        "release_id": simulation.get("release_id") if simulation else "",
        "rollback_plan_id": simulation.get("rollback_plan_id") if simulation else "",
        "rollback_dry_run_hash": simulation.get("rollback_dry_run_hash") if simulation else "",
        "safe_blocked_by_release_gate": simulation.get("safe_blocked_by_release_gate") if simulation else False,
        "dry_run_executes_rollback": False,
        "dry_run_deletes_data": False,
        "dry_run_modifies_files": False,
        "dry_run_runs_git_reset": False,
        "dry_run_runs_git_force_push": False,
        "approval_token_included": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "blockers": blockers,
        "warnings": warnings
    }

    state.setdefault("validations", []).append(validation)
    state["validations"] = state["validations"][-300:]

    if simulation and len(blockers) == 0:
        simulation["validated_at"] = validation["generated_at"]
        simulation["validated"] = True

    save_state(state)
    write_validation(validation)

    event("rollback_dry_run.validation_completed", {
        "simulation_id": validation.get("simulation_id"),
        "ok": validation.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_simulation_for_report(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "simulation_id": item.get("simulation_id"),
        "created_at": item.get("created_at"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "release_id": item.get("release_id"),
        "release_status": item.get("release_status"),
        "rollback_plan_id": item.get("rollback_plan_id"),
        "rollback_dry_run_hash": item.get("rollback_dry_run_hash"),
        "safe_blocked_by_release_gate": item.get("safe_blocked_by_release_gate"),
        "dry_run_executes_rollback": False,
        "dry_run_deletes_data": False,
        "dry_run_modifies_files": False,
        "dry_run_runs_git_reset": False,
        "dry_run_runs_git_force_push": False,
        "approval_token_included": False,
        "release_token_included": False,
        "raw_payload_included": False,
        "blockers": item.get("blockers", [])
    }


def compute_metrics(simulations: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for item in simulations:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "simulation_count": len(simulations),
        "validation_count": len(validations),
        "simulated_count": status_counts.get("simulated", 0),
        "simulated_blocked_count": status_counts.get("simulated_blocked", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "rollback_execution_count": 0,
        "data_delete_count": 0,
        "file_modify_count": 0,
        "git_reset_count": 0,
        "git_force_push_count": 0,
        "raw_payload_count": 0,
        "status_counts": status_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    simulations = [safe_simulation_for_report(item) for item in reversed(state.get("simulations", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(simulations, validations)

    report = {
        "ok": True,
        "checkpoint": "055",
        "module": "k_os_agent_rollback_dry_run_simulator_core",
        "status": "audit_generated",
        "generated_at": now(),
        "dry_run_state_path": "local_secrets/k_os_rollback_dry_run/agent_rollback_dry_run_state.json",
        "dry_run_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "dry_run_executes_rollback": False,
        "dry_run_deletes_data": False,
        "dry_run_modifies_files": False,
        "dry_run_runs_git_reset": False,
        "dry_run_runs_git_force_push": False,
        "human_approval_required_for_real_execution": True,
        "release_record_available": RELEASE_RECORD.exists(),
        "release_validation_available": RELEASE_VALIDATION.exists(),
        "rollback_plan_available": ROLLBACK_PLAN.exists(),
        "incident_record_available": INCIDENT_RECORD.exists(),
        "forensics_bundle_available": FORENSICS_BUNDLE.exists(),
        "ledger_record_available": LEDGER_RECORD.exists(),
        "metrics": metrics,
        "recent_simulations": simulations,
        "recent_validations": validations,
        "blocked_actions": policy.get("blocked_actions", []),
        "required_gates_before_rollback_dry_run": policy.get("required_gates_before_rollback_dry_run", []),
        "next_checkpoint": policy.get("next_checkpoint", "056 - K-Agent Rollback Execution Final Gate Core")
    }

    write_report(report)
    event("rollback_dry_run.audit_generated", {
        "simulation_count": metrics.get("simulation_count")
    })
    return report


def write_simulation(simulation: dict[str, Any]) -> None:
    SIM_JSON.write_text(json.dumps(simulation, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Dry Run Simulation",
        "",
        "- Simulation ID: " + str(simulation.get("simulation_id")),
        "- Status: " + str(simulation.get("status")),
        "- OK: " + str(simulation.get("ok")),
        "- Release ID: " + str(simulation.get("release_id")),
        "- Release status: " + str(simulation.get("release_status")),
        "- Rollback Plan ID: " + str(simulation.get("rollback_plan_id")),
        "- Dry-run hash: " + str(simulation.get("rollback_dry_run_hash")),
        "- Safely blocked by release gate: " + str(simulation.get("safe_blocked_by_release_gate")),
        "- Executes rollback: " + str(simulation.get("dry_run_executes_rollback")),
        "- Deletes data: " + str(simulation.get("dry_run_deletes_data")),
        "- Modifies files: " + str(simulation.get("dry_run_modifies_files")),
        "- Runs git reset: " + str(simulation.get("dry_run_runs_git_reset")),
        "- Runs git force push: " + str(simulation.get("dry_run_runs_git_force_push")),
        "",
        "## Simulation steps",
        ""
    ]

    for item in simulation.get("simulation_steps", []):
        lines.append(
            "- " + str(item.get("step")) +
            " | " + str(item.get("name")) +
            " | result=" + str(item.get("result")) +
            " | executes_rollback=" + str(item.get("executes_rollback"))
        )

    lines.extend(["", "## Blockers", ""])

    if simulation.get("blockers"):
        for item in simulation.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    SIM_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Rollback Dry Run Validation",
        "",
        "- Simulation ID: " + str(result.get("simulation_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Simulation status: " + str(result.get("simulation_status")),
        "- Rollback Plan ID: " + str(result.get("rollback_plan_id")),
        "- Dry-run hash: " + str(result.get("rollback_dry_run_hash")),
        "- Safely blocked by release gate: " + str(result.get("safe_blocked_by_release_gate")),
        "- Executes rollback: " + str(result.get("dry_run_executes_rollback")),
        "- Deletes data: " + str(result.get("dry_run_deletes_data")),
        "- Modifies files: " + str(result.get("dry_run_modifies_files")),
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
        "# K-OS Agent Rollback Dry Run Simulator Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("dry_run_state_committed")),
        "- Executes rollback: " + str(report.get("dry_run_executes_rollback")),
        "- Deletes data: " + str(report.get("dry_run_deletes_data")),
        "- Modifies files: " + str(report.get("dry_run_modifies_files")),
        "- Runs git reset: " + str(report.get("dry_run_runs_git_reset")),
        "- Runs git force push: " + str(report.get("dry_run_runs_git_force_push")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent simulations", ""])

    if report.get("recent_simulations"):
        for item in report.get("recent_simulations", [])[:30]:
            lines.append(
                "- " + str(item.get("simulation_id")) +
                " | status=" + str(item.get("status")) +
                " | release=" + str(item.get("release_id")) +
                " | plan=" + str(item.get("rollback_plan_id"))
            )
    else:
        lines.append("- Nenhuma simulacao registrada.")

    lines.extend(["", "## Required gates before rollback dry-run", ""])

    for gate in report.get("required_gates_before_rollback_dry_run", []):
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
    parser.add_argument("--mode", choices=["init", "simulate", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--operator", default="operator_k_os")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "simulate":
        result = create_simulation(args.reason, args.operator)

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