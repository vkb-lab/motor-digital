# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "support" / "k_os_support_desk_ticketing_policy.json"
SUPPORT_DIR = ROOT / "local_secrets" / "k_os_support"
SUPPORT_PATH = SUPPORT_DIR / "support_ticket_registry.json"

REPORT_DIR = ROOT / "reports" / "support"
MEMORY_DIR = ROOT / "memory" / "support"

LATEST_JSON = REPORT_DIR / "latest_support_desk_report.json"
LATEST_MD = REPORT_DIR / "latest_support_desk_report.md"
SLA_JSON = REPORT_DIR / "latest_support_sla_snapshot.json"
SLA_MD = REPORT_DIR / "latest_support_sla_snapshot.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

CRM_REPORT = ROOT / "reports" / "crm" / "latest_customer_registry_report.json"
SUCCESS_REPORT = ROOT / "reports" / "customer_success" / "latest_customer_success_delivery_report.json"
INCIDENT_REPORT = ROOT / "reports" / "incident" / "latest_incident_readiness_report.json"


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
        raise RuntimeError("Support policy not found.")
    return data


def ensure_registry() -> dict[str, Any]:
    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not SUPPORT_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_send_enabled": False,
            "automatic_message_enabled": False,
            "tickets": [],
            "notes": [],
            "activities": []
        }
        write_json(SUPPORT_PATH, data)

    registry = read_json(SUPPORT_PATH)
    if not registry:
        raise RuntimeError("Could not load support registry.")
    return registry


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(SUPPORT_PATH, data)


def first_or_none(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    return items[0] if items else None


def find_by_alias(items: list[dict[str, Any]], alias: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("customer_alias") == alias:
            return item
    return None


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def load_context(customer_alias: str = "") -> dict[str, Any]:
    crm = read_json(CRM_REPORT) or {}
    success = read_json(SUCCESS_REPORT) or {}

    customers = crm.get("customers", [])
    accounts = success.get("accounts", [])
    deliveries = success.get("deliveries", [])

    customer = find_by_alias(customers, customer_alias) if customer_alias else first_or_none(customers)
    alias = customer.get("customer_alias") if customer else customer_alias or "demo_customer"

    account = find_by_alias(accounts, alias) if alias else first_or_none(accounts)
    delivery = find_by_alias(deliveries, alias) if alias else first_or_none(deliveries)

    agent_id = ""
    for item in [customer, account, delivery]:
        if item and item.get("agent_id"):
            agent_id = item.get("agent_id")
            break

    return {
        "customer_alias": alias,
        "customer": customer,
        "success_account": account,
        "delivery": delivery,
        "agent_id": agent_id or "marketplace_ia_agent",
        "reports": {
            "crm_report_exists": CRM_REPORT.exists(),
            "customer_success_report_exists": SUCCESS_REPORT.exists(),
            "incident_report_exists": INCIDENT_REPORT.exists()
        }
    }


def sla_due_at(priority: str) -> str:
    policy = load_policy()
    hours = int(policy.get("sla_targets_hours", {}).get(priority, 24))
    return (now_dt() + timedelta(hours=hours)).isoformat()


def sla_state(ticket: dict[str, Any]) -> str:
    if ticket.get("status") in {"closed", "cancelled"}:
        return "closed"

    due = parse_dt(ticket.get("sla_due_at", ""))
    if not due:
        return "unknown"

    remaining = (due - now_dt()).total_seconds() / 3600

    if remaining < 0:
        return "breached"

    if remaining <= 2:
        return "at_risk"

    return "ok"


def safe_ticket(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticket_id": item.get("ticket_id"),
        "customer_alias": item.get("customer_alias"),
        "agent_id": item.get("agent_id", ""),
        "success_account_id": item.get("success_account_id", ""),
        "delivery_id": item.get("delivery_id", ""),
        "incident_id": item.get("incident_id", ""),
        "category": item.get("category"),
        "priority": item.get("priority"),
        "status": item.get("status"),
        "subject": item.get("subject"),
        "summary": item.get("summary"),
        "support_owner": item.get("support_owner"),
        "next_action": item.get("next_action"),
        "sla_due_at": item.get("sla_due_at", ""),
        "sla_state": sla_state(item),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def safe_note(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "note_id": item.get("note_id"),
        "ticket_id": item.get("ticket_id"),
        "note_type": item.get("note_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by")
    }


def safe_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": item.get("activity_id"),
        "ticket_id": item.get("ticket_id"),
        "activity_type": item.get("activity_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by")
    }


def create_ticket(customer_alias: str, category: str, priority: str, subject: str, summary: str, owner: str) -> dict[str, Any]:
    policy = load_policy()

    if category not in set(policy.get("ticket_categories", [])):
        raise RuntimeError(f"Invalid category: {category}")

    if priority not in set(policy.get("ticket_priorities", [])):
        raise RuntimeError(f"Invalid priority: {priority}")

    registry = ensure_registry()
    ctx = load_context(customer_alias)

    ticket_id = "tkt_" + uuid.uuid4().hex[:12]

    success_account = ctx.get("success_account") or {}
    delivery = ctx.get("delivery") or {}

    status = "triage" if priority in {"high", "critical"} else "new"

    ticket = {
        "ticket_id": ticket_id,
        "customer_alias": ctx["customer_alias"],
        "agent_id": ctx["agent_id"],
        "success_account_id": success_account.get("success_account_id", ""),
        "delivery_id": delivery.get("delivery_id", ""),
        "incident_id": "",
        "category": category,
        "priority": priority,
        "status": status,
        "subject": subject,
        "summary": summary,
        "support_owner": owner or "k_os_operator",
        "next_action": "triagem inicial e definição de resposta manual",
        "sla_due_at": sla_due_at(priority),
        "created_at": now(),
        "updated_at": now()
    }

    if category in {"incident", "security"} or priority == "critical":
        ticket["next_action"] = "avaliar escalonamento para Incident Response Runbook"

    registry["tickets"].append(ticket)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "ticket_id": ticket_id,
        "activity_type": "ticket_created",
        "summary": f"Ticket criado em {category}/{priority}.",
        "created_at": now(),
        "created_by": "k_os_support_desk"
    })

    save_registry(registry)
    event("support.ticket_created", {"ticket_id": ticket_id, "customer_alias": ctx["customer_alias"], "priority": priority})
    return audit_report()


def create_demo() -> dict[str, Any]:
    return create_ticket(
        customer_alias="demo_customer",
        category="delivery",
        priority="medium",
        subject="Validar primeira entrega operacional",
        summary="Ticket demo para acompanhar suporte de entrega inicial.",
        owner="k_os_operator"
    )


def set_status(ticket_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()
    allowed = set(policy.get("ticket_statuses", []))

    if status not in allowed:
        raise RuntimeError(f"Invalid ticket status: {status}")

    registry = ensure_registry()
    found = False

    for ticket in registry.get("tickets", []):
        if ticket.get("ticket_id") == ticket_id:
            if status in {"closed", "resolved_pending_review"} and ticket.get("priority") == "critical":
                if reason.lower().find("review") < 0:
                    raise RuntimeError("Critical tickets require explicit review reason before close/resolution.")

            ticket["status"] = status
            ticket["last_status_reason"] = reason or "manual_update"
            ticket["updated_at"] = now()

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "ticket_id": ticket_id,
                "activity_type": "status_changed",
                "summary": f"Status alterado para {status}.",
                "created_at": now(),
                "created_by": "operator"
            })

            found = True

    if not found:
        raise RuntimeError(f"Ticket not found: {ticket_id}")

    save_registry(registry)
    event("support.ticket_status_changed", {"ticket_id": ticket_id, "status": status})
    return audit_report()


def set_priority(ticket_id: str, priority: str, reason: str) -> dict[str, Any]:
    policy = load_policy()
    allowed = set(policy.get("ticket_priorities", []))

    if priority not in allowed:
        raise RuntimeError(f"Invalid priority: {priority}")

    registry = ensure_registry()
    found = False

    for ticket in registry.get("tickets", []):
        if ticket.get("ticket_id") == ticket_id:
            ticket["priority"] = priority
            ticket["sla_due_at"] = sla_due_at(priority)
            ticket["last_priority_reason"] = reason or "manual_priority_update"
            ticket["updated_at"] = now()

            if priority == "critical":
                ticket["status"] = "escalated"
                ticket["next_action"] = "acionar revisão crítica e avaliar incidente"

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "ticket_id": ticket_id,
                "activity_type": "priority_changed",
                "summary": f"Prioridade alterada para {priority}.",
                "created_at": now(),
                "created_by": "operator"
            })

            found = True

    if not found:
        raise RuntimeError(f"Ticket not found: {ticket_id}")

    save_registry(registry)
    event("support.ticket_priority_changed", {"ticket_id": ticket_id, "priority": priority})
    return audit_report()


def add_note(ticket_id: str, summary: str, note_type: str, owner: str) -> dict[str, Any]:
    registry = ensure_registry()

    if not any(t.get("ticket_id") == ticket_id for t in registry.get("tickets", [])):
        raise RuntimeError(f"Ticket not found: {ticket_id}")

    note = {
        "note_id": "note_" + uuid.uuid4().hex[:12],
        "ticket_id": ticket_id,
        "note_type": note_type or "internal",
        "summary": summary,
        "created_at": now(),
        "created_by": owner or "k_os_operator"
    }

    registry["notes"].append(note)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "ticket_id": ticket_id,
        "activity_type": "note_added",
        "summary": "Nota sanitizada adicionada.",
        "created_at": now(),
        "created_by": owner or "k_os_operator"
    })

    save_registry(registry)
    event("support.note_added", {"ticket_id": ticket_id, "note_type": note_type})
    return audit_report()


def escalation_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    tickets = report.get("tickets", [])

    at_risk = [item for item in tickets if item.get("sla_state") in {"at_risk", "breached"}]
    escalated = [item for item in tickets if item.get("status") == "escalated" or item.get("priority") == "critical"]

    snapshot = {
        "ok": True,
        "checkpoint": "032",
        "module": "k_os_support_desk_ticketing_core",
        "status": "sla_snapshot",
        "generated_at": now(),
        "at_risk_count": len(at_risk),
        "escalated_count": len(escalated),
        "at_risk_tickets": at_risk,
        "escalated_tickets": escalated,
        "external_send_enabled": False,
        "automatic_message_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    SLA_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Support SLA Snapshot",
        "",
        f"- Generated at: {snapshot.get('generated_at')}",
        f"- At risk count: {snapshot.get('at_risk_count')}",
        f"- Escalated count: {snapshot.get('escalated_count')}",
        f"- External send enabled: {snapshot.get('external_send_enabled')}",
        "",
        "## At risk tickets",
        ""
    ]

    if at_risk:
        for item in at_risk:
            lines.append(f"- {item.get('ticket_id')} | {item.get('customer_alias')} | {item.get('priority')} | {item.get('sla_state')} | {item.get('next_action')}")
    else:
        lines.append("- Nenhum ticket em risco de SLA operacional.")

    lines.extend(["", "## Escalated tickets", ""])

    if escalated:
        for item in escalated:
            lines.append(f"- {item.get('ticket_id')} | {item.get('customer_alias')} | {item.get('priority')} | {item.get('status')}")
    else:
        lines.append("- Nenhum ticket escalonado.")

    SLA_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def compute_metrics(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    sla_counts: dict[str, int] = {}

    for ticket in tickets:
        status = ticket.get("status", "unknown")
        priority = ticket.get("priority", "medium")
        category = ticket.get("category", "question")
        state = ticket.get("sla_state", "unknown")

        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1
        sla_counts[state] = sla_counts.get(state, 0) + 1

    open_statuses = {"new", "triage", "in_progress", "waiting_customer", "waiting_internal", "escalated", "resolved_pending_review"}

    return {
        "ticket_count": len(tickets),
        "open_ticket_count": sum(1 for t in tickets if t.get("status") in open_statuses),
        "critical_ticket_count": priority_counts.get("critical", 0),
        "high_ticket_count": priority_counts.get("high", 0),
        "sla_at_risk_count": sla_counts.get("at_risk", 0),
        "sla_breached_count": sla_counts.get("breached", 0),
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "category_counts": category_counts,
        "sla_counts": sla_counts
    }


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    policy = load_policy()

    tickets = [safe_ticket(item) for item in registry.get("tickets", [])]
    notes = [safe_note(item) for item in registry.get("notes", [])[-30:]]
    activities = [safe_activity(item) for item in registry.get("activities", [])[-30:]]

    metrics = compute_metrics(tickets)

    report = {
        "ok": True,
        "checkpoint": "032",
        "module": "k_os_support_desk_ticketing_core",
        "status": "audit_generated",
        "generated_at": now(),
        "support_registry_path": "local_secrets/k_os_support/support_ticket_registry.json",
        "support_registry_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "tickets": tickets,
        "recent_notes": notes,
        "recent_activities": activities,
        "metrics": metrics,
        "required_gates_before_ticket_close": policy.get("required_gates_before_ticket_close", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "033 - K-Knowledge Base and Support Playbooks")
    }

    write_report(report)
    escalation_snapshot(report)
    event("support.audit_generated", {"ticket_count": metrics["ticket_count"]})
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Support Desk and Ticketing Core",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Registry committed: {report.get('support_registry_committed')}",
        f"- External send enabled: {report.get('external_send_enabled')}",
        f"- Automatic message enabled: {report.get('automatic_message_enabled')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in report.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Tickets", ""])

    if report.get("tickets"):
        for item in report.get("tickets", []):
            lines.append(
                f"- {item.get('ticket_id')} | {item.get('customer_alias')} | {item.get('category')} | "
                f"{item.get('priority')} | {item.get('status')} | sla={item.get('sla_state')}"
            )
    else:
        lines.append("- Nenhum ticket registrado.")

    lines.extend(["", "## Required gates before ticket close", ""])

    for gate in report.get("required_gates_before_ticket_close", []):
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
    parser.add_argument("--mode", choices=["init", "create-demo", "create-ticket", "set-status", "set-priority", "add-note", "audit", "show"], required=True)
    parser.add_argument("--customer-alias", default="")
    parser.add_argument("--category", default="question")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--subject", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--owner", default="k_os_operator")
    parser.add_argument("--ticket-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--note-type", default="internal")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "create-ticket":
        if not args.customer_alias:
            raise SystemExit("Informe --customer-alias")
        if not args.subject:
            raise SystemExit("Informe --subject")
        if not args.summary:
            raise SystemExit("Informe --summary")
        result = create_ticket(args.customer_alias, args.category, args.priority, args.subject, args.summary, args.owner)

    elif args.mode == "set-status":
        if not args.ticket_id:
            raise SystemExit("Informe --ticket-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = set_status(args.ticket_id, args.status, args.reason)

    elif args.mode == "set-priority":
        if not args.ticket_id:
            raise SystemExit("Informe --ticket-id")
        result = set_priority(args.ticket_id, args.priority, args.reason)

    elif args.mode == "add-note":
        if not args.ticket_id:
            raise SystemExit("Informe --ticket-id")
        if not args.summary:
            raise SystemExit("Informe --summary")
        result = add_note(args.ticket_id, args.summary, args.note_type, args.owner)

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