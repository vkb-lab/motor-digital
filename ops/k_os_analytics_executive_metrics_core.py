# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "analytics" / "k_os_analytics_executive_metrics_policy.json"
ANALYTICS_DIR = ROOT / "local_secrets" / "k_os_analytics"
HISTORY_PATH = ANALYTICS_DIR / "analytics_history.json"

REPORT_DIR = ROOT / "reports" / "analytics"
MEMORY_DIR = ROOT / "memory" / "analytics"

LATEST_JSON = REPORT_DIR / "latest_executive_metrics_report.json"
LATEST_MD = REPORT_DIR / "latest_executive_metrics_report.md"
DASHBOARD_JSON = REPORT_DIR / "latest_executive_dashboard_snapshot.json"
DASHBOARD_MD = REPORT_DIR / "latest_executive_dashboard_snapshot.md"
HEALTH_JSON = REPORT_DIR / "latest_operational_health_snapshot.json"
HEALTH_MD = REPORT_DIR / "latest_operational_health_snapshot.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

DATA_SOURCES = {
    "crm": "reports/crm/latest_customer_registry_report.json",
    "billing": "reports/billing/latest_billing_subscription_report.json",
    "license": "reports/license/latest_license_gate_report.json",
    "sales": "reports/sales/latest_sales_pipeline_report.json",
    "proposals": "reports/proposals/latest_proposal_factory_report.json",
    "onboarding": "reports/onboarding/latest_onboarding_activation_report.json",
    "customer_success": "reports/customer_success/latest_customer_success_delivery_report.json",
    "support": "reports/support/latest_support_desk_report.json",
    "knowledge_base": "reports/knowledge_base/latest_knowledge_base_report.json",
    "product_feedback": "reports/product_feedback/latest_product_feedback_report.json",
    "roadmap": "reports/roadmap/latest_roadmap_release_report.json",
    "security": "reports/security/latest_security_firewall_report.json",
    "schema": "reports/schema/latest_schema_guard_report.json",
    "governance": "reports/governance/latest_agent_permission_matrix_report.json",
    "audit": "reports/audit/latest_audit_evidence_pack.json",
    "enterprise": "reports/enterprise/latest_enterprise_readiness_report.json",
    "incident": "reports/incident/latest_incident_readiness_report.json"
}

FOUNDATION_CLOSURES = {
    "015_security_firewall": "reports/security/k_os_015_closure_report.json",
    "016_schema_guard": "reports/schema/k_os_016_closure_report.json",
    "017_agent_permission_matrix": "reports/governance/k_os_017_closure_report.json",
    "018_vault_guard": "reports/vault/k_os_018_closure_report.json",
    "019_audit_evidence_pack": "reports/audit/k_os_019_closure_report.json",
    "020_mission_control": "reports/mission_control/k_os_020_closure_report.json",
    "021_risk_license": "reports/risk/k_os_021_closure_report.json",
    "022_external_sandbox": "reports/external_sandbox/k_os_022_closure_report.json",
    "023_enterprise_readiness": "reports/enterprise/k_os_023_closure_report.json",
    "024_incident_runbook": "reports/incident/k_os_024_closure_report.json",
    "025_legal_templates": "reports/legal/k_os_025_closure_report.json",
    "026_billing": "reports/billing/k_os_026_closure_report.json",
    "027_crm": "reports/crm/k_os_027_closure_report.json",
    "028_sales": "reports/sales/k_os_028_closure_report.json",
    "029_proposals": "reports/proposals/k_os_029_closure_report.json",
    "030_onboarding": "reports/onboarding/k_os_030_closure_report.json",
    "031_customer_success": "reports/customer_success/k_os_031_closure_report.json",
    "032_support": "reports/support/k_os_032_closure_report.json",
    "033_knowledge_base": "reports/knowledge_base/k_os_033_closure_report.json",
    "034_product_feedback": "reports/product_feedback/k_os_034_closure_report.json",
    "035_roadmap": "reports/roadmap/k_os_035_closure_report.json"
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
        raise RuntimeError("Analytics policy not found.")
    return data


def ensure_state() -> dict[str, Any]:
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not HISTORY_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_publish_enabled": False,
            "snapshots": []
        }
        write_json(HISTORY_PATH, data)

    state = read_json(HISTORY_PATH)
    if not state:
        raise RuntimeError("Could not load analytics state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(HISTORY_PATH, data)


def source_status() -> list[dict[str, Any]]:
    result = []
    for name, rel in DATA_SOURCES.items():
        path = ROOT / rel
        data = read_json(path)
        result.append({
            "name": name,
            "path": rel,
            "exists": path.exists(),
            "ok": bool(data and data.get("ok") is True),
            "status": data.get("status") if isinstance(data, dict) else "missing",
            "read_error": data.get("_read_error") if isinstance(data, dict) else ""
        })
    return result


def foundation_status() -> list[dict[str, Any]]:
    result = []
    for name, rel in FOUNDATION_CLOSURES.items():
        path = ROOT / rel
        data = read_json(path)
        result.append({
            "checkpoint": name,
            "path": rel,
            "exists": path.exists(),
            "ok": bool(data and data.get("ok") is True),
            "status": data.get("status") if isinstance(data, dict) else "missing"
        })
    return result


def get_data(name: str) -> dict[str, Any]:
    rel = DATA_SOURCES.get(name, "")
    if not rel:
        return {}
    return read_json(ROOT / rel) or {}


def num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def list_len(data: dict[str, Any], key: str) -> int:
    value = data.get(key, [])
    if isinstance(value, list):
        return len(value)
    return 0


def estimate_mrr_brl(billing: dict[str, Any], sales: dict[str, Any]) -> float:
    metrics = billing.get("metrics", {})
    for key in ["estimated_mrr_brl", "mrr_brl", "active_mrr_brl", "monthly_recurring_revenue_brl"]:
        if key in metrics:
            return round(num(metrics.get(key)), 2)

    total = 0.0
    for item in billing.get("subscriptions", []):
        status = item.get("status", "")
        if status in {"active", "trial"}:
            for key in ["mrr_brl", "monthly_price_brl", "amount_brl", "recurring_total", "plan_price_brl"]:
                if key in item:
                    total += num(item.get(key))
                    break

    if total > 0:
        return round(total, 2)

    sales_metrics = sales.get("metrics", {})
    return round(num(sales_metrics.get("weighted_forecast_brl", 0)), 2)


def weighted_pipeline_brl(sales: dict[str, Any]) -> float:
    metrics = sales.get("metrics", {})
    for key in ["weighted_forecast_brl", "weighted_pipeline_brl", "weighted_mrr_brl"]:
        if key in metrics:
            return round(num(metrics.get(key)), 2)

    total = 0.0
    for deal in sales.get("deals", []):
        amount = num(deal.get("estimated_mrr_brl", deal.get("estimated_value_brl", 0)))
        probability = num(deal.get("probability", deal.get("probability_percent", 0)))
        if probability > 1:
            probability = probability / 100
        total += amount * probability

    return round(total, 2)


def build_metrics() -> dict[str, Any]:
    crm = get_data("crm")
    billing = get_data("billing")
    license_data = get_data("license")
    sales = get_data("sales")
    proposals = get_data("proposals")
    onboarding = get_data("onboarding")
    success = get_data("customer_success")
    support = get_data("support")
    kb = get_data("knowledge_base")
    feedback = get_data("product_feedback")
    roadmap = get_data("roadmap")

    success_metrics = success.get("metrics", {})
    support_metrics = support.get("metrics", {})
    feedback_metrics = feedback.get("metrics", {})
    roadmap_metrics = roadmap.get("metrics", {})
    onboarding_metrics = onboarding.get("metrics", {})

    customer_count = list_len(crm, "customers")
    subscription_count = list_len(billing, "subscriptions")
    active_license_count = sum(1 for item in license_data.get("licenses", []) if item.get("status") == "active")
    deal_count = list_len(sales, "deals")
    proposal_count = list_len(proposals, "proposals")
    onboarding_case_count = list_len(onboarding, "cases")
    support_ticket_count = list_len(support, "tickets")
    feedback_count = list_len(feedback, "feedback_items")
    feature_count = list_len(feedback, "feature_requests")
    release_count = list_len(roadmap, "releases")

    open_task_count = int(num(success_metrics.get("open_task_count", 0)))
    open_ticket_count = int(num(support_metrics.get("open_ticket_count", 0)))
    high_risk_customer_count = int(num(success_metrics.get("high_risk_count", 0)))
    red_health_count = int(num(success_metrics.get("red_health_count", 0)))
    onboarding_blocked_count = int(num(onboarding_metrics.get("blocked_count", 0)))
    critical_ticket_count = int(num(support_metrics.get("critical_ticket_count", 0)))
    critical_feedback_count = int(num(feedback_metrics.get("critical_feedback_count", 0)))
    roadmap_candidate_count = int(num(feedback_metrics.get("roadmap_candidate_count", 0)))

    foundation = foundation_status()
    ok_foundation = sum(1 for item in foundation if item.get("ok"))
    total_foundation = len(foundation)
    foundation_score = round((ok_foundation / total_foundation) * 100, 2) if total_foundation else 0.0

    return {
        "customer_count": customer_count,
        "subscription_count": subscription_count,
        "active_license_count": active_license_count,
        "estimated_mrr_brl": estimate_mrr_brl(billing, sales),
        "deal_count": deal_count,
        "weighted_pipeline_brl": weighted_pipeline_brl(sales),
        "proposal_count": proposal_count,
        "onboarding_case_count": onboarding_case_count,
        "onboarding_blocked_count": onboarding_blocked_count,
        "open_task_count": open_task_count,
        "open_ticket_count": open_ticket_count,
        "support_ticket_count": support_ticket_count,
        "critical_ticket_count": critical_ticket_count,
        "high_risk_customer_count": high_risk_customer_count,
        "red_health_count": red_health_count,
        "feedback_count": feedback_count,
        "critical_feedback_count": critical_feedback_count,
        "feature_count": feature_count,
        "roadmap_candidate_count": roadmap_candidate_count,
        "roadmap_release_count": release_count,
        "knowledge_article_count": list_len(kb, "articles"),
        "knowledge_playbook_count": list_len(kb, "playbooks"),
        "foundation_control_ok_count": ok_foundation,
        "foundation_control_total_count": total_foundation,
        "foundation_control_score": foundation_score
    }


def classify_operational_health(metrics: dict[str, Any], sources: list[dict[str, Any]]) -> dict[str, Any]:
    blockers = []
    warnings = []

    missing_sources = [item["name"] for item in sources if not item.get("exists")]
    failed_sources = [item["name"] for item in sources if item.get("exists") and not item.get("ok")]

    if missing_sources:
        warnings.append("some_source_reports_missing")

    if failed_sources:
        warnings.append("some_source_reports_not_ok")

    if metrics.get("foundation_control_score", 0) < 90:
        blockers.append("foundation_control_score_below_90")

    if metrics.get("critical_ticket_count", 0) > 0:
        warnings.append("critical_support_tickets_present")

    if metrics.get("high_risk_customer_count", 0) > 0:
        warnings.append("high_risk_customers_present")

    if metrics.get("onboarding_blocked_count", 0) > 0:
        warnings.append("blocked_onboarding_cases_present")

    if blockers:
        level = "blocked"
    elif warnings:
        level = "attention"
    else:
        level = "healthy"

    return {
        "health_level": level,
        "blockers": blockers,
        "warnings": warnings,
        "missing_sources": missing_sources,
        "failed_sources": failed_sources
    }


def executive_report() -> dict[str, Any]:
    ensure_state()
    policy = load_policy()
    sources = source_status()
    foundation = foundation_status()
    metrics = build_metrics()
    health = classify_operational_health(metrics, sources)

    report = {
        "ok": True,
        "checkpoint": "036",
        "module": "k_os_analytics_executive_metrics_core",
        "status": "audit_generated",
        "generated_at": now(),
        "analytics_history_path": "local_secrets/k_os_analytics/analytics_history.json",
        "analytics_history_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "executive_dashboard_sanitized_only": True,
        "financial_numbers_are_operational_estimates": True,
        "metrics": metrics,
        "operational_health": health,
        "data_sources": sources,
        "foundation_controls": foundation,
        "required_gates_before_external_metric_export": policy.get("required_gates_before_external_metric_export", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "037 - K-Executive Cockpit Consolidation Layer")
    }

    write_report(report)
    write_dashboard(report)
    write_health(report)
    append_history(report)
    event("analytics.audit_generated", {
        "health_level": health.get("health_level"),
        "foundation_score": metrics.get("foundation_control_score")
    })
    return report


def append_history(report: dict[str, Any]) -> None:
    state = ensure_state()
    snapshot = {
        "created_at": report.get("generated_at"),
        "health_level": report.get("operational_health", {}).get("health_level"),
        "metrics": report.get("metrics", {})
    }
    state.setdefault("snapshots", []).append(snapshot)
    state["snapshots"] = state["snapshots"][-100:]
    save_state(state)


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    metrics = report.get("metrics", {})
    health = report.get("operational_health", {})

    lines = [
        "# K-OS Analytics and Executive Metrics Core",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Health: {health.get('health_level')}",
        f"- Sanitized only: {report.get('sanitized_reports_only')}",
        f"- External publish enabled: {report.get('external_publish_enabled')}",
        "",
        "## Executive KPIs",
        ""
    ]

    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Blockers", ""])

    if health.get("blockers"):
        for item in health.get("blockers", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker executivo registrado.")

    lines.extend(["", "## Warnings", ""])

    if health.get("warnings"):
        for item in health.get("warnings", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum warning executivo registrado.")

    lines.extend(["", "## Required gates before external metric export", ""])

    for gate in report.get("required_gates_before_external_metric_export", []):
        lines.append(f"- {gate}")

    lines.extend(["", "## Next checkpoint", "", f"- {report.get('next_checkpoint')}"])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def write_dashboard(report: dict[str, Any]) -> dict[str, Any]:
    metrics = report.get("metrics", {})
    health = report.get("operational_health", {})

    dashboard = {
        "ok": True,
        "checkpoint": "036",
        "module": "k_os_analytics_executive_metrics_core",
        "status": "executive_dashboard_snapshot",
        "generated_at": now(),
        "health_level": health.get("health_level"),
        "top_kpis": {
            "customers": metrics.get("customer_count", 0),
            "subscriptions": metrics.get("subscription_count", 0),
            "estimated_mrr_brl": metrics.get("estimated_mrr_brl", 0),
            "weighted_pipeline_brl": metrics.get("weighted_pipeline_brl", 0),
            "open_tickets": metrics.get("open_ticket_count", 0),
            "open_tasks": metrics.get("open_task_count", 0),
            "high_risk_customers": metrics.get("high_risk_customer_count", 0),
            "features": metrics.get("feature_count", 0),
            "roadmap_releases": metrics.get("roadmap_release_count", 0),
            "foundation_score": metrics.get("foundation_control_score", 0)
        },
        "external_publish_enabled": False,
        "customer_identifiable_data_included": False,
        "manual_approval_required": True,
        "next_checkpoint": report.get("next_checkpoint")
    }

    DASHBOARD_JSON.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Executive Dashboard Snapshot",
        "",
        f"- Generated at: {dashboard.get('generated_at')}",
        f"- Health: {dashboard.get('health_level')}",
        f"- External publish enabled: {dashboard.get('external_publish_enabled')}",
        f"- Customer identifiable data included: {dashboard.get('customer_identifiable_data_included')}",
        "",
        "## Top KPIs",
        ""
    ]

    for key, value in dashboard.get("top_kpis", {}).items():
        lines.append(f"- {key}: {value}")

    DASHBOARD_MD.write_text("\n".join(lines), encoding="utf-8")
    return dashboard


def write_health(report: dict[str, Any]) -> dict[str, Any]:
    health = report.get("operational_health", {})
    metrics = report.get("metrics", {})

    snapshot = {
        "ok": True,
        "checkpoint": "036",
        "module": "k_os_analytics_executive_metrics_core",
        "status": "operational_health_snapshot",
        "generated_at": now(),
        "health_level": health.get("health_level"),
        "blockers": health.get("blockers", []),
        "warnings": health.get("warnings", []),
        "foundation_control_score": metrics.get("foundation_control_score", 0),
        "critical_ticket_count": metrics.get("critical_ticket_count", 0),
        "high_risk_customer_count": metrics.get("high_risk_customer_count", 0),
        "onboarding_blocked_count": metrics.get("onboarding_blocked_count", 0),
        "external_publish_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    HEALTH_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Operational Health Snapshot",
        "",
        f"- Generated at: {snapshot.get('generated_at')}",
        f"- Health: {snapshot.get('health_level')}",
        f"- Foundation score: {snapshot.get('foundation_control_score')}",
        f"- Critical tickets: {snapshot.get('critical_ticket_count')}",
        f"- High risk customers: {snapshot.get('high_risk_customer_count')}",
        f"- Blocked onboarding: {snapshot.get('onboarding_blocked_count')}",
        "",
        "## Blockers",
        ""
    ]

    if snapshot.get("blockers"):
        for item in snapshot.get("blockers", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker operacional.")

    lines.extend(["", "## Warnings", ""])

    if snapshot.get("warnings"):
        for item in snapshot.get("warnings", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum warning operacional.")

    HEALTH_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def show_latest() -> int:
    if LATEST_JSON.exists():
        print(LATEST_JSON.read_text(encoding="utf-8-sig"))
    else:
        print("{}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "audit", "dashboard", "health", "show"], required=True)
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = executive_report()

    elif args.mode == "audit":
        result = executive_report()

    elif args.mode == "dashboard":
        report = executive_report()
        result = write_dashboard(report)

    elif args.mode == "health":
        report = executive_report()
        result = write_health(report)

    elif args.mode == "show":
        return show_latest()

    else:
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())