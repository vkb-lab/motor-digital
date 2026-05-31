# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "billing" / "k_os_billing_subscription_policy.json"
LEDGER_DIR = ROOT / "local_secrets" / "k_os_billing"
LEDGER_PATH = LEDGER_DIR / "billing_ledger.json"
REPORT_DIR = ROOT / "reports" / "billing"
MEMORY_DIR = ROOT / "memory" / "billing"
LATEST_JSON = REPORT_DIR / "latest_billing_subscription_report.json"
LATEST_MD = REPORT_DIR / "latest_billing_subscription_report.md"
RECONCILE_JSON = REPORT_DIR / "latest_billing_reconciliation_dry_run.json"
RECONCILE_MD = REPORT_DIR / "latest_billing_reconciliation_dry_run.md"
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
        raise RuntimeError("Billing policy not found.")
    return data


def ensure_ledger() -> dict[str, Any]:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not LEDGER_PATH.exists():
        ledger = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "real_payment_processor_enabled": False,
            "real_charge_enabled": False,
            "currency_default": "BRL",
            "customers": [],
            "subscriptions": [],
            "payment_events": []
        }
        write_json(LEDGER_PATH, ledger)

    data = read_json(LEDGER_PATH)
    if not data:
        raise RuntimeError("Could not load billing ledger.")
    return data


def save_ledger(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(LEDGER_PATH, data)


def plan_by_id(plan_id: str) -> dict[str, Any]:
    policy = load_policy()
    for plan in policy.get("plans", []):
        if plan.get("plan_id") == plan_id:
            return plan
    raise RuntimeError(f"Plan not found: {plan_id}")


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def safe_customer(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "customer_id": item.get("customer_id"),
        "customer_alias": item.get("customer_alias"),
        "status": item.get("status"),
        "created_at": item.get("created_at"),
        "commercial_owner": item.get("commercial_owner")
    }


def safe_subscription(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "subscription_id": item.get("subscription_id"),
        "customer_alias": item.get("customer_alias"),
        "agent_id": item.get("agent_id"),
        "plan_id": item.get("plan_id"),
        "status": item.get("status"),
        "currency": item.get("currency"),
        "amount": item.get("amount"),
        "billing_cycle": item.get("billing_cycle"),
        "started_at": item.get("started_at"),
        "expires_at": item.get("expires_at"),
        "payment_status": item.get("payment_status"),
        "license_gate_status": item.get("license_gate_status"),
        "approval_required": item.get("approval_required"),
        "last_status_reason": item.get("last_status_reason", "")
    }


def create_demo() -> dict[str, Any]:
    ledger = ensure_ledger()
    plan = plan_by_id("trial_7d")

    customer_alias = "demo_customer"
    customer_exists = any(c.get("customer_alias") == customer_alias for c in ledger.get("customers", []))

    if not customer_exists:
        ledger["customers"].append({
            "customer_id": "cus_" + uuid.uuid4().hex[:12],
            "customer_alias": customer_alias,
            "status": "demo",
            "created_at": now(),
            "commercial_owner": "k_os_operator",
            "notes": "Demo local. Dados reais nao devem ser registrados aqui sem politica comercial."
        })

    active_demo = [
        s for s in ledger.get("subscriptions", [])
        if s.get("customer_alias") == customer_alias and s.get("agent_id") == "marketplace_ia_agent"
    ]

    if not active_demo:
        start = now_dt()
        expires = start + timedelta(days=int(plan.get("default_days", 7)))

        ledger["subscriptions"].append({
            "subscription_id": "sub_" + uuid.uuid4().hex[:12],
            "customer_alias": customer_alias,
            "agent_id": "marketplace_ia_agent",
            "plan_id": plan["plan_id"],
            "status": "trial",
            "currency": "BRL",
            "amount": float(plan.get("price_brl", 0.0)),
            "billing_cycle": plan.get("billing_cycle", "trial"),
            "started_at": start.isoformat(),
            "expires_at": expires.isoformat(),
            "payment_status": "not_required_trial",
            "license_gate_status": "requires_license_gate_validation",
            "commercial_owner": "k_os_operator",
            "approval_required": False,
            "created_at": now(),
            "last_status_reason": "demo_created"
        })

        ledger["payment_events"].append({
            "payment_event_id": "payevt_" + uuid.uuid4().hex[:12],
            "subscription_id": ledger["subscriptions"][-1]["subscription_id"],
            "event_type": "trial_started",
            "amount": 0.0,
            "currency": "BRL",
            "manual": True,
            "real_charge_performed": False,
            "created_at": now()
        })

    save_ledger(ledger)
    event("billing.demo_created", {"customer_alias": customer_alias})
    return audit_report()


def set_status(subscription_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()
    allowed = set(policy.get("subscription_statuses", []))

    if status not in allowed:
        raise RuntimeError(f"Invalid status: {status}")

    ledger = ensure_ledger()
    found = False

    for item in ledger.get("subscriptions", []):
        if item.get("subscription_id") == subscription_id:
            item["status"] = status
            item["last_status_reason"] = reason or "manual_update"
            item["status_updated_at"] = now()
            found = True

            ledger["payment_events"].append({
                "payment_event_id": "payevt_" + uuid.uuid4().hex[:12],
                "subscription_id": subscription_id,
                "event_type": "status_changed",
                "new_status": status,
                "reason": reason or "manual_update",
                "manual": True,
                "real_charge_performed": False,
                "created_at": now()
            })

    if not found:
        raise RuntimeError(f"Subscription not found: {subscription_id}")

    save_ledger(ledger)
    event("billing.status_changed", {"subscription_id": subscription_id, "status": status})
    return audit_report()


def payment_status(subscription: dict[str, Any]) -> str:
    status = subscription.get("status")
    expires_at = parse_dt(subscription.get("expires_at", ""))

    if status in {"cancelled", "suspended", "expired", "past_due"}:
        return status

    if expires_at and expires_at < now_dt():
        return "expired"

    return subscription.get("payment_status", "unknown")


def compute_metrics(subscriptions: list[dict[str, Any]]) -> dict[str, Any]:
    active = []
    trial = []
    past_due = []
    suspended = []
    expired = []

    for item in subscriptions:
        effective = payment_status(item)

        if item.get("status") == "active":
            active.append(item)
        if item.get("status") == "trial":
            trial.append(item)
        if effective == "past_due":
            past_due.append(item)
        if effective == "suspended":
            suspended.append(item)
        if effective == "expired":
            expired.append(item)

    mrr = 0.0
    for item in active:
        if item.get("billing_cycle") == "monthly":
            mrr += float(item.get("amount", 0.0) or 0.0)

    return {
        "subscription_count": len(subscriptions),
        "active_count": len(active),
        "trial_count": len(trial),
        "past_due_count": len(past_due),
        "suspended_count": len(suspended),
        "expired_count": len(expired),
        "mrr_estimate_brl": round(mrr, 2),
        "arr_estimate_brl": round(mrr * 12, 2)
    }


def audit_report() -> dict[str, Any]:
    ledger = ensure_ledger()
    policy = load_policy()

    safe_customers = [safe_customer(item) for item in ledger.get("customers", [])]
    safe_subscriptions = [safe_subscription(item) for item in ledger.get("subscriptions", [])]
    metrics = compute_metrics(ledger.get("subscriptions", []))

    report = {
        "ok": True,
        "checkpoint": "026",
        "module": "k_os_billing_subscription_ledger",
        "status": "audit_generated",
        "generated_at": now(),
        "ledger_path": "local_secrets/k_os_billing/billing_ledger.json",
        "ledger_committed": False,
        "real_payment_processor_enabled": False,
        "real_charge_enabled": False,
        "invoice_generation_enabled": False,
        "tax_document_generation_enabled": False,
        "manual_payment_status_only": True,
        "customers": safe_customers,
        "subscriptions": safe_subscriptions,
        "metrics": metrics,
        "required_gates_before_paid_activation": policy.get("required_gates_before_paid_activation", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "safe_suspension_meaning": policy.get("commercial_policy", {}).get("safe_suspension_meaning"),
        "silent_customer_data_wipe_allowed": False,
        "audit_log_deletion_allowed": False,
        "next_checkpoint": policy.get("next_checkpoint", "027 - K-Customer Registry and CRM Core")
    }

    write_report(report)
    event("billing.audit_generated", {"subscription_count": metrics["subscription_count"]})
    return report


def reconcile_dry_run() -> dict[str, Any]:
    ledger = ensure_ledger()
    policy = load_policy()

    actions = []

    for sub in ledger.get("subscriptions", []):
        effective = payment_status(sub)

        if effective == "expired" and sub.get("status") not in {"expired", "cancelled", "suspended"}:
            actions.append({
                "action": "mark_subscription_expired",
                "subscription_id": sub.get("subscription_id"),
                "customer_alias": sub.get("customer_alias"),
                "agent_id": sub.get("agent_id"),
                "reason": "expires_at_is_past",
                "dry_run": True
            })
            actions.append({
                "action": "review_license_suspension",
                "subscription_id": sub.get("subscription_id"),
                "customer_alias": sub.get("customer_alias"),
                "agent_id": sub.get("agent_id"),
                "reason": "subscription_expired",
                "dry_run": True
            })

        if sub.get("status") == "past_due":
            actions.append({
                "action": "block_new_activation",
                "subscription_id": sub.get("subscription_id"),
                "customer_alias": sub.get("customer_alias"),
                "agent_id": sub.get("agent_id"),
                "reason": "past_due",
                "dry_run": True
            })

    result = {
        "ok": True,
        "checkpoint": "026",
        "module": "k_os_billing_subscription_ledger",
        "status": "reconciliation_dry_run",
        "generated_at": now(),
        "actions_count": len(actions),
        "actions": actions,
        "real_charge_performed": False,
        "license_revocation_performed": False,
        "customer_data_deleted": False,
        "audit_log_deleted": False,
        "manual_approval_required_before_enforcement": True,
        "safe_suspension_meaning": policy.get("commercial_policy", {}).get("safe_suspension_meaning"),
        "next_checkpoint": policy.get("next_checkpoint", "027 - K-Customer Registry and CRM Core")
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RECONCILE_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Billing Reconciliation Dry Run",
        "",
        f"- Status: {result.get('status')}",
        f"- Actions: {result.get('actions_count')}",
        f"- Real charge performed: {result.get('real_charge_performed')}",
        f"- License revocation performed: {result.get('license_revocation_performed')}",
        f"- Customer data deleted: {result.get('customer_data_deleted')}",
        f"- Generated at: {result.get('generated_at')}",
        "",
        "## Actions",
        ""
    ]

    if actions:
        for item in actions:
            lines.append(f"- {item.get('action')} | {item.get('customer_alias')} | {item.get('agent_id')} | {item.get('reason')} | dry_run={item.get('dry_run')}")
    else:
        lines.append("- Nenhuma acao de reconciliacao necessaria.")

    RECONCILE_MD.write_text("\n".join(lines), encoding="utf-8")

    event("billing.reconciliation_dry_run", {"actions_count": len(actions)})
    return result


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Billing and Subscription Ledger",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Ledger committed: {report.get('ledger_committed')}",
        f"- Real charge enabled: {report.get('real_charge_enabled')}",
        f"- Manual payment status only: {report.get('manual_payment_status_only')}",
        "",
        "## Metrics",
        ""
    ]

    metrics = report.get("metrics", {})
    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "## Subscriptions",
        ""
    ])

    subs = report.get("subscriptions", [])
    if subs:
        for item in subs:
            lines.append(f"- {item.get('subscription_id')} | {item.get('customer_alias')} | {item.get('agent_id')} | {item.get('plan_id')} | {item.get('status')}")
    else:
        lines.append("- Nenhuma assinatura registrada.")

    lines.extend([
        "",
        "## Required gates before paid activation",
        ""
    ])

    for gate in report.get("required_gates_before_paid_activation", []):
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "create-demo", "audit", "reconcile-dry-run", "set-status", "show"], required=True)
    parser.add_argument("--subscription-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_ledger()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "audit":
        result = audit_report()

    elif args.mode == "reconcile-dry-run":
        result = reconcile_dry_run()

    elif args.mode == "set-status":
        if not args.subscription_id:
            raise SystemExit("Informe --subscription-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = set_status(args.subscription_id, args.status, args.reason)

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