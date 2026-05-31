# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "cockpit" / "k_os_executive_cockpit_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_cockpit"
STATE_PATH = STATE_DIR / "cockpit_state.json"

REPORT_DIR = ROOT / "reports" / "cockpit"
MEMORY_DIR = ROOT / "memory" / "cockpit"

LATEST_JSON = REPORT_DIR / "latest_executive_cockpit_report.json"
LATEST_MD = REPORT_DIR / "latest_executive_cockpit_report.md"
NAV_JSON = REPORT_DIR / "latest_cockpit_navigation_map.json"
NAV_MD = REPORT_DIR / "latest_cockpit_navigation_map.md"
HEALTH_JSON = REPORT_DIR / "latest_cockpit_health_snapshot.json"
HEALTH_MD = REPORT_DIR / "latest_cockpit_health_snapshot.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

ANALYTICS_REPORT = ROOT / "reports" / "analytics" / "latest_executive_metrics_report.json"
ANALYTICS_DASHBOARD = ROOT / "reports" / "analytics" / "latest_executive_dashboard_snapshot.json"
ANALYTICS_HEALTH = ROOT / "reports" / "analytics" / "latest_operational_health_snapshot.json"

MODULES = [
    {"checkpoint": "015", "domain": "security", "name": "Security Firewall", "page": "pages/915_K_OS_Security_Firewall.py", "report": "reports/security/latest_security_firewall_report.json", "closure": "reports/security/k_os_015_closure_report.json"},
    {"checkpoint": "016", "domain": "security", "name": "Schema Guard", "page": "pages/916_K_OS_Schema_Guard.py", "report": "reports/schema/latest_schema_guard_report.json", "closure": "reports/schema/k_os_016_closure_report.json"},
    {"checkpoint": "017", "domain": "governance", "name": "Agent Permission Matrix", "page": "pages/917_K_OS_Agent_Permission_Matrix.py", "report": "reports/governance/latest_agent_permission_matrix_report.json", "closure": "reports/governance/k_os_017_closure_report.json"},
    {"checkpoint": "018", "domain": "security", "name": "Vault Guard", "page": "pages/918_K_OS_Vault_Guard.py", "report": "reports/vault/latest_vault_guard_report.json", "closure": "reports/vault/k_os_018_closure_report.json"},
    {"checkpoint": "019", "domain": "audit", "name": "Audit Evidence Pack", "page": "pages/919_K_OS_Audit_Evidence_Pack.py", "report": "reports/audit/latest_audit_evidence_pack.json", "closure": "reports/audit/k_os_019_closure_report.json"},
    {"checkpoint": "020", "domain": "foundation", "name": "Mission Control 2.0", "page": "pages/920_K_OS_Mission_Control_2.py", "report": "reports/mission_control/latest_mission_control_status.json", "closure": "reports/mission_control/k_os_020_closure_report.json"},
    {"checkpoint": "021", "domain": "security", "name": "AI Risk Classifier + License Gate", "page": "pages/921_K_OS_AI_Risk_Classifier.py", "report": "reports/risk/latest_ai_risk_classifier_report.json", "closure": "reports/risk/k_os_021_closure_report.json"},
    {"checkpoint": "022", "domain": "security", "name": "External API Sandbox", "page": "pages/922_K_OS_External_API_Sandbox.py", "report": "reports/external_sandbox/latest_external_api_sandbox_report.json", "closure": "reports/external_sandbox/k_os_022_closure_report.json"},
    {"checkpoint": "023", "domain": "audit", "name": "Enterprise Readiness Report", "page": "pages/923_K_OS_Enterprise_Readiness_Report.py", "report": "reports/enterprise/latest_enterprise_readiness_report.json", "closure": "reports/enterprise/k_os_023_closure_report.json"},
    {"checkpoint": "024", "domain": "security", "name": "Incident Response and Rollback Runbook", "page": "pages/924_K_OS_Incident_Response_Rollback_Runbook.py", "report": "reports/incident/latest_incident_readiness_report.json", "closure": "reports/incident/k_os_024_closure_report.json"},
    {"checkpoint": "025", "domain": "commercial", "name": "Legal Commercial License Templates", "page": "pages/925_K_OS_Legal_Commercial_License_Templates.py", "report": "reports/legal/latest_legal_commercial_templates_report.json", "closure": "reports/legal/k_os_025_closure_report.json"},
    {"checkpoint": "026", "domain": "commercial", "name": "Billing and Subscription Ledger", "page": "pages/926_K_OS_Billing_Subscription_Ledger.py", "report": "reports/billing/latest_billing_subscription_report.json", "closure": "reports/billing/k_os_026_closure_report.json"},
    {"checkpoint": "027", "domain": "commercial", "name": "Customer Registry and CRM Core", "page": "pages/927_K_OS_Customer_Registry_CRM_Core.py", "report": "reports/crm/latest_customer_registry_report.json", "closure": "reports/crm/k_os_027_closure_report.json"},
    {"checkpoint": "028", "domain": "commercial", "name": "Sales Pipeline and Deal Desk", "page": "pages/928_K_OS_Sales_Pipeline_Deal_Desk.py", "report": "reports/sales/latest_sales_pipeline_report.json", "closure": "reports/sales/k_os_028_closure_report.json"},
    {"checkpoint": "029", "domain": "commercial", "name": "Proposal Factory and Quote Builder", "page": "pages/929_K_OS_Proposal_Factory_Quote_Builder.py", "report": "reports/proposals/latest_proposal_factory_report.json", "closure": "reports/proposals/k_os_029_closure_report.json"},
    {"checkpoint": "030", "domain": "customer_ops", "name": "Onboarding and Activation Gate", "page": "pages/930_K_OS_Onboarding_Activation_Gate.py", "report": "reports/onboarding/latest_onboarding_activation_report.json", "closure": "reports/onboarding/k_os_030_closure_report.json"},
    {"checkpoint": "031", "domain": "customer_ops", "name": "Customer Success and Delivery Tracker", "page": "pages/931_K_OS_Customer_Success_Delivery_Tracker.py", "report": "reports/customer_success/latest_customer_success_delivery_report.json", "closure": "reports/customer_success/k_os_031_closure_report.json"},
    {"checkpoint": "032", "domain": "support", "name": "Support Desk and Ticketing Core", "page": "pages/932_K_OS_Support_Desk_Ticketing_Core.py", "report": "reports/support/latest_support_desk_report.json", "closure": "reports/support/k_os_032_closure_report.json"},
    {"checkpoint": "033", "domain": "support", "name": "Knowledge Base and Support Playbooks", "page": "pages/933_K_OS_Knowledge_Base_Support_Playbooks.py", "report": "reports/knowledge_base/latest_knowledge_base_report.json", "closure": "reports/knowledge_base/k_os_033_closure_report.json"},
    {"checkpoint": "034", "domain": "product", "name": "Product Feedback and Feature Request Core", "page": "pages/934_K_OS_Product_Feedback_Feature_Request_Core.py", "report": "reports/product_feedback/latest_product_feedback_report.json", "closure": "reports/product_feedback/k_os_034_closure_report.json"},
    {"checkpoint": "035", "domain": "product", "name": "Roadmap Planner and Release Notes Core", "page": "pages/935_K_OS_Roadmap_Planner_Release_Notes_Core.py", "report": "reports/roadmap/latest_roadmap_release_report.json", "closure": "reports/roadmap/k_os_035_closure_report.json"},
    {"checkpoint": "036", "domain": "analytics", "name": "Analytics and Executive Metrics Core", "page": "pages/936_K_OS_Analytics_Executive_Metrics_Core.py", "report": "reports/analytics/latest_executive_metrics_report.json", "closure": "reports/analytics/k_os_036_closure_report.json"}
]


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
        raise RuntimeError("Cockpit policy not found.")
    return data


def ensure_state() -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not STATE_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_publish_enabled": False,
            "layout": {
                "default_view": "executive",
                "show_security": True,
                "show_commercial": True,
                "show_product": True,
                "show_support": True,
                "show_analytics": True
            },
            "snapshots": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load cockpit state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def module_index() -> list[dict[str, Any]]:
    result = []

    for item in MODULES:
        page_path = ROOT / item["page"]
        report_path = ROOT / item["report"]
        closure_path = ROOT / item["closure"]

        report = read_json(report_path)
        closure = read_json(closure_path)

        result.append({
            "checkpoint": item["checkpoint"],
            "domain": item["domain"],
            "name": item["name"],
            "page": item["page"],
            "report": item["report"],
            "closure": item["closure"],
            "page_exists": page_path.exists(),
            "report_exists": report_path.exists(),
            "closure_exists": closure_path.exists(),
            "report_ok": bool(report and report.get("ok") is True),
            "closure_ok": bool(closure and closure.get("ok") is True),
            "report_status": report.get("status") if isinstance(report, dict) else "missing",
            "closure_status": closure.get("status") if isinstance(closure, dict) else "missing"
        })

    return result


def analytics_snapshot() -> dict[str, Any]:
    report = read_json(ANALYTICS_REPORT) or {}
    dashboard = read_json(ANALYTICS_DASHBOARD) or {}
    health = read_json(ANALYTICS_HEALTH) or {}

    return {
        "metrics": report.get("metrics", {}),
        "operational_health": report.get("operational_health", {}),
        "dashboard": dashboard,
        "health_snapshot": health,
        "analytics_report_exists": ANALYTICS_REPORT.exists(),
        "dashboard_exists": ANALYTICS_DASHBOARD.exists(),
        "health_exists": ANALYTICS_HEALTH.exists()
    }


def compute_cockpit_health(modules: list[dict[str, Any]], analytics: dict[str, Any]) -> dict[str, Any]:
    missing_pages = [item for item in modules if not item.get("page_exists")]
    missing_reports = [item for item in modules if not item.get("report_exists")]
    missing_closures = [item for item in modules if not item.get("closure_exists")]
    failed_reports = [item for item in modules if item.get("report_exists") and not item.get("report_ok")]
    failed_closures = [item for item in modules if item.get("closure_exists") and not item.get("closure_ok")]

    blockers = []
    warnings = []

    if missing_pages:
        blockers.append("module_pages_missing")

    if missing_closures:
        blockers.append("checkpoint_closures_missing")

    if failed_closures:
        warnings.append("some_closure_reports_not_ok")

    if missing_reports:
        warnings.append("some_latest_reports_missing")

    if failed_reports:
        warnings.append("some_latest_reports_not_ok")

    analytics_health = analytics.get("operational_health", {})
    if analytics_health.get("health_level") == "blocked":
        blockers.append("analytics_health_blocked")
    elif analytics_health.get("health_level") == "attention":
        warnings.append("analytics_health_attention")

    if blockers:
        level = "blocked"
    elif warnings:
        level = "attention"
    else:
        level = "healthy"

    total = len(modules)
    complete = sum(1 for item in modules if item.get("page_exists") and item.get("closure_ok"))
    completion_score = round((complete / total) * 100, 2) if total else 0.0

    return {
        "health_level": level,
        "module_total": total,
        "module_complete_count": complete,
        "completion_score": completion_score,
        "blockers": blockers,
        "warnings": warnings,
        "missing_pages": [{"checkpoint": i["checkpoint"], "name": i["name"], "path": i["page"]} for i in missing_pages],
        "missing_reports": [{"checkpoint": i["checkpoint"], "name": i["name"], "path": i["report"]} for i in missing_reports],
        "missing_closures": [{"checkpoint": i["checkpoint"], "name": i["name"], "path": i["closure"]} for i in missing_closures],
        "failed_reports": [{"checkpoint": i["checkpoint"], "name": i["name"], "status": i["report_status"]} for i in failed_reports],
        "failed_closures": [{"checkpoint": i["checkpoint"], "name": i["name"], "status": i["closure_status"]} for i in failed_closures]
    }


def domain_summary(modules: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for item in modules:
        domain = item.get("domain", "unknown")
        if domain not in result:
            result[domain] = {
                "module_count": 0,
                "page_ok": 0,
                "report_ok": 0,
                "closure_ok": 0
            }

        result[domain]["module_count"] += 1
        result[domain]["page_ok"] += 1 if item.get("page_exists") else 0
        result[domain]["report_ok"] += 1 if item.get("report_ok") else 0
        result[domain]["closure_ok"] += 1 if item.get("closure_ok") else 0

    return result


def write_navigation(modules: list[dict[str, Any]]) -> dict[str, Any]:
    nav = {
        "ok": True,
        "checkpoint": "037",
        "module": "k_os_executive_cockpit_consolidation_layer",
        "status": "navigation_map_generated",
        "generated_at": now(),
        "modules": modules,
        "external_publish_enabled": False,
        "customer_identifiable_data_included": False,
        "streamlit_entrypoint": "pages/937_K_OS_Executive_Cockpit_Consolidation_Layer.py"
    }

    NAV_JSON.write_text(json.dumps(nav, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Cockpit Navigation Map",
        "",
        f"- Generated at: {nav.get('generated_at')}",
        f"- External publish enabled: {nav.get('external_publish_enabled')}",
        f"- Entrypoint: {nav.get('streamlit_entrypoint')}",
        "",
        "## Modules",
        ""
    ]

    for item in modules:
        lines.append(
            f"- {item.get('checkpoint')} | {item.get('domain')} | {item.get('name')} | "
            f"page={item.get('page_exists')} | report={item.get('report_ok')} | closure={item.get('closure_ok')}"
        )

    NAV_MD.write_text("\n".join(lines), encoding="utf-8")
    return nav


def write_health(snapshot: dict[str, Any]) -> dict[str, Any]:
    health = snapshot.get("cockpit_health", {})

    out = {
        "ok": True,
        "checkpoint": "037",
        "module": "k_os_executive_cockpit_consolidation_layer",
        "status": "cockpit_health_snapshot",
        "generated_at": now(),
        "health_level": health.get("health_level"),
        "completion_score": health.get("completion_score"),
        "module_complete_count": health.get("module_complete_count"),
        "module_total": health.get("module_total"),
        "blockers": health.get("blockers", []),
        "warnings": health.get("warnings", []),
        "external_publish_enabled": False,
        "next_checkpoint": snapshot.get("next_checkpoint")
    }

    HEALTH_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Executive Cockpit Health Snapshot",
        "",
        f"- Generated at: {out.get('generated_at')}",
        f"- Health: {out.get('health_level')}",
        f"- Completion score: {out.get('completion_score')}",
        f"- Complete modules: {out.get('module_complete_count')}/{out.get('module_total')}",
        f"- External publish enabled: {out.get('external_publish_enabled')}",
        "",
        "## Blockers",
        ""
    ]

    if out.get("blockers"):
        for item in out.get("blockers", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker do cockpit.")

    lines.extend(["", "## Warnings", ""])

    if out.get("warnings"):
        for item in out.get("warnings", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum warning do cockpit.")

    HEALTH_MD.write_text("\n".join(lines), encoding="utf-8")
    return out


def cockpit_report() -> dict[str, Any]:
    ensure_state()
    policy = load_policy()
    modules = module_index()
    analytics = analytics_snapshot()
    health = compute_cockpit_health(modules, analytics)

    report = {
        "ok": True,
        "checkpoint": "037",
        "module": "k_os_executive_cockpit_consolidation_layer",
        "status": "audit_generated",
        "generated_at": now(),
        "cockpit_state_path": "local_secrets/k_os_cockpit/cockpit_state.json",
        "cockpit_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "executive_cockpit_sanitized_only": True,
        "customer_identifiable_data_blocked": True,
        "streamlit_entrypoint": "pages/937_K_OS_Executive_Cockpit_Consolidation_Layer.py",
        "analytics": analytics,
        "modules": modules,
        "domain_summary": domain_summary(modules),
        "cockpit_health": health,
        "required_gates_before_external_cockpit_export": policy.get("required_gates_before_external_cockpit_export", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "038 - K-Command Center Action Router")
    }

    write_report(report)
    write_navigation(modules)
    write_health(report)
    append_state(report)
    event("cockpit.audit_generated", {
        "health_level": health.get("health_level"),
        "completion_score": health.get("completion_score")
    })
    return report


def append_state(report: dict[str, Any]) -> None:
    state = ensure_state()
    state.setdefault("snapshots", []).append({
        "created_at": report.get("generated_at"),
        "health_level": report.get("cockpit_health", {}).get("health_level"),
        "completion_score": report.get("cockpit_health", {}).get("completion_score")
    })
    state["snapshots"] = state["snapshots"][-100:]
    save_state(state)


def write_report(report: dict[str, Any]) -> None:
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    health = report.get("cockpit_health", {})
    analytics = report.get("analytics", {})
    metrics = analytics.get("metrics", {})

    lines = [
        "# K-OS Executive Cockpit Consolidation Layer",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Health: {health.get('health_level')}",
        f"- Completion score: {health.get('completion_score')}",
        f"- Modules complete: {health.get('module_complete_count')}/{health.get('module_total')}",
        f"- Entrypoint: {report.get('streamlit_entrypoint')}",
        f"- External publish enabled: {report.get('external_publish_enabled')}",
        "",
        "## Executive KPIs",
        ""
    ]

    key_order = [
        "customer_count",
        "subscription_count",
        "estimated_mrr_brl",
        "weighted_pipeline_brl",
        "open_ticket_count",
        "open_task_count",
        "high_risk_customer_count",
        "feature_count",
        "roadmap_release_count",
        "foundation_control_score"
    ]

    for key in key_order:
        if key in metrics:
            lines.append(f"- {key}: {metrics.get(key)}")

    lines.extend(["", "## Domain summary", ""])

    for domain, item in report.get("domain_summary", {}).items():
        lines.append(
            f"- {domain}: modules={item.get('module_count')} | pages={item.get('page_ok')} | "
            f"reports={item.get('report_ok')} | closures={item.get('closure_ok')}"
        )

    lines.extend(["", "## Blockers", ""])

    if health.get("blockers"):
        for item in health.get("blockers", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker do cockpit.")

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
    parser.add_argument("--mode", choices=["init", "audit", "navigation", "health", "show"], required=True)
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = cockpit_report()

    elif args.mode == "audit":
        result = cockpit_report()

    elif args.mode == "navigation":
        result = write_navigation(module_index())

    elif args.mode == "health":
        result = write_health(cockpit_report())

    elif args.mode == "show":
        return show_latest()

    else:
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())