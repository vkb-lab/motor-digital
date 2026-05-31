# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "onboarding" / "k_os_onboarding_activation_policy.json"
ONBOARDING_DIR = ROOT / "local_secrets" / "k_os_onboarding"
ONBOARDING_PATH = ONBOARDING_DIR / "onboarding_registry.json"

REPORT_DIR = ROOT / "reports" / "onboarding"
MEMORY_DIR = ROOT / "memory" / "onboarding"

LATEST_JSON = REPORT_DIR / "latest_onboarding_activation_report.json"
LATEST_MD = REPORT_DIR / "latest_onboarding_activation_report.md"
LATEST_PACKAGE_MD = REPORT_DIR / "latest_onboarding_package.md"
LATEST_VALIDATION_JSON = REPORT_DIR / "latest_activation_gate_validation.json"
LATEST_VALIDATION_MD = REPORT_DIR / "latest_activation_gate_validation.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

CRM_REPORT = ROOT / "reports" / "crm" / "latest_customer_registry_report.json"
BILLING_REPORT = ROOT / "reports" / "billing" / "latest_billing_subscription_report.json"
LICENSE_REPORT = ROOT / "reports" / "license" / "latest_license_gate_report.json"
SALES_REPORT = ROOT / "reports" / "sales" / "latest_sales_pipeline_report.json"
PROPOSAL_REPORT = ROOT / "reports" / "proposals" / "latest_proposal_factory_report.json"
RISK_SCRIPT = ROOT / "ops" / "k_os_ai_risk_classifier.py"

FOUNDATION_EVIDENCE = {
    "security_firewall": "reports/security/k_os_015_closure_report.json",
    "schema_guard": "reports/schema/k_os_016_closure_report.json",
    "agent_permission_matrix": "reports/governance/k_os_017_closure_report.json",
    "vault_guard": "reports/vault/k_os_018_closure_report.json",
    "audit_evidence_pack": "reports/audit/k_os_019_closure_report.json",
    "mission_control": "reports/mission_control/k_os_020_closure_report.json",
    "risk_classifier": "reports/risk/k_os_021_closure_report.json",
    "external_api_sandbox": "reports/external_sandbox/k_os_022_closure_report.json",
    "enterprise_readiness": "reports/enterprise/k_os_023_closure_report.json",
    "incident_runbook": "reports/incident/k_os_024_closure_report.json",
    "legal_templates": "reports/legal/k_os_025_closure_report.json",
    "billing_ledger": "reports/billing/k_os_026_closure_report.json",
    "crm_core": "reports/crm/k_os_027_closure_report.json",
    "deal_desk": "reports/sales/k_os_028_closure_report.json",
    "proposal_factory": "reports/proposals/k_os_029_closure_report.json"
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
        raise RuntimeError("Onboarding policy not found.")
    return data


def ensure_registry() -> dict[str, Any]:
    ONBOARDING_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not ONBOARDING_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "real_customer_activation_enabled": False,
            "activation_dry_run_only": True,
            "onboarding_cases": [],
            "activities": []
        }
        write_json(ONBOARDING_PATH, data)

    registry = read_json(ONBOARDING_PATH)
    if not registry:
        raise RuntimeError("Could not load onboarding registry.")
    return registry


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(ONBOARDING_PATH, data)


def safe_case(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "onboarding_id": item.get("onboarding_id"),
        "customer_alias": item.get("customer_alias"),
        "customer_id": item.get("customer_id", ""),
        "agent_id": item.get("agent_id", ""),
        "deal_id": item.get("deal_id", ""),
        "proposal_id": item.get("proposal_id", ""),
        "subscription_id": item.get("subscription_id", ""),
        "license_id": item.get("license_id", ""),
        "status": item.get("status"),
        "activation_decision": item.get("activation_decision", "not_validated"),
        "blockers_count": item.get("blockers_count", 0),
        "manual_activation_allowed": item.get("manual_activation_allowed", False),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def first_or_none(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    return items[0] if items else None


def find_by_alias(items: list[dict[str, Any]], alias: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("customer_alias") == alias:
            return item
    return None


def foundation_status() -> list[dict[str, Any]]:
    result = []
    for name, rel in FOUNDATION_EVIDENCE.items():
        path = ROOT / rel
        data = read_json(path)
        result.append({
            "name": name,
            "path": rel,
            "exists": path.exists(),
            "ok": bool(data and data.get("ok") is True),
            "status": data.get("status") if isinstance(data, dict) else "missing"
        })
    return result


def run_risk(customer_alias: str, agent_id: str) -> dict[str, Any]:
    if not RISK_SCRIPT.exists():
        return {
            "available": False,
            "ok": False,
            "risk_level": "unknown",
            "decision": "requires_approval",
            "required_gates": ["human_operator_approval"]
        }

    completed = subprocess.run(
        [
            "python",
            str(RISK_SCRIPT),
            "--mode",
            "classify",
            "--action",
            "activate customer onboarding gate",
            "--agent",
            agent_id or "unknown_agent",
            "--target",
            customer_alias or "unknown_customer"
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if completed.returncode != 0:
        return {
            "available": True,
            "ok": False,
            "risk_level": "unknown",
            "decision": "requires_approval",
            "stderr": completed.stderr
        }

    try:
        parsed = json.loads(completed.stdout)
        results = parsed.get("results", [])
        if results:
            item = results[0]
            item["available"] = True
            return item
    except Exception:
        pass

    return {
        "available": True,
        "ok": False,
        "risk_level": "unknown",
        "decision": "requires_approval"
    }


def build_context(customer_alias: str) -> dict[str, Any]:
    crm = read_json(CRM_REPORT) or {}
    billing = read_json(BILLING_REPORT) or {}
    license_report = read_json(LICENSE_REPORT) or {}
    sales = read_json(SALES_REPORT) or {}
    proposals = read_json(PROPOSAL_REPORT) or {}

    customers = crm.get("customers", [])
    subscriptions = billing.get("subscriptions", [])
    licenses = license_report.get("licenses", [])
    deals = sales.get("deals", [])
    proposal_items = proposals.get("proposals", [])

    customer = find_by_alias(customers, customer_alias) if customer_alias else first_or_none(customers)
    alias = customer.get("customer_alias") if customer else customer_alias

    subscription = find_by_alias(subscriptions, alias) if alias else first_or_none(subscriptions)
    license_item = find_by_alias(licenses, alias) if alias else first_or_none(licenses)
    deal = find_by_alias(deals, alias) if alias else first_or_none(deals)
    proposal = find_by_alias(proposal_items, alias) if alias else first_or_none(proposal_items)

    agent_id = ""
    for item in [customer, deal, proposal, subscription, license_item]:
        if item and item.get("agent_id"):
            agent_id = item.get("agent_id")
            break

    return {
        "customer_alias": alias or customer_alias or "unknown_customer",
        "customer": customer,
        "subscription": subscription,
        "license": license_item,
        "deal": deal,
        "proposal": proposal,
        "agent_id": agent_id or "marketplace_ia_agent",
        "reports": {
            "crm_report_exists": CRM_REPORT.exists(),
            "billing_report_exists": BILLING_REPORT.exists(),
            "license_report_exists": LICENSE_REPORT.exists(),
            "sales_report_exists": SALES_REPORT.exists(),
            "proposal_report_exists": PROPOSAL_REPORT.exists()
        }
    }


def validate_activation(customer_alias: str = "") -> dict[str, Any]:
    policy = load_policy()
    ctx = build_context(customer_alias)

    blockers = []
    warnings = []
    gates = []

    customer = ctx["customer"]
    subscription = ctx["subscription"]
    license_item = ctx["license"]
    deal = ctx["deal"]
    proposal = ctx["proposal"]
    alias = ctx["customer_alias"]
    agent_id = ctx["agent_id"]

    if customer:
        gates.append({"gate": "crm_customer_exists", "ok": True})
    else:
        gates.append({"gate": "crm_customer_exists", "ok": False})
        blockers.append("crm_customer_missing")

    if subscription and subscription.get("status") in {"trial", "active"}:
        gates.append({"gate": "billing_subscription_active_or_trial", "ok": True})
    else:
        gates.append({"gate": "billing_subscription_active_or_trial", "ok": False})
        blockers.append("billing_subscription_not_active_or_trial")

    if license_item and license_item.get("status") == "active" and license_item.get("emergency_lockdown") is not True:
        gates.append({"gate": "license_gate_active", "ok": True})
    else:
        gates.append({"gate": "license_gate_active", "ok": False})
        blockers.append("license_gate_not_active")

    if deal and deal.get("approval_status") in {"commercial_approved", "final_approved"}:
        gates.append({"gate": "deal_commercially_approved", "ok": True})
    else:
        gates.append({"gate": "deal_commercially_approved", "ok": False})
        blockers.append("deal_not_commercially_approved")

    if proposal and proposal.get("status") in {"approved_for_manual_send", "sent_manually", "accepted"}:
        gates.append({"gate": "proposal_approved_for_manual_send_or_accepted", "ok": True})
    else:
        gates.append({"gate": "proposal_approved_for_manual_send_or_accepted", "ok": False})
        blockers.append("proposal_not_approved")

    foundation = foundation_status()
    foundation_missing = [item for item in foundation if not item.get("ok")]

    for item in foundation:
        gates.append({"gate": item["name"], "ok": item["ok"], "status": item["status"]})

    if foundation_missing:
        blockers.append("foundation_evidence_missing_or_not_ok")

    risk = run_risk(alias, agent_id)
    risk_ok = bool(risk.get("available")) and risk.get("risk_level") in {"low", "medium", "high", "critical"}

    gates.append({
        "gate": "ai_risk_classifier_valid",
        "ok": risk_ok,
        "risk_level": risk.get("risk_level"),
        "decision": risk.get("decision")
    })

    if not risk_ok:
        blockers.append("risk_classifier_not_valid")

    if risk.get("decision") in {"requires_approval", "blocked_until_explicit_approval"}:
        warnings.append("risk_classifier_requires_human_approval")

    manual_activation_allowed = len(blockers) == 0

    validation = {
        "ok": True,
        "checkpoint": "030",
        "module": "k_os_onboarding_activation_gate",
        "status": "validated",
        "generated_at": now(),
        "customer_alias": alias,
        "agent_id": agent_id,
        "activation_decision": "ready_for_manual_activation" if manual_activation_allowed else "blocked_until_requirements_met",
        "manual_activation_allowed": manual_activation_allowed,
        "real_customer_activation_performed": False,
        "external_send_performed": False,
        "external_publish_performed": False,
        "real_provider_call_performed": False,
        "blockers": blockers,
        "warnings": warnings,
        "gates": gates,
        "context": {
            "customer": customer,
            "subscription": subscription,
            "license": license_item,
            "deal": deal,
            "proposal": proposal,
            "reports": ctx["reports"]
        },
        "risk": risk,
        "required_gates_before_activation": policy.get("required_gates_before_activation", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "031 - K-Customer Success and Delivery Tracker")
    }

    write_validation(validation)
    event("onboarding.activation_validated", {
        "customer_alias": alias,
        "decision": validation["activation_decision"],
        "blockers_count": len(blockers)
    })

    return validation


def write_validation(validation: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_VALIDATION_JSON.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Activation Gate Validation",
        "",
        f"- Customer: {validation.get('customer_alias')}",
        f"- Agent: {validation.get('agent_id')}",
        f"- Decision: {validation.get('activation_decision')}",
        f"- Manual activation allowed: {validation.get('manual_activation_allowed')}",
        f"- Real activation performed: {validation.get('real_customer_activation_performed')}",
        f"- Generated at: {validation.get('generated_at')}",
        "",
        "## Blockers",
        ""
    ]

    if validation.get("blockers"):
        for blocker in validation.get("blockers", []):
            lines.append(f"- {blocker}")
    else:
        lines.append("- Nenhum blocker encontrado. Ainda exige aprovação humana final.")

    lines.extend(["", "## Warnings", ""])

    if validation.get("warnings"):
        for warning in validation.get("warnings", []):
            lines.append(f"- {warning}")
    else:
        lines.append("- Nenhum warning registrado.")

    lines.extend(["", "## Gates", ""])

    for gate in validation.get("gates", []):
        lines.append(f"- {gate.get('gate')}: {gate.get('ok')}")

    LATEST_VALIDATION_MD.write_text("\n".join(lines), encoding="utf-8")


def create_onboarding_case(customer_alias: str = "") -> dict[str, Any]:
    registry = ensure_registry()
    validation = validate_activation(customer_alias)

    onboarding_id = "onb_" + uuid.uuid4().hex[:12]

    customer = validation.get("context", {}).get("customer") or {}
    subscription = validation.get("context", {}).get("subscription") or {}
    license_item = validation.get("context", {}).get("license") or {}
    deal = validation.get("context", {}).get("deal") or {}
    proposal = validation.get("context", {}).get("proposal") or {}

    case = {
        "onboarding_id": onboarding_id,
        "customer_alias": validation.get("customer_alias"),
        "customer_id": customer.get("customer_id", ""),
        "agent_id": validation.get("agent_id"),
        "deal_id": deal.get("deal_id", ""),
        "proposal_id": proposal.get("proposal_id", ""),
        "subscription_id": subscription.get("subscription_id", ""),
        "license_id": license_item.get("license_id", ""),
        "status": "ready_for_review" if validation.get("manual_activation_allowed") else "blocked",
        "activation_decision": validation.get("activation_decision"),
        "blockers": validation.get("blockers", []),
        "blockers_count": len(validation.get("blockers", [])),
        "warnings": validation.get("warnings", []),
        "manual_activation_allowed": validation.get("manual_activation_allowed"),
        "real_customer_activation_performed": False,
        "external_send_performed": False,
        "created_at": now(),
        "updated_at": now()
    }

    registry["onboarding_cases"].append(case)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "onboarding_id": onboarding_id,
        "activity_type": "onboarding_case_created",
        "summary": f"Onboarding criado com decisão {case['activation_decision']}",
        "created_at": now(),
        "created_by": "k_os_onboarding_activation_gate"
    })

    save_registry(registry)
    write_package(case, validation)
    event("onboarding.case_created", {
        "onboarding_id": onboarding_id,
        "customer_alias": case["customer_alias"],
        "decision": case["activation_decision"]
    })

    return audit_report()


def write_package(case: dict[str, Any], validation: dict[str, Any]) -> None:
    proposal = validation.get("context", {}).get("proposal") or {}
    deal = validation.get("context", {}).get("deal") or {}
    subscription = validation.get("context", {}).get("subscription") or {}
    license_item = validation.get("context", {}).get("license") or {}
    customer = validation.get("context", {}).get("customer") or {}

    lines = [
        "# K-OS Onboarding Package",
        "",
        "Este pacote é local e operacional. Não ativa cliente automaticamente.",
        "",
        "## Customer Summary",
        "",
        f"- Customer alias: {case.get('customer_alias')}",
        f"- Customer ID: {case.get('customer_id')}",
        f"- Agent ID: {case.get('agent_id')}",
        f"- Onboarding ID: {case.get('onboarding_id')}",
        "",
        "## Commercial Summary",
        "",
        f"- Deal ID: {case.get('deal_id')}",
        f"- Deal stage: {deal.get('stage', '')}",
        f"- Deal approval: {deal.get('approval_status', '')}",
        f"- Proposal ID: {case.get('proposal_id')}",
        f"- Proposal status: {proposal.get('status', '')}",
        "",
        "## Subscription Summary",
        "",
        f"- Subscription ID: {case.get('subscription_id')}",
        f"- Subscription status: {subscription.get('status', '')}",
        f"- Payment status: {subscription.get('payment_status', '')}",
        "",
        "## License Summary",
        "",
        f"- License ID: {case.get('license_id')}",
        f"- License status: {license_item.get('status', '')}",
        f"- Emergency lockdown: {license_item.get('emergency_lockdown', '')}",
        "",
        "## Activation Decision",
        "",
        f"- Decision: {case.get('activation_decision')}",
        f"- Manual activation allowed: {case.get('manual_activation_allowed')}",
        f"- Real activation performed: {case.get('real_customer_activation_performed')}",
        "",
        "## Activation Blockers",
        ""
    ]

    if case.get("blockers"):
        for blocker in case.get("blockers", []):
            lines.append(f"- {blocker}")
    else:
        lines.append("- Nenhum blocker encontrado. Ainda exige aprovação humana final.")

    lines.extend([
        "",
        "## Manual Next Steps",
        "",
        "- revisar blockers",
        "- aprovar proposta comercial",
        "- ativar ou validar assinatura",
        "- ativar License Gate",
        "- confirmar permissões do agente",
        "- registrar aprovação humana",
        "- somente depois executar ativação manual controlada",
        "",
        "## Operator Approval Checklist",
        "",
        "- CRM revisado",
        "- assinatura revisada",
        "- licença revisada",
        "- proposta revisada",
        "- deal revisado",
        "- risco revisado",
        "- permissões revisadas",
        "- incidente/rollback disponível",
        "- aprovação humana registrada",
        "",
        "## Safety Rules",
        "",
        "- não enviar mensagem externa automaticamente",
        "- não publicar externamente",
        "- não chamar provedor externo",
        "- não apagar dados de cliente",
        "- não apagar logs de auditoria"
    ]

    LATEST_PACKAGE_MD.write_text("\n".join(lines), encoding="utf-8")


def create_demo() -> dict[str, Any]:
    ctx = build_context("demo_customer")
    return create_onboarding_case(ctx.get("customer_alias") or "demo_customer")


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    policy = load_policy()

    cases = [safe_case(item) for item in registry.get("onboarding_cases", [])]
    foundation = foundation_status()

    status_counts: dict[str, int] = {}
    for item in cases:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    report = {
        "ok": True,
        "checkpoint": "030",
        "module": "k_os_onboarding_activation_gate",
        "status": "audit_generated",
        "generated_at": now(),
        "onboarding_registry_path": "local_secrets/k_os_onboarding/onboarding_registry.json",
        "onboarding_registry_committed": False,
        "real_customer_activation_enabled": False,
        "activation_dry_run_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "real_provider_call_enabled": False,
        "cases": cases,
        "metrics": {
            "onboarding_case_count": len(cases),
            "status_counts": status_counts,
            "blocked_count": status_counts.get("blocked", 0),
            "ready_for_review_count": status_counts.get("ready_for_review", 0)
        },
        "foundation": foundation,
        "required_gates_before_activation": policy.get("required_gates_before_activation", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "031 - K-Customer Success and Delivery Tracker")
    }

    write_report(report)
    event("onboarding.audit_generated", {"case_count": len(cases)})
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Onboarding and Activation Gate",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Registry committed: {report.get('onboarding_registry_committed')}",
        f"- Real customer activation enabled: {report.get('real_customer_activation_enabled')}",
        f"- Activation dry-run only: {report.get('activation_dry_run_only')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in report.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Onboarding Cases", ""])

    if report.get("cases"):
        for item in report.get("cases", []):
            lines.append(
                f"- {item.get('onboarding_id')} | {item.get('customer_alias')} | {item.get('status')} | "
                f"decision={item.get('activation_decision')} | blockers={item.get('blockers_count')}"
            )
    else:
        lines.append("- Nenhum onboarding case registrado.")

    lines.extend(["", "## Required gates before activation", ""])

    for gate in report.get("required_gates_before_activation", []):
        lines.append(f"- {gate}")

    lines.extend(["", "## Blocked actions", ""])

    for action in report.get("blocked_actions", []):
        lines.append(f"- {action}")

    lines.extend(["", "## Next checkpoint", "", f"- {report.get('next_checkpoint')}"])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def show_latest() -> int:
    if LATEST_JSON.exists():
        print(LATEST_JSON.read_text(encoding="utf-8-sig"))
    else:
        print("{}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "create-demo", "validate", "create-case", "audit", "show"], required=True)
    parser.add_argument("--customer-alias", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "validate":
        result = validate_activation(args.customer_alias)

    elif args.mode == "create-case":
        result = create_onboarding_case(args.customer_alias)

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