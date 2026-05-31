# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "memory_bus" / "k_os_memory_event_bus_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_memory_bus"
STATE_PATH = STATE_DIR / "memory_event_bus_index.json"

REPORT_DIR = ROOT / "reports" / "memory_bus"
MEMORY_DIR = ROOT / "memory" / "memory_bus"

LATEST_JSON = REPORT_DIR / "latest_memory_event_bus_report.json"
LATEST_MD = REPORT_DIR / "latest_memory_event_bus_report.md"
INDEX_JSON = REPORT_DIR / "latest_context_index_snapshot.json"
INDEX_MD = REPORT_DIR / "latest_context_index_snapshot.md"
SEARCH_JSON = REPORT_DIR / "latest_memory_search_report.json"
SEARCH_MD = REPORT_DIR / "latest_memory_search_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

EVENT_SOURCES = [
    {"domain": "analytics", "module": "analytics", "path": "memory/analytics/events.jsonl"},
    {"domain": "cockpit", "module": "cockpit", "path": "memory/cockpit/events.jsonl"},
    {"domain": "command_center", "module": "command_center", "path": "memory/command_center/events.jsonl"},
    {"domain": "agent_queue", "module": "agent_queue", "path": "memory/agent_queue/events.jsonl"},
    {"domain": "agent_runtime", "module": "agent_runtime", "path": "memory/agent_runtime/events.jsonl"},
    {"domain": "agent_ledger", "module": "agent_ledger", "path": "memory/agent_ledger/events.jsonl"},
    {"domain": "roadmap", "module": "roadmap", "path": "memory/roadmap/events.jsonl"},
    {"domain": "product", "module": "product_feedback", "path": "memory/product_feedback/events.jsonl"},
    {"domain": "support", "module": "support", "path": "memory/support/events.jsonl"},
    {"domain": "commercial", "module": "billing", "path": "memory/billing/events.jsonl"},
    {"domain": "commercial", "module": "crm", "path": "memory/crm/events.jsonl"},
    {"domain": "commercial", "module": "sales", "path": "memory/sales/events.jsonl"},
    {"domain": "customer_ops", "module": "onboarding", "path": "memory/onboarding/events.jsonl"},
    {"domain": "customer_ops", "module": "customer_success", "path": "memory/customer_success/events.jsonl"},
    {"domain": "memory_bus", "module": "memory_bus", "path": "memory/memory_bus/events.jsonl"}
]

REPORT_SOURCES = [
    {"domain": "security", "module": "security_firewall", "path": "reports/security/latest_security_firewall_report.json"},
    {"domain": "security", "module": "schema_guard", "path": "reports/schema/latest_schema_guard_report.json"},
    {"domain": "governance", "module": "agent_permission_matrix", "path": "reports/governance/latest_agent_permission_matrix_report.json"},
    {"domain": "audit", "module": "audit_evidence_pack", "path": "reports/audit/latest_audit_evidence_pack.json"},
    {"domain": "commercial", "module": "billing", "path": "reports/billing/latest_billing_subscription_report.json"},
    {"domain": "commercial", "module": "crm", "path": "reports/crm/latest_customer_registry_report.json"},
    {"domain": "commercial", "module": "sales", "path": "reports/sales/latest_sales_pipeline_report.json"},
    {"domain": "commercial", "module": "proposals", "path": "reports/proposals/latest_proposal_factory_report.json"},
    {"domain": "customer_ops", "module": "onboarding", "path": "reports/onboarding/latest_onboarding_activation_report.json"},
    {"domain": "customer_ops", "module": "customer_success", "path": "reports/customer_success/latest_customer_success_delivery_report.json"},
    {"domain": "support", "module": "support", "path": "reports/support/latest_support_desk_report.json"},
    {"domain": "support", "module": "knowledge_base", "path": "reports/knowledge_base/latest_knowledge_base_report.json"},
    {"domain": "product", "module": "product_feedback", "path": "reports/product_feedback/latest_product_feedback_report.json"},
    {"domain": "roadmap", "module": "roadmap", "path": "reports/roadmap/latest_roadmap_release_report.json"},
    {"domain": "analytics", "module": "analytics", "path": "reports/analytics/latest_executive_metrics_report.json"},
    {"domain": "cockpit", "module": "cockpit", "path": "reports/cockpit/latest_executive_cockpit_report.json"},
    {"domain": "command_center", "module": "command_center", "path": "reports/command_center/latest_command_center_action_router_report.json"},
    {"domain": "agent_queue", "module": "agent_queue", "path": "reports/agent_queue/latest_agent_orchestration_queue_report.json"},
    {"domain": "agent_runtime", "module": "agent_runtime", "path": "reports/agent_runtime/latest_agent_runtime_supervisor_report.json"},
    {"domain": "agent_ledger", "module": "agent_ledger", "path": "reports/agent_ledger/latest_agent_execution_ledger_report.json"}
]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows

    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({
                "_read_error": "invalid_jsonl_line",
                "_line_hash": stable_hash(line)
            })

    return rows


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
        raise RuntimeError("Memory Event Bus policy not found.")
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
            "events": [],
            "context_items": [],
            "queries": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load Memory Event Bus state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def payload_keys(data: Any) -> list[str]:
    if isinstance(data, dict):
        return sorted([str(key) for key in data.keys()])[:50]
    return []


def sanitize_event(source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    payload = raw.get("data", {})
    event_name = raw.get("event", raw.get("event_type", "unknown_event"))
    created_at = raw.get("created_at", raw.get("generated_at", ""))

    safe = {
        "event_id": "evt_" + stable_hash({
            "source": source.get("path"),
            "event": event_name,
            "created_at": created_at,
            "payload_hash": stable_hash(payload)
        })[:16],
        "source_path": source.get("path"),
        "domain": source.get("domain"),
        "module": source.get("module"),
        "event": event_name,
        "created_at": created_at,
        "payload_hash": stable_hash(payload),
        "payload_keys": payload_keys(payload),
        "raw_payload_included": False
    }

    return safe


def sanitize_report_source(source: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    summary_keys = [
        "ok",
        "checkpoint",
        "module",
        "status",
        "generated_at",
        "next_checkpoint",
        "external_send_enabled",
        "external_publish_enabled",
        "manual_approval_required"
    ]

    summary = {}
    for key in summary_keys:
        if key in data:
            summary[key] = data.get(key)

    metrics = data.get("metrics", {})
    metric_keys = payload_keys(metrics)

    return {
        "context_id": "ctx_" + stable_hash({
            "path": source.get("path"),
            "hash": stable_hash(data)
        })[:16],
        "source_path": source.get("path"),
        "domain": source.get("domain"),
        "module": source.get("module"),
        "exists": True,
        "ok": bool(data.get("ok") is True),
        "status": data.get("status", "unknown"),
        "checkpoint": data.get("checkpoint", ""),
        "generated_at": data.get("generated_at", ""),
        "report_hash": stable_hash(data),
        "summary": summary,
        "metric_keys": metric_keys,
        "raw_report_included": False
    }


def ingest_events() -> list[dict[str, Any]]:
    events = []

    for source in EVENT_SOURCES:
        path = ROOT / source["path"]
        rows = read_jsonl(path)

        for row in rows:
            events.append(sanitize_event(source, row))

    events = sorted(events, key=lambda item: item.get("created_at", ""), reverse=True)
    return events[:3000]


def index_reports() -> list[dict[str, Any]]:
    items = []

    for source in REPORT_SOURCES:
        path = ROOT / source["path"]
        data = read_json(path)

        if data:
            items.append(sanitize_report_source(source, data))
        else:
            items.append({
                "context_id": "ctx_" + stable_hash(source)[:16],
                "source_path": source.get("path"),
                "domain": source.get("domain"),
                "module": source.get("module"),
                "exists": False,
                "ok": False,
                "status": "missing",
                "checkpoint": "",
                "generated_at": "",
                "report_hash": "",
                "summary": {},
                "metric_keys": [],
                "raw_report_included": False
            })

    return items


def build_index() -> dict[str, Any]:
    state = ensure_state()

    events = ingest_events()
    context_items = index_reports()

    state["events"] = events
    state["context_items"] = context_items
    state["last_indexed_at"] = now()
    save_state(state)

    event("memory_bus.index_built", {
        "event_count": len(events),
        "context_item_count": len(context_items)
    })

    return audit_report()


def domain_summary(events: list[dict[str, Any]], context_items: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for item in events:
        domain = item.get("domain", "unknown")
        result.setdefault(domain, {
            "event_count": 0,
            "context_item_count": 0,
            "context_ok_count": 0,
            "missing_context_count": 0
        })
        result[domain]["event_count"] += 1

    for item in context_items:
        domain = item.get("domain", "unknown")
        result.setdefault(domain, {
            "event_count": 0,
            "context_item_count": 0,
            "context_ok_count": 0,
            "missing_context_count": 0
        })
        result[domain]["context_item_count"] += 1
        if item.get("ok"):
            result[domain]["context_ok_count"] += 1
        if not item.get("exists"):
            result[domain]["missing_context_count"] += 1

    return result


def search_local(query: str) -> dict[str, Any]:
    state = ensure_state()
    query_norm = query.lower().strip()

    if not query_norm:
        raise RuntimeError("Informe query para busca local.")

    event_matches = []
    context_matches = []

    for item in state.get("events", []):
        haystack = " ".join([
            str(item.get("domain", "")),
            str(item.get("module", "")),
            str(item.get("event", "")),
            str(item.get("source_path", "")),
            " ".join(item.get("payload_keys", []))
        ]).lower()

        if query_norm in haystack:
            event_matches.append(item)

    for item in state.get("context_items", []):
        haystack = " ".join([
            str(item.get("domain", "")),
            str(item.get("module", "")),
            str(item.get("status", "")),
            str(item.get("checkpoint", "")),
            str(item.get("source_path", "")),
            " ".join(item.get("metric_keys", [])),
            json.dumps(item.get("summary", {}), ensure_ascii=False)
        ]).lower()

        if query_norm in haystack:
            context_matches.append(item)

    result = {
        "ok": True,
        "checkpoint": "042",
        "module": "k_os_memory_event_bus_context_index_core",
        "status": "search_completed",
        "generated_at": now(),
        "query": query,
        "event_match_count": len(event_matches),
        "context_match_count": len(context_matches),
        "events": event_matches[:50],
        "context_items": context_matches[:50],
        "raw_payload_included": False,
        "external_send_enabled": False,
        "external_publish_enabled": False
    }

    state.setdefault("queries", []).append({
        "query_id": "qry_" + uuid.uuid4().hex[:12],
        "query": query,
        "created_at": result["generated_at"],
        "event_match_count": len(event_matches),
        "context_match_count": len(context_matches)
    })
    state["queries"] = state["queries"][-200:]
    save_state(state)

    write_search(result)
    event("memory_bus.search_completed", {
        "query": query,
        "event_match_count": len(event_matches),
        "context_match_count": len(context_matches)
    })

    return result


def write_search(result: dict[str, Any]) -> None:
    SEARCH_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Memory Search Report",
        "",
        "- Status: " + str(result.get("status")),
        "- Query: " + str(result.get("query")),
        "- Event matches: " + str(result.get("event_match_count")),
        "- Context matches: " + str(result.get("context_match_count")),
        "- Raw payload included: " + str(result.get("raw_payload_included")),
        "- External publish enabled: " + str(result.get("external_publish_enabled")),
        "",
        "## Event matches",
        ""
    ]

    if result.get("events"):
        for item in result.get("events", [])[:20]:
            lines.append(
                "- " + str(item.get("created_at")) +
                " | " + str(item.get("domain")) +
                " | " + str(item.get("module")) +
                " | " + str(item.get("event"))
            )
    else:
        lines.append("- Nenhum evento encontrado.")

    lines.extend(["", "## Context matches", ""])

    if result.get("context_items"):
        for item in result.get("context_items", [])[:20]:
            lines.append(
                "- " + str(item.get("domain")) +
                " | " + str(item.get("module")) +
                " | status=" + str(item.get("status")) +
                " | path=" + str(item.get("source_path"))
            )
    else:
        lines.append("- Nenhum contexto encontrado.")

    SEARCH_MD.write_text("\n".join(lines), encoding="utf-8")


def write_index_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    snapshot = {
        "ok": True,
        "checkpoint": "042",
        "module": "k_os_memory_event_bus_context_index_core",
        "status": "context_index_snapshot",
        "generated_at": now(),
        "event_count": report.get("metrics", {}).get("event_count", 0),
        "context_item_count": report.get("metrics", {}).get("context_item_count", 0),
        "domain_summary": report.get("domain_summary", {}),
        "latest_events": report.get("latest_events", [])[:30],
        "latest_context_items": report.get("context_items", [])[:30],
        "raw_payload_included": False,
        "external_publish_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    INDEX_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Context Index Snapshot",
        "",
        "- Generated at: " + str(snapshot.get("generated_at")),
        "- Events: " + str(snapshot.get("event_count")),
        "- Context items: " + str(snapshot.get("context_item_count")),
        "- Raw payload included: " + str(snapshot.get("raw_payload_included")),
        "- External publish enabled: " + str(snapshot.get("external_publish_enabled")),
        "",
        "## Domain summary",
        ""
    ]

    for domain, item in snapshot.get("domain_summary", {}).items():
        lines.append(
            "- " + str(domain) +
            ": events=" + str(item.get("event_count")) +
            " | context=" + str(item.get("context_item_count")) +
            " | ok=" + str(item.get("context_ok_count")) +
            " | missing=" + str(item.get("missing_context_count"))
        )

    INDEX_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def compute_metrics(events: list[dict[str, Any]], context_items: list[dict[str, Any]], queries: list[dict[str, Any]]) -> dict[str, Any]:
    domains = domain_summary(events, context_items)
    missing_context_count = sum(1 for item in context_items if not item.get("exists"))
    ok_context_count = sum(1 for item in context_items if item.get("ok"))

    return {
        "event_count": len(events),
        "context_item_count": len(context_items),
        "context_ok_count": ok_context_count,
        "missing_context_count": missing_context_count,
        "query_count": len(queries),
        "domain_count": len(domains),
        "raw_payload_included": False
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()

    events = state.get("events", [])
    context_items = state.get("context_items", [])
    queries = state.get("queries", [])

    metrics = compute_metrics(events, context_items, queries)
    domains = domain_summary(events, context_items)

    report = {
        "ok": True,
        "checkpoint": "042",
        "module": "k_os_memory_event_bus_context_index_core",
        "status": "audit_generated",
        "generated_at": now(),
        "memory_bus_state_path": "local_secrets/k_os_memory_bus/memory_event_bus_index.json",
        "memory_bus_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "raw_payload_storage_in_reports": False,
        "payload_hashing_enabled": True,
        "context_index_enabled": True,
        "local_search_enabled": True,
        "cross_module_event_index_enabled": True,
        "event_sources": [
            {
                "domain": item.get("domain"),
                "module": item.get("module"),
                "path": item.get("path"),
                "exists": (ROOT / item.get("path")).exists()
            }
            for item in EVENT_SOURCES
        ],
        "report_sources": [
            {
                "domain": item.get("domain"),
                "module": item.get("module"),
                "path": item.get("path"),
                "exists": (ROOT / item.get("path")).exists()
            }
            for item in REPORT_SOURCES
        ],
        "metrics": metrics,
        "domain_summary": domains,
        "latest_events": events[:50],
        "context_items": context_items,
        "recent_queries": queries[-30:],
        "required_gates_before_external_memory_export": policy.get("required_gates_before_external_memory_export", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "043 - K-Context Retrieval API Core")
    }

    write_report(report)
    write_index_snapshot(report)
    event("memory_bus.audit_generated", {
        "event_count": metrics.get("event_count"),
        "context_item_count": metrics.get("context_item_count")
    })

    return report


def write_report(report: dict[str, Any]) -> None:
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    metrics = report.get("metrics", {})

    lines = [
        "# K-OS Memory Event Bus and Context Index Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- State committed: " + str(report.get("memory_bus_state_committed")),
        "- Sanitized reports only: " + str(report.get("sanitized_reports_only")),
        "- Raw payload storage in reports: " + str(report.get("raw_payload_storage_in_reports")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "",
        "## Metrics",
        ""
    ]

    for key, value in metrics.items():
        lines.append("- " + str(key) + ": " + str(value))

    lines.extend(["", "## Domain summary", ""])

    for domain, item in report.get("domain_summary", {}).items():
        lines.append(
            "- " + str(domain) +
            ": events=" + str(item.get("event_count")) +
            " | context=" + str(item.get("context_item_count")) +
            " | ok=" + str(item.get("context_ok_count")) +
            " | missing=" + str(item.get("missing_context_count"))
        )

    lines.extend(["", "## Latest events", ""])

    if report.get("latest_events"):
        for item in report.get("latest_events", [])[:25]:
            lines.append(
                "- " + str(item.get("created_at")) +
                " | " + str(item.get("domain")) +
                " | " + str(item.get("module")) +
                " | " + str(item.get("event"))
            )
    else:
        lines.append("- Nenhum evento indexado.")

    lines.extend(["", "## Required gates before external memory export", ""])

    for gate in report.get("required_gates_before_external_memory_export", []):
        lines.append("- " + str(gate))

    lines.extend(["", "## Blocked actions", ""])

    for item in report.get("blocked_actions", []):
        lines.append("- " + str(item))

    lines.extend(["", "## Next checkpoint", "", "- " + str(report.get("next_checkpoint"))])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def show_latest() -> int:
    if LATEST_JSON.exists():
        print(LATEST_JSON.read_text(encoding="utf-8-sig"))
    else:
        print("{}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "build-index", "search", "audit", "show"], required=True)
    parser.add_argument("--query", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "build-index":
        result = build_index()

    elif args.mode == "search":
        result = search_local(args.query)

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