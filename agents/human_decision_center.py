# -*- coding: utf-8 -*-
"""
K-Atlas OS - Human Decision Center
Stage 63

Centro local, supervisionado e auditavel para aprovar, negar ou pedir ajustes
nos pacotes gerados pelo Planning Approval Packager.

Sem API externa real.
Sem navegador automatico.
Sem mouse automatico.
Sem deploy automatico.
Sem publicacao automatica.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

LIVE_DIR = ROOT / "live" / "human_decision_center"
MEMORY_DIR = ROOT / "memory" / "human_decision_center"
REPORTS_DIR = ROOT / "reports" / "human_decision_center"
PACKAGES_DIR = ROOT / "reports" / "planning_approval_packages"

QUEUE_PATH = LIVE_DIR / "decision_queue.json"
DECISIONS_JSONL = MEMORY_DIR / "decisions.jsonl"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"
LATEST_STATE_PATH = LIVE_DIR / "latest_decision_state.json"

ALLOWED_DECISIONS = {
    "APPROVE": {
        "status": "APPROVED",
        "label_pt": "Aprovar",
        "effect": "Pacote aprovado para proxima etapa interna. Nenhuma publicacao automatica sera feita.",
    },
    "DENY": {
        "status": "DENIED",
        "label_pt": "Negar",
        "effect": "Pacote negado. A execucao deve ser bloqueada ate nova criacao ou revisao manual.",
    },
    "REQUEST_ADJUSTMENTS": {
        "status": "ADJUSTMENTS_REQUESTED",
        "label_pt": "Pedir ajustes",
        "effect": "Pacote devolvido para ajustes. O planejamento deve gerar uma nova versao revisada.",
    },
}

PACKAGE_SEARCH_DIRS = [
    PACKAGES_DIR,
    ROOT / "reports" / "planning_approval_packager",
    ROOT / "reports" / "planning_approval_packager" / "packages",
    ROOT / "reports" / "approval_packages",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_dirs() -> None:
    for path in [LIVE_DIR, MEMORY_DIR, REPORTS_DIR, PACKAGES_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def safe_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        return data
    return {"items": data}


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


def stable_id(value: str, prefix: str = "pkg") -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def stage_tag(stage: int) -> str:
    return f"stage_{int(stage):03d}"


def as_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        return value.strip() or fallback
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def infer_title(data: Dict[str, Any], path: Path) -> str:
    for key in ["title", "package_title", "name", "mission", "objective", "objetivo"]:
        value = as_text(data.get(key))
        if value:
            return value[:160]
    return path.stem.replace("_", " ").replace("-", " ").title()


def infer_summary(data: Dict[str, Any]) -> str:
    for key in ["summary", "description", "objective", "objetivo", "mission", "missao"]:
        value = as_text(data.get(key))
        if value:
            return value[:1000]
    actions = data.get("proposed_actions") or data.get("actions") or data.get("steps")
    if actions:
        return as_text(actions)[:1000]
    return "Pacote sem resumo explicito. Revisao humana obrigatoria antes de qualquer continuidade."


def infer_risk(data: Dict[str, Any]) -> str:
    for key in ["risk_level", "risk", "risco", "governance_risk"]:
        value = as_text(data.get(key))
        if value:
            return value.upper()[:60]
    governance = data.get("governance")
    if isinstance(governance, dict):
        value = as_text(governance.get("risk_level") or governance.get("risk"))
        if value:
            return value.upper()[:60]
    return "UNKNOWN"


def normalize_package(path: Path, data: Dict[str, Any]) -> Dict[str, Any]:
    source = safe_relative(path)
    package_id = as_text(
        data.get("package_id")
        or data.get("id")
        or data.get("approval_package_id")
        or data.get("mission_id")
    )

    if not package_id:
        package_id = stable_id(source, "pkg")

    return {
        "package_id": package_id,
        "title": infer_title(data, path),
        "summary": infer_summary(data),
        "risk_level": infer_risk(data),
        "source_path": source,
        "source_modified_at": datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=timezone.utc
        ).replace(microsecond=0).isoformat(),
        "created_at": as_text(
            data.get("created_at") or data.get("generated_at") or data.get("timestamp"),
            fallback="unknown"
        ),
        "requires_human_decision": True,
        "allowed_decisions": list(ALLOWED_DECISIONS.keys()),
        "no_auto_publish": True,
        "raw_keys": sorted(str(key) for key in data.keys()),
    }


def discover_packages() -> List[Dict[str, Any]]:
    ensure_dirs()
    found: Dict[str, Dict[str, Any]] = {}

    for directory in PACKAGE_SEARCH_DIRS:
        if not directory.exists():
            continue

        for path in sorted(directory.rglob("*.json")):
            if any(part in {"human_decision_center", ".git"} for part in path.parts):
                continue

            try:
                data = read_json(path)
                normalized = normalize_package(path, data)
            except Exception as exc:
                append_jsonl(EVENTS_JSONL, {
                    "event_type": "PACKAGE_DISCOVERY_ERROR",
                    "created_at": now_utc(),
                    "source_path": safe_relative(path),
                    "error": str(exc),
                })
                continue

            found[normalized["package_id"]] = normalized

    return sorted(
        found.values(),
        key=lambda item: (item["source_modified_at"], item["package_id"]),
        reverse=True
    )


def load_latest_decisions() -> Dict[str, Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}

    if not DECISIONS_JSONL.exists():
        return latest

    with DECISIONS_JSONL.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            package_id = as_text(item.get("package_id"))
            if package_id:
                latest[package_id] = item

    return latest


def render_queue_markdown(queue: Dict[str, Any]) -> str:
    lines = [
        f"# K-Atlas Human Decision Center - Stage {queue['stage']}",
        "",
        f"Gerado em: {queue['generated_at']}",
        "",
        "## Governanca",
        "",
        "- Aprovacao humana obrigatoria: sim",
        "- Publicacao automatica: nao",
        "- Deploy automatico: nao",
        "- API externa real: nao",
        "- Navegador automatico: nao",
        "- Mouse automatico: nao",
        "",
        "## Resumo",
        "",
        f"- Total de pacotes: {queue['summary']['total_packages']}",
        f"- Pendentes de decisao: {queue['summary']['pending_decisions']}",
        f"- Ja decididos: {queue['summary']['decided_packages']}",
        "",
        "## Fila",
        "",
    ]

    if not queue["packages"]:
        lines.append("Nenhum pacote encontrado. O centro esta pronto e aguardando pacotes do Planning Approval Packager.")
    else:
        for index, package in enumerate(queue["packages"], start=1):
            lines.extend([
                f"### {index}. {package['title']}",
                "",
                f"- Package ID: `{package['package_id']}`",
                f"- Status: `{package['decision_status']}`",
                f"- Risco: `{package['risk_level']}`",
                f"- Origem: `{package['source_path']}`",
                f"- Proxima acao: `{package['next_required_action']}`",
                "",
                package["summary"],
                "",
            ])

    return "\n".join(lines).rstrip() + "\n"


def build_queue(stage: int = 63, emit_event: bool = True) -> Dict[str, Any]:
    ensure_dirs()

    packages = discover_packages()
    latest_decisions = load_latest_decisions()

    queue_items: List[Dict[str, Any]] = []

    for package in packages:
        latest = latest_decisions.get(package["package_id"])
        decision_status = "PENDING"
        latest_decision_id = None
        latest_decision = None
        latest_reason = None

        if latest:
            latest_decision = latest.get("decision")
            latest_decision_id = latest.get("decision_id")
            latest_reason = latest.get("reason")
            decision_status = latest.get("status") or ALLOWED_DECISIONS.get(
                latest_decision,
                {}
            ).get("status", "DECIDED")

        queue_items.append({
            **package,
            "decision_status": decision_status,
            "latest_decision": latest_decision,
            "latest_decision_id": latest_decision_id,
            "latest_reason": latest_reason,
            "next_required_action": "HUMAN_DECISION" if decision_status == "PENDING" else "NO_AUTOMATIC_ACTION",
        })

    pending_count = sum(1 for item in queue_items if item["decision_status"] == "PENDING")

    queue = {
        "system": "K-Atlas OS",
        "module": "human_decision_center",
        "stage": int(stage),
        "generated_at": now_utc(),
        "source_module": "planning_approval_packager",
        "governance": {
            "human_approval_required": True,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_calls": False,
            "browser_automation": False,
            "mouse_automation": False,
        },
        "summary": {
            "total_packages": len(queue_items),
            "pending_decisions": pending_count,
            "decided_packages": len(queue_items) - pending_count,
        },
        "packages": queue_items,
    }

    write_json(QUEUE_PATH, queue)
    write_json(REPORTS_DIR / f"{stage_tag(stage)}_decision_queue_report.json", queue)
    write_text(REPORTS_DIR / f"{stage_tag(stage)}_decision_queue_report.md", render_queue_markdown(queue))

    if emit_event:
        append_jsonl(EVENTS_JSONL, {
            "event_type": "DECISION_QUEUE_BUILT",
            "created_at": queue["generated_at"],
            "stage": int(stage),
            "total_packages": len(queue_items),
            "pending_decisions": pending_count,
            "artifact_path": safe_relative(QUEUE_PATH),
        })

    return queue


def render_decision_markdown(record: Dict[str, Any]) -> str:
    return "\n".join([
        f"# Human Decision Report - {record['decision_id']}",
        "",
        f"Stage: {record['stage']}",
        f"Gerado em: {record['created_at']}",
        "",
        "## Pacote",
        "",
        f"- Package ID: `{record['package_id']}`",
        f"- Titulo: {record['package_title']}",
        f"- Origem: `{record['package_source_path']}`",
        "",
        "## Decisao humana",
        "",
        f"- Decisao: `{record['decision']}`",
        f"- Status: `{record['status']}`",
        f"- Operador: `{record['operator']}`",
        "",
        "## Justificativa",
        "",
        record["reason"],
        "",
        "## Efeito operacional",
        "",
        record["effect"],
        "",
        "## Travas de seguranca",
        "",
        "- Sem publicacao automatica",
        "- Sem deploy automatico",
        "- Sem chamada real a API externa",
        "- Sem navegador automatico",
        "- Sem mouse automatico",
        "",
    ])


def record_decision(
    package_id: str,
    decision: str,
    reason: str,
    operator: str = "human_operator",
    stage: int = 63,
) -> Dict[str, Any]:
    ensure_dirs()

    decision = decision.strip().upper()

    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"Decision invalida: {decision}. Use: {', '.join(ALLOWED_DECISIONS.keys())}")

    reason = reason.strip()

    if len(reason) < 5:
        raise ValueError("A justificativa deve ter pelo menos 5 caracteres.")

    queue = build_queue(stage=stage, emit_event=False)
    packages_by_id = {item["package_id"]: item for item in queue["packages"]}
    package = packages_by_id.get(package_id)

    if not package:
        raise ValueError(f"Package ID nao encontrado na fila: {package_id}")

    meta = ALLOWED_DECISIONS[decision]
    created_at = now_utc()
    decision_id = f"hdc_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"

    record = {
        "decision_id": decision_id,
        "system": "K-Atlas OS",
        "module": "human_decision_center",
        "stage": int(stage),
        "created_at": created_at,
        "operator": operator.strip() or "human_operator",
        "package_id": package_id,
        "package_title": package["title"],
        "package_source_path": package["source_path"],
        "decision": decision,
        "status": meta["status"],
        "reason": reason,
        "effect": meta["effect"],
        "governance": {
            "human_approval_required": True,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_calls": False,
            "browser_automation": False,
            "mouse_automation": False,
        },
        "audit": {
            "decision_file": f"memory/human_decision_center/{decision_id}.json",
            "events_file": "memory/human_decision_center/events.jsonl",
            "decisions_file": "memory/human_decision_center/decisions.jsonl",
        },
    }

    decision_path = MEMORY_DIR / f"{decision_id}.json"
    write_json(decision_path, record)
    append_jsonl(DECISIONS_JSONL, record)

    append_jsonl(EVENTS_JSONL, {
        "event_type": "HUMAN_DECISION_RECORDED",
        "created_at": created_at,
        "stage": int(stage),
        "decision_id": decision_id,
        "package_id": package_id,
        "decision": decision,
        "status": meta["status"],
        "artifact_path": safe_relative(decision_path),
    })

    write_json(LATEST_STATE_PATH, {
        "generated_at": now_utc(),
        "latest_decision": record,
        "queue_path": safe_relative(QUEUE_PATH),
    })

    report_path = REPORTS_DIR / f"{stage_tag(stage)}_{decision_id}_decision_report.md"
    write_text(report_path, render_decision_markdown(record))

    build_queue(stage=stage, emit_event=True)

    return record


def create_demo_packages(stage: int = 63) -> List[Path]:
    ensure_dirs()

    created: List[Path] = []

    examples = [
        {
            "slug": "approval",
            "title": "Pacote demo para aprovacao humana",
            "summary": "Validar se uma campanha interna pode avancar para a proxima etapa supervisionada.",
            "risk_level": "LOW",
            "suggested_smoke_decision": "APPROVE",
        },
        {
            "slug": "denial",
            "title": "Pacote demo para negacao humana",
            "summary": "Validar bloqueio humano quando o pacote nao possui contexto suficiente.",
            "risk_level": "MEDIUM",
            "suggested_smoke_decision": "DENY",
        },
        {
            "slug": "adjustments",
            "title": "Pacote demo para pedido de ajustes",
            "summary": "Validar retorno do pacote ao planejamento para revisao antes de qualquer continuidade.",
            "risk_level": "MEDIUM",
            "suggested_smoke_decision": "REQUEST_ADJUSTMENTS",
        },
    ]

    for index, item in enumerate(examples, start=1):
        package_id = f"{stage_tag(stage)}_demo_{item['slug']}"
        path = PACKAGES_DIR / f"{stage_tag(stage)}_demo_package_{index}_{item['slug']}.json"

        write_json(path, {
            "package_id": package_id,
            "title": item["title"],
            "summary": item["summary"],
            "risk_level": item["risk_level"],
            "created_at": now_utc(),
            "source_module": "planning_approval_packager_demo",
            "stage": int(stage),
            "proposed_actions": [
                "Gerar fila de decisao humana",
                "Exigir justificativa do operador",
                "Registrar log e memoria auditavel",
                "Manter publicacao e deploy bloqueados",
            ],
            "governance": {
                "human_approval_required": True,
                "auto_publish": False,
                "auto_deploy": False,
                "external_api_calls": False,
                "browser_automation": False,
                "mouse_automation": False,
            },
            "suggested_smoke_decision": item["suggested_smoke_decision"],
        })

        created.append(path)

    return created


def render_next_prompt(stage: int) -> str:
    next_stage = int(stage) + 1

    return f"""K-Atlas Engineer, contexto operacional atual:

A etapa {stage} criou o Human Decision Center local para pacotes do Planning Approval Packager.

Estado atual:
- Centro de decisao humana criado
- Fila local em live/human_decision_center/decision_queue.json
- Decisoes auditaveis em memory/human_decision_center/
- Relatorios em reports/human_decision_center/
- Sem publicacao automatica
- Sem deploy automatico
- Sem API externa real
- Sem navegador automatico
- Sem mouse automatico
- Governanca humana mantida

Missao:
Gerar a etapa {next_stage} do K-Atlas OS.

Objetivo recomendado:
Conectar o resultado da decisao humana ao fluxo seguinte:
- APPROVE permite continuidade interna supervisionada
- DENY bloqueia execucao
- REQUEST_ADJUSTMENTS devolve ao planejador para revisao

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


def render_smoke_markdown(result: Dict[str, Any]) -> str:
    lines = [
        f"# K-Atlas Stage {result['stage']} - Human Decision Center Smoke Report",
        "",
        f"Status: `{result['status']}`",
        f"Gerado em: {result['generated_at']}",
        "",
        "## Resultado",
        "",
        f"- Pacotes demo criados: {len(result['demo_packages'])}",
        f"- Decisoes registradas: {len(result['decisions_recorded'])}",
        f"- Fila antes: {json.dumps(result['queue_before'], ensure_ascii=False)}",
        f"- Fila depois: {json.dumps(result['queue_after'], ensure_ascii=False)}",
        "",
        "## Decisoes testadas",
        "",
    ]

    for record in result["decisions_recorded"]:
        lines.append(f"- `{record['package_id']}` -> `{record['decision']}` -> `{record['status']}`")

    lines.extend([
        "",
        "## Artefatos",
        "",
    ])

    for key, path in result["artifacts"].items():
        lines.append(f"- {key}: `{path}`")

    lines.extend([
        "",
        "## Travas confirmadas",
        "",
        "- Sem API externa real",
        "- Sem publicacao automatica",
        "- Sem deploy automatico",
        "- Sem navegador automatico",
        "- Sem mouse automatico",
        "",
    ])

    if result["missing_files"]:
        lines.extend(["## Arquivos ausentes", ""])
        for path in result["missing_files"]:
            lines.append(f"- `{path}`")

    return "\n".join(lines).rstrip() + "\n"


def run_smoke_test(stage: int = 63) -> Dict[str, Any]:
    ensure_dirs()

    demo_paths = create_demo_packages(stage=stage)
    queue_before = build_queue(stage=stage, emit_event=True)

    smoke_decisions = [
        (
            "stage_%03d_demo_approval" % int(stage),
            "APPROVE",
            "Smoke test: aprovacao humana registrada sem publicacao automatica."
        ),
        (
            "stage_%03d_demo_denial" % int(stage),
            "DENY",
            "Smoke test: negacao humana registrada com bloqueio operacional."
        ),
        (
            "stage_%03d_demo_adjustments" % int(stage),
            "REQUEST_ADJUSTMENTS",
            "Smoke test: ajustes solicitados antes de continuidade."
        ),
    ]

    decision_records = []

    for package_id, decision, reason in smoke_decisions:
        decision_records.append(record_decision(
            package_id=package_id,
            decision=decision,
            reason=reason,
            operator="smoke_test",
            stage=stage,
        ))

    queue_after = build_queue(stage=stage, emit_event=True)

    required_files = [
        QUEUE_PATH,
        DECISIONS_JSONL,
        EVENTS_JSONL,
        LATEST_STATE_PATH,
        REPORTS_DIR / f"{stage_tag(stage)}_decision_queue_report.md",
    ]

    missing = [safe_relative(path) for path in required_files if not path.exists()]
    status = "PASS" if not missing and len(decision_records) == 3 else "FAIL"

    next_prompt_path = REPORTS_DIR / f"stage_{int(stage) + 1:03d}_next_prompt.md"
    write_text(next_prompt_path, render_next_prompt(stage))

    result = {
        "system": "K-Atlas OS",
        "module": "human_decision_center",
        "stage": int(stage),
        "status": status,
        "generated_at": now_utc(),
        "demo_packages": [safe_relative(path) for path in demo_paths],
        "queue_before": queue_before["summary"],
        "queue_after": queue_after["summary"],
        "decisions_recorded": [
            {
                "decision_id": record["decision_id"],
                "package_id": record["package_id"],
                "decision": record["decision"],
                "status": record["status"],
            }
            for record in decision_records
        ],
        "artifacts": {
            "queue": safe_relative(QUEUE_PATH),
            "decisions_jsonl": safe_relative(DECISIONS_JSONL),
            "events_jsonl": safe_relative(EVENTS_JSONL),
            "latest_state": safe_relative(LATEST_STATE_PATH),
            "queue_report": safe_relative(REPORTS_DIR / f"{stage_tag(stage)}_decision_queue_report.md"),
            "next_prompt": safe_relative(next_prompt_path),
        },
        "missing_files": missing,
        "governance": {
            "external_api_calls": False,
            "auto_publish": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
        },
    }

    json_report_path = REPORTS_DIR / f"{stage_tag(stage)}_smoke_report.json"
    md_report_path = REPORTS_DIR / f"{stage_tag(stage)}_smoke_report.md"

    write_json(json_report_path, result)
    write_text(md_report_path, render_smoke_markdown(result))

    append_jsonl(EVENTS_JSONL, {
        "event_type": "SMOKE_TEST_COMPLETED",
        "created_at": result["generated_at"],
        "stage": int(stage),
        "status": status,
        "artifact_path": safe_relative(md_report_path),
    })

    print(f"OK smoke test Human Decision Center: {status}")
    print(f"Relatorio: {safe_relative(md_report_path)}")
    print(f"Fila: {safe_relative(QUEUE_PATH)}")
    print(f"Proximo prompt: {safe_relative(next_prompt_path)}")

    if status != "PASS":
        raise RuntimeError(f"Smoke test failed. Missing files: {missing}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="K-Atlas Human Decision Center")
    parser.add_argument("--stage", type=int, default=63)
    parser.add_argument("--queue", action="store_true", help="Build decision queue")
    parser.add_argument("--smoke-test", action="store_true", help="Run local smoke test")
    parser.add_argument("--decide", action="store_true", help="Record a human decision")
    parser.add_argument("--package-id", default="")
    parser.add_argument("--decision", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--operator", default="human_operator")

    args = parser.parse_args()

    ensure_dirs()

    if args.smoke_test:
        run_smoke_test(stage=args.stage)
        return 0

    if args.queue:
        queue = build_queue(stage=args.stage, emit_event=True)
        print(f"OK queue generated: {safe_relative(QUEUE_PATH)}")
        print(json.dumps(queue["summary"], ensure_ascii=False))
        return 0

    if args.decide:
        record = record_decision(
            package_id=args.package_id,
            decision=args.decision,
            reason=args.reason,
            operator=args.operator,
            stage=args.stage,
        )
        print(f"OK decision recorded: {record['decision_id']}")
        print(f"Status: {record['status']}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
