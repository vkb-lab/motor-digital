# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "product_feedback" / "k_os_product_feedback_policy.json"
FEEDBACK_DIR = ROOT / "local_secrets" / "k_os_product_feedback"
FEEDBACK_PATH = FEEDBACK_DIR / "product_feedback_registry.json"

REPORT_DIR = ROOT / "reports" / "product_feedback"
MEMORY_DIR = ROOT / "memory" / "product_feedback"

LATEST_JSON = REPORT_DIR / "latest_product_feedback_report.json"
LATEST_MD = REPORT_DIR / "latest_product_feedback_report.md"
BACKLOG_JSON = REPORT_DIR / "latest_product_backlog_snapshot.json"
BACKLOG_MD = REPORT_DIR / "latest_product_backlog_snapshot.md"
ROADMAP_JSON = REPORT_DIR / "latest_roadmap_candidate_snapshot.json"
ROADMAP_MD = REPORT_DIR / "latest_roadmap_candidate_snapshot.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

SUPPORT_REPORT = ROOT / "reports" / "support" / "latest_support_desk_report.json"
SUCCESS_REPORT = ROOT / "reports" / "customer_success" / "latest_customer_success_delivery_report.json"
CRM_REPORT = ROOT / "reports" / "crm" / "latest_customer_registry_report.json"


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
        raise RuntimeError("Product feedback policy not found.")
    return data


def ensure_registry() -> dict[str, Any]:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not FEEDBACK_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_send_enabled": False,
            "automatic_roadmap_commitment_enabled": False,
            "feedback_items": [],
            "feature_requests": [],
            "feature_feedback_links": [],
            "activities": []
        }
        write_json(FEEDBACK_PATH, data)

    registry = read_json(FEEDBACK_PATH)
    if not registry:
        raise RuntimeError("Could not load product feedback registry.")
    return registry


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(FEEDBACK_PATH, data)


def first_or_none(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    return items[0] if items else None


def find_by_alias(items: list[dict[str, Any]], alias: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("customer_alias") == alias:
            return item
    return None


def load_context(customer_alias: str = "") -> dict[str, Any]:
    crm = read_json(CRM_REPORT) or {}
    support = read_json(SUPPORT_REPORT) or {}
    success = read_json(SUCCESS_REPORT) or {}

    customers = crm.get("customers", [])
    tickets = support.get("tickets", [])
    accounts = success.get("accounts", [])

    customer = find_by_alias(customers, customer_alias) if customer_alias else first_or_none(customers)
    alias = customer.get("customer_alias") if customer else customer_alias or "demo_customer"

    ticket = find_by_alias(tickets, alias) if alias else first_or_none(tickets)
    account = find_by_alias(accounts, alias) if alias else first_or_none(accounts)

    agent_id = ""
    for item in [customer, ticket, account]:
        if item and item.get("agent_id"):
            agent_id = item.get("agent_id")
            break

    return {
        "customer_alias": alias,
        "customer": customer,
        "ticket": ticket,
        "success_account": account,
        "agent_id": agent_id or "marketplace_ia_agent",
        "reports": {
            "crm_report_exists": CRM_REPORT.exists(),
            "support_report_exists": SUPPORT_REPORT.exists(),
            "customer_success_report_exists": SUCCESS_REPORT.exists()
        }
    }


def score_value(value: str, table: dict[str, int], default: int) -> int:
    return table.get(str(value or "").lower(), default)


def calculate_impact_score(impact: str, urgency: str, effort: str, revenue_signal: str) -> int:
    impact_score = score_value(impact, {"low": 1, "medium": 2, "high": 3, "critical": 4}, 2)
    urgency_score = score_value(urgency, {"low": 1, "medium": 2, "high": 3, "critical": 4}, 2)
    effort_penalty = score_value(effort, {"small": 1, "medium": 2, "large": 3, "unknown": 2}, 2)
    revenue_score = score_value(revenue_signal, {"none": 0, "low": 1, "medium": 2, "high": 3, "strategic": 4}, 0)

    score = (impact_score * 3) + (urgency_score * 2) + (revenue_score * 2) - effort_penalty
    return max(score, 0)


def priority_from_score(score: int) -> str:
    if score >= 17:
        return "strategic"
    if score >= 13:
        return "critical"
    if score >= 9:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


def safe_feedback(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedback_id": item.get("feedback_id"),
        "customer_alias": item.get("customer_alias"),
        "agent_id": item.get("agent_id", ""),
        "ticket_id": item.get("ticket_id", ""),
        "success_account_id": item.get("success_account_id", ""),
        "feedback_type": item.get("feedback_type"),
        "category": item.get("category"),
        "status": item.get("status"),
        "summary": item.get("summary"),
        "impact": item.get("impact"),
        "urgency": item.get("urgency"),
        "sentiment": item.get("sentiment", "neutral"),
        "owner": item.get("owner"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def safe_feature(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "feature_id": item.get("feature_id"),
        "title": item.get("title"),
        "category": item.get("category"),
        "status": item.get("status"),
        "priority": item.get("priority"),
        "impact": item.get("impact"),
        "urgency": item.get("urgency"),
        "effort": item.get("effort"),
        "revenue_signal": item.get("revenue_signal", "none"),
        "impact_score": item.get("impact_score", 0),
        "linked_feedback_count": len(item.get("linked_feedback_ids", [])),
        "linked_feedback_ids": item.get("linked_feedback_ids", []),
        "owner": item.get("owner"),
        "next_action": item.get("next_action", ""),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def safe_link(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "link_id": item.get("link_id"),
        "feedback_id": item.get("feedback_id"),
        "feature_id": item.get("feature_id"),
        "reason": item.get("reason"),
        "created_at": item.get("created_at")
    }


def safe_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": item.get("activity_id"),
        "activity_type": item.get("activity_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by")
    }


def create_feedback(customer_alias: str, feedback_type: str, category: str, summary: str, impact: str, urgency: str, sentiment: str, owner: str) -> dict[str, Any]:
    policy = load_policy()

    if feedback_type not in set(policy.get("feedback_types", [])):
        raise RuntimeError(f"Invalid feedback type: {feedback_type}")

    if category not in set(policy.get("feature_categories", [])):
        raise RuntimeError(f"Invalid category: {category}")

    if impact not in set(policy.get("impact_levels", [])):
        raise RuntimeError(f"Invalid impact: {impact}")

    registry = ensure_registry()
    ctx = load_context(customer_alias)

    ticket = ctx.get("ticket") or {}
    success_account = ctx.get("success_account") or {}

    feedback_id = "fb_" + uuid.uuid4().hex[:12]

    item = {
        "feedback_id": feedback_id,
        "customer_alias": ctx["customer_alias"],
        "agent_id": ctx["agent_id"],
        "ticket_id": ticket.get("ticket_id", ""),
        "success_account_id": success_account.get("success_account_id", ""),
        "feedback_type": feedback_type,
        "category": category,
        "status": "new",
        "summary": summary,
        "impact": impact,
        "urgency": urgency,
        "sentiment": sentiment or "neutral",
        "owner": owner or "k_os_operator",
        "created_at": now(),
        "updated_at": now()
    }

    registry["feedback_items"].append(item)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "feedback_created",
        "summary": f"Feedback criado: {feedback_type}/{category}.",
        "created_at": now(),
        "created_by": owner or "k_os_operator"
    })

    save_registry(registry)
    event("product_feedback.feedback_created", {"feedback_id": feedback_id, "customer_alias": ctx["customer_alias"]})
    return audit_report()


def create_feature(title: str, category: str, impact: str, urgency: str, effort: str, revenue_signal: str, owner: str, next_action: str) -> dict[str, Any]:
    policy = load_policy()

    if category not in set(policy.get("feature_categories", [])):
        raise RuntimeError(f"Invalid feature category: {category}")

    if impact not in set(policy.get("impact_levels", [])):
        raise RuntimeError(f"Invalid impact: {impact}")

    if effort not in set(policy.get("effort_levels", [])):
        raise RuntimeError(f"Invalid effort: {effort}")

    registry = ensure_registry()

    score = calculate_impact_score(impact, urgency, effort, revenue_signal)
    priority = priority_from_score(score)
    feature_id = "feat_" + uuid.uuid4().hex[:12]

    feature = {
        "feature_id": feature_id,
        "title": title,
        "category": category,
        "status": "new",
        "priority": priority,
        "impact": impact,
        "urgency": urgency,
        "effort": effort,
        "revenue_signal": revenue_signal or "none",
        "impact_score": score,
        "linked_feedback_ids": [],
        "owner": owner or "k_os_operator",
        "next_action": next_action or "triagem de produto e revisão de viabilidade",
        "customer_facing_roadmap_allowed": False,
        "roadmap_commitment_allowed": False,
        "created_at": now(),
        "updated_at": now()
    }

    registry["feature_requests"].append(feature)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "feature_created",
        "summary": f"Feature criada: {title}.",
        "created_at": now(),
        "created_by": owner or "k_os_operator"
    })

    save_registry(registry)
    event("product_feedback.feature_created", {"feature_id": feature_id, "priority": priority, "impact_score": score})
    return audit_report()


def link_feedback_to_feature(feedback_id: str, feature_id: str, reason: str) -> dict[str, Any]:
    registry = ensure_registry()

    feedback = next((item for item in registry.get("feedback_items", []) if item.get("feedback_id") == feedback_id), None)
    feature = next((item for item in registry.get("feature_requests", []) if item.get("feature_id") == feature_id), None)

    if not feedback:
        raise RuntimeError(f"Feedback not found: {feedback_id}")

    if not feature:
        raise RuntimeError(f"Feature not found: {feature_id}")

    link_id = "pfl_" + uuid.uuid4().hex[:12]

    link = {
        "link_id": link_id,
        "feedback_id": feedback_id,
        "feature_id": feature_id,
        "reason": reason or "manual_link",
        "created_at": now()
    }

    registry["feature_feedback_links"].append(link)

    linked = set(feature.get("linked_feedback_ids", []))
    linked.add(feedback_id)
    feature["linked_feedback_ids"] = sorted(linked)
    feature["updated_at"] = now()

    feedback["status"] = "linked_to_feature"
    feedback["updated_at"] = now()

    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "feedback_linked_to_feature",
        "summary": f"Feedback {feedback_id} vinculado a feature {feature_id}.",
        "created_at": now(),
        "created_by": "operator"
    })

    save_registry(registry)
    event("product_feedback.feedback_linked_to_feature", {"feedback_id": feedback_id, "feature_id": feature_id})
    return audit_report()


def set_feature_status(feature_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()

    if status not in set(policy.get("feature_statuses", [])):
        raise RuntimeError(f"Invalid feature status: {status}")

    registry = ensure_registry()
    found = False

    for feature in registry.get("feature_requests", []):
        if feature.get("feature_id") == feature_id:
            if status == "shipped" and "review" not in (reason or "").lower():
                raise RuntimeError("Feature shipped requires explicit review reason.")

            feature["status"] = status
            feature["last_status_reason"] = reason or "manual_update"
            feature["updated_at"] = now()

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "activity_type": "feature_status_changed",
                "summary": f"Feature {feature_id} alterada para {status}.",
                "created_at": now(),
                "created_by": "operator"
            })

            found = True

    if not found:
        raise RuntimeError(f"Feature not found: {feature_id}")

    save_registry(registry)
    event("product_feedback.feature_status_changed", {"feature_id": feature_id, "status": status})
    return audit_report()


def set_feature_priority(feature_id: str, priority: str, reason: str) -> dict[str, Any]:
    policy = load_policy()

    if priority not in set(policy.get("priority_levels", [])):
        raise RuntimeError(f"Invalid priority: {priority}")

    registry = ensure_registry()
    found = False

    for feature in registry.get("feature_requests", []):
        if feature.get("feature_id") == feature_id:
            feature["priority"] = priority
            feature["last_priority_reason"] = reason or "manual_priority_update"
            feature["updated_at"] = now()

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "activity_type": "feature_priority_changed",
                "summary": f"Feature {feature_id} alterada para prioridade {priority}.",
                "created_at": now(),
                "created_by": "operator"
            })

            found = True

    if not found:
        raise RuntimeError(f"Feature not found: {feature_id}")

    save_registry(registry)
    event("product_feedback.feature_priority_changed", {"feature_id": feature_id, "priority": priority})
    return audit_report()


def create_demo() -> dict[str, Any]:
    registry = ensure_registry()

    if not registry.get("feedback_items"):
        ctx = load_context("demo_customer")
        ticket = ctx.get("ticket") or {}
        account = ctx.get("success_account") or {}

        feedback_id = "fb_" + uuid.uuid4().hex[:12]
        registry["feedback_items"].append({
            "feedback_id": feedback_id,
            "customer_alias": ctx["customer_alias"],
            "agent_id": ctx["agent_id"],
            "ticket_id": ticket.get("ticket_id", ""),
            "success_account_id": account.get("success_account_id", ""),
            "feedback_type": "feature_request",
            "category": "cockpit",
            "status": "new",
            "summary": "Cliente demo pediu melhor visualização de tarefas, tickets e entregas no cockpit.",
            "impact": "high",
            "urgency": "medium",
            "sentiment": "neutral",
            "owner": "k_os_operator",
            "created_at": now(),
            "updated_at": now()
        })

    if not registry.get("feature_requests"):
        feature_id = "feat_" + uuid.uuid4().hex[:12]
        score = calculate_impact_score("high", "medium", "medium", "medium")
        registry["feature_requests"].append({
            "feature_id": feature_id,
            "title": "Cockpit unificado de cliente",
            "category": "cockpit",
            "status": "backlog",
            "priority": priority_from_score(score),
            "impact": "high",
            "urgency": "medium",
            "effort": "medium",
            "revenue_signal": "medium",
            "impact_score": score,
            "linked_feedback_ids": [],
            "owner": "k_os_operator",
            "next_action": "revisar escopo do cockpit e dependências de Customer Success, Support e CRM",
            "customer_facing_roadmap_allowed": False,
            "roadmap_commitment_allowed": False,
            "created_at": now(),
            "updated_at": now()
        })

    if registry.get("feedback_items") and registry.get("feature_requests") and not registry.get("feature_feedback_links"):
        feedback_id = registry["feedback_items"][0]["feedback_id"]
        feature_id = registry["feature_requests"][0]["feature_id"]

        registry["feature_feedback_links"].append({
            "link_id": "pfl_" + uuid.uuid4().hex[:12],
            "feedback_id": feedback_id,
            "feature_id": feature_id,
            "reason": "demo_initial_link",
            "created_at": now()
        })

        registry["feedback_items"][0]["status"] = "linked_to_feature"
        registry["feature_requests"][0]["linked_feedback_ids"] = [feedback_id]

    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "demo_created",
        "summary": "Demo de product feedback criada localmente.",
        "created_at": now(),
        "created_by": "k_os_product_feedback"
    })

    save_registry(registry)
    event("product_feedback.demo_created", {"ok": True})
    return audit_report()


def compute_metrics(feedback_items: list[dict[str, Any]], features: list[dict[str, Any]]) -> dict[str, Any]:
    feedback_status_counts: dict[str, int] = {}
    feature_status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}

    for item in feedback_items:
        feedback_status_counts[item.get("status", "unknown")] = feedback_status_counts.get(item.get("status", "unknown"), 0) + 1
        category_counts[item.get("category", "unknown")] = category_counts.get(item.get("category", "unknown"), 0) + 1
        type_counts[item.get("feedback_type", "unknown")] = type_counts.get(item.get("feedback_type", "unknown"), 0) + 1

    for feature in features:
        feature_status_counts[feature.get("status", "unknown")] = feature_status_counts.get(feature.get("status", "unknown"), 0) + 1
        priority_counts[feature.get("priority", "unknown")] = priority_counts.get(feature.get("priority", "unknown"), 0) + 1
        category_counts[feature.get("category", "unknown")] = category_counts.get(feature.get("category", "unknown"), 0) + 1

    critical_feedback_count = sum(1 for item in feedback_items if item.get("impact") == "critical" or item.get("urgency") == "critical")
    roadmap_candidate_count = sum(1 for item in features if item.get("status") in {"backlog", "planned"} and int(item.get("impact_score", 0) or 0) >= 9)

    return {
        "feedback_count": len(feedback_items),
        "feature_count": len(features),
        "critical_feedback_count": critical_feedback_count,
        "roadmap_candidate_count": roadmap_candidate_count,
        "feedback_status_counts": feedback_status_counts,
        "feature_status_counts": feature_status_counts,
        "priority_counts": priority_counts,
        "category_counts": category_counts,
        "type_counts": type_counts
    }


def backlog_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    features = report.get("feature_requests", [])

    backlog = [item for item in features if item.get("status") in {"new", "triage", "backlog", "planned", "blocked"}]
    backlog_sorted = sorted(backlog, key=lambda item: int(item.get("impact_score", 0) or 0), reverse=True)

    snapshot = {
        "ok": True,
        "checkpoint": "034",
        "module": "k_os_product_feedback_feature_request_core",
        "status": "backlog_snapshot",
        "generated_at": now(),
        "backlog_count": len(backlog_sorted),
        "top_backlog_items": backlog_sorted[:20],
        "customer_facing_roadmap_allowed": False,
        "automatic_roadmap_commitment_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    BACKLOG_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Product Backlog Snapshot",
        "",
        f"- Generated at: {snapshot.get('generated_at')}",
        f"- Backlog count: {snapshot.get('backlog_count')}",
        f"- Customer-facing roadmap allowed: {snapshot.get('customer_facing_roadmap_allowed')}",
        f"- Automatic roadmap commitment: {snapshot.get('automatic_roadmap_commitment_enabled')}",
        "",
        "## Top backlog items",
        ""
    ]

    if backlog_sorted:
        for item in backlog_sorted[:20]:
            lines.append(
                f"- {item.get('feature_id')} | {item.get('title')} | priority={item.get('priority')} | "
                f"score={item.get('impact_score')} | status={item.get('status')}"
            )
    else:
        lines.append("- Nenhum item no backlog.")

    BACKLOG_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def roadmap_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    features = report.get("feature_requests", [])

    candidates = [
        item for item in features
        if item.get("status") in {"backlog", "planned"} and int(item.get("impact_score", 0) or 0) >= 9
    ]

    candidates = sorted(candidates, key=lambda item: int(item.get("impact_score", 0) or 0), reverse=True)

    snapshot = {
        "ok": True,
        "checkpoint": "034",
        "module": "k_os_product_feedback_feature_request_core",
        "status": "roadmap_candidate_snapshot",
        "generated_at": now(),
        "candidate_count": len(candidates),
        "candidates": candidates[:20],
        "customer_facing_roadmap_allowed": False,
        "roadmap_commitment_performed": False,
        "manual_approval_required": True,
        "next_checkpoint": report.get("next_checkpoint")
    }

    ROADMAP_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Roadmap Candidate Snapshot",
        "",
        "Snapshot interno. Não publicar externamente sem aprovação.",
        "",
        f"- Generated at: {snapshot.get('generated_at')}",
        f"- Candidate count: {snapshot.get('candidate_count')}",
        f"- Customer-facing roadmap allowed: {snapshot.get('customer_facing_roadmap_allowed')}",
        f"- Roadmap commitment performed: {snapshot.get('roadmap_commitment_performed')}",
        "",
        "## Candidates",
        ""
    ]

    if candidates:
        for item in candidates[:20]:
            lines.append(
                f"- {item.get('feature_id')} | {item.get('title')} | score={item.get('impact_score')} | "
                f"priority={item.get('priority')} | linked_feedback={item.get('linked_feedback_count')}"
            )
    else:
        lines.append("- Nenhum candidato de roadmap no momento.")

    ROADMAP_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    policy = load_policy()

    feedback_items = [safe_feedback(item) for item in registry.get("feedback_items", [])]
    features = [safe_feature(item) for item in registry.get("feature_requests", [])]
    links = [safe_link(item) for item in registry.get("feature_feedback_links", [])]
    activities = [safe_activity(item) for item in registry.get("activities", [])[-30:]]

    metrics = compute_metrics(feedback_items, features)

    report = {
        "ok": True,
        "checkpoint": "034",
        "module": "k_os_product_feedback_feature_request_core",
        "status": "audit_generated",
        "generated_at": now(),
        "product_feedback_registry_path": "local_secrets/k_os_product_feedback/product_feedback_registry.json",
        "product_feedback_registry_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "automatic_roadmap_commitment_enabled": False,
        "feedback_items": feedback_items,
        "feature_requests": features,
        "feature_feedback_links": links,
        "recent_activities": activities,
        "metrics": metrics,
        "required_gates_before_roadmap_commitment": policy.get("required_gates_before_roadmap_commitment", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "035 - K-Roadmap Planner and Release Notes Core")
    }

    write_report(report)
    backlog_snapshot(report)
    roadmap_snapshot(report)
    event("product_feedback.audit_generated", {
        "feedback_count": metrics["feedback_count"],
        "feature_count": metrics["feature_count"]
    })
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Product Feedback and Feature Request Core",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Registry committed: {report.get('product_feedback_registry_committed')}",
        f"- External publish enabled: {report.get('external_publish_enabled')}",
        f"- Automatic roadmap commitment: {report.get('automatic_roadmap_commitment_enabled')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in report.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Feedback items", ""])

    if report.get("feedback_items"):
        for item in report.get("feedback_items", []):
            lines.append(
                f"- {item.get('feedback_id')} | {item.get('customer_alias')} | {item.get('feedback_type')} | "
                f"{item.get('category')} | impact={item.get('impact')} | status={item.get('status')}"
            )
    else:
        lines.append("- Nenhum feedback registrado.")

    lines.extend(["", "## Feature requests", ""])

    if report.get("feature_requests"):
        for item in report.get("feature_requests", []):
            lines.append(
                f"- {item.get('feature_id')} | {item.get('title')} | {item.get('category')} | "
                f"priority={item.get('priority')} | score={item.get('impact_score')} | status={item.get('status')}"
            )
    else:
        lines.append("- Nenhuma feature registrada.")

    lines.extend(["", "## Required gates before roadmap commitment", ""])

    for gate in report.get("required_gates_before_roadmap_commitment", []):
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
    parser.add_argument("--mode", choices=["init", "create-demo", "create-feedback", "create-feature", "link-feedback", "set-feature-status", "set-feature-priority", "audit", "show"], required=True)
    parser.add_argument("--customer-alias", default="")
    parser.add_argument("--feedback-type", default="feature_request")
    parser.add_argument("--category", default="cockpit")
    parser.add_argument("--summary", default="")
    parser.add_argument("--impact", default="medium")
    parser.add_argument("--urgency", default="medium")
    parser.add_argument("--sentiment", default="neutral")
    parser.add_argument("--title", default="")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--revenue-signal", default="none")
    parser.add_argument("--owner", default="k_os_operator")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--feedback-id", default="")
    parser.add_argument("--feature-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--priority", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "create-feedback":
        if not args.summary:
            raise SystemExit("Informe --summary")
        result = create_feedback(
            args.customer_alias,
            args.feedback_type,
            args.category,
            args.summary,
            args.impact,
            args.urgency,
            args.sentiment,
            args.owner
        )

    elif args.mode == "create-feature":
        if not args.title:
            raise SystemExit("Informe --title")
        result = create_feature(
            args.title,
            args.category,
            args.impact,
            args.urgency,
            args.effort,
            args.revenue_signal,
            args.owner,
            args.next_action
        )

    elif args.mode == "link-feedback":
        if not args.feedback_id:
            raise SystemExit("Informe --feedback-id")
        if not args.feature_id:
            raise SystemExit("Informe --feature-id")
        result = link_feedback_to_feature(args.feedback_id, args.feature_id, args.reason)

    elif args.mode == "set-feature-status":
        if not args.feature_id:
            raise SystemExit("Informe --feature-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = set_feature_status(args.feature_id, args.status, args.reason)

    elif args.mode == "set-feature-priority":
        if not args.feature_id:
            raise SystemExit("Informe --feature-id")
        if not args.priority:
            raise SystemExit("Informe --priority")
        result = set_feature_priority(args.feature_id, args.priority, args.reason)

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