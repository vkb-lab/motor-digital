# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "knowledge_base" / "k_os_knowledge_base_playbooks_policy.json"
KB_DIR = ROOT / "local_secrets" / "k_os_knowledge_base"
KB_PATH = KB_DIR / "knowledge_base_registry.json"

REPORT_DIR = ROOT / "reports" / "knowledge_base"
MEMORY_DIR = ROOT / "memory" / "knowledge_base"

LATEST_JSON = REPORT_DIR / "latest_knowledge_base_report.json"
LATEST_MD = REPORT_DIR / "latest_knowledge_base_report.md"
PLAYBOOK_JSON = REPORT_DIR / "latest_support_playbook_snapshot.json"
PLAYBOOK_MD = REPORT_DIR / "latest_support_playbook_snapshot.md"
DRAFT_JSON = REPORT_DIR / "latest_response_draft.json"
DRAFT_MD = REPORT_DIR / "latest_response_draft.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

SUPPORT_REPORT = ROOT / "reports" / "support" / "latest_support_desk_report.json"


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
        raise RuntimeError("Knowledge Base policy not found.")
    return data


def ensure_registry() -> dict[str, Any]:
    KB_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not KB_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_send_enabled": False,
            "automatic_message_enabled": False,
            "articles": [],
            "playbooks": [],
            "response_templates": [],
            "ticket_links": [],
            "activities": []
        }
        write_json(KB_PATH, data)

    registry = read_json(KB_PATH)
    if not registry:
        raise RuntimeError("Could not load knowledge base registry.")
    return registry


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(KB_PATH, data)


def safe_article(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "article_id": item.get("article_id"),
        "title": item.get("title"),
        "category": item.get("category"),
        "status": item.get("status"),
        "summary": item.get("summary"),
        "owner": item.get("owner"),
        "linked_ticket_ids": item.get("linked_ticket_ids", []),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def safe_playbook(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "playbook_id": item.get("playbook_id"),
        "title": item.get("title"),
        "category": item.get("category"),
        "status": item.get("status"),
        "steps_count": len(item.get("steps", [])),
        "owner": item.get("owner"),
        "linked_ticket_ids": item.get("linked_ticket_ids", []),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def safe_template(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_id": item.get("template_id"),
        "title": item.get("title"),
        "category": item.get("category"),
        "status": item.get("status"),
        "requires_approval_before_send": item.get("requires_approval_before_send", True),
        "created_at": item.get("created_at")
    }


def safe_link(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "link_id": item.get("link_id"),
        "ticket_id": item.get("ticket_id"),
        "article_id": item.get("article_id", ""),
        "playbook_id": item.get("playbook_id", ""),
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


def load_support_tickets() -> list[dict[str, Any]]:
    data = read_json(SUPPORT_REPORT) or {}
    return data.get("tickets", [])


def first_ticket_id() -> str:
    tickets = load_support_tickets()
    if tickets:
        return tickets[0].get("ticket_id", "")
    return ""


def create_article(title: str, category: str, summary: str, content: str, owner: str) -> dict[str, Any]:
    policy = load_policy()

    if category not in set(policy.get("article_categories", [])):
        raise RuntimeError(f"Invalid article category: {category}")

    registry = ensure_registry()
    article_id = "kb_" + uuid.uuid4().hex[:12]

    article = {
        "article_id": article_id,
        "title": title,
        "category": category,
        "status": "draft",
        "summary": summary,
        "content": content,
        "owner": owner or "k_os_operator",
        "linked_ticket_ids": [],
        "customer_facing_allowed": False,
        "external_publish_allowed": False,
        "created_at": now(),
        "updated_at": now()
    }

    registry["articles"].append(article)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "article_created",
        "summary": f"Artigo criado: {title}",
        "created_at": now(),
        "created_by": owner or "k_os_operator"
    })

    save_registry(registry)
    event("knowledge.article_created", {"article_id": article_id, "category": category})
    return audit_report()


def create_playbook(title: str, category: str, steps: list[str], owner: str) -> dict[str, Any]:
    policy = load_policy()

    if category not in set(policy.get("playbook_categories", [])):
        raise RuntimeError(f"Invalid playbook category: {category}")

    registry = ensure_registry()
    playbook_id = "pb_" + uuid.uuid4().hex[:12]

    playbook = {
        "playbook_id": playbook_id,
        "title": title,
        "category": category,
        "status": "draft",
        "steps": steps,
        "owner": owner or "k_os_operator",
        "linked_ticket_ids": [],
        "customer_facing_allowed": False,
        "external_publish_allowed": False,
        "created_at": now(),
        "updated_at": now()
    }

    registry["playbooks"].append(playbook)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "playbook_created",
        "summary": f"Playbook criado: {title}",
        "created_at": now(),
        "created_by": owner or "k_os_operator"
    })

    save_registry(registry)
    event("knowledge.playbook_created", {"playbook_id": playbook_id, "category": category})
    return audit_report()


def add_template(title: str, category: str, body: str, owner: str) -> dict[str, Any]:
    registry = ensure_registry()
    template_id = "tpl_" + uuid.uuid4().hex[:12]

    template = {
        "template_id": template_id,
        "title": title,
        "category": category or "support",
        "status": "draft",
        "body": body,
        "owner": owner or "k_os_operator",
        "requires_approval_before_send": True,
        "external_send_allowed": False,
        "created_at": now()
    }

    registry["response_templates"].append(template)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "response_template_created",
        "summary": f"Template criado: {title}",
        "created_at": now(),
        "created_by": owner or "k_os_operator"
    })

    save_registry(registry)
    event("knowledge.template_created", {"template_id": template_id})
    return audit_report()


def create_demo() -> dict[str, Any]:
    registry = ensure_registry()

    if not registry.get("articles"):
        create_article(
            title="Como validar primeira entrega K-OS",
            category="delivery",
            summary="Checklist interno para revisar primeira entrega antes de marcar como concluída.",
            content="Verificar escopo, tarefas abertas, aceite necessário, riscos e evidência de auditoria.",
            owner="k_os_operator"
        )

    registry = ensure_registry()

    if not registry.get("playbooks"):
        create_playbook(
            title="Playbook de triagem de ticket de delivery",
            category="delivery",
            steps=[
                "confirmar customer_alias e vínculo com Customer Success",
                "verificar ticket e prioridade",
                "consultar entrega relacionada",
                "registrar nota interna sanitizada",
                "definir próxima ação",
                "escalar se houver risco comercial, técnico ou de dados",
                "não enviar resposta externa sem aprovação"
            ],
            owner="k_os_operator"
        )

    registry = ensure_registry()

    if not registry.get("response_templates"):
        add_template(
            title="Resposta interna para atualização de entrega",
            category="delivery",
            body="Rascunho interno: recebemos a solicitação, estamos revisando a entrega e retornaremos após aprovação do operador.",
            owner="k_os_operator"
        )

    ticket_id = first_ticket_id()
    registry = ensure_registry()

    if ticket_id:
        article_id = registry["articles"][0]["article_id"] if registry.get("articles") else ""
        playbook_id = registry["playbooks"][0]["playbook_id"] if registry.get("playbooks") else ""
        link_ticket(ticket_id, article_id, playbook_id, "demo_link_to_support_ticket")

    return audit_report()


def link_ticket(ticket_id: str, article_id: str, playbook_id: str, reason: str) -> dict[str, Any]:
    if not ticket_id:
        raise RuntimeError("ticket_id is required.")

    registry = ensure_registry()

    if article_id and not any(a.get("article_id") == article_id for a in registry.get("articles", [])):
        raise RuntimeError(f"Article not found: {article_id}")

    if playbook_id and not any(p.get("playbook_id") == playbook_id for p in registry.get("playbooks", [])):
        raise RuntimeError(f"Playbook not found: {playbook_id}")

    link_id = "lnk_" + uuid.uuid4().hex[:12]

    link = {
        "link_id": link_id,
        "ticket_id": ticket_id,
        "article_id": article_id,
        "playbook_id": playbook_id,
        "reason": reason or "manual_link",
        "created_at": now()
    }

    registry["ticket_links"].append(link)

    for article in registry.get("articles", []):
        if article.get("article_id") == article_id:
            linked = set(article.get("linked_ticket_ids", []))
            linked.add(ticket_id)
            article["linked_ticket_ids"] = sorted(linked)
            article["updated_at"] = now()

    for playbook in registry.get("playbooks", []):
        if playbook.get("playbook_id") == playbook_id:
            linked = set(playbook.get("linked_ticket_ids", []))
            linked.add(ticket_id)
            playbook["linked_ticket_ids"] = sorted(linked)
            playbook["updated_at"] = now()

    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "ticket_linked",
        "summary": f"Ticket vinculado a base de conhecimento: {ticket_id}",
        "created_at": now(),
        "created_by": "operator"
    })

    save_registry(registry)
    event("knowledge.ticket_linked", {"ticket_id": ticket_id, "article_id": article_id, "playbook_id": playbook_id})
    return audit_report()


def set_article_status(article_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()
    if status not in set(policy.get("article_statuses", [])):
        raise RuntimeError(f"Invalid article status: {status}")

    registry = ensure_registry()
    found = False

    for article in registry.get("articles", []):
        if article.get("article_id") == article_id:
            article["status"] = status
            article["updated_at"] = now()
            article["last_status_reason"] = reason or "manual_update"
            found = True

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "activity_type": "article_status_changed",
                "summary": f"Artigo alterado para {status}.",
                "created_at": now(),
                "created_by": "operator"
            })

    if not found:
        raise RuntimeError(f"Article not found: {article_id}")

    save_registry(registry)
    event("knowledge.article_status_changed", {"article_id": article_id, "status": status})
    return audit_report()


def set_playbook_status(playbook_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()
    if status not in set(policy.get("playbook_statuses", [])):
        raise RuntimeError(f"Invalid playbook status: {status}")

    registry = ensure_registry()
    found = False

    for playbook in registry.get("playbooks", []):
        if playbook.get("playbook_id") == playbook_id:
            playbook["status"] = status
            playbook["updated_at"] = now()
            playbook["last_status_reason"] = reason or "manual_update"
            found = True

            registry["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "activity_type": "playbook_status_changed",
                "summary": f"Playbook alterado para {status}.",
                "created_at": now(),
                "created_by": "operator"
            })

    if not found:
        raise RuntimeError(f"Playbook not found: {playbook_id}")

    save_registry(registry)
    event("knowledge.playbook_status_changed", {"playbook_id": playbook_id, "status": status})
    return audit_report()


def generate_response_draft(ticket_id: str, template_id: str) -> dict[str, Any]:
    registry = ensure_registry()
    tickets = load_support_tickets()

    ticket = next((t for t in tickets if t.get("ticket_id") == ticket_id), None)
    template = next((t for t in registry.get("response_templates", []) if t.get("template_id") == template_id), None)

    if not ticket:
        raise RuntimeError(f"Ticket not found in sanitized support report: {ticket_id}")

    if not template:
        raise RuntimeError(f"Template not found: {template_id}")

    draft = {
        "ok": True,
        "checkpoint": "033",
        "module": "k_os_knowledge_base_support_playbooks",
        "status": "response_draft_generated",
        "generated_at": now(),
        "ticket_id": ticket_id,
        "customer_alias": ticket.get("customer_alias"),
        "template_id": template_id,
        "subject": ticket.get("subject"),
        "draft_body": template.get("body"),
        "external_send_enabled": False,
        "external_send_performed": False,
        "requires_approval_before_send": True,
        "manual_approval_required": True,
        "next_checkpoint": "034 - K-Product Feedback and Feature Request Core"
    }

    DRAFT_JSON.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Response Draft",
        "",
        "Rascunho interno. Não enviar sem aprovação humana.",
        "",
        f"- Ticket: {ticket_id}",
        f"- Customer: {ticket.get('customer_alias')}",
        f"- Template: {template_id}",
        f"- External send performed: {draft.get('external_send_performed')}",
        f"- Requires approval: {draft.get('requires_approval_before_send')}",
        "",
        "## Draft",
        "",
        str(template.get("body", ""))
    ]

    DRAFT_MD.write_text("\n".join(lines), encoding="utf-8")
    event("knowledge.response_draft_generated", {"ticket_id": ticket_id, "template_id": template_id})
    return draft


def playbook_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    playbooks = report.get("playbooks", [])
    articles = report.get("articles", [])

    snapshot = {
        "ok": True,
        "checkpoint": "033",
        "module": "k_os_knowledge_base_support_playbooks",
        "status": "playbook_snapshot",
        "generated_at": now(),
        "approved_playbooks": [p for p in playbooks if p.get("status") == "approved_internal"],
        "draft_playbooks": [p for p in playbooks if p.get("status") == "draft"],
        "linked_articles": [a for a in articles if a.get("linked_ticket_ids")],
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    PLAYBOOK_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Support Playbook Snapshot",
        "",
        f"- Generated at: {snapshot.get('generated_at')}",
        f"- Approved playbooks: {len(snapshot.get('approved_playbooks', []))}",
        f"- Draft playbooks: {len(snapshot.get('draft_playbooks', []))}",
        f"- Linked articles: {len(snapshot.get('linked_articles', []))}",
        f"- External publish enabled: {snapshot.get('external_publish_enabled')}",
        "",
        "## Draft playbooks",
        ""
    ]

    if snapshot.get("draft_playbooks"):
        for item in snapshot.get("draft_playbooks", []):
            lines.append(f"- {item.get('playbook_id')} | {item.get('title')} | {item.get('category')}")
    else:
        lines.append("- Nenhum playbook em draft.")

    lines.extend(["", "## Linked articles", ""])

    if snapshot.get("linked_articles"):
        for item in snapshot.get("linked_articles", []):
            lines.append(f"- {item.get('article_id')} | {item.get('title')} | tickets={len(item.get('linked_ticket_ids', []))}")
    else:
        lines.append("- Nenhum artigo vinculado a ticket.")

    PLAYBOOK_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def compute_metrics(articles: list[dict[str, Any]], playbooks: list[dict[str, Any]], templates: list[dict[str, Any]], links: list[dict[str, Any]]) -> dict[str, Any]:
    article_status_counts: dict[str, int] = {}
    playbook_status_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}

    for article in articles:
        status = article.get("status", "unknown")
        category = article.get("category", "unknown")
        article_status_counts[status] = article_status_counts.get(status, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1

    for playbook in playbooks:
        status = playbook.get("status", "unknown")
        category = playbook.get("category", "unknown")
        playbook_status_counts[status] = playbook_status_counts.get(status, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1

    return {
        "article_count": len(articles),
        "playbook_count": len(playbooks),
        "template_count": len(templates),
        "ticket_link_count": len(links),
        "article_status_counts": article_status_counts,
        "playbook_status_counts": playbook_status_counts,
        "category_counts": category_counts
    }


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    policy = load_policy()

    articles = [safe_article(item) for item in registry.get("articles", [])]
    playbooks = [safe_playbook(item) for item in registry.get("playbooks", [])]
    templates = [safe_template(item) for item in registry.get("response_templates", [])]
    links = [safe_link(item) for item in registry.get("ticket_links", [])]
    activities = [safe_activity(item) for item in registry.get("activities", [])[-30:]]

    metrics = compute_metrics(articles, playbooks, templates, links)

    report = {
        "ok": True,
        "checkpoint": "033",
        "module": "k_os_knowledge_base_support_playbooks",
        "status": "audit_generated",
        "generated_at": now(),
        "knowledge_base_registry_path": "local_secrets/k_os_knowledge_base/knowledge_base_registry.json",
        "knowledge_base_registry_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "response_drafts_only": True,
        "articles": articles,
        "playbooks": playbooks,
        "response_templates": templates,
        "ticket_links": links,
        "recent_activities": activities,
        "metrics": metrics,
        "required_gates_before_customer_facing_use": policy.get("required_gates_before_customer_facing_use", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "034 - K-Product Feedback and Feature Request Core")
    }

    write_report(report)
    playbook_snapshot(report)
    event("knowledge.audit_generated", {"article_count": metrics["article_count"], "playbook_count": metrics["playbook_count"]})
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Knowledge Base and Support Playbooks",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Registry committed: {report.get('knowledge_base_registry_committed')}",
        f"- External send enabled: {report.get('external_send_enabled')}",
        f"- External publish enabled: {report.get('external_publish_enabled')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in report.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Articles", ""])

    if report.get("articles"):
        for item in report.get("articles", []):
            lines.append(f"- {item.get('article_id')} | {item.get('title')} | {item.get('category')} | {item.get('status')}")
    else:
        lines.append("- Nenhum artigo registrado.")

    lines.extend(["", "## Playbooks", ""])

    if report.get("playbooks"):
        for item in report.get("playbooks", []):
            lines.append(f"- {item.get('playbook_id')} | {item.get('title')} | {item.get('category')} | {item.get('status')} | steps={item.get('steps_count')}")
    else:
        lines.append("- Nenhum playbook registrado.")

    lines.extend(["", "## Response templates", ""])

    if report.get("response_templates"):
        for item in report.get("response_templates", []):
            lines.append(f"- {item.get('template_id')} | {item.get('title')} | approval={item.get('requires_approval_before_send')}")
    else:
        lines.append("- Nenhum template registrado.")

    lines.extend(["", "## Required gates before customer-facing use", ""])

    for gate in report.get("required_gates_before_customer_facing_use", []):
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
    parser.add_argument("--mode", choices=["init", "create-demo", "create-article", "create-playbook", "add-template", "link-ticket", "set-article-status", "set-playbook-status", "generate-draft", "audit", "show"], required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--category", default="support")
    parser.add_argument("--summary", default="")
    parser.add_argument("--content", default="")
    parser.add_argument("--steps", default="")
    parser.add_argument("--owner", default="k_os_operator")
    parser.add_argument("--ticket-id", default="")
    parser.add_argument("--article-id", default="")
    parser.add_argument("--playbook-id", default="")
    parser.add_argument("--template-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "create-article":
        if not args.title:
            raise SystemExit("Informe --title")
        result = create_article(args.title, args.category, args.summary, args.content, args.owner)

    elif args.mode == "create-playbook":
        if not args.title:
            raise SystemExit("Informe --title")
        steps = [item.strip() for item in args.steps.split("|") if item.strip()]
        if not steps:
            steps = ["triagem inicial", "revisão interna", "aprovação humana"]
        result = create_playbook(args.title, args.category, steps, args.owner)

    elif args.mode == "add-template":
        if not args.title:
            raise SystemExit("Informe --title")
        if not args.content:
            raise SystemExit("Informe --content")
        result = add_template(args.title, args.category, args.content, args.owner)

    elif args.mode == "link-ticket":
        result = link_ticket(args.ticket_id, args.article_id, args.playbook_id, args.reason)

    elif args.mode == "set-article-status":
        if not args.article_id:
            raise SystemExit("Informe --article-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = set_article_status(args.article_id, args.status, args.reason)

    elif args.mode == "set-playbook-status":
        if not args.playbook_id:
            raise SystemExit("Informe --playbook-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = set_playbook_status(args.playbook_id, args.status, args.reason)

    elif args.mode == "generate-draft":
        if not args.ticket_id:
            raise SystemExit("Informe --ticket-id")
        if not args.template_id:
            raise SystemExit("Informe --template-id")
        result = generate_response_draft(args.ticket_id, args.template_id)

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