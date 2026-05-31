# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "proposals" / "k_os_proposal_factory_policy.json"
PROPOSAL_DIR = ROOT / "local_secrets" / "k_os_proposals"
PROPOSAL_PATH = PROPOSAL_DIR / "proposal_registry.json"
SALES_PATH = ROOT / "local_secrets" / "k_os_sales" / "sales_pipeline.json"
REPORT_DIR = ROOT / "reports" / "proposals"
TEMPLATE_DIR = REPORT_DIR / "templates"
MEMORY_DIR = ROOT / "memory" / "proposals"
LATEST_JSON = REPORT_DIR / "latest_proposal_factory_report.json"
LATEST_MD = REPORT_DIR / "latest_proposal_factory_report.md"
APPROVAL_JSON = REPORT_DIR / "latest_proposal_approval_dry_run.json"
APPROVAL_MD = REPORT_DIR / "latest_proposal_approval_dry_run.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"


def now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def now() -> str:
    return now_dt().isoformat()


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
        raise RuntimeError("Proposal policy not found.")
    return data


def ensure_registry() -> dict[str, Any]:
    PROPOSAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not PROPOSAL_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_send_enabled": False,
            "automatic_send_enabled": False,
            "proposals": [],
            "activities": []
        }
        write_json(PROPOSAL_PATH, data)

    registry = read_json(PROPOSAL_PATH)
    if not registry:
        raise RuntimeError("Could not load proposal registry.")
    return registry


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(PROPOSAL_PATH, data)


def load_sales_deals() -> list[dict[str, Any]]:
    data = read_json(SALES_PATH)
    if not data:
        return []
    return data.get("deals", [])


def safe_proposal(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposal_id": item.get("proposal_id"),
        "deal_id": item.get("deal_id", ""),
        "customer_alias": item.get("customer_alias"),
        "agent_id": item.get("agent_id"),
        "proposal_title": item.get("proposal_title"),
        "status": item.get("status"),
        "currency": item.get("currency"),
        "setup_total": item.get("setup_total", 0.0),
        "recurring_total": item.get("recurring_total", 0.0),
        "valid_until": item.get("valid_until"),
        "commercial_owner": item.get("commercial_owner"),
        "approval_status": item.get("approval_status"),
        "manual_send_allowed": item.get("manual_send_allowed", False),
        "created_at": item.get("created_at")
    }


def safe_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": item.get("activity_id"),
        "proposal_id": item.get("proposal_id"),
        "activity_type": item.get("activity_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by")
    }


def quote_totals(items: list[dict[str, Any]]) -> dict[str, float]:
    setup_total = 0.0
    recurring_total = 0.0

    for item in items:
        item_type = item.get("type", "")
        quantity = float(item.get("quantity", 1) or 1)
        unit_price = float(item.get("unit_price", 0.0) or 0.0)
        total = quantity * unit_price

        if item_type in {"setup", "custom_service", "training", "integration"}:
            setup_total += total
        else:
            recurring_total += total

    return {
        "setup_total": round(setup_total, 2),
        "recurring_total": round(recurring_total, 2),
        "first_month_total": round(setup_total + recurring_total, 2)
    }


def render_proposal_md(proposal: dict[str, Any]) -> str:
    lines = [
        f"# {proposal.get('proposal_title')}",
        "",
        "AVISO: Proposta gerada pelo K-OS em modo local. Envio ao cliente exige aprovação humana.",
        "",
        "## Resumo",
        "",
        f"- Cliente: {proposal.get('customer_alias')}",
        f"- Agente: {proposal.get('agent_id')}",
        f"- Proposal ID: {proposal.get('proposal_id')}",
        f"- Deal ID: {proposal.get('deal_id', '')}",
        f"- Validade: {proposal.get('valid_until')}",
        f"- Status: {proposal.get('status')}",
        "",
        "## Escopo",
        ""
    ]

    for scope in proposal.get("scope", []):
        lines.append(f"- {scope}")

    lines.extend([
        "",
        "## Itens do orçamento",
        "",
        "| Item | Tipo | Qtd | Valor unitario | Total |",
        "|---|---|---:|---:|---:|"
    ])

    for item in proposal.get("items", []):
        quantity = float(item.get("quantity", 1) or 1)
        unit_price = float(item.get("unit_price", 0.0) or 0.0)
        total = quantity * unit_price
        lines.append(
            f"| {item.get('name')} | {item.get('type')} | {quantity:g} | {unit_price:.2f} | {total:.2f} |"
        )

    lines.extend([
        "",
        "## Totais",
        "",
        f"- Setup: {proposal.get('currency')} {proposal.get('setup_total')}",
        f"- Recorrente: {proposal.get('currency')} {proposal.get('recurring_total')}",
        f"- Primeiro mês estimado: {proposal.get('currency')} {proposal.get('first_month_total')}",
        "",
        "## Condições",
        "",
        f"- Prazo de pagamento: {proposal.get('payment_terms')}",
        f"- Observação fiscal: {proposal.get('tax_note')}",
        f"- Observação jurídica: {proposal.get('legal_note')}",
        "",
        "## Gates antes do envio",
        ""
    ])

    for gate in proposal.get("required_gates_before_manual_send", []):
        lines.append(f"- {gate}")

    lines.extend([
        "",
        "## Limites",
        "",
        "- Esta proposta não garante receita ou resultado comercial.",
        "- Esta proposta não ativa cliente automaticamente.",
        "- Esta proposta não autoriza envio externo sem approval gate.",
        "- Uso real exige revisão comercial e jurídica quando aplicável."
    ])

    return "\n".join(lines)


def write_proposal_file(proposal: dict[str, Any]) -> str:
    filename = f"{proposal['proposal_id']}.md"
    path = PROPOSAL_DIR / filename
    path.write_text(render_proposal_md(proposal), encoding="utf-8")
    return str(path.relative_to(ROOT)).replace("\\", "/")


def proposal_templates() -> list[dict[str, Any]]:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

    templates = {
        "proposal_brief_template.md": """# Proposal Brief Template

Cliente: [customer_alias]
Deal: [deal_id]
Agente: [agent_id]
Problema principal: [problem]
Resultado esperado: [outcome]
Escopo permitido: [scope]
Plano sugerido: [plan]
Valor setup: [setup]
Valor recorrente: [recurring]
Gates antes do envio: approval humano, revisão comercial, revisão jurídica se pago
""",
        "quote_items_template.md": """# Quote Items Template

- setup inicial
- assinatura mensal
- pacote de uso
- treinamento
- suporte
- integração

Todos os itens precisam de tipo, quantidade e valor unitário.
""",
        "manual_send_pack_template.md": """# Manual Send Pack Template

Assunto: Proposta K-OS para [customer_alias]

Mensagem:
Olá, [nome].
Segue proposta revisada para [objetivo].
Antes de avançarmos, confirmamos que a ativação depende de aceite formal, assinatura ativa e permissões K-OS.

Anexo/Link: [proposal_file]

Envio externo somente manual e aprovado.
"""
    }

    result = []
    for filename, content in templates.items():
        path = TEMPLATE_DIR / filename
        path.write_text(content, encoding="utf-8")
        result.append({
            "filename": filename,
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "size_bytes": path.stat().st_size
        })

    return result


def create_from_deal(deal_id: str) -> dict[str, Any]:
    policy = load_policy()
    registry = ensure_registry()
    deals = load_sales_deals()

    deal = next((item for item in deals if item.get("deal_id") == deal_id), None)
    if not deal:
        raise RuntimeError(f"Deal not found: {deal_id}")

    existing = next((p for p in registry.get("proposals", []) if p.get("deal_id") == deal_id), None)
    if existing:
        return audit_report()

    defaults = policy.get("default_quote_terms", {})
    valid_until = (now_dt() + timedelta(days=int(defaults.get("validity_days", 7)))).date().isoformat()

    estimated_setup = float(deal.get("estimated_setup_brl", 0.0) or 0.0)
    estimated_mrr = float(deal.get("estimated_mrr_brl", 0.0) or 0.0)

    items = [
        {
            "name": "Setup operacional K-OS",
            "type": "setup",
            "quantity": 1,
            "unit_price": estimated_setup
        },
        {
            "name": "Assinatura mensal do agente IA",
            "type": "monthly_subscription",
            "quantity": 1,
            "unit_price": estimated_mrr
        }
    ]

    totals = quote_totals(items)
    proposal_id = "prop_" + uuid.uuid4().hex[:12]

    proposal = {
        "proposal_id": proposal_id,
        "deal_id": deal_id,
        "customer_alias": deal.get("customer_alias", "unknown_customer"),
        "agent_id": deal.get("agent_id", "marketplace_ia_agent"),
        "proposal_title": f"Proposta K-OS para {deal.get('customer_alias', 'cliente')}",
        "status": "draft",
        "currency": defaults.get("currency", "BRL"),
        "items": items,
        "scope": [
            "Diagnóstico operacional inicial",
            "Configuração de agente IA dentro do escopo aprovado",
            "Geração de proposta e fluxo de aprovação",
            "Operação com License Gate, Risk Classifier e auditoria",
            "Envio externo somente manual e aprovado"
        ],
        "setup_total": totals["setup_total"],
        "recurring_total": totals["recurring_total"],
        "first_month_total": totals["first_month_total"],
        "valid_until": valid_until,
        "payment_terms": defaults.get("payment_terms"),
        "tax_note": defaults.get("tax_note"),
        "legal_note": defaults.get("legal_note"),
        "commercial_owner": deal.get("commercial_owner", "k_os_operator"),
        "approval_status": "pending_commercial_review",
        "manual_send_allowed": False,
        "required_gates_before_manual_send": policy.get("required_gates_before_manual_send", []),
        "created_at": now(),
        "proposal_file": ""
    }

    proposal["proposal_file"] = write_proposal_file(proposal)

    registry["proposals"].append(proposal)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "proposal_id": proposal_id,
        "activity_type": "proposal_created_from_deal",
        "summary": "Proposta criada a partir de deal local.",
        "created_at": now(),
        "created_by": "k_os_proposal_factory"
    })

    save_registry(registry)
    event("proposal.created_from_deal", {"proposal_id": proposal_id, "deal_id": deal_id})
    return audit_report()


def create_demo() -> dict[str, Any]:
    deals = load_sales_deals()
    if deals:
        return create_from_deal(deals[0].get("deal_id"))

    registry = ensure_registry()
    existing = next((p for p in registry.get("proposals", []) if p.get("customer_alias") == "demo_customer"), None)

    if existing:
        return audit_report()

    policy = load_policy()
    defaults = policy.get("default_quote_terms", {})
    proposal_id = "prop_" + uuid.uuid4().hex[:12]
    items = [
        {"name": "Setup demo K-OS", "type": "setup", "quantity": 1, "unit_price": 1500.0},
        {"name": "Assinatura demo agente IA", "type": "monthly_subscription", "quantity": 1, "unit_price": 997.0}
    ]
    totals = quote_totals(items)

    proposal = {
        "proposal_id": proposal_id,
        "deal_id": "demo_deal",
        "customer_alias": "demo_customer",
        "agent_id": "marketplace_ia_agent",
        "proposal_title": "Proposta K-OS Demo",
        "status": "draft",
        "currency": "BRL",
        "items": items,
        "scope": [
            "Demonstração local",
            "Agente Marketplace IA",
            "Operação com approval gate",
            "Sem envio externo automático"
        ],
        "setup_total": totals["setup_total"],
        "recurring_total": totals["recurring_total"],
        "first_month_total": totals["first_month_total"],
        "valid_until": (now_dt() + timedelta(days=7)).date().isoformat(),
        "payment_terms": defaults.get("payment_terms"),
        "tax_note": defaults.get("tax_note"),
        "legal_note": defaults.get("legal_note"),
        "commercial_owner": "k_os_operator",
        "approval_status": "pending_commercial_review",
        "manual_send_allowed": False,
        "required_gates_before_manual_send": policy.get("required_gates_before_manual_send", []),
        "created_at": now(),
        "proposal_file": ""
    }

    proposal["proposal_file"] = write_proposal_file(proposal)

    registry["proposals"].append(proposal)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "proposal_id": proposal_id,
        "activity_type": "demo_proposal_created",
        "summary": "Proposta demo criada localmente.",
        "created_at": now(),
        "created_by": "k_os_proposal_factory"
    })

    save_registry(registry)
    event("proposal.demo_created", {"proposal_id": proposal_id})
    return audit_report()


def set_status(proposal_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()
    allowed = set(policy.get("proposal_statuses", []))

    if status not in allowed:
        raise RuntimeError(f"Invalid proposal status: {status}")

    registry = ensure_registry()
    found = False

    for proposal in registry.get("proposals", []):
        if proposal.get("proposal_id") == proposal_id:
            if status in {"approved_for_manual_send", "sent_manually"}:
                if proposal.get("approval_status") != "commercial_approved":
                    raise RuntimeError("Proposal cannot be approved/sent without commercial approval.")

            proposal["status"] = status
            proposal["last_status_reason"] = reason or "manual_update"
            proposal["status_updated_at"] = now()

            if status == "approved_for_manual_send":
                proposal["manual_send_allowed"] = True

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "proposal_id": proposal_id,
                "activity_type": "status_changed",
                "summary": f"Status alterado para {status}. Motivo: {reason or 'manual_update'}",
                "created_at": now(),
                "created_by": "operator"
            })

            write_proposal_file(proposal)
            found = True

    if not found:
        raise RuntimeError(f"Proposal not found: {proposal_id}")

    save_registry(registry)
    event("proposal.status_changed", {"proposal_id": proposal_id, "status": status})
    return audit_report()


def approval_dry_run(proposal_id: str) -> dict[str, Any]:
    policy = load_policy()
    registry = ensure_registry()

    proposal = next((p for p in registry.get("proposals", []) if p.get("proposal_id") == proposal_id), None)
    if not proposal:
        raise RuntimeError(f"Proposal not found: {proposal_id}")

    blockers = []

    if not proposal.get("deal_id"):
        blockers.append("deal_id_missing")

    if not proposal.get("customer_alias"):
        blockers.append("customer_alias_missing")

    if not proposal.get("agent_id"):
        blockers.append("agent_id_missing")

    if float(proposal.get("setup_total", 0.0) or 0.0) < 0:
        blockers.append("setup_total_invalid")

    if float(proposal.get("recurring_total", 0.0) or 0.0) < 0:
        blockers.append("recurring_total_invalid")

    if not proposal.get("valid_until"):
        blockers.append("valid_until_missing")

    if proposal.get("approval_status") != "commercial_approved":
        blockers.append("commercial_approval_required")

    if proposal.get("status") not in {"commercial_review", "approved_for_manual_send"}:
        blockers.append("proposal_must_be_in_review_or_approved_status")

    decision = "ready_for_manual_send" if not blockers else "blocked_until_requirements_met"

    result = {
        "ok": True,
        "checkpoint": "029",
        "module": "k_os_proposal_factory_quote_builder",
        "status": "approval_dry_run",
        "generated_at": now(),
        "proposal": safe_proposal(proposal),
        "approval_decision": decision,
        "blockers": blockers,
        "required_gates_before_manual_send": policy.get("required_gates_before_manual_send", []),
        "external_send_performed": False,
        "manual_send_allowed": decision == "ready_for_manual_send",
        "customer_activation_performed": False,
        "manual_approval_required": True,
        "next_checkpoint": policy.get("next_checkpoint", "030 - K-Onboarding and Activation Gate")
    }

    APPROVAL_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Proposal Approval Dry Run",
        "",
        f"- Status: {result.get('status')}",
        f"- Decision: {result.get('approval_decision')}",
        f"- Proposal: {proposal_id}",
        f"- Customer: {proposal.get('customer_alias')}",
        f"- External send performed: {result.get('external_send_performed')}",
        f"- Manual send allowed: {result.get('manual_send_allowed')}",
        "",
        "## Blockers",
        ""
    ]

    if blockers:
        for item in blockers:
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker encontrado. Ainda exige envio manual pelo operador.")

    APPROVAL_MD.write_text("\n".join(lines), encoding="utf-8")
    event("proposal.approval_dry_run", {"proposal_id": proposal_id, "blockers": blockers})
    return result


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    policy = load_policy()
    template_files = proposal_templates()

    proposals = [safe_proposal(item) for item in registry.get("proposals", [])]
    activities = [safe_activity(item) for item in registry.get("activities", [])[-30:]]

    setup_total = round(sum(float(item.get("setup_total", 0.0) or 0.0) for item in proposals), 2)
    recurring_total = round(sum(float(item.get("recurring_total", 0.0) or 0.0) for item in proposals), 2)

    status_counts: dict[str, int] = {}
    for item in proposals:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    report = {
        "ok": True,
        "checkpoint": "029",
        "module": "k_os_proposal_factory_quote_builder",
        "status": "audit_generated",
        "generated_at": now(),
        "proposal_registry_path": "local_secrets/k_os_proposals/proposal_registry.json",
        "proposal_registry_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_send_enabled": False,
        "proposals": proposals,
        "recent_activities": activities,
        "templates": template_files,
        "metrics": {
            "proposal_count": len(proposals),
            "setup_total_brl": setup_total,
            "recurring_total_brl": recurring_total,
            "status_counts": status_counts
        },
        "required_gates_before_manual_send": policy.get("required_gates_before_manual_send", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "030 - K-Onboarding and Activation Gate")
    }

    write_report(report)
    event("proposal.audit_generated", {"proposal_count": len(proposals)})
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Proposal Factory and Quote Builder",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Registry committed: {report.get('proposal_registry_committed')}",
        f"- External send enabled: {report.get('external_send_enabled')}",
        f"- Automatic send enabled: {report.get('automatic_send_enabled')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in report.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "## Proposals",
        ""
    ])

    if report.get("proposals"):
        for item in report.get("proposals", []):
            lines.append(
                f"- {item.get('proposal_id')} | {item.get('customer_alias')} | {item.get('status')} | "
                f"setup={item.get('setup_total')} | recurring={item.get('recurring_total')} | manual_send={item.get('manual_send_allowed')}"
            )
    else:
        lines.append("- Nenhuma proposta registrada.")

    lines.extend([
        "",
        "## Required gates before manual send",
        ""
    ])

    for gate in report.get("required_gates_before_manual_send", []):
        lines.append(f"- {gate}")

    lines.extend([
        "",
        "## Blocked actions",
        ""
    ])

    for action in report.get("blocked_actions", []):
        lines.append(f"- {action}")

    lines.extend([
        "",
        "## Templates",
        ""
    ])

    for item in report.get("templates", []):
        lines.append(f"- {item.get('path')}")

    lines.extend([
        "",
        "## Next checkpoint",
        "",
        f"- {report.get('next_checkpoint')}"
    ])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "create-demo", "create-from-deal", "audit", "set-status", "approval-dry-run", "show"], required=True)
    parser.add_argument("--deal-id", default="")
    parser.add_argument("--proposal-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "create-from-deal":
        if not args.deal_id:
            raise SystemExit("Informe --deal-id")
        result = create_from_deal(args.deal_id)

    elif args.mode == "audit":
        result = audit_report()

    elif args.mode == "set-status":
        if not args.proposal_id:
            raise SystemExit("Informe --proposal-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = set_status(args.proposal_id, args.status, args.reason)

    elif args.mode == "approval-dry-run":
        if not args.proposal_id:
            raise SystemExit("Informe --proposal-id")
        result = approval_dry_run(args.proposal_id)

    elif args.mode == "show":
        if LATEST_JSON.exists():
            print(LATEST_JSON.read_text(encoding="utf-8-sig"))
            return 0
        print("{}")
        return 0

    else:
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())