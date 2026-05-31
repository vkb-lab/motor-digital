# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "context_api" / "k_os_context_retrieval_api_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_context_api"
STATE_PATH = STATE_DIR / "context_retrieval_api_state.json"

REPORT_DIR = ROOT / "reports" / "context_api"
MEMORY_DIR = ROOT / "memory" / "context_api"

LATEST_JSON = REPORT_DIR / "latest_context_retrieval_api_report.json"
LATEST_MD = REPORT_DIR / "latest_context_retrieval_api_report.md"
CATALOG_JSON = REPORT_DIR / "latest_context_api_catalog.json"
CATALOG_MD = REPORT_DIR / "latest_context_api_catalog.md"
RETRIEVAL_JSON = REPORT_DIR / "latest_context_retrieval_report.json"
RETRIEVAL_MD = REPORT_DIR / "latest_context_retrieval_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

MEMORY_BUS_STATE = ROOT / "local_secrets" / "k_os_memory_bus" / "memory_event_bus_index.json"
MEMORY_BUS_REPORT = ROOT / "reports" / "memory_bus" / "latest_memory_event_bus_report.json"
MEMORY_INDEX_SNAPSHOT = ROOT / "reports" / "memory_bus" / "latest_context_index_snapshot.json"


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
        raise RuntimeError("Context Retrieval API policy not found.")
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
            "retrievals": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load Context API state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def load_memory_index() -> dict[str, Any]:
    state = read_json(MEMORY_BUS_STATE)
    if state and not state.get("_read_error"):
        return {
            "source": "local_secrets/k_os_memory_bus/memory_event_bus_index.json",
            "events": state.get("events", []),
            "context_items": state.get("context_items", []),
            "source_available": True
        }

    report = read_json(MEMORY_BUS_REPORT)
    if report and not report.get("_read_error"):
        return {
            "source": "reports/memory_bus/latest_memory_event_bus_report.json",
            "events": report.get("latest_events", []),
            "context_items": report.get("context_items", []),
            "source_available": True
        }

    snapshot = read_json(MEMORY_INDEX_SNAPSHOT)
    if snapshot and not snapshot.get("_read_error"):
        return {
            "source": "reports/memory_bus/latest_context_index_snapshot.json",
            "events": snapshot.get("latest_events", []),
            "context_items": snapshot.get("latest_context_items", []),
            "source_available": True
        }

    return {
        "source": "",
        "events": [],
        "context_items": [],
        "source_available": False
    }


def as_int(value: Any, default: int = 20, minimum: int = 1, maximum: int = 100) -> int:
    try:
        number = int(value)
    except Exception:
        number = default

    if number < minimum:
        number = minimum

    if number > maximum:
        number = maximum

    return number


def normalize(value: Any) -> str:
    return str(value or "").lower().strip()


def item_haystack(item: dict[str, Any]) -> str:
    parts = [
        str(item.get("domain", "")),
        str(item.get("module", "")),
        str(item.get("event", "")),
        str(item.get("status", "")),
        str(item.get("checkpoint", "")),
        str(item.get("source_path", "")),
        " ".join([str(x) for x in item.get("payload_keys", [])]),
        " ".join([str(x) for x in item.get("metric_keys", [])]),
        json.dumps(item.get("summary", {}), ensure_ascii=False)
    ]
    return " ".join(parts).lower()


def sanitize_event_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "event",
        "event_id": item.get("event_id", ""),
        "domain": item.get("domain", ""),
        "module": item.get("module", ""),
        "event": item.get("event", ""),
        "created_at": item.get("created_at", ""),
        "source_path": item.get("source_path", ""),
        "payload_hash": item.get("payload_hash", ""),
        "payload_keys": item.get("payload_keys", []),
        "raw_payload_included": False
    }


def sanitize_context_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "context",
        "context_id": item.get("context_id", ""),
        "domain": item.get("domain", ""),
        "module": item.get("module", ""),
        "checkpoint": item.get("checkpoint", ""),
        "status": item.get("status", ""),
        "ok": item.get("ok", False),
        "generated_at": item.get("generated_at", ""),
        "source_path": item.get("source_path", ""),
        "report_hash": item.get("report_hash", ""),
        "metric_keys": item.get("metric_keys", []),
        "summary": item.get("summary", {}),
        "raw_report_included": False
    }


def matches_filters(item: dict[str, Any], query: str, domain: str, module: str, event_filter: str) -> bool:
    if domain and normalize(item.get("domain")) != domain:
        return False

    if module and normalize(item.get("module")) != module:
        return False

    if event_filter and normalize(item.get("event")) != event_filter:
        return False

    if query:
        return query in item_haystack(item)

    return True


def retrieve_context(query: str = "", domain: str = "", module: str = "", event_filter: str = "", limit: int = 20) -> dict[str, Any]:
    ensure_state()

    index = load_memory_index()
    events = index.get("events", [])
    context_items = index.get("context_items", [])

    query_norm = normalize(query)
    domain_norm = normalize(domain)
    module_norm = normalize(module)
    event_norm = normalize(event_filter)
    limit_value = as_int(limit)

    matched_events = []
    matched_context = []

    for item in events:
        if matches_filters(item, query_norm, domain_norm, module_norm, event_norm):
            matched_events.append(sanitize_event_item(item))

    for item in context_items:
        if matches_filters(item, query_norm, domain_norm, module_norm, ""):
            matched_context.append(sanitize_context_item(item))

    matched_events = matched_events[:limit_value]
    matched_context = matched_context[:limit_value]

    result = {
        "ok": True,
        "checkpoint": "043",
        "module": "k_os_context_retrieval_api_core",
        "status": "retrieval_completed",
        "generated_at": now(),
        "retrieval_id": "ret_" + uuid.uuid4().hex[:12],
        "query": query,
        "domain": domain,
        "module_filter": module,
        "event_filter": event_filter,
        "limit": limit_value,
        "memory_source": index.get("source"),
        "memory_source_available": index.get("source_available"),
        "event_match_count": len(matched_events),
        "context_match_count": len(matched_context),
        "events": matched_events,
        "context_items": matched_context,
        "raw_payload_included": False,
        "raw_report_included": False,
        "external_send_enabled": False,
        "external_publish_enabled": False
    }

    write_retrieval(result)
    record_retrieval(result)
    event("context_api.retrieval_completed", {
        "query": query,
        "domain": domain,
        "module": module,
        "event_match_count": len(matched_events),
        "context_match_count": len(matched_context)
    })

    return result


def record_retrieval(result: dict[str, Any]) -> None:
    state = ensure_state()
    state.setdefault("retrievals", []).append({
        "retrieval_id": result.get("retrieval_id"),
        "created_at": result.get("generated_at"),
        "query": result.get("query"),
        "domain": result.get("domain"),
        "module_filter": result.get("module_filter"),
        "event_match_count": result.get("event_match_count"),
        "context_match_count": result.get("context_match_count"),
        "raw_payload_included": False
    })
    state["retrievals"] = state["retrievals"][-300:]
    save_state(state)


def write_retrieval(result: dict[str, Any]) -> None:
    RETRIEVAL_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Context Retrieval Report",
        "",
        "- Status: " + str(result.get("status")),
        "- Retrieval ID: " + str(result.get("retrieval_id")),
        "- Query: " + str(result.get("query")),
        "- Domain: " + str(result.get("domain")),
        "- Module: " + str(result.get("module_filter")),
        "- Events: " + str(result.get("event_match_count")),
        "- Contexts: " + str(result.get("context_match_count")),
        "- Raw payload included: " + str(result.get("raw_payload_included")),
        "- External publish enabled: " + str(result.get("external_publish_enabled")),
        "",
        "## Events",
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
        lines.append("- Nenhum evento retornado.")

    lines.extend(["", "## Context items", ""])

    if result.get("context_items"):
        for item in result.get("context_items", [])[:20]:
            lines.append(
                "- " + str(item.get("domain")) +
                " | " + str(item.get("module")) +
                " | status=" + str(item.get("status")) +
                " | path=" + str(item.get("source_path"))
            )
    else:
        lines.append("- Nenhum contexto retornado.")

    RETRIEVAL_MD.write_text("\n".join(lines), encoding="utf-8")


def endpoint_catalog() -> dict[str, Any]:
    policy = load_policy()

    catalog = {
        "ok": True,
        "checkpoint": "043",
        "module": "k_os_context_retrieval_api_core",
        "status": "endpoint_catalog_generated",
        "generated_at": now(),
        "bind_address": policy.get("context_api_policy", {}).get("network_bind_address", "127.0.0.1"),
        "default_port": policy.get("context_api_policy", {}).get("default_port", 8583),
        "local_only": True,
        "raw_payload_return_allowed": False,
        "endpoints": [
            {
                "path": "/health",
                "method": "GET",
                "purpose": "Retornar status local da API."
            },
            {
                "path": "/catalog",
                "method": "GET",
                "purpose": "Listar endpoints e filtros permitidos."
            },
            {
                "path": "/retrieve",
                "method": "GET",
                "purpose": "Recuperar eventos e contexto sanitizado.",
                "query_params": ["query", "domain", "module", "event", "limit"]
            },
            {
                "path": "/domains",
                "method": "GET",
                "purpose": "Listar domínios disponíveis no índice."
            },
            {
                "path": "/events",
                "method": "GET",
                "purpose": "Recuperar apenas eventos sanitizados.",
                "query_params": ["query", "domain", "module", "event", "limit"]
            },
            {
                "path": "/context",
                "method": "GET",
                "purpose": "Recuperar apenas contexto sanitizado.",
                "query_params": ["query", "domain", "module", "limit"]
            }
        ],
        "blocked_actions": policy.get("blocked_actions", []),
        "external_send_enabled": False,
        "external_publish_enabled": False
    }

    CATALOG_JSON.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Context API Catalog",
        "",
        "- Status: " + str(catalog.get("status")),
        "- Bind address: " + str(catalog.get("bind_address")),
        "- Default port: " + str(catalog.get("default_port")),
        "- Local only: " + str(catalog.get("local_only")),
        "- Raw payload return allowed: " + str(catalog.get("raw_payload_return_allowed")),
        "",
        "## Endpoints",
        ""
    ]

    for item in catalog.get("endpoints", []):
        lines.append("- " + str(item.get("method")) + " " + str(item.get("path")) + " - " + str(item.get("purpose")))

    CATALOG_MD.write_text("\n".join(lines), encoding="utf-8")
    return catalog


def domains_report() -> dict[str, Any]:
    index = load_memory_index()
    domains = {}

    for item in index.get("events", []):
        domain = item.get("domain", "unknown")
        domains.setdefault(domain, {"event_count": 0, "context_count": 0})
        domains[domain]["event_count"] += 1

    for item in index.get("context_items", []):
        domain = item.get("domain", "unknown")
        domains.setdefault(domain, {"event_count": 0, "context_count": 0})
        domains[domain]["context_count"] += 1

    return {
        "ok": True,
        "status": "domains_generated",
        "generated_at": now(),
        "domains": domains,
        "raw_payload_included": False
    }


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()
    index = load_memory_index()
    catalog = endpoint_catalog()

    events = index.get("events", [])
    context_items = index.get("context_items", [])
    domains = domains_report().get("domains", {})

    report = {
        "ok": True,
        "checkpoint": "043",
        "module": "k_os_context_retrieval_api_core",
        "status": "audit_generated",
        "generated_at": now(),
        "context_api_state_path": "local_secrets/k_os_context_api/context_retrieval_api_state.json",
        "context_api_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "local_only": True,
        "bind_address": policy.get("context_api_policy", {}).get("network_bind_address", "127.0.0.1"),
        "default_port": policy.get("context_api_policy", {}).get("default_port", 8583),
        "raw_payload_return_allowed": False,
        "payload_hashes_only": True,
        "memory_source": index.get("source"),
        "memory_source_available": index.get("source_available"),
        "event_count": len(events),
        "context_item_count": len(context_items),
        "domain_count": len(domains),
        "domains": domains,
        "endpoint_count": len(catalog.get("endpoints", [])),
        "recent_retrievals": state.get("retrievals", [])[-50:],
        "required_gates_before_external_context_export": policy.get("required_gates_before_external_context_export", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "044 - K-Agent Context Injection Layer")
    }

    write_report(report)
    event("context_api.audit_generated", {
        "event_count": len(events),
        "context_item_count": len(context_items)
    })
    return report


def write_report(report: dict[str, Any]) -> None:
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Context Retrieval API Core",
        "",
        "- Status: " + str(report.get("status")),
        "- OK: " + str(report.get("ok")),
        "- Generated at: " + str(report.get("generated_at")),
        "- Local only: " + str(report.get("local_only")),
        "- Bind address: " + str(report.get("bind_address")),
        "- Default port: " + str(report.get("default_port")),
        "- Raw payload return allowed: " + str(report.get("raw_payload_return_allowed")),
        "- External publish enabled: " + str(report.get("external_publish_enabled")),
        "- Memory source available: " + str(report.get("memory_source_available")),
        "",
        "## Metrics",
        "",
        "- Events: " + str(report.get("event_count")),
        "- Context items: " + str(report.get("context_item_count")),
        "- Domains: " + str(report.get("domain_count")),
        "- Endpoints: " + str(report.get("endpoint_count")),
        "",
        "## Domains",
        ""
    ]

    for domain, item in report.get("domains", {}).items():
        lines.append(
            "- " + str(domain) +
            ": events=" + str(item.get("event_count")) +
            " | context=" + str(item.get("context_count"))
        )

    lines.extend(["", "## Recent retrievals", ""])

    if report.get("recent_retrievals"):
        for item in report.get("recent_retrievals", [])[-20:]:
            lines.append(
                "- " + str(item.get("retrieval_id")) +
                " | query=" + str(item.get("query")) +
                " | events=" + str(item.get("event_match_count")) +
                " | contexts=" + str(item.get("context_match_count"))
            )
    else:
        lines.append("- Nenhuma recuperação registrada.")

    lines.extend(["", "## Required gates before external context export", ""])

    for gate in report.get("required_gates_before_external_context_export", []):
        lines.append("- " + str(gate))

    lines.extend(["", "## Blocked actions", ""])

    for item in report.get("blocked_actions", []):
        lines.append("- " + str(item))

    lines.extend(["", "## Next checkpoint", "", "- " + str(report.get("next_checkpoint"))])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def api_response(payload: dict[str, Any], code: int = 200) -> tuple[int, bytes]:
    return code, json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


class ContextAPIHandler(BaseHTTPRequestHandler):
    server_version = "KOSContextAPI/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, payload: dict[str, Any], code: int = 200) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        def first(name: str, default: str = "") -> str:
            values = params.get(name, [default])
            return values[0] if values else default

        try:
            if parsed.path == "/health":
                self.send_json({
                    "ok": True,
                    "status": "healthy",
                    "module": "k_os_context_retrieval_api_core",
                    "generated_at": now(),
                    "local_only": True,
                    "external_publish_enabled": False
                })

            elif parsed.path == "/catalog":
                self.send_json(endpoint_catalog())

            elif parsed.path == "/domains":
                self.send_json(domains_report())

            elif parsed.path == "/retrieve":
                self.send_json(retrieve_context(
                    query=first("query"),
                    domain=first("domain"),
                    module=first("module"),
                    event_filter=first("event"),
                    limit=as_int(first("limit", "20"))
                ))

            elif parsed.path == "/events":
                result = retrieve_context(
                    query=first("query"),
                    domain=first("domain"),
                    module=first("module"),
                    event_filter=first("event"),
                    limit=as_int(first("limit", "20"))
                )
                result["context_items"] = []
                result["context_match_count"] = 0
                result["status"] = "events_retrieval_completed"
                self.send_json(result)

            elif parsed.path == "/context":
                result = retrieve_context(
                    query=first("query"),
                    domain=first("domain"),
                    module=first("module"),
                    event_filter="",
                    limit=as_int(first("limit", "20"))
                )
                result["events"] = []
                result["event_match_count"] = 0
                result["status"] = "context_retrieval_completed"
                self.send_json(result)

            else:
                self.send_json({
                    "ok": False,
                    "status": "not_found",
                    "path": parsed.path
                }, code=404)

        except Exception as exc:
            self.send_json({
                "ok": False,
                "status": "error",
                "error": str(exc),
                "external_publish_enabled": False
            }, code=500)


def serve(host: str, port: int) -> None:
    policy = load_policy()
    allowed_host = policy.get("context_api_policy", {}).get("network_bind_address", "127.0.0.1")

    if host != allowed_host:
        raise RuntimeError("Public bind blocked. Use 127.0.0.1 only.")

    endpoint_catalog()
    audit_report()

    server = ThreadingHTTPServer((host, port), ContextAPIHandler)

    print(json.dumps({
        "ok": True,
        "status": "serving",
        "module": "k_os_context_retrieval_api_core",
        "url": f"http://{host}:{port}",
        "local_only": True,
        "external_publish_enabled": False
    }, ensure_ascii=False, indent=2))

    server.serve_forever()


def show_latest() -> int:
    if LATEST_JSON.exists():
        print(LATEST_JSON.read_text(encoding="utf-8-sig"))
    else:
        print("{}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "catalog", "retrieve", "audit", "serve", "show"], required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--domain", default="")
    parser.add_argument("--module-filter", default="")
    parser.add_argument("--event", default="")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="8583")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "catalog":
        result = endpoint_catalog()

    elif args.mode == "retrieve":
        result = retrieve_context(
            query=args.query,
            domain=args.domain,
            module=args.module_filter,
            event_filter=args.event,
            limit=as_int(args.limit)
        )

    elif args.mode == "audit":
        result = audit_report()

    elif args.mode == "serve":
        serve(args.host, as_int(args.port, default=8583, minimum=1024, maximum=65535))
        return 0

    elif args.mode == "show":
        return show_latest()

    else:
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())