# -*- coding: utf-8 -*-
"""
K-Atlas OS - Decision Flow Router
Stage 64

Conecta decisoes humanas ao fluxo seguinte:
- APPROVE permite continuidade interna supervisionada
- DENY bloqueia execucao
- REQUEST_ADJUSTMENTS devolve ao planejador para revisao

Sem API externa real.
Sem publicacao automatica.
Sem deploy automatico.
Sem navegador automatico.
Sem mouse automatico.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]

HDC_MEMORY_DIR = ROOT / "memory" / "human_decision_center"
HDC_DECISIONS_JSONL = HDC_MEMORY_DIR / "decisions.jsonl"

LIVE_DIR = ROOT / "live" / "decision_flow_router"
MEMORY_DIR = ROOT / "memory" / "decision_flow_router"
REPORTS_DIR = ROOT / "reports" / "decision_flow_router"

SUPERVISED_QUEUE_DIR = ROOT / "live" / "supervised_continuation_queue"
SUPERVISED_REPORTS_DIR = ROOT / "reports" / "supervised_continuation_queue"
BLOCK_REPORTS_DIR = ROOT / "reports" / "decision_blocks"
ADJUSTMENT_REPORTS_DIR = ROOT / "reports" / "planning_adjustment_requests"

EVENTS_JSONL = MEMORY_DIR / "events.jsonl"
ROUTES_JSONL = MEMORY_DIR / "routes.jsonl"

LATEST_ROUTE_STATE = LIVE_DIR / "latest_route_state.json"
APPROVED_QUEUE = LIVE_DIR / "approved_continuation_queue.json"
DENIED_QUEUE = LIVE_DIR / "blocked_denied_queue.json"
ADJUSTMENT_QUEUE = LIVE_DIR / "adjustment_request_queue.json"
ROUTED_DECISIONS = LIVE_DIR / "routed_decisions.json"

SUPERVISED_QUEUE = SUPERVISED_QUEUE_DIR / "stage_064_supervised_continuation_queue.json"


ROUTE_RULES = {
    "APPROVE": {
        "route_type": "SUPERVISED_CONTINUATION",
        "route_status": "READY_FOR_SUPERVISED_INTERNAL_CONTINUATION",
        "next_action": "ALLOW_INTERNAL_SUPERVISED_CONTINUATION",
        "queue_name": "approved_continuation_queue",
        "effect": "A decisao humana aprovou continuidade interna supervisionada. Publicacao e deploy seguem bloqueados.",
    },
    "APPROVED": {
        "route_type": "SUPERVISED_CONTINUATION",
        "route_status": "READY_FOR_SUPERVISED_INTERNAL_CONTINUATION",
        "next_action": "ALLOW_INTERNAL_SUPERVISED_CONTINUATION",
        "queue_name": "approved_continuation_queue",
        "effect": "A decisao humana aprovou continuidade interna supervisionada. Publicacao e deploy seguem bloqueados.",
    },
    "DENY": {
        "route_type": "EXECUTION_BLOCK",
        "route_status": "BLOCKED_BY_HUMAN_DECISION",
        "next_action": "BLOCK_EXECUTION",
        "queue_name": "blocked_denied_queue",
        "effect": "A decisao humana negou o pacote. Qualquer continuidade automatica deve ser bloqueada.",
    },
    "DENIED": {
        "route_type": "EXECUTION_BLOCK",
        "route_status": "BLOCKED_BY_HUMAN_DECISION",
        "next_action": "BLOCK_EXECUTION",
        "queue_name": "blocked_denied_queue",
        "effect": "A decisao humana negou o pacote. Qualquer continuidade automatica deve ser bloqueada.",
    },
    "REQUEST_ADJUSTMENTS": {
        "route_type": "PLANNER_REVISION_REQUEST",
        "route_status": "RETURNED_TO_PLANNER_FOR_REVISION",
        "next_action": "REQUEST_PLANNER_ADJUSTMENTS",
        "queue_name": "adjustment_request_queue",
        "effect": "A decisao humana pediu ajustes. O pacote deve voltar ao planejador antes de qualquer continuidade.",
    },
    "ADJUSTMENTS_REQUESTED": {
        "route_type": "PLANNER_REVISION_REQUEST",
        "route_status": "RETURNED_TO_PLANNER_FOR_REVISION",
        "next_action": "REQUEST_PLANNER_ADJUSTMENTS",
        "queue_name": "adjustment_request_queue",
        "effect": "A decisao humana pediu ajustes. O pacote deve voltar ao planejador antes de qualquer continuidade.",
    },
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stage_tag(stage: int) -> str:
    return f"stage_{int(stage):03d}"


def ensure_dirs() -> None:
    for path in [
        HDC_MEMORY_DIR,
        LIVE_DIR,
        MEMORY_DIR,
        REPORTS_DIR,
        SUPERVISED_QUEUE_DIR,
        SUPERVISED_REPORTS_DIR,
        BLOCK_REPORTS_DIR,
        ADJUSTMENT_REPORTS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def safe_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def safe_slug(value: str) -> str:
    allowed = []
    for char in value:
        if char.isalnum() or char in ("-", "_"):
            allowed.append(char)
        else:
            allowed.append("_")
    slug = "".join(allowed).strip("_")
    return slug[:120] or "item"


def stable_hash(value: str, size: int = 12) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:size]


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_jsonl(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    items: List[Dict[str, Any]] = []

    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                append_jsonl(EVENTS_JSONL, {
                    "event_type": "JSONL_READ_ERROR",
                    "created_at": now_utc(),
                    "source_path": safe_relative(path),
                    "line_preview": line[:160],
                })
                continue

            if isinstance(data, dict):
                items.append(data)

    return items


def normalize_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else fallback
    return str(value)


def decision_key(record: Dict[str, Any]) -> str:
    decision = normalize_text(record.get("decision")).upper()
    status = normalize_text(record.get("status")).upper()

    if decision in ROUTE_RULES:
        return decision

    if status in ROUTE_RULES:
        return status

    return decision or status or "UNKNOWN"


def latest_decisions_by_package() -> Dict[str, Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}

    for record in read_jsonl(HDC_DECISIONS_JSONL):
        package_id = normalize_text(record.get("package_id"))

        if not package_id:
            continue

        key = decision_key(record)

        if key not in ROUTE_RULES:
            append_jsonl(EVENTS_JSONL, {
                "event_type": "UNROUTABLE_HUMAN_DECISION",
                "created_at": now_utc(),
                "package_id": package_id,
                "decision": normalize_text(record.get("decision")),
                "status": normalize_text(record.get("status")),
            })
            continue

        latest[package_id] = record

    return latest


def make_route(record: Dict[str, Any], stage: int) -> Dict[str, Any]:
    key = decision_key(record)
    rule = ROUTE_RULES[key]

    package_id = normalize_text(record.get("package_id"))
    decision_id = normalize_text(record.get("decision_id"), fallback=f"missing_decision_id_{stable_hash(package_id)}")
    route_id = f"route_{stable_hash(package_id + '|' + decision_id + '|' + rule['route_type'], 16)}"

    route = {
        "route_id": route_id,
        "system": "K-Atlas OS",
        "module": "decision_flow_router",
        "stage": int(stage),
        "created_at": now_utc(),
        "source_module": "human_decision_center",
        "source_decision_id": decision_id,
        "package_id": package_id,
        "package_title": normalize_text(record.get("package_title"), fallback="Pacote sem titulo"),
        "package_source_path": normalize_text(record.get("package_source_path"), fallback="unknown"),
        "human_decision": normalize_text(record.get("decision")),
        "human_status": normalize_text(record.get("status")),
        "human_reason": normalize_text(record.get("reason"), fallback="Sem justificativa informada."),
        "operator": normalize_text(record.get("operator"), fallback="human_operator"),
        "route_type": rule["route_type"],
        "route_status": rule["route_status"],
        "next_action": rule["next_action"],
        "queue_name": rule["queue_name"],
        "effect": rule["effect"],
        "requires_human_governance": True,
        "requires_runner_confirmation": True,
        "governance": {
            "human_approval_required": True,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_calls": False,
            "browser_automation": False,
            "mouse_automation": False,
            "unsafe_automation_allowed": False,
        },
    }

    return route


def write_route_artifact(route: Dict[str, Any], stage: int) -> str:
    package_slug = safe_slug(route["package_id"])
    route_type = route["route_type"]

    if route_type == "SUPERVISED_CONTINUATION":
        path = SUPERVISED_REPORTS_DIR / f"{stage_tag(stage)}_{package_slug}_continuation.json"
        payload = {
            "artifact_type": "supervised_continuation_task",
            "created_at": now_utc(),
            "route": route,
            "allowed_scope": [
                "internal_planning",
                "local_file_generation",
                "local_report_generation",
                "supervised_runner_execution",
            ],
            "blocked_scope": [
                "auto_publish",
                "auto_deploy",
                "external_api_call",
                "browser_automation",
                "mouse_automation",
            ],
        }
    elif route_type == "EXECUTION_BLOCK":
        path = BLOCK_REPORTS_DIR / f"{stage_tag(stage)}_{package_slug}_block.json"
        payload = {
            "artifact_type": "execution_block",
            "created_at": now_utc(),
            "route": route,
            "blocked": True,
            "block_reason": route["human_reason"],
            "unlock_condition": "Criar novo pacote ou nova decisao humana aprovada.",
        }
    elif route_type == "PLANNER_REVISION_REQUEST":
        path = ADJUSTMENT_REPORTS_DIR / f"{stage_tag(stage)}_{package_slug}_adjustment_request.json"
        payload = {
            "artifact_type": "planner_revision_request",
            "created_at": now_utc(),
            "route": route,
            "requested_adjustments": route["human_reason"],
            "return_to_module": "planning_approval_packager",
            "required_output": "novo pacote revisado para decisao humana",
        }
    else:
        path = REPORTS_DIR / f"{stage_tag(stage)}_{package_slug}_unknown_route.json"
        payload = {
            "artifact_type": "unknown_route",
            "created_at": now_utc(),
            "route": route,
        }

    write_json(path, payload)
    return safe_relative(path)


def render_route_report(result: Dict[str, Any]) -> str:
    lines = [
        f"# K-Atlas Stage {result['stage']} - Decision Flow Router Report",
        "",
        f"Status: `{result['status']}`",
        f"Gerado em: {result['generated_at']}",
        "",
        "## Objetivo",
        "",
        "Conectar decisoes humanas ao fluxo seguinte com governanca local e auditavel.",
        "",
        "## Resumo",
        "",
        f"- Decisoes humanas lidas: {result['summary']['human_decisions_read']}",
        f"- Rotas geradas: {result['summary']['routes_total']}",
        f"- Aprovadas para continuidade supervisionada: {result['summary']['approved_routes']}",
        f"- Bloqueadas por negacao humana: {result['summary']['denied_routes']}",
        f"- Devolvidas ao planejador para ajustes: {result['summary']['adjustment_routes']}",
        "",
        "## Rotas",
        "",
    ]

    if not result["routes"]:
        lines.append("Nenhuma decisao humana roteavel encontrada.")
    else:
        for route in result["routes"]:
            lines.extend([
                f"### {route['package_id']}",
                "",
                f"- Route ID: `{route['route_id']}`",
                f"- Decisao humana: `{route['human_decision']}`",
                f"- Status humano: `{route['human_status']}`",
                f"- Tipo de rota: `{route['route_type']}`",
                f"- Proxima acao: `{route['next_action']}`",
                f"- Artefato: `{route.get('route_artifact_path', 'nao gerado')}`",
                "",
                route["effect"],
                "",
            ])

    lines.extend([
        "## Travas confirmadas",
        "",
        "- Sem API externa real",
        "- Sem publicacao automatica",
        "- Sem deploy automatico",
        "- Sem navegador automatico",
        "- Sem mouse automatico",
        "- Continuidade somente supervisionada",
        "",
    ])

    return "\n".join(lines).rstrip() + "\n"


def render_next_prompt(stage: int) -> str:
    next_stage = int(stage) + 1

    return f"""K-Atlas Engineer, contexto operacional atual:

A etapa {stage} criou o Decision Flow Router.

Estado atual:
- Decisoes humanas sao roteadas para fluxos internos
- APPROVE gera fila de continuidade supervisionada
- DENY gera bloqueio auditavel
- REQUEST_ADJUSTMENTS gera pedido de revisao para o planejador
- Sem publicacao automatica
- Sem deploy automatico
- Sem API externa real
- Sem navegador automatico
- Sem mouse automatico
- Cada rota gera arquivo, log e relatorio

Artefatos principais:
- live/decision_flow_router/routed_decisions.json
- live/decision_flow_router/approved_continuation_queue.json
- live/decision_flow_router/blocked_denied_queue.json
- live/decision_flow_router/adjustment_request_queue.json
- live/supervised_continuation_queue/stage_064_supervised_continuation_queue.json
- memory/decision_flow_router/routes.jsonl
- memory/decision_flow_router/events.jsonl
- reports/decision_flow_router/stage_064_route_report.md

Missao:
Gerar a etapa {next_stage} do K-Atlas OS.

Objetivo recomendado:
Criar o executor interno supervisionado da fila aprovada, sem publicar, sem deploy e sem API externa real.
Ele deve pegar apenas itens APPROVE roteados, transformar em tarefas locais seguras, gerar relatorio de execucao simulada e manter bloqueios para DENY e REQUEST_ADJUSTMENTS.

Regras obrigatorias:
- responder em portugues
- entregar um unico bloco PowerShell completo
- compativel com Windows PowerShell
- usar UTF-8
- incluir smoke test
- incluir commit
- incluir push
- nao usar navegador automatico
- nao usar mouse automatico
- nao chamar API externa real
- nao publicar nada
- nao fazer deploy automatico
- cada acao importante deve gerar arquivo, log ou relatorio
"""


def route_latest_decisions(stage: int = 64) -> Dict[str, Any]:
    ensure_dirs()

    latest = latest_decisions_by_package()

    routes: List[Dict[str, Any]] = []
    approved: List[Dict[str, Any]] = []
    denied: List[Dict[str, Any]] = []
    adjustments: List[Dict[str, Any]] = []

    for package_id in sorted(latest.keys()):
        record = latest[package_id]
        route = make_route(record, stage=stage)
        route["route_artifact_path"] = write_route_artifact(route, stage=stage)

        routes.append(route)

        if route["route_type"] == "SUPERVISED_CONTINUATION":
            approved.append(route)
        elif route["route_type"] == "EXECUTION_BLOCK":
            denied.append(route)
        elif route["route_type"] == "PLANNER_REVISION_REQUEST":
            adjustments.append(route)

        append_jsonl(ROUTES_JSONL, route)
        append_jsonl(EVENTS_JSONL, {
            "event_type": "DECISION_ROUTED",
            "created_at": route["created_at"],
            "stage": int(stage),
            "route_id": route["route_id"],
            "package_id": route["package_id"],
            "route_type": route["route_type"],
            "next_action": route["next_action"],
            "artifact_path": route["route_artifact_path"],
        })

    generated_at = now_utc()

    result = {
        "system": "K-Atlas OS",
        "module": "decision_flow_router",
        "stage": int(stage),
        "status": "PASS",
        "generated_at": generated_at,
        "summary": {
            "human_decisions_read": len(latest),
            "routes_total": len(routes),
            "approved_routes": len(approved),
            "denied_routes": len(denied),
            "adjustment_routes": len(adjustments),
        },
        "governance": {
            "human_approval_required": True,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_calls": False,
            "browser_automation": False,
            "mouse_automation": False,
            "unsafe_automation_allowed": False,
        },
        "routes": routes,
        "queues": {
            "approved_continuation_queue": safe_relative(APPROVED_QUEUE),
            "blocked_denied_queue": safe_relative(DENIED_QUEUE),
            "adjustment_request_queue": safe_relative(ADJUSTMENT_QUEUE),
            "supervised_continuation_queue": safe_relative(SUPERVISED_QUEUE),
        },
    }

    write_json(ROUTED_DECISIONS, result)
    write_json(APPROVED_QUEUE, {
        "generated_at": generated_at,
        "queue_type": "approved_continuation_queue",
        "count": len(approved),
        "items": approved,
    })
    write_json(DENIED_QUEUE, {
        "generated_at": generated_at,
        "queue_type": "blocked_denied_queue",
        "count": len(denied),
        "items": denied,
    })
    write_json(ADJUSTMENT_QUEUE, {
        "generated_at": generated_at,
        "queue_type": "adjustment_request_queue",
        "count": len(adjustments),
        "items": adjustments,
    })
    write_json(SUPERVISED_QUEUE, {
        "generated_at": generated_at,
        "queue_type": "supervised_internal_continuation",
        "count": len(approved),
        "items": approved,
        "runner_policy": {
            "requires_manual_runner_confirmation": True,
            "allowed_execution": "local_supervised_only",
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_calls": False,
        },
    })

    write_json(LATEST_ROUTE_STATE, result)
    write_json(REPORTS_DIR / f"{stage_tag(stage)}_route_report.json", result)
    write_text(REPORTS_DIR / f"{stage_tag(stage)}_route_report.md", render_route_report(result))
    write_text(REPORTS_DIR / f"stage_{int(stage) + 1:03d}_next_prompt.md", render_next_prompt(stage))

    append_jsonl(EVENTS_JSONL, {
        "event_type": "ROUTE_REPORT_GENERATED",
        "created_at": generated_at,
        "stage": int(stage),
        "routes_total": len(routes),
        "approved_routes": len(approved),
        "denied_routes": len(denied),
        "adjustment_routes": len(adjustments),
        "artifact_path": safe_relative(REPORTS_DIR / f"{stage_tag(stage)}_route_report.md"),
    })

    return result


def existing_decision_ids() -> set:
    ids = set()

    for record in read_jsonl(HDC_DECISIONS_JSONL):
        decision_id = normalize_text(record.get("decision_id"))
        if decision_id:
            ids.add(decision_id)

    return ids


def ensure_smoke_human_decisions(stage: int = 64) -> List[Dict[str, Any]]:
    ensure_dirs()

    existing = existing_decision_ids()

    smoke_records = [
        {
            "decision_id": f"{stage_tag(stage)}_smoke_approve",
            "system": "K-Atlas OS",
            "module": "human_decision_center",
            "stage": int(stage),
            "created_at": now_utc(),
            "operator": "smoke_test",
            "package_id": f"{stage_tag(stage)}_router_demo_approve",
            "package_title": "Smoke router demo - aprovado",
            "package_source_path": "reports/planning_approval_packages/stage_064_router_demo_approve.json",
            "decision": "APPROVE",
            "status": "APPROVED",
            "reason": "Smoke test: aprovado para continuidade interna supervisionada.",
            "effect": "Permitir continuidade local supervisionada sem publicacao automatica.",
            "governance": {
                "human_approval_required": True,
                "auto_publish": False,
                "auto_deploy": False,
                "external_api_calls": False,
                "browser_automation": False,
                "mouse_automation": False,
            },
        },
        {
            "decision_id": f"{stage_tag(stage)}_smoke_deny",
            "system": "K-Atlas OS",
            "module": "human_decision_center",
            "stage": int(stage),
            "created_at": now_utc(),
            "operator": "smoke_test",
            "package_id": f"{stage_tag(stage)}_router_demo_deny",
            "package_title": "Smoke router demo - negado",
            "package_source_path": "reports/planning_approval_packages/stage_064_router_demo_deny.json",
            "decision": "DENY",
            "status": "DENIED",
            "reason": "Smoke test: negado e bloqueado por decisao humana.",
            "effect": "Bloquear continuidade ate nova decisao humana.",
            "governance": {
                "human_approval_required": True,
                "auto_publish": False,
                "auto_deploy": False,
                "external_api_calls": False,
                "browser_automation": False,
                "mouse_automation": False,
            },
        },
        {
            "decision_id": f"{stage_tag(stage)}_smoke_adjustments",
            "system": "K-Atlas OS",
            "module": "human_decision_center",
            "stage": int(stage),
            "created_at": now_utc(),
            "operator": "smoke_test",
            "package_id": f"{stage_tag(stage)}_router_demo_adjustments",
            "package_title": "Smoke router demo - ajustes",
            "package_source_path": "reports/planning_approval_packages/stage_064_router_demo_adjustments.json",
            "decision": "REQUEST_ADJUSTMENTS",
            "status": "ADJUSTMENTS_REQUESTED",
            "reason": "Smoke test: devolver ao planejador para revisao antes da continuidade.",
            "effect": "Gerar pedido de ajustes para o planejador.",
            "governance": {
                "human_approval_required": True,
                "auto_publish": False,
                "auto_deploy": False,
                "external_api_calls": False,
                "browser_automation": False,
                "mouse_automation": False,
            },
        },
    ]

    inserted: List[Dict[str, Any]] = []

    for record in smoke_records:
        if record["decision_id"] not in existing:
            append_jsonl(HDC_DECISIONS_JSONL, record)
            inserted.append(record)

            append_jsonl(EVENTS_JSONL, {
                "event_type": "SMOKE_HUMAN_DECISION_CREATED",
                "created_at": record["created_at"],
                "stage": int(stage),
                "decision_id": record["decision_id"],
                "package_id": record["package_id"],
                "decision": record["decision"],
            })

    return smoke_records


def render_smoke_report(result: Dict[str, Any]) -> str:
    lines = [
        f"# K-Atlas Stage {result['stage']} - Decision Flow Router Smoke Report",
        "",
        f"Status: `{result['status']}`",
        f"Gerado em: {result['generated_at']}",
        "",
        "## Validacoes",
        "",
    ]

    for item in result["validations"]:
        lines.append(f"- {item['name']}: `{item['status']}`")

    lines.extend([
        "",
        "## Resumo de rotas",
        "",
        f"- Total de rotas: {result['route_summary']['routes_total']}",
        f"- Aprovadas: {result['route_summary']['approved_routes']}",
        f"- Negadas/bloqueadas: {result['route_summary']['denied_routes']}",
        f"- Ajustes solicitados: {result['route_summary']['adjustment_routes']}",
        "",
        "## Artefatos",
        "",
    ])

    for key, value in result["artifacts"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend([
        "",
        "## Travas confirmadas",
        "",
        "- Sem API externa real",
        "- Sem publicacao automatica",
        "- Sem deploy automatico",
        "- Sem navegador automatico",
        "- Sem mouse automatico",
        "- Governanca humana mantida",
        "",
    ])

    return "\n".join(lines).rstrip() + "\n"


def run_smoke_test(stage: int = 64) -> Dict[str, Any]:
    ensure_dirs()
    smoke_records = ensure_smoke_human_decisions(stage=stage)
    route_result = route_latest_decisions(stage=stage)

    smoke_package_ids = {record["package_id"] for record in smoke_records}

    approved_ids = {item["package_id"] for item in route_result["routes"] if item["route_type"] == "SUPERVISED_CONTINUATION"}
    denied_ids = {item["package_id"] for item in route_result["routes"] if item["route_type"] == "EXECUTION_BLOCK"}
    adjustment_ids = {item["package_id"] for item in route_result["routes"] if item["route_type"] == "PLANNER_REVISION_REQUEST"}

    validations = [
        {
            "name": "approve_routes_to_supervised_continuation",
            "status": "PASS" if f"{stage_tag(stage)}_router_demo_approve" in approved_ids else "FAIL",
        },
        {
            "name": "deny_routes_to_execution_block",
            "status": "PASS" if f"{stage_tag(stage)}_router_demo_deny" in denied_ids else "FAIL",
        },
        {
            "name": "request_adjustments_routes_to_planner_revision",
            "status": "PASS" if f"{stage_tag(stage)}_router_demo_adjustments" in adjustment_ids else "FAIL",
        },
        {
            "name": "all_smoke_packages_routed",
            "status": "PASS" if smoke_package_ids.issubset({item["package_id"] for item in route_result["routes"]}) else "FAIL",
        },
        {
            "name": "approved_queue_file_exists",
            "status": "PASS" if APPROVED_QUEUE.exists() else "FAIL",
        },
        {
            "name": "denied_queue_file_exists",
            "status": "PASS" if DENIED_QUEUE.exists() else "FAIL",
        },
        {
            "name": "adjustment_queue_file_exists",
            "status": "PASS" if ADJUSTMENT_QUEUE.exists() else "FAIL",
        },
        {
            "name": "supervised_queue_file_exists",
            "status": "PASS" if SUPERVISED_QUEUE.exists() else "FAIL",
        },
    ]

    status = "PASS" if all(item["status"] == "PASS" for item in validations) else "FAIL"

    result = {
        "system": "K-Atlas OS",
        "module": "decision_flow_router",
        "stage": int(stage),
        "status": status,
        "generated_at": now_utc(),
        "validations": validations,
        "route_summary": route_result["summary"],
        "artifacts": {
            "routed_decisions": safe_relative(ROUTED_DECISIONS),
            "approved_queue": safe_relative(APPROVED_QUEUE),
            "denied_queue": safe_relative(DENIED_QUEUE),
            "adjustment_queue": safe_relative(ADJUSTMENT_QUEUE),
            "supervised_queue": safe_relative(SUPERVISED_QUEUE),
            "route_report": safe_relative(REPORTS_DIR / f"{stage_tag(stage)}_route_report.md"),
            "smoke_report": safe_relative(REPORTS_DIR / f"{stage_tag(stage)}_smoke_report.md"),
            "next_prompt": safe_relative(REPORTS_DIR / f"stage_{int(stage) + 1:03d}_next_prompt.md"),
        },
        "governance": {
            "human_approval_required": True,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_calls": False,
            "browser_automation": False,
            "mouse_automation": False,
        },
    }

    write_json(REPORTS_DIR / f"{stage_tag(stage)}_smoke_report.json", result)
    write_text(REPORTS_DIR / f"{stage_tag(stage)}_smoke_report.md", render_smoke_report(result))

    append_jsonl(EVENTS_JSONL, {
        "event_type": "SMOKE_TEST_COMPLETED",
        "created_at": result["generated_at"],
        "stage": int(stage),
        "status": status,
        "artifact_path": safe_relative(REPORTS_DIR / f"{stage_tag(stage)}_smoke_report.md"),
    })

    print(f"OK Decision Flow Router smoke test: {status}")
    print(f"Relatorio: {safe_relative(REPORTS_DIR / f'{stage_tag(stage)}_smoke_report.md')}")
    print(f"Rotas: {safe_relative(ROUTED_DECISIONS)}")
    print(f"Fila aprovada: {safe_relative(APPROVED_QUEUE)}")
    print(f"Fila bloqueada: {safe_relative(DENIED_QUEUE)}")
    print(f"Fila de ajustes: {safe_relative(ADJUSTMENT_QUEUE)}")
    print(f"Proximo prompt: {safe_relative(REPORTS_DIR / f'stage_{int(stage) + 1:03d}_next_prompt.md')}")

    if status != "PASS":
        raise RuntimeError("Smoke test failed.")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="K-Atlas Decision Flow Router")
    parser.add_argument("--stage", type=int, default=64)
    parser.add_argument("--route", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    ensure_dirs()

    if args.smoke_test:
        run_smoke_test(stage=args.stage)
        return 0

    if args.route:
        result = route_latest_decisions(stage=args.stage)
        print(f"OK routes generated: {safe_relative(ROUTED_DECISIONS)}")
        print(json.dumps(result["summary"], ensure_ascii=False))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
