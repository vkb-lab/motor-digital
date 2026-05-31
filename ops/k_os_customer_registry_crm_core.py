# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "crm" / "k_os_customer_registry_crm_policy.json"
CRM_DIR = ROOT / "local_secrets" / "k_os_crm"
CRM_PATH = CRM_DIR / "customer_registry.json"
REPORT_DIR = ROOT / "reports" / "crm"
MEMORY_DIR = ROOT / "memory" / "crm"
LATEST_JSON = REPORT_DIR / "latest_customer_registry_report.json"
LATEST_MD = REPORT_DIR / "latest_customer_registry_report.md"
PIPELINE_JSON = REPORT_DIR / "latest_crm_pipeline_snapshot.json"
PIPELINE_MD = REPORT_DIR / "latest_crm_pipeline_snapshot.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"


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
        raise RuntimeError("CRM policy not found.")
    return data


def ensure_registry() -> dict[str, Any]:
    CRM_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not CRM_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_send_enabled": False,
            "customers": [],
            "contacts": [],
            "activities": [],
            "links": []
        }
        write_json(CRM_PATH, data)

    registry = read_json(CRM_PATH)
    if not registry:
        raise RuntimeError("Could not load CRM registry.")
    return registry


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(CRM_PATH, data)


def safe_customer(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "customer_id": item.get("customer_id"),
        "customer_alias": item.get("customer_alias"),
        "status": item.get("status"),
        "source": item.get("source"),
        "created_at": item.get("created_at"),
        "commercial_owner": item.get("commercial_owner"),
        "next_action": item.get("next_action"),
        "risk_level": item.get("risk_level"),
        "subscription_id": item.get("subscription_id", ""),
        "license_id": item.get("license_id", ""),
        "proposal_id": item.get("proposal_id", ""),
        "agent_id": item.get("agent_id", "")
    }


def safe_contact(item: dict[str, Any]) -> dict[str, Any]:
    value = item.get("contact_value", "")
    masked = ""
    if value:
        masked = "***" + value[-4:] if len(value) >= 4 else "***"

    return {
        "contact_id": item.get("contact_id"),
        "customer_id": item.get("customer_id"),
        "contact_type": item.get("contact_type"),
        "contact_masked": masked,
        "is_primary": item.get("is_primary", False),
        "consent_status": item.get("consent_status", "unknown")
    }


def safe_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": item.get("activity_id"),
        "customer_id": item.get("customer_id"),
        "activity_type": item.get("activity_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by"),
        "requires_follow_up": item.get("requires_follow_up", False)
    }


def create_demo() -> dict[str, Any]:
    registry = ensure_registry()

    alias = "demo_customer"
    existing = next((c for c in registry.get("customers", []) if c.get("customer_alias") == alias), None)

    if not existing:
        customer_id = "cus_" + uuid.uuid4().hex[:12]
        customer = {
            "customer_id": customer_id,
            "customer_alias": alias,
            "status": "trial",
            "source": "internal_demo",
            "created_at": now(),
            "commercial_owner": "k_os_operator",
            "next_action": "validar proposta demo e assinatura trial",
            "risk_level": "low",
            "subscription_id": "linked_by_billing_demo",
            "license_id": "pending_license_gate",
            "proposal_id": "demo_marketplace_ia",
            "agent_id": "marketplace_ia_agent",
            "notes": "Demo local. Não registrar dados reais sem política comercial e consentimento adequado."
        }
        registry["customers"].append(customer)

        registry["contacts"].append({
            "contact_id": "con_" + uuid.uuid4().hex[:12],
            "customer_id": customer_id,
            "contact_type": "email_alias",
            "contact_value": "demo@example.local",
            "is_primary": True,
            "consent_status": "demo_only",
            "created_at": now()
        })

        registry["activities"].append({
            "activity_id": "act_" + uuid.uuid4().hex[:12],
            "customer_id": customer_id,
            "activity_type": "demo_created",
            "summary": "Cliente demo criado para validar CRM Core.",
            "created_at": now(),
            "created_by": "k_os_crm_core",
            "requires_follow_up": True
        })

        registry["links"].append({
            "link_id": "lnk_" + uuid.uuid4().hex[:12],
            "customer_id": customer_id,
            "type": "billing_subscription",
            "target": "reports/billing/latest_billing_subscription_report.json",
            "created_at": now()
        })

    save_registry(registry)
    event("crm.demo_created", {"customer_alias": alias})
    return audit_report()


def add_customer(alias: str, source: str, owner: str, next_action: str, agent_id: str) -> dict[str, Any]:
    policy = load_policy()
    allowed_sources = set(policy.get("lead_sources", []))

    if source not in allowed_sources:
        raise RuntimeError(f"Invalid source: {source}")

    registry = ensure_registry()

    if any(c.get("customer_alias") == alias for c in registry.get("customers", [])):
        raise RuntimeError(f"Customer alias already exists: {alias}")

    customer_id = "cus_" + uuid.uuid4().hex[:12]
    customer = {
        "customer_id": customer_id,
        "customer_alias": alias,
        "status": "lead",
        "source": source,
        "created_at": now(),
        "commercial_owner": owner or "k_os_operator",
        "next_action": next_action or "qualificar lead",
        "risk_level": "medium",
        "subscription_id": "",
        "license_id": "",
        "proposal_id": "",
        "agent_id": agent_id or "",
        "notes": "Cliente criado manualmente no CRM Core."
    }

    registry["customers"].append(customer)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "customer_id": customer_id,
        "activity_type": "customer_created",
        "summary": "Cliente registrado no CRM Core.",
        "created_at": now(),
        "created_by": "operator",
        "requires_follow_up": True
    })

    save_registry(registry)
    event("crm.customer_created", {"customer_id": customer_id, "customer_alias": alias})
    return audit_report()


def update_status(customer_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()
    allowed = set(policy.get("customer_statuses", []))

    if status not in allowed:
        raise RuntimeError(f"Invalid status: {status}")

    registry = ensure_registry()
    found = False

    for item in registry.get("customers", []):
        if item.get("customer_id") == customer_id:
            item["status"] = status
            item["last_status_reason"] = reason or "manual_update"
            item["status_updated_at"] = now()
            found = True

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "customer_id": customer_id,
                "activity_type": "status_changed",
                "summary": f"Status alterado para {status}. Motivo: {reason or 'manual_update'}",
                "created_at": now(),
                "created_by": "operator",
                "requires_follow_up": status in {"qualified", "proposal_sent", "negotiation", "past_due"}
            })

    if not found:
        raise RuntimeError(f"Customer not found: {customer_id}")

    save_registry(registry)
    event("crm.status_changed", {"customer_id": customer_id, "status": status})
    return audit_report()


def link_record(customer_id: str, link_type: str, target: str) -> dict[str, Any]:
    allowed = {
        "billing_subscription",
        "license_gate",
        "proposal",
        "incident",
        "audit",
        "commercial_order",
        "manual_note"
    }

    if link_type not in allowed:
        raise RuntimeError(f"Invalid link type: {link_type}")

    registry = ensure_registry()

    if not any(c.get("customer_id") == customer_id for c in registry.get("customers", [])):
        raise RuntimeError(f"Customer not found: {customer_id}")

    registry["links"].append({
        "link_id": "lnk_" + uuid.uuid4().hex[:12],
        "customer_id": customer_id,
        "type": link_type,
        "target": target,
        "created_at": now()
    })

    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "customer_id": customer_id,
        "activity_type": "record_linked",
        "summary": f"Registro vinculado: {link_type}",
        "created_at": now(),
        "created_by": "operator",
        "requires_follow_up": False
    })

    save_registry(registry)
    event("crm.record_linked", {"customer_id": customer_id, "type": link_type})
    return audit_report()


def pipeline_snapshot(customers: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = {}
    for item in customers:
        status = item.get("status", "unknown")
        statuses[status] = statuses.get(status, 0) + 1

    open_statuses = {"lead", "qualified", "proposal_sent", "negotiation", "trial", "past_due"}
    open_count = sum(1 for item in customers if item.get("status") in open_statuses)

    return {
        "customer_count": len(customers),
        "open_pipeline_count": open_count,
        "status_counts": statuses,
        "active_customer_count": statuses.get("active_customer", 0),
        "trial_count": statuses.get("trial", 0),
        "past_due_count": statuses.get("past_due", 0),
        "suspended_count": statuses.get("suspended", 0)
    }


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    policy = load_policy()

    customers = [safe_customer(item) for item in registry.get("customers", [])]
    contacts = [safe_contact(item) for item in registry.get("contacts", [])]
    activities = [safe_activity(item) for item in registry.get("activities", [])[-20:]]

    pipeline = pipeline_snapshot(customers)

    report = {
        "ok": True,
        "checkpoint": "027",
        "module": "k_os_customer_registry_crm_core",
        "status": "audit_generated",
        "generated_at": now(),
        "crm_registry_path": "local_secrets/k_os_crm/customer_registry.json",
        "crm_registry_committed": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "sanitized_reports_only": True,
        "customers": customers,
        "contacts_sanitized": contacts,
        "recent_activities": activities,
        "pipeline": pipeline,
        "required_gates_before_customer_activation": policy.get("required_gates_before_customer_activation", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "028 - K-Sales Pipeline and Deal Desk")
    }

    write_report(report)
    write_pipeline(report)
    event("crm.audit_generated", {"customer_count": pipeline["customer_count"]})
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Customer Registry and CRM Core",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Registry committed: {report.get('crm_registry_committed')}",
        f"- External send enabled: {report.get('external_send_enabled')}",
        f"- Automatic message enabled: {report.get('automatic_message_enabled')}",
        "",
        "## Pipeline",
        ""
    ]

    for key, value in report.get("pipeline", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "## Customers",
        ""
    ])

    if report.get("customers"):
        for item in report.get("customers", []):
            lines.append(f"- {item.get('customer_id')} | {item.get('customer_alias')} | {item.get('status')} | agent={item.get('agent_id')}")
    else:
        lines.append("- Nenhum cliente registrado.")

    lines.extend([
        "",
        "## Required gates before customer activation",
        ""
    ])

    for gate in report.get("required_gates_before_customer_activation", []):
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
        "## Next checkpoint",
        "",
        f"- {report.get('next_checkpoint')}"
    ])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def write_pipeline(report: dict[str, Any]) -> None:
    pipeline = {
        "ok": True,
        "checkpoint": "027",
        "module": "k_os_customer_registry_crm_core",
        "status": "pipeline_snapshot",
        "generated_at": now(),
        "pipeline": report.get("pipeline", {}),
        "customers": report.get("customers", []),
        "next_checkpoint": report.get("next_checkpoint")
    }

    PIPELINE_JSON.write_text(json.dumps(pipeline, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS CRM Pipeline Snapshot",
        "",
        f"- Generated at: {pipeline.get('generated_at')}",
        "",
        "## Status counts",
        ""
    ]

    for status, count in pipeline.get("pipeline", {}).get("status_counts", {}).items():
        lines.append(f"- {status}: {count}")

    lines.extend([
        "",
        "## Customers",
        ""
    ])

    for item in pipeline.get("customers", []):
        lines.append(f"- {item.get('customer_alias')} | {item.get('status')} | next={item.get('next_action')}")

    PIPELINE_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "create-demo", "audit", "add-customer", "set-status", "link-record", "show"], required=True)
    parser.add_argument("--alias", default="")
    parser.add_argument("--source", default="manual")
    parser.add_argument("--owner", default="k_os_operator")
    parser.add_argument("--next-action", default="qualificar lead")
    parser.add_argument("--agent-id", default="")
    parser.add_argument("--customer-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--link-type", default="")
    parser.add_argument("--target", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "audit":
        result = audit_report()

    elif args.mode == "add-customer":
        if not args.alias:
            raise SystemExit("Informe --alias")
        result = add_customer(args.alias, args.source, args.owner, args.next_action, args.agent_id)

    elif args.mode == "set-status":
        if not args.customer_id:
            raise SystemExit("Informe --customer-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = update_status(args.customer_id, args.status, args.reason)

    elif args.mode == "link-record":
        if not args.customer_id:
            raise SystemExit("Informe --customer-id")
        if not args.link_type:
            raise SystemExit("Informe --link-type")
        if not args.target:
            raise SystemExit("Informe --target")
        result = link_record(args.customer_id, args.link_type, args.target)

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