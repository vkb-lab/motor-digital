# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "customer_success" / "k_os_customer_success_delivery_policy.json"
SUCCESS_DIR = ROOT / "local_secrets" / "k_os_customer_success"
SUCCESS_PATH = SUCCESS_DIR / "customer_success_registry.json"

REPORT_DIR = ROOT / "reports" / "customer_success"
MEMORY_DIR = ROOT / "memory" / "customer_success"

LATEST_JSON = REPORT_DIR / "latest_customer_success_delivery_report.json"
LATEST_MD = REPORT_DIR / "latest_customer_success_delivery_report.md"
HEALTH_JSON = REPORT_DIR / "latest_customer_success_health_snapshot.json"
HEALTH_MD = REPORT_DIR / "latest_customer_success_health_snapshot.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

CRM_REPORT = ROOT / "reports" / "crm" / "latest_customer_registry_report.json"
ONBOARDING_REPORT = ROOT / "reports" / "onboarding" / "latest_onboarding_activation_report.json"
BILLING_REPORT = ROOT / "reports" / "billing" / "latest_billing_subscription_report.json"
LICENSE_REPORT = ROOT / "reports" / "license" / "latest_license_gate_report.json"


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
        raise RuntimeError("Customer success policy not found.")
    return data


def ensure_registry() -> dict[str, Any]:
    SUCCESS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not SUCCESS_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_send_enabled": False,
            "automatic_message_enabled": False,
            "accounts": [],
            "deliveries": [],
            "tasks": [],
            "activities": []
        }
        write_json(SUCCESS_PATH, data)

    registry = read_json(SUCCESS_PATH)
    if not registry:
        raise RuntimeError("Could not load customer success registry.")
    return registry


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(SUCCESS_PATH, data)


def first_or_none(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    return items[0] if items else None


def find_by_alias(items: list[dict[str, Any]], alias: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("customer_alias") == alias:
            return item
    return None


def load_context(customer_alias: str = "") -> dict[str, Any]:
    crm = read_json(CRM_REPORT) or {}
    onboarding = read_json(ONBOARDING_REPORT) or {}
    billing = read_json(BILLING_REPORT) or {}
    license_report = read_json(LICENSE_REPORT) or {}

    customers = crm.get("customers", [])
    onboarding_cases = onboarding.get("cases", [])
    subscriptions = billing.get("subscriptions", [])
    licenses = license_report.get("licenses", [])

    customer = find_by_alias(customers, customer_alias) if customer_alias else first_or_none(customers)
    alias = customer.get("customer_alias") if customer else customer_alias or "demo_customer"

    onboarding_case = find_by_alias(onboarding_cases, alias) if alias else first_or_none(onboarding_cases)
    subscription = find_by_alias(subscriptions, alias) if alias else first_or_none(subscriptions)
    license_item = find_by_alias(licenses, alias) if alias else first_or_none(licenses)

    agent_id = ""
    for item in [customer, onboarding_case, subscription, license_item]:
        if item and item.get("agent_id"):
            agent_id = item.get("agent_id")
            break

    return {
        "customer_alias": alias,
        "customer": customer,
        "onboarding": onboarding_case,
        "subscription": subscription,
        "license": license_item,
        "agent_id": agent_id or "marketplace_ia_agent",
        "reports": {
            "crm_report_exists": CRM_REPORT.exists(),
            "onboarding_report_exists": ONBOARDING_REPORT.exists(),
            "billing_report_exists": BILLING_REPORT.exists(),
            "license_report_exists": LICENSE_REPORT.exists()
        }
    }


def safe_account(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "success_account_id": item.get("success_account_id"),
        "customer_alias": item.get("customer_alias"),
        "agent_id": item.get("agent_id"),
        "onboarding_id": item.get("onboarding_id", ""),
        "subscription_id": item.get("subscription_id", ""),
        "license_id": item.get("license_id", ""),
        "health": item.get("health", "unknown"),
        "risk_level": item.get("risk_level", "medium"),
        "next_action": item.get("next_action", ""),
        "success_owner": item.get("success_owner", "k_os_operator"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def safe_delivery(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "delivery_id": item.get("delivery_id"),
        "success_account_id": item.get("success_account_id"),
        "customer_alias": item.get("customer_alias"),
        "title": item.get("title"),
        "status": item.get("status"),
        "priority": item.get("priority", "medium"),
        "due_date": item.get("due_date", ""),
        "completion_review_required": item.get("completion_review_required", True),
        "created_at": item.get("created_at"),
        "completed_at": item.get("completed_at", "")
    }


def safe_task(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": item.get("task_id"),
        "delivery_id": item.get("delivery_id", ""),
        "success_account_id": item.get("success_account_id"),
        "customer_alias": item.get("customer_alias"),
        "title": item.get("title"),
        "status": item.get("status"),
        "owner": item.get("owner"),
        "priority": item.get("priority", "medium"),
        "due_date": item.get("due_date", ""),
        "created_at": item.get("created_at"),
        "completed_at": item.get("completed_at", "")
    }


def safe_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": item.get("activity_id"),
        "success_account_id": item.get("success_account_id"),
        "activity_type": item.get("activity_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by")
    }


def create_account(customer_alias: str, owner: str = "k_os_operator") -> dict[str, Any]:
    registry = ensure_registry()
    ctx = load_context(customer_alias)

    alias = ctx["customer_alias"]
    existing = next((a for a in registry.get("accounts", []) if a.get("customer_alias") == alias), None)

    if existing:
        return audit_report()

    onboarding = ctx.get("onboarding") or {}
    subscription = ctx.get("subscription") or {}
    license_item = ctx.get("license") or {}

    account_id = "csa_" + uuid.uuid4().hex[:12]

    account = {
        "success_account_id": account_id,
        "customer_alias": alias,
        "agent_id": ctx["agent_id"],
        "onboarding_id": onboarding.get("onboarding_id", ""),
        "subscription_id": subscription.get("subscription_id", ""),
        "license_id": license_item.get("license_id", ""),
        "health": "yellow",
        "risk_level": "medium",
        "next_action": "revisar onboarding e confirmar primeira entrega",
        "success_owner": owner or "k_os_operator",
        "created_at": now(),
        "updated_at": now()
    }

    registry["accounts"].append(account)

    delivery_id = "del_" + uuid.uuid4().hex[:12]
    registry["deliveries"].append({
        "delivery_id": delivery_id,
        "success_account_id": account_id,
        "customer_alias": alias,
        "title": "Primeira entrega operacional K-OS",
        "status": "planned",
        "priority": "medium",
        "due_date": "",
        "completion_review_required": True,
        "created_at": now()
    })

    default_tasks = [
        "Confirmar escopo de onboarding",
        "Validar permissões do agente",
        "Revisar pacote de proposta e assinatura",
        "Definir rotina de acompanhamento",
        "Registrar critério de sucesso do cliente"
    ]

    for title in default_tasks:
        registry["tasks"].append({
            "task_id": "tsk_" + uuid.uuid4().hex[:12],
            "delivery_id": delivery_id,
            "success_account_id": account_id,
            "customer_alias": alias,
            "title": title,
            "status": "todo",
            "owner": owner or "k_os_operator",
            "priority": "medium",
            "due_date": "",
            "created_at": now()
        })

    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "success_account_id": account_id,
        "activity_type": "success_account_created",
        "summary": "Conta de Customer Success criada localmente.",
        "created_at": now(),
        "created_by": "k_os_customer_success"
    })

    save_registry(registry)
    event("customer_success.account_created", {"success_account_id": account_id, "customer_alias": alias})
    return audit_report()


def create_demo() -> dict[str, Any]:
    return create_account("demo_customer", "k_os_operator")


def add_task(account_id: str, title: str, priority: str, owner: str, due_date: str) -> dict[str, Any]:
    registry = ensure_registry()
    account = next((a for a in registry.get("accounts", []) if a.get("success_account_id") == account_id), None)

    if not account:
        raise RuntimeError(f"Success account not found: {account_id}")

    task = {
        "task_id": "tsk_" + uuid.uuid4().hex[:12],
        "delivery_id": "",
        "success_account_id": account_id,
        "customer_alias": account.get("customer_alias"),
        "title": title,
        "status": "todo",
        "owner": owner or "k_os_operator",
        "priority": priority or "medium",
        "due_date": due_date or "",
        "created_at": now()
    }

    registry["tasks"].append(task)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "success_account_id": account_id,
        "activity_type": "task_created",
        "summary": f"Tarefa criada: {title}",
        "created_at": now(),
        "created_by": "operator"
    })

    save_registry(registry)
    event("customer_success.task_created", {"success_account_id": account_id, "task_id": task["task_id"]})
    return audit_report()


def set_task_status(task_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()
    allowed = set(policy.get("task_statuses", []))

    if status not in allowed:
        raise RuntimeError(f"Invalid task status: {status}")

    registry = ensure_registry()
    found = False

    for task in registry.get("tasks", []):
        if task.get("task_id") == task_id:
            task["status"] = status
            task["last_status_reason"] = reason or "manual_update"
            task["updated_at"] = now()

            if status == "done":
                task["completed_at"] = now()

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "success_account_id": task.get("success_account_id"),
                "activity_type": "task_status_changed",
                "summary": f"Tarefa {task_id} alterada para {status}.",
                "created_at": now(),
                "created_by": "operator"
            })

            found = True

    if not found:
        raise RuntimeError(f"Task not found: {task_id}")

    save_registry(registry)
    event("customer_success.task_status_changed", {"task_id": task_id, "status": status})
    return audit_report()


def set_health(account_id: str, health: str, risk_level: str, next_action: str) -> dict[str, Any]:
    policy = load_policy()

    if health not in set(policy.get("health_levels", [])):
        raise RuntimeError(f"Invalid health: {health}")

    if risk_level not in set(policy.get("risk_levels", [])):
        raise RuntimeError(f"Invalid risk level: {risk_level}")

    registry = ensure_registry()
    found = False

    for account in registry.get("accounts", []):
        if account.get("success_account_id") == account_id:
            account["health"] = health
            account["risk_level"] = risk_level
            account["next_action"] = next_action or account.get("next_action")
            account["updated_at"] = now()

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "success_account_id": account_id,
                "activity_type": "health_updated",
                "summary": f"Health={health}, risk={risk_level}.",
                "created_at": now(),
                "created_by": "operator"
            })

            found = True

    if not found:
        raise RuntimeError(f"Success account not found: {account_id}")

    save_registry(registry)
    event("customer_success.health_updated", {"success_account_id": account_id, "health": health, "risk_level": risk_level})
    return audit_report()


def compute_metrics(accounts: list[dict[str, Any]], deliveries: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> dict[str, Any]:
    health_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    delivery_counts: dict[str, int] = {}
    task_counts: dict[str, int] = {}

    for account in accounts:
        health = account.get("health", "unknown")
        risk = account.get("risk_level", "medium")
        health_counts[health] = health_counts.get(health, 0) + 1
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    for delivery in deliveries:
        status = delivery.get("status", "unknown")
        delivery_counts[status] = delivery_counts.get(status, 0) + 1

    for task in tasks:
        status = task.get("status", "unknown")
        task_counts[status] = task_counts.get(status, 0) + 1

    open_task_statuses = {"todo", "doing", "blocked", "waiting_customer", "review"}
    open_task_count = sum(1 for task in tasks if task.get("status") in open_task_statuses)

    high_risk_count = risk_counts.get("high", 0) + risk_counts.get("critical", 0)
    red_health_count = health_counts.get("red", 0)

    return {
        "account_count": len(accounts),
        "delivery_count": len(deliveries),
        "task_count": len(tasks),
        "open_task_count": open_task_count,
        "high_risk_count": high_risk_count,
        "red_health_count": red_health_count,
        "health_counts": health_counts,
        "risk_counts": risk_counts,
        "delivery_counts": delivery_counts,
        "task_counts": task_counts
    }


def health_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    accounts = report.get("accounts", [])
    tasks = report.get("tasks", [])

    risks = []
    for account in accounts:
        if account.get("health") == "red" or account.get("risk_level") in {"high", "critical"}:
            risks.append({
                "customer_alias": account.get("customer_alias"),
                "health": account.get("health"),
                "risk_level": account.get("risk_level"),
                "next_action": account.get("next_action"),
                "success_owner": account.get("success_owner")
            })

    snapshot = {
        "ok": True,
        "checkpoint": "031",
        "module": "k_os_customer_success_delivery_tracker",
        "status": "health_snapshot",
        "generated_at": now(),
        "metrics": report.get("metrics", {}),
        "risk_accounts": risks,
        "open_tasks": [item for item in tasks if item.get("status") in {"todo", "doing", "blocked", "waiting_customer", "review"}],
        "external_send_enabled": False,
        "automatic_message_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    HEALTH_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Customer Success Health Snapshot",
        "",
        f"- Generated at: {snapshot.get('generated_at')}",
        f"- Risk accounts: {len(risks)}",
        f"- Open tasks: {len(snapshot.get('open_tasks', []))}",
        f"- External send enabled: {snapshot.get('external_send_enabled')}",
        "",
        "## Risk accounts",
        ""
    ]

    if risks:
        for item in risks:
            lines.append(f"- {item.get('customer_alias')} | health={item.get('health')} | risk={item.get('risk_level')} | next={item.get('next_action')}")
    else:
        lines.append("- Nenhuma conta em risco alto registrada.")

    lines.extend(["", "## Open tasks", ""])

    if snapshot.get("open_tasks"):
        for item in snapshot.get("open_tasks", []):
            lines.append(f"- {item.get('customer_alias')} | {item.get('title')} | {item.get('status')} | owner={item.get('owner')}")
    else:
        lines.append("- Nenhuma tarefa aberta.")

    HEALTH_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    policy = load_policy()

    accounts = [safe_account(item) for item in registry.get("accounts", [])]
    deliveries = [safe_delivery(item) for item in registry.get("deliveries", [])]
    tasks = [safe_task(item) for item in registry.get("tasks", [])]
    activities = [safe_activity(item) for item in registry.get("activities", [])[-30:]]

    metrics = compute_metrics(accounts, deliveries, tasks)

    report = {
        "ok": True,
        "checkpoint": "031",
        "module": "k_os_customer_success_delivery_tracker",
        "status": "audit_generated",
        "generated_at": now(),
        "customer_success_registry_path": "local_secrets/k_os_customer_success/customer_success_registry.json",
        "customer_success_registry_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "accounts": accounts,
        "deliveries": deliveries,
        "tasks": tasks,
        "recent_activities": activities,
        "metrics": metrics,
        "required_gates_before_delivery_completion": policy.get("required_gates_before_delivery_completion", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "032 - K-Support Desk and Ticketing Core")
    }

    write_report(report)
    health_snapshot(report)
    event("customer_success.audit_generated", {"account_count": metrics["account_count"]})
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Customer Success and Delivery Tracker",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Registry committed: {report.get('customer_success_registry_committed')}",
        f"- External send enabled: {report.get('external_send_enabled')}",
        f"- Automatic message enabled: {report.get('automatic_message_enabled')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in report.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Accounts", ""])

    if report.get("accounts"):
        for item in report.get("accounts", []):
            lines.append(
                f"- {item.get('success_account_id')} | {item.get('customer_alias')} | health={item.get('health')} | "
                f"risk={item.get('risk_level')} | next={item.get('next_action')}"
            )
    else:
        lines.append("- Nenhuma conta Customer Success registrada.")

    lines.extend(["", "## Open Tasks", ""])

    open_tasks = [item for item in report.get("tasks", []) if item.get("status") in {"todo", "doing", "blocked", "waiting_customer", "review"}]

    if open_tasks:
        for item in open_tasks:
            lines.append(f"- {item.get('task_id')} | {item.get('customer_alias')} | {item.get('title')} | {item.get('status')}")
    else:
        lines.append("- Nenhuma tarefa aberta.")

    lines.extend(["", "## Required gates before delivery completion", ""])

    for gate in report.get("required_gates_before_delivery_completion", []):
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
    parser.add_argument("--mode", choices=["init", "create-demo", "create-account", "add-task", "set-task-status", "set-health", "audit", "show"], required=True)
    parser.add_argument("--customer-alias", default="")
    parser.add_argument("--owner", default="k_os_operator")
    parser.add_argument("--account-id", default="")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--due-date", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--health", default="yellow")
    parser.add_argument("--risk-level", default="medium")
    parser.add_argument("--next-action", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "create-account":
        if not args.customer_alias:
            raise SystemExit("Informe --customer-alias")
        result = create_account(args.customer_alias, args.owner)

    elif args.mode == "add-task":
        if not args.account_id:
            raise SystemExit("Informe --account-id")
        if not args.title:
            raise SystemExit("Informe --title")
        result = add_task(args.account_id, args.title, args.priority, args.owner, args.due_date)

    elif args.mode == "set-task-status":
        if not args.task_id:
            raise SystemExit("Informe --task-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = set_task_status(args.task_id, args.status, args.reason)

    elif args.mode == "set-health":
        if not args.account_id:
            raise SystemExit("Informe --account-id")
        result = set_health(args.account_id, args.health, args.risk_level, args.next_action)

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