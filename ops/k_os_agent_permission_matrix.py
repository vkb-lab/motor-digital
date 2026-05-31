# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
MATRIX_PATH = ROOT / "config" / "governance" / "k_os_agent_permission_matrix.json"
REPORT_DIR = ROOT / "reports" / "governance"
MEMORY_DIR = ROOT / "memory" / "governance"
LATEST_JSON = REPORT_DIR / "latest_agent_permission_matrix_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_permission_matrix_report.md"
EVENTS_JSONL = MEMORY_DIR / "agent_permission_events.jsonl"

REQUIRED_AGENT_FIELDS = [
    "agent_id",
    "name",
    "type",
    "purpose",
    "human_owner",
    "risk_level",
    "autonomy_level",
    "can_read",
    "can_write",
    "can_execute_local",
    "can_commit",
    "can_push",
    "can_publish_external",
    "can_send_external",
    "can_access_credentials",
    "approval_gate_required",
    "required_gates",
    "forbidden_actions",
    "evidence_required",
]

VALID_RISK = {"low", "medium", "high", "critical"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def err(code: str, msg: str, field: str = "", severity: str = "high") -> dict[str, Any]:
    return {
        "code": code,
        "message": msg,
        "field": field,
        "severity": severity,
    }


def load_matrix() -> dict[str, Any]:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8-sig"))


def validate_agent(agent: dict[str, Any], ids: set[str]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    for field in REQUIRED_AGENT_FIELDS:
        if field not in agent:
            errors.append(err("missing_field", f"Campo obrigatório ausente: {field}", field))

    agent_id = agent.get("agent_id", "")

    if not isinstance(agent_id, str) or not agent_id.strip():
        errors.append(err("invalid_agent_id", "agent_id inválido", "agent_id"))

    if agent_id in ids:
        errors.append(err("duplicate_agent_id", f"agent_id duplicado: {agent_id}", "agent_id", "critical"))

    ids.add(agent_id)

    risk = agent.get("risk_level")
    if risk not in VALID_RISK:
        errors.append(err("invalid_risk_level", "risk_level deve ser low, medium, high ou critical", "risk_level"))

    autonomy = agent.get("autonomy_level")
    if not isinstance(autonomy, int) or autonomy < 0 or autonomy > 5:
        errors.append(err("invalid_autonomy_level", "autonomy_level deve ser inteiro entre 0 e 5", "autonomy_level"))

    for list_field in ["can_read", "can_write", "required_gates", "forbidden_actions", "evidence_required"]:
        if not isinstance(agent.get(list_field), list):
            errors.append(err("invalid_list", f"{list_field} deve ser lista", list_field))

    for bool_field in [
        "can_execute_local",
        "can_commit",
        "can_push",
        "can_publish_external",
        "can_send_external",
        "can_access_credentials",
        "approval_gate_required",
    ]:
        if not isinstance(agent.get(bool_field), bool):
            errors.append(err("invalid_bool", f"{bool_field} deve ser booleano", bool_field))

    if agent.get("can_publish_external") is True:
        errors.append(err("external_publish_blocked", "Nenhum agente pode publicar externamente neste estágio", "can_publish_external", "critical"))

    if agent.get("can_send_external") is True:
        errors.append(err("external_send_blocked", "Nenhum agente pode enviar externamente neste estágio", "can_send_external", "critical"))

    if agent.get("can_access_credentials") is True:
        errors.append(err("credential_access_blocked", "Acesso a credenciais exige K-Credential Vault futuro", "can_access_credentials", "critical"))

    if agent.get("can_commit") is True and "security_firewall" not in agent.get("required_gates", []):
        errors.append(err("commit_without_firewall", "Agente com commit precisa security_firewall em required_gates", "required_gates", "critical"))

    if agent.get("risk_level") in {"high", "critical"} and agent.get("approval_gate_required") is False:
        automatic_ok = any(
            gate in agent.get("required_gates", [])
            for gate in ["automatic_blocking_policy", "automatic_schema_validation"]
        )

        if not automatic_ok:
            errors.append(err("high_risk_without_gate", "Agente high/critical precisa approval gate ou política automática", "approval_gate_required", "critical"))

    return errors


def validate_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    if not isinstance(matrix, dict):
        errors.append(err("invalid_root", "Matriz precisa ser objeto", "root", "critical"))
        return build_report(False, errors, 0, 0, [])

    policy = matrix.get("policy", {})
    agents = matrix.get("agents", [])
    councils = matrix.get("councils", [])

    if not isinstance(policy, dict):
        errors.append(err("invalid_policy", "policy precisa ser objeto", "policy"))

    if policy.get("default_external_send_enabled") is not False:
        errors.append(err("unsafe_policy", "default_external_send_enabled precisa ser false", "policy.default_external_send_enabled", "critical"))

    if policy.get("default_external_publish_enabled") is not False:
        errors.append(err("unsafe_policy", "default_external_publish_enabled precisa ser false", "policy.default_external_publish_enabled", "critical"))

    if policy.get("manual_approval_required") is not True:
        errors.append(err("unsafe_policy", "manual_approval_required precisa ser true", "policy.manual_approval_required", "critical"))

    if not isinstance(councils, list) or not councils:
        errors.append(err("missing_councils", "É obrigatório registrar conselhos de governança", "councils"))

    if not isinstance(agents, list) or not agents:
        errors.append(err("missing_agents", "É obrigatório registrar agentes", "agents", "critical"))
        return build_report(False, errors, 0, len(councils) if isinstance(councils, list) else 0, [])

    ids: set[str] = set()
    agent_results = []

    for agent in agents:
        if not isinstance(agent, dict):
            errors.append(err("invalid_agent", "Agente precisa ser objeto", "agents"))
            continue

        agent_errors = validate_agent(agent, ids)
        errors.extend(agent_errors)
        agent_results.append({
            "agent_id": agent.get("agent_id"),
            "name": agent.get("name"),
            "risk_level": agent.get("risk_level"),
            "autonomy_level": agent.get("autonomy_level"),
            "errors_count": len(agent_errors),
            "ok": len([e for e in agent_errors if e.get("severity") in {"critical", "high"}]) == 0,
        })

    blocking = [e for e in errors if e.get("severity") in {"critical", "high"}]

    return build_report(
        ok=len(blocking) == 0,
        errors=errors,
        agent_count=len(agents),
        council_count=len(councils) if isinstance(councils, list) else 0,
        agent_results=agent_results,
    )


def build_report(ok: bool, errors: list[dict[str, Any]], agent_count: int, council_count: int, agent_results: list[dict[str, Any]]) -> dict[str, Any]:
    blocking = [e for e in errors if e.get("severity") in {"critical", "high"}]

    return {
        "ok": ok,
        "checkpoint": "017",
        "module": "k_os_agent_permission_matrix",
        "status": "passed" if ok else "blocked_by_permission_policy",
        "generated_at": now(),
        "matrix_path": "config/governance/k_os_agent_permission_matrix.json",
        "agent_count": agent_count,
        "council_count": council_count,
        "errors_count": len(errors),
        "blocking_errors_count": len(blocking),
        "errors": errors,
        "agent_results": agent_results,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "manual_approval_required": True,
        "next_checkpoint": "018 - K-Credential Vault",
    }


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Permission Matrix Report",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Agents: {report.get('agent_count')}",
        f"- Councils: {report.get('council_count')}",
        f"- Errors: {report.get('errors_count')}",
        f"- Blocking errors: {report.get('blocking_errors_count')}",
        "",
        "## Agents",
        "",
    ]

    for agent in report.get("agent_results", []):
        lines.append(
            f"- {agent.get('agent_id')} | risk={agent.get('risk_level')} | autonomy={agent.get('autonomy_level')} | ok={agent.get('ok')}"
        )

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": "agent_permission_matrix.validation",
            "created_at": now(),
            "ok": report.get("ok"),
            "status": report.get("status"),
            "blocking_errors_count": report.get("blocking_errors_count"),
        }, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["validate", "show"], default="validate")
    args = parser.parse_args()

    matrix = load_matrix()

    if args.mode == "show":
        print(json.dumps(matrix, ensure_ascii=False, indent=2))
        return 0

    report = validate_matrix(matrix)
    write_report(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())