# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "prompt_assembly" / "k_os_agent_prompt_assembly_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_prompt_assembly"
STATE_PATH = STATE_DIR / "agent_prompt_assembly_state.json"

REPORT_DIR = ROOT / "reports" / "prompt_assembly"
MEMORY_DIR = ROOT / "memory" / "prompt_assembly"

LATEST_JSON = REPORT_DIR / "latest_agent_prompt_assembly_report.json"
LATEST_MD = REPORT_DIR / "latest_agent_prompt_assembly_report.md"
PROMPT_JSON = REPORT_DIR / "latest_agent_prompt_package.json"
PROMPT_MD = REPORT_DIR / "latest_agent_prompt_package.md"
PLAN_JSON = REPORT_DIR / "latest_agent_execution_plan.json"
PLAN_MD = REPORT_DIR / "latest_agent_execution_plan.md"
VALIDATION_JSON = REPORT_DIR / "latest_prompt_assembly_validation_report.json"
VALIDATION_MD = REPORT_DIR / "latest_prompt_assembly_validation_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

CONTEXT_PACKET_REPORT = ROOT / "reports" / "context_injection" / "latest_agent_context_packet.json"
CONTEXT_INJECTION_REPORT = ROOT / "reports" / "context_injection" / "latest_agent_context_injection_report.json"
AGENT_QUEUE_REPORT = ROOT / "reports" / "agent_queue" / "latest_agent_orchestration_queue_report.json"
AGENT_RUNTIME_REPORT = ROOT / "reports" / "agent_runtime" / "latest_agent_runtime_supervisor_report.json"
COMMAND_CENTER_REPORT = ROOT / "reports" / "command_center" / "latest_command_center_action_router_report.json"


SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_\-]{20,}",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"[PRIVATE_KEY_PATTERN_REDACTED]",
    r"api[_-]?key\s*[:=]",
    r"secret\s*[:=]",
    r"token\s*[:=]",
    r"password\s*[:=]"
]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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
        raise RuntimeError("Prompt Assembly policy not found.")
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
            "external_publish_enabled": False,
            "prompt_packages": [],
            "execution_plans": [],
            "validations": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load Prompt Assembly state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def has_secret_marker(data: Any) -> bool:
    raw = json.dumps(data, ensure_ascii=False)
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, raw, flags=re.IGNORECASE):
            return True
    return False


def has_raw_payload_marker(data: Any) -> bool:
    raw = json.dumps(data, ensure_ascii=False).lower()
    markers = [
        '"raw_payload_included": true',
        '"raw_report_included": true',
        '"raw_payload":',
        '"raw_report":',
        '"secret":',
        '"token":',
        '"api_key":',
        '"password":'
    ]
    return any(marker in raw for marker in markers)


def load_context_packet() -> dict[str, Any]:
    packet = read_json(CONTEXT_PACKET_REPORT)
    if packet and not packet.get("_read_error"):
        return packet

    return {
        "ok": False,
        "status": "missing",
        "packet_id": "",
        "agent_id": "k_atlas_engineer",
        "task_id": "manual_prompt_task",
        "action_id": "cockpit_audit",
        "context_event_count": 0,
        "context_item_count": 0,
        "context_packet_hash": "",
        "context": {
            "events": [],
            "context_items": []
        },
        "blockers": ["context_packet_missing"],
        "raw_payload_included": False
    }


def summarize_context(packet: dict[str, Any]) -> dict[str, Any]:
    context = packet.get("context", {})
    events = context.get("events", [])
    context_items = context.get("context_items", [])

    event_summary = []
    for item in events[:10]:
        event_summary.append({
            "domain": item.get("domain", ""),
            "module": item.get("module", ""),
            "event": item.get("event", ""),
            "created_at": item.get("created_at", ""),
            "payload_hash": item.get("payload_hash", ""),
            "raw_payload_included": False
        })

    context_summary = []
    for item in context_items[:10]:
        context_summary.append({
            "domain": item.get("domain", ""),
            "module": item.get("module", ""),
            "checkpoint": item.get("checkpoint", ""),
            "status": item.get("status", ""),
            "ok": item.get("ok", False),
            "report_hash": item.get("report_hash", ""),
            "raw_report_included": False
        })

    return {
        "source_packet_id": packet.get("packet_id", ""),
        "source_packet_hash": packet.get("context_packet_hash", ""),
        "event_count": len(events),
        "context_item_count": len(context_items),
        "events": event_summary,
        "context_items": context_summary,
        "raw_payload_included": False,
        "raw_report_included": False
    }


def infer_task_objective(action_id: str, query: str) -> str:
    if action_id == "cockpit_audit":
        return "Atualizar e auditar o cockpit executivo do K-OS usando contexto operacional sanitizado."
    if action_id == "analytics_audit":
        return "Atualizar métricas executivas e gerar snapshot sanitizado."
    if action_id == "security_scan_staged":
        return "Rodar firewall de segurança no conteúdo staged antes de qualquer commit."
    if query:
        return "Executar tarefa operacional relacionada a: " + query
    return "Executar tarefa operacional governada para o agente."


def build_execution_plan(agent_id: str, task_id: str, action_id: str, objective: str, context_summary: dict[str, Any]) -> dict[str, Any]:
    steps = [
        {
            "step": 1,
            "name": "validar_contexto",
            "description": "Confirmar que o pacote de contexto existe, está sanitizado e possui hash.",
            "gate": "context_packet_validated"
        },
        {
            "step": 2,
            "name": "confirmar_permissao",
            "description": "Confirmar que o agente e a ação são compatíveis com fila, runtime e Command Center.",
            "gate": "agent_permission_and_command_center_gate"
        },
        {
            "step": 3,
            "name": "executar_dry_run",
            "description": "Preparar execução apenas em dry-run, sem envio externo e sem publicação.",
            "gate": "dry_run_completed"
        },
        {
            "step": 4,
            "name": "registrar_evidencia",
            "description": "Registrar pacote, plano, hashes e resultado esperado para auditoria.",
            "gate": "audit_event_recorded"
        }
    ]

    plan = {
        "plan_id": "plan_" + uuid.uuid4().hex[:12],
        "created_at": now(),
        "agent_id": agent_id,
        "task_id": task_id,
        "action_id": action_id,
        "objective": objective,
        "risk_level": "medium",
        "dry_run": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "requires_human_approval_for_real_execution": True,
        "context_packet_hash": context_summary.get("source_packet_hash", ""),
        "steps": steps,
        "expected_output": {
            "type": "sanitized_execution_plan",
            "must_include": [
                "status",
                "dry_run_result",
                "blockers",
                "evidence_hash",
                "next_action"
            ],
            "must_not_include": [
                "raw_payload",
                "secret",
                "token",
                "api_key",
                "password"
            ]
        },
        "blocked_actions": [
            "external_send",
            "external_publish",
            "raw_payload_use",
            "secret_use",
            "real_execution_without_approval"
        ]
    }

    return plan


def assemble_prompt(agent_id: str, task_id: str, action_id: str, query: str, reason: str) -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    packet = load_context_packet()

    if not agent_id:
        agent_id = packet.get("agent_id", "k_atlas_engineer")

    if not task_id:
        task_id = packet.get("task_id", "manual_prompt_task")

    if not action_id:
        action_id = packet.get("action_id", "cockpit_audit")

    if not query:
        query = packet.get("query", action_id)

    objective = infer_task_objective(action_id, query)
    context_summary = summarize_context(packet)
    execution_plan = build_execution_plan(agent_id, task_id, action_id, objective, context_summary)

    prompt_sections = {
        "agent_identity": {
            "agent_id": agent_id,
            "role": "K-OS governed operational agent",
            "must_follow_governance": True
        },
        "task_objective": objective,
        "context_summary": context_summary,
        "constraints": [
            "Não usar payload bruto.",
            "Não revelar secrets.",
            "Não enviar mensagem externa.",
            "Não publicar conteúdo externo.",
            "Executar somente em dry-run até aprovação humana.",
            "Registrar evidência e hashes."
        ],
        "allowed_actions": [
            action_id,
            "audit",
            "validate",
            "dry_run"
        ],
        "execution_plan": execution_plan,
        "expected_output": execution_plan["expected_output"],
        "safety_gates": policy.get("required_gates_before_agent_execution", [])
    }

    package_body = {
        "agent_id": agent_id,
        "task_id": task_id,
        "action_id": action_id,
        "prompt_sections": prompt_sections
    }

    blockers = []

    if not packet.get("packet_id"):
        blockers.append("context_packet_missing")

    if packet.get("status") not in {"created", "validated", "ready_for_agent"}:
        blockers.append("context_packet_not_validated_or_ready")

    if has_raw_payload_marker(package_body):
        blockers.append("raw_payload_marker_detected")

    if has_secret_marker(package_body):
        blockers.append("secret_marker_detected")

    prompt_package = {
        "ok": len(blockers) == 0,
        "checkpoint": "045",
        "module": "k_os_agent_prompt_assembly_execution_plan_core",
        "status": "blocked" if blockers else "assembled",
        "prompt_package_id": "prmpt_" + uuid.uuid4().hex[:12],
        "created_at": now(),
        "agent_id": agent_id,
        "task_id": task_id,
        "action_id": action_id,
        "reason": reason or "prompt_assembled",
        "objective": objective,
        "context_packet_id": packet.get("packet_id", ""),
        "context_packet_hash": packet.get("context_packet_hash", ""),
        "prompt_package_hash": stable_hash(package_body),
        "execution_plan_id": execution_plan.get("plan_id"),
        "execution_plan_hash": stable_hash(execution_plan),
        "raw_payload_included": False,
        "secret_included": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "dry_run": True,
        "blockers": blockers,
        "prompt_sections": prompt_sections,
        "next_action": "validate_prompt_package" if not blockers else "resolve_blockers"
    }

    state.setdefault("prompt_packages", []).append(prompt_package)
    state.setdefault("execution_plans", []).append(execution_plan)
    state["prompt_packages"] = state["prompt_packages"][-300:]
    state["execution_plans"] = state["execution_plans"][-300:]
    save_state(state)

    write_prompt_package(prompt_package)
    write_execution_plan(execution_plan)

    event("prompt_assembly.prompt_assembled", {
        "prompt_package_id": prompt_package.get("prompt_package_id"),
        "agent_id": agent_id,
        "task_id": task_id,
        "blockers": blockers
    })

    return audit_report()


def create_demo() -> dict[str, Any]:
    packet = load_context_packet()
    return assemble_prompt(
        agent_id=packet.get("agent_id", "k_atlas_engineer"),
        task_id=packet.get("task_id", "manual_prompt_task"),
        action_id=packet.get("action_id", "cockpit_audit"),
        query=packet.get("query", "agent"),
        reason="demo_prompt_assembly"
    )


def latest_prompt_package_raw() -> dict[str, Any] | None:
    state = ensure_state()
    items = state.get("prompt_packages", [])
    if not items:
        return None
    return items[-1]


def validate_latest() -> dict[str, Any]:
    state = ensure_state()
    package = latest_prompt_package_raw()

    blockers = []
    warnings = []

    if not package:
        blockers.append("prompt_package_not_found")
    else:
        if not package.get("prompt_package_hash"):
            blockers.append("prompt_package_hash_missing")

        if not package.get("execution_plan_hash"):
            blockers.append("execution_plan_hash_missing")

        if not package.get("context_packet_hash"):
            warnings.append("context_packet_hash_missing")

        if package.get("raw_payload_included") is True:
            blockers.append("raw_payload_included")

        if package.get("secret_included") is True:
            blockers.append("secret_included")

        if has_raw_payload_marker(package):
            blockers.append("raw_payload_marker_detected")

        if has_secret_marker(package):
            blockers.append("secret_marker_detected")

        if package.get("external_send_enabled") is True:
            blockers.append("external_send_enabled")

        if package.get("external_publish_enabled") is True:
            blockers.append("external_publish_enabled")

    result = {
        "ok": len(blockers) == 0,
        "checkpoint": "045",
        "module": "k_os_agent_prompt_assembly_execution_plan_core",
        "status": "validated" if len(blockers) == 0 else "blocked",
        "generated_at": now(),
        "prompt_package_id": package.get("prompt_package_id") if package else "",
        "agent_id": package.get("agent_id") if package else "",
        "task_id": package.get("task_id") if package else "",
        "action_id": package.get("action_id") if package else "",
        "prompt_package_hash": package.get("prompt_package_hash") if package else "",
        "execution_plan_hash": package.get("execution_plan_hash") if package else "",
        "blockers": blockers,
        "warnings": warnings,
        "raw_payload_included": False,
        "secret_included": False,
        "external_send_enabled": False,
        "external_publish_enabled": False
    }

    if package and len(blockers) == 0:
        package["status"] = "validated"
        package["validated_at"] = result["generated_at"]
        package["next_action"] = "ready_for_dry_run_executor"
        save_state(state)

    state.setdefault("validations", []).append(result)
    state["validations"] = state["validations"][-300:]
    save_state(state)

    write_validation(result)

    event("prompt_assembly.validation_completed", {
        "prompt_package_id": result.get("prompt_package_id"),
        "ok": result.get("ok"),
        "blockers": blockers
    })

    return audit_report()


def safe_package(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "prompt_package_id": item.get("prompt_package_id"),
        "created_at": item.get("created_at"),
        "agent_id": item.get("agent_id"),
        "task_id": item.get("task_id"),
        "action_id": item.get("action_id"),
        "status": item.get("status"),
        "ok": item.get("ok"),
        "objective": item.get("objective"),
        "context_packet_id": item.get("context_packet_id"),
        "context_packet_hash": item.get("context_packet_hash"),
        "prompt_package_hash": item.get("prompt_package_hash"),
        "execution_plan_id": item.get("execution_plan_id"),
        "execution_plan_hash": item.get("execution_plan_hash"),
        "raw_payload_included": False,
        "secret_included": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "dry_run": True,
        "blockers": item.get("blockers", [])
    }


def compute_metrics(packages: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    agent_counts: dict[str, int] = {}

    for item in packages:
        status = item.get("status", "unknown")
        agent_id = item.get("agent_id", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1

    return {
        "prompt_package_count": len(packages),
        "validation_count": len(validations),
        "assembled_count": status_counts.get("assembled", 0),
        "validated_count": status_counts.get("validated", 0),
        "blocked_count": status_counts.get("blocked", 0),
        "raw_payload_package_count": 0,
        "secret_package_count": 0,
        "status_counts": status_counts,
        "agent_counts": agent_counts
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    packages = [safe_package(item) for item in reversed(state.get("prompt_packages", []))][:100]
    validations = list(reversed(state.get("validations", [])))[:50]
    metrics = compute_metrics(packages, validations)

    report = {
        "ok": True,
        "checkpoint": "045",
        "module": "k_os_agent_prompt_assembly_execution_plan_core",
        "status": "audit_generated",
        "generated_at": now(),
        "prompt_assembly_state_path": "local_secrets/k_os_prompt_assembly/agent_prompt_assembly_state.json",
        "prompt_assembly_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "raw_payload_prompt_allowed": False,
        "secret_in_prompt_allowed": False,
        "dry_run_default": True,
        "context_packet_report_available": CONTEXT_PACKET_REPORT.exists(),
        "context_injection_report_available": CONTEXT_INJECTION_REPORT.exists(),
        "agent_queue_report_available": AGENT_QUEUE_REPORT.exists(),
        "agent_runtime_report_available": AGENT_RUNTIME_REPORT.exists(),
        "command_center_report_available": COMMAND_CENTER_REPORT.exists(),
        "metrics": metrics,
        "recent_prompt_packages": packages,
        "recent_validations": validations,
        "required_gates_before_agent_execution": policy.get("required_gates_before_agent_execution", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "046 - K-Agent Dry Run Executor Core")
    }

    write_report(report)
    event("prompt_assembly.audit_generated", {
        "prompt_package_count": metrics.get("prompt_package_count")
    })
    return report


def write_prompt_package(package: dict[str, Any]) -> None:
    PROMPT_JSON.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Prompt Package",
        "",
        "- Prompt Package ID: " + str(package.get("prompt_package_id")),
        "- Status: " + str(package.get("status")),
        "- OK: " + str(package.get("ok")),
        "- Agent: " + str(package.get("agent_id")),
        "- Task: " + str(package.get("task_id")),
        "- Action: " + str(package.get("action_id")),
        "- Objective: " + str(package.get("objective")),
        "- Context packet hash: " + str(package.get("context_packet_hash")),
        "- Prompt package hash: " + str(package.get("prompt_package_hash")),
        "- Execution plan hash: " + str(package.get("execution_plan_hash")),
        "- Raw payload included: " + str(package.get("raw_payload_included")),
        "- Secret included: " + str(package.get("secret_included")),
        "- External publish enabled: " + str(package.get("external_publish_enabled")),
        "",
        "## Blockers",
        ""
    ]

    if package.get("blockers"):
        for item in package.get("blockers", []):
            lines.append("- " + str(item))
    else:
        lines.append("- Nenhum blocker.")

    PROMPT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_execution_plan(plan: dict[str, Any]) -> None:
    PLAN_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Agent Execution Plan",
        "",
        "- Plan ID: " + str(plan.get("plan_id")),
        "- Agent: " + str(plan.get("agent_id")),
        "- Task: " + str(plan.get("task_id")),
        "- Action: " + str(plan.get("action_id")),
        "- Objective: " + str(plan.get("objective")),
        "- Dry run: " + str(plan.get("dry_run")),
        "- Requires approval for real execution: " + str(plan.get("requires_human_approval_for_real_execution")),
        "",
        "## Steps",
        ""
    ]

    for item in plan.get("steps", []):
        lines.append(
            "- " + str(item.get("step")) +
            " | " + str(item.get("name")) +
            " | gate=" + str(item.get("gate"))
        )

    lines.extend(["", "## Blocked actions", ""])

    for item in plan.get("blocked_actions", []):
        lines.append("- " + str(item))

    PLAN_MD.write_text("\n".join(lines), encoding="utf-8")


def write_validation(result: dict[str, Any]) -> None:
    VALIDATION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Prompt Assembly Validation Report",
        "",
        "- Prompt Package ID: " + str(result.get("prompt_package_id")),
        "- Status: " + str(result.get("status")),
        "- OK: " + str(result.get("ok")),
        "- Agent: " + str(result.get("agent_id")),
        "- Task: " + str(result.get("task_id")),
        "- Action: " + str(result.get("action_id")),
        "- Raw payload included: " + str(result.get("raw_payload_included")),
        "- Secret included: " + str(result.get("secret_included")),
        "- External publish enabled: " + str(result.get("external_publish_enabled")),
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
        "# K-OS Agent Prompt Assembly and Execution Plan Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("prompt_assembly_state_committed")),
        "- Raw payload prompt allowed: " + str(report.get("raw_payload_prompt_allowed")),
        "- Secret in prompt allowed: " + str(report.get("secret_in_prompt_allowed")),
        "- Dry-run default: " + str(report.get("dry_run_default")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Recent prompt packages", ""])

    if report.get("recent_prompt_packages"):
        for item in report.get("recent_prompt_packages", [])[:30]:
            lines.append(
                "- " + str(item.get("prompt_package_id")) +
                " | agent=" + str(item.get("agent_id")) +
                " | task=" + str(item.get("task_id")) +
                " | status=" + str(item.get("status")) +
                " | action=" + str(item.get("action_id"))
            )
    else:
        lines.append("- Nenhum prompt package registrado.")

    lines.extend(["", "## Required gates before agent execution", ""])

    for gate in report.get("required_gates_before_agent_execution", []):
        lines.append("- " + str(gate))

    lines.extend(["", "## Blocked actions", ""])

    for item in report.get("blocked_actions", []):
        lines.append("- " + str(item))

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
    parser.add_argument("--mode", choices=["init", "create-demo", "assemble", "validate-latest", "audit", "show"], required=True)
    parser.add_argument("--agent-id", default="k_atlas_engineer")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--action-id", default="")
    parser.add_argument("--query", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "assemble":
        result = assemble_prompt(
            agent_id=args.agent_id,
            task_id=args.task_id,
            action_id=args.action_id,
            query=args.query,
            reason=args.reason
        )

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
