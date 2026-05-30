# -*- coding: utf-8 -*-
"""
K-Atlas OS - Executor Package Builder
Checkpoint 64

Pega decisoes aprovadas no Human Decision Center e transforma em pacotes
de execucao futura supervisionada.

Nao executa acao real.
Nao chama API externa.
Nao publica.
Nao faz deploy.
Nao envia nada automaticamente.
Nao usa token em texto puro.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

HDC_MEMORY_DIR = ROOT / "memory" / "human_decision_center"
HDC_DECISIONS_JSONL = HDC_MEMORY_DIR / "decisions.jsonl"

LIVE_DIR = ROOT / "live" / "executor_package_builder"
MEMORY_DIR = ROOT / "memory" / "executor_package_builder"
REPORTS_DIR = ROOT / "reports" / "executor_package_builder"
EXECUTOR_PACKAGES_DIR = ROOT / "reports" / "executor_packages"

EVENTS_JSONL = MEMORY_DIR / "events.jsonl"
PACKAGES_JSONL = MEMORY_DIR / "executor_packages.jsonl"

QUEUE_PATH = LIVE_DIR / "executor_package_queue.json"
LATEST_STATE_PATH = LIVE_DIR / "latest_executor_package_state.json"

APPROVED_KEYS = {"APPROVE", "APPROVED"}
DENIED_KEYS = {"DENY", "DENIED"}
ADJUSTMENT_KEYS = {"REQUEST_ADJUSTMENTS", "ADJUSTMENTS_REQUESTED"}


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
        EXECUTOR_PACKAGES_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def safe_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def normalize_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else fallback
    return str(value)


def stable_hash(value: str, size: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:size]


def safe_slug(value: str) -> str:
    cleaned = []
    for char in value:
        if char.isalnum() or char in ("-", "_"):
            cleaned.append(char)
        else:
            cleaned.append("_")
    slug = "".join(cleaned).strip("_")
    return slug[:120] or "executor_package"


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
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                append_jsonl(EVENTS_JSONL, {
                    "event_type": "JSONL_READ_ERROR",
                    "created_at": now_utc(),
                    "source_path": safe_relative(path),
                    "line_number": line_number,
                })
                continue

            if isinstance(item, dict):
                items.append(item)

    return items


def decision_key(record: Dict[str, Any]) -> str:
    decision = normalize_text(record.get("decision")).upper()
    status = normalize_text(record.get("status")).upper()

    if decision:
        return decision

    return status


def classify_decision(record: Dict[str, Any]) -> str:
    key = decision_key(record)
    status = normalize_text(record.get("status")).upper()

    if key in APPROVED_KEYS or status in APPROVED_KEYS:
        return "APPROVED"

    if key in DENIED_KEYS or status in DENIED_KEYS:
        return "DENIED"

    if key in ADJUSTMENT_KEYS or status in ADJUSTMENT_KEYS:
        return "ADJUSTMENTS_REQUESTED"

    return "UNKNOWN"


def latest_human_decisions_by_package() -> Dict[str, Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}

    for record in read_jsonl(HDC_DECISIONS_JSONL):
        package_id = normalize_text(record.get("package_id"))

        if not package_id:
            continue

        latest[package_id] = record

    return latest


def build_executor_package(record: Dict[str, Any], stage: int) -> Dict[str, Any]:
    package_id = normalize_text(record.get("package_id"), "unknown_package")
    decision_id = normalize_text(record.get("decision_id"), f"missing_decision_{stable_hash(package_id)}")
    package_title = normalize_text(record.get("package_title"), "Pacote sem titulo")
    package_source_path = normalize_text(record.get("package_source_path"), "unknown")
    operator = normalize_text(record.get("operator"), "human_operator")
    reason = normalize_text(record.get("reason"), "Aprovado por decisao humana.")

    executor_package_id = f"execpkg_{stable_hash(package_id + '|' + decision_id, 18)}"

    tasks = [
        {
            "task_id": f"{executor_package_id}_task_001",
            "task_type": "LOCAL_CONTEXT_PRECHECK",
            "title": "Validar contexto local antes de qualquer execucao futura",
            "execution_status": "NOT_EXECUTED",
            "requires_human_confirmation": True,
        },
        {
            "task_id": f"{executor_package_id}_task_002",
            "task_type": "FUTURE_EXECUTION_PLAN_DRAFT",
            "title": "Preparar plano de execucao futura em modo supervisionado",
            "execution_status": "NOT_EXECUTED",
            "requires_human_confirmation": True,
        },
        {
            "task_id": f"{executor_package_id}_task_003",
            "task_type": "SAFETY_GATE",
            "title": "Confirmar travas de seguranca antes do runner executar qualquer acao",
            "execution_status": "NOT_EXECUTED",
            "requires_human_confirmation": True,
        },
    ]

    package = {
        "executor_package_id": executor_package_id,
        "system": "K-Atlas OS",
        "module": "executor_package_builder",
        "stage": int(stage),
        "created_at": now_utc(),
        "source_module": "human_decision_center",
        "source_decision_id": decision_id,
        "source_package_id": package_id,
        "source_package_title": package_title,
        "source_package_path": package_source_path,
        "human_operator": operator,
        "human_decision": normalize_text(record.get("decision")),
        "human_status": normalize_text(record.get("status")),
        "human_reason": reason,
        "package_status": "BUILT_NOT_EXECUTED",
        "execution_mode": "FUTURE_SUPERVISED_LOCAL_ONLY",
        "next_required_action": "HUMAN_RUNNER_CONFIRMATION_REQUIRED",
        "can_execute_now": False,
        "real_action_executed": False,
        "tasks": tasks,
        "governance": {
            "human_approval_required": True,
            "runner_confirmation_required": True,
            "auto_publish": False,
            "auto_deploy": False,
            "auto_send": False,
            "external_api_calls": False,
            "browser_automation": False,
            "mouse_automation": False,
            "plain_text_tokens_allowed": False,
            "unsafe_automation_allowed": False,
        },
        "allowed_future_scope": [
            "local_file_generation",
            "local_report_generation",
            "dry_run_only",
            "supervised_runner_execution_after_confirmation",
        ],
        "blocked_scope": [
            "real_external_api_call",
            "automatic_publication",
            "automatic_deploy",
            "automatic_sending",
            "plain_text_token_usage",
            "browser_automation",
            "mouse_automation",
        ],
    }

    return package


def render_executor_package_markdown(package: Dict[str, Any]) -> str:
    lines = [
        f"# Executor Package - {package['executor_package_id']}",
        "",
        f"Gerado em: {package['created_at']}",
        "",
        "## Origem",
        "",
        f"- Pacote aprovado: `{package['source_package_id']}`",
        f"- Decisao humana: `{package['source_decision_id']}`",
        f"- Operador: `{package['human_operator']}`",
        f"- Status: `{package['package_status']}`",
        "",
        "## Justificativa humana",
        "",
        package["human_reason"],
        "",
        "## Tarefas futuras",
        "",
    ]

    for task in package["tasks"]:
        lines.extend([
            f"### {task['task_id']}",
            "",
            f"- Tipo: `{task['task_type']}`",
            f"- Titulo: {task['title']}",
            f"- Status: `{task['execution_status']}`",
            f"- Confirmacao humana obrigatoria: `{task['requires_human_confirmation']}`",
            "",
        ])

    lines.extend([
        "## Governanca",
        "",
        "- Nenhuma acao real foi executada",
        "- Sem API externa real",
        "- Sem publicacao automatica",
        "- Sem deploy automatico",
        "- Sem envio automatico",
        "- Sem token em texto puro",
        "- Execucao futura somente com confirmacao humana no runner",
        "",
    ])

    return "\n".join(lines).rstrip() + "\n"


def write_executor_package_artifacts(package: Dict[str, Any], stage: int) -> Dict[str, str]:
    slug = safe_slug(package["source_package_id"])
    json_path = EXECUTOR_PACKAGES_DIR / f"{stage_tag(stage)}_{slug}_executor_package.json"
    md_path = EXECUTOR_PACKAGES_DIR / f"{stage_tag(stage)}_{slug}_executor_package.md"

    package["artifact_paths"] = {
        "json": safe_relative(json_path),
        "markdown": safe_relative(md_path),
    }

    write_json(json_path, package)
    write_text(md_path, render_executor_package_markdown(package))

    return package["artifact_paths"]


def render_builder_report(result: Dict[str, Any]) -> str:
    lines = [
        f"# K-Atlas Checkpoint {result['stage']} - Executor Package Builder",
        "",
        f"Status: `{result['status']}`",
        f"Gerado em: {result['generated_at']}",
        "",
        "## Resumo",
        "",
        f"- Decisoes humanas lidas: {result['summary']['human_decisions_read']}",
        f"- Decisoes aprovadas: {result['summary']['approved_decisions']}",
        f"- Pacotes de execucao futura criados: {result['summary']['executor_packages_built']}",
        f"- Decisoes negadas ignoradas: {result['summary']['denied_decisions_skipped']}",
        f"- Pedidos de ajuste ignorados: {result['summary']['adjustment_decisions_skipped']}",
        f"- Decisoes desconhecidas ignoradas: {result['summary']['unknown_decisions_skipped']}",
        "",
        "## Pacotes criados",
        "",
    ]

    if not result["executor_packages"]:
        lines.append("Nenhum pacote de execucao futura foi criado.")
    else:
        for package in result["executor_packages"]:
            lines.extend([
                f"### {package['executor_package_id']}",
                "",
                f"- Pacote origem: `{package['source_package_id']}`",
                f"- Status: `{package['package_status']}`",
                f"- Proxima acao: `{package['next_required_action']}`",
                f"- Arquivo JSON: `{package['artifact_paths']['json']}`",
                f"- Arquivo Markdown: `{package['artifact_paths']['markdown']}`",
                "",
            ])

    lines.extend([
        "## Travas confirmadas",
        "",
        "- Sem API externa real",
        "- Sem publicacao automatica",
        "- Sem deploy automatico",
        "- Sem envio automatico",
        "- Sem token em texto puro",
        "- Sem execucao real",
        "- Governanca humana mantida",
        "",
    ])

    return "\n".join(lines).rstrip() + "\n"


def render_next_prompt(stage: int) -> str:
    next_stage = int(stage) + 1

    return f"""K-Atlas Engineer, contexto operacional atual:

O Checkpoint {stage} criou o Executor Package Builder supervisionado.

Estado atual:
- Decisoes aprovadas no Human Decision Center viram pacotes de execucao futura
- Pacotes ficam em reports/executor_packages/
- Fila fica em live/executor_package_builder/executor_package_queue.json
- Nenhuma acao real e executada
- Sem API externa real
- Sem publicacao automatica
- Sem deploy automatico
- Sem envio automatico
- Sem token em texto puro
- Governanca humana mantida

Missao:
Gerar o Checkpoint {next_stage} do K-Atlas OS.

Objetivo recomendado:
Criar o Executor Dry Run Validator, que valida os pacotes de execucao futura sem executar nada real.
Ele deve verificar seguranca, escopo permitido, bloqueios, dependencias locais e gerar um relatorio de prontidao para o Runner supervisionado.

Regras obrigatorias:
- responder em portugues
- entregar um unico bloco PowerShell completo
- compativel com Windows PowerShell
- usar UTF-8
- incluir smoke test
- incluir commit
- incluir push
- logs e relatorios
- sem API externa real
- sem publicacao automatica
- sem deploy automatico
- sem envio automatico
- sem token em texto puro
- manter governanca humana
"""


def build_executor_packages(stage: int = 64) -> Dict[str, Any]:
    ensure_dirs()

    latest = latest_human_decisions_by_package()

    executor_packages: List[Dict[str, Any]] = []
    approved_count = 0
    denied_count = 0
    adjustment_count = 0
    unknown_count = 0

    for package_id in sorted(latest.keys()):
        record = latest[package_id]
        classification = classify_decision(record)

        if classification == "APPROVED":
            approved_count += 1
            package = build_executor_package(record, stage=stage)
            write_executor_package_artifacts(package, stage=stage)
            executor_packages.append(package)

            append_jsonl(PACKAGES_JSONL, package)
            append_jsonl(EVENTS_JSONL, {
                "event_type": "EXECUTOR_PACKAGE_BUILT",
                "created_at": package["created_at"],
                "stage": int(stage),
                "executor_package_id": package["executor_package_id"],
                "source_package_id": package["source_package_id"],
                "artifact_json": package["artifact_paths"]["json"],
            })

        elif classification == "DENIED":
            denied_count += 1
            append_jsonl(EVENTS_JSONL, {
                "event_type": "DECISION_SKIPPED_DENIED",
                "created_at": now_utc(),
                "stage": int(stage),
                "source_package_id": package_id,
            })

        elif classification == "ADJUSTMENTS_REQUESTED":
            adjustment_count += 1
            append_jsonl(EVENTS_JSONL, {
                "event_type": "DECISION_SKIPPED_ADJUSTMENTS_REQUESTED",
                "created_at": now_utc(),
                "stage": int(stage),
                "source_package_id": package_id,
            })

        else:
            unknown_count += 1
            append_jsonl(EVENTS_JSONL, {
                "event_type": "DECISION_SKIPPED_UNKNOWN",
                "created_at": now_utc(),
                "stage": int(stage),
                "source_package_id": package_id,
            })

    generated_at = now_utc()

    result = {
        "system": "K-Atlas OS",
        "module": "executor_package_builder",
        "stage": int(stage),
        "status": "PASS",
        "generated_at": generated_at,
        "summary": {
            "human_decisions_read": len(latest),
            "approved_decisions": approved_count,
            "executor_packages_built": len(executor_packages),
            "denied_decisions_skipped": denied_count,
            "adjustment_decisions_skipped": adjustment_count,
            "unknown_decisions_skipped": unknown_count,
        },
        "executor_packages": executor_packages,
        "queue_path": safe_relative(QUEUE_PATH),
        "governance": {
            "human_approval_required": True,
            "runner_confirmation_required": True,
            "auto_publish": False,
            "auto_deploy": False,
            "auto_send": False,
            "external_api_calls": False,
            "plain_text_tokens_allowed": False,
            "real_action_executed": False,
        },
    }

    queue = {
        "system": "K-Atlas OS",
        "module": "executor_package_builder",
        "stage": int(stage),
        "generated_at": generated_at,
        "queue_type": "future_supervised_execution_packages",
        "count": len(executor_packages),
        "items": executor_packages,
        "runner_policy": {
            "requires_manual_confirmation": True,
            "execution_allowed_now": False,
            "future_execution_mode": "supervised_local_only",
            "auto_publish": False,
            "auto_deploy": False,
            "auto_send": False,
            "external_api_calls": False,
        },
    }

    write_json(QUEUE_PATH, queue)
    write_json(LATEST_STATE_PATH, result)
    write_json(REPORTS_DIR / f"{stage_tag(stage)}_builder_report.json", result)
    write_text(REPORTS_DIR / f"{stage_tag(stage)}_builder_report.md", render_builder_report(result))
    write_text(REPORTS_DIR / f"stage_{int(stage) + 1:03d}_next_prompt.md", render_next_prompt(stage))

    append_jsonl(EVENTS_JSONL, {
        "event_type": "EXECUTOR_PACKAGE_QUEUE_BUILT",
        "created_at": generated_at,
        "stage": int(stage),
        "executor_packages_built": len(executor_packages),
        "queue_path": safe_relative(QUEUE_PATH),
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

    records = [
        {
            "decision_id": f"{stage_tag(stage)}_epb_smoke_approve",
            "system": "K-Atlas OS",
            "module": "human_decision_center",
            "stage": int(stage),
            "created_at": now_utc(),
            "operator": "smoke_test",
            "package_id": f"{stage_tag(stage)}_epb_demo_approved",
            "package_title": "Smoke demo aprovado para Executor Package Builder",
            "package_source_path": "reports/planning_approval_packages/stage_064_epb_demo_approved.json",
            "decision": "APPROVE",
            "status": "APPROVED",
            "reason": "Smoke test: aprovado para gerar pacote de execucao futura sem acao real.",
            "governance": {
                "human_approval_required": True,
                "auto_publish": False,
                "auto_deploy": False,
                "auto_send": False,
                "external_api_calls": False,
                "plain_text_tokens_allowed": False,
            },
        },
        {
            "decision_id": f"{stage_tag(stage)}_epb_smoke_deny",
            "system": "K-Atlas OS",
            "module": "human_decision_center",
            "stage": int(stage),
            "created_at": now_utc(),
            "operator": "smoke_test",
            "package_id": f"{stage_tag(stage)}_epb_demo_denied",
            "package_title": "Smoke demo negado",
            "package_source_path": "reports/planning_approval_packages/stage_064_epb_demo_denied.json",
            "decision": "DENY",
            "status": "DENIED",
            "reason": "Smoke test: pacote negado nao deve gerar pacote de execucao.",
            "governance": {
                "human_approval_required": True,
                "auto_publish": False,
                "auto_deploy": False,
                "auto_send": False,
                "external_api_calls": False,
                "plain_text_tokens_allowed": False,
            },
        },
        {
            "decision_id": f"{stage_tag(stage)}_epb_smoke_adjustments",
            "system": "K-Atlas OS",
            "module": "human_decision_center",
            "stage": int(stage),
            "created_at": now_utc(),
            "operator": "smoke_test",
            "package_id": f"{stage_tag(stage)}_epb_demo_adjustments",
            "package_title": "Smoke demo ajustes solicitados",
            "package_source_path": "reports/planning_approval_packages/stage_064_epb_demo_adjustments.json",
            "decision": "REQUEST_ADJUSTMENTS",
            "status": "ADJUSTMENTS_REQUESTED",
            "reason": "Smoke test: pacote com ajustes nao deve gerar pacote de execucao.",
            "governance": {
                "human_approval_required": True,
                "auto_publish": False,
                "auto_deploy": False,
                "auto_send": False,
                "external_api_calls": False,
                "plain_text_tokens_allowed": False,
            },
        },
    ]

    for record in records:
        if record["decision_id"] not in existing:
            append_jsonl(HDC_DECISIONS_JSONL, record)
            append_jsonl(EVENTS_JSONL, {
                "event_type": "SMOKE_HUMAN_DECISION_CREATED",
                "created_at": record["created_at"],
                "stage": int(stage),
                "decision_id": record["decision_id"],
                "package_id": record["package_id"],
                "decision": record["decision"],
            })

    return records


def render_smoke_report(result: Dict[str, Any]) -> str:
    lines = [
        f"# K-Atlas Checkpoint {result['stage']} - Smoke Test Executor Package Builder",
        "",
        f"Status: `{result['status']}`",
        f"Gerado em: {result['generated_at']}",
        "",
        "## Validacoes",
        "",
    ]

    for validation in result["validations"]:
        lines.append(f"- {validation['name']}: `{validation['status']}`")

    lines.extend([
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
        "- Sem envio automatico",
        "- Sem token em texto puro",
        "- Sem execucao real",
        "- Governanca humana mantida",
        "",
    ])

    return "\n".join(lines).rstrip() + "\n"


def run_smoke_test(stage: int = 64) -> Dict[str, Any]:
    ensure_smoke_human_decisions(stage=stage)

    build_result = build_executor_packages(stage=stage)

    package_source_ids = {item["source_package_id"] for item in build_result["executor_packages"]}

    approved_demo_id = f"{stage_tag(stage)}_epb_demo_approved"
    denied_demo_id = f"{stage_tag(stage)}_epb_demo_denied"
    adjustments_demo_id = f"{stage_tag(stage)}_epb_demo_adjustments"

    all_packages_safe = True
    for package in build_result["executor_packages"]:
        governance = package.get("governance", {})
        if package.get("real_action_executed") is not False:
            all_packages_safe = False
        if package.get("can_execute_now") is not False:
            all_packages_safe = False
        if governance.get("external_api_calls") is not False:
            all_packages_safe = False
        if governance.get("auto_publish") is not False:
            all_packages_safe = False
        if governance.get("auto_deploy") is not False:
            all_packages_safe = False
        if governance.get("auto_send") is not False:
            all_packages_safe = False
        if governance.get("plain_text_tokens_allowed") is not False:
            all_packages_safe = False

    validations = [
        {
            "name": "approved_decision_generates_executor_package",
            "status": "PASS" if approved_demo_id in package_source_ids else "FAIL",
        },
        {
            "name": "denied_decision_does_not_generate_executor_package",
            "status": "PASS" if denied_demo_id not in package_source_ids else "FAIL",
        },
        {
            "name": "adjustment_decision_does_not_generate_executor_package",
            "status": "PASS" if adjustments_demo_id not in package_source_ids else "FAIL",
        },
        {
            "name": "queue_file_exists",
            "status": "PASS" if QUEUE_PATH.exists() else "FAIL",
        },
        {
            "name": "events_log_exists",
            "status": "PASS" if EVENTS_JSONL.exists() else "FAIL",
        },
        {
            "name": "packages_log_exists",
            "status": "PASS" if PACKAGES_JSONL.exists() else "FAIL",
        },
        {
            "name": "all_executor_packages_are_not_executed",
            "status": "PASS" if all_packages_safe else "FAIL",
        },
    ]

    status = "PASS" if all(item["status"] == "PASS" for item in validations) else "FAIL"

    result = {
        "system": "K-Atlas OS",
        "module": "executor_package_builder",
        "stage": int(stage),
        "status": status,
        "generated_at": now_utc(),
        "validations": validations,
        "build_summary": build_result["summary"],
        "artifacts": {
            "queue": safe_relative(QUEUE_PATH),
            "latest_state": safe_relative(LATEST_STATE_PATH),
            "events_log": safe_relative(EVENTS_JSONL),
            "packages_log": safe_relative(PACKAGES_JSONL),
            "builder_report": safe_relative(REPORTS_DIR / f"{stage_tag(stage)}_builder_report.md"),
            "smoke_report": safe_relative(REPORTS_DIR / f"{stage_tag(stage)}_smoke_report.md"),
            "next_prompt": safe_relative(REPORTS_DIR / f"stage_{int(stage) + 1:03d}_next_prompt.md"),
            "executor_packages_dir": safe_relative(EXECUTOR_PACKAGES_DIR),
        },
        "governance": {
            "human_approval_required": True,
            "runner_confirmation_required": True,
            "auto_publish": False,
            "auto_deploy": False,
            "auto_send": False,
            "external_api_calls": False,
            "plain_text_tokens_allowed": False,
            "real_action_executed": False,
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

    print(f"OK Executor Package Builder smoke test: {status}")
    print(f"Relatorio: {safe_relative(REPORTS_DIR / f'{stage_tag(stage)}_smoke_report.md')}")
    print(f"Fila: {safe_relative(QUEUE_PATH)}")
    print(f"Pacotes: {safe_relative(EXECUTOR_PACKAGES_DIR)}")
    print(f"Proximo prompt: {safe_relative(REPORTS_DIR / f'stage_{int(stage) + 1:03d}_next_prompt.md')}")

    if status != "PASS":
        raise RuntimeError("Smoke test failed.")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="K-Atlas Executor Package Builder")
    parser.add_argument("--stage", type=int, default=64)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    ensure_dirs()

    if args.smoke_test:
        run_smoke_test(stage=args.stage)
        return 0

    if args.build:
        result = build_executor_packages(stage=args.stage)
        print(f"OK executor package queue generated: {safe_relative(QUEUE_PATH)}")
        print(json.dumps(result["summary"], ensure_ascii=False))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
