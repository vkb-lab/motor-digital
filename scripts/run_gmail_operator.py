from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "local_runtime" / "google_oauth"
REPORTS = ROOT / "reports" / "gmail_operator"

CLIENT_SECRET_PATH = RUNTIME / "client_secret.json"

SCOPES = {
    "readonly": ["https://www.googleapis.com/auth/gmail.readonly"],
    "operator": ["https://www.googleapis.com/auth/gmail.modify"],
    "full_delete": ["https://mail.google.com/"],
}


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def token_path(profile: str) -> Path:
    safe = "".join(ch for ch in profile if ch.isalnum() or ch in ("_", "-")).strip() or "default"
    return RUNTIME / f"token_gmail_{safe}.json"


def deps_status() -> dict[str, Any]:
    libs = {}
    for name in [
        "googleapiclient.discovery",
        "google_auth_oauthlib.flow",
        "google.oauth2.credentials",
        "google.auth.transport.requests",
    ]:
        try:
            __import__(name)
            libs[name] = "ok"
        except Exception as exc:
            libs[name] = f"missing: {exc.__class__.__name__}"
    return libs


def require_google_libs():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        return Credentials, InstalledAppFlow, Request, build
    except Exception as exc:
        raise SystemExit(
            "[KOS] Dependencias Google ausentes. Rode:\n"
            "python -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib\n\n"
            f"Erro: {exc}"
        )


def load_service(profile: str, scope_preset: str, interactive: bool = False):
    Credentials, InstalledAppFlow, Request, build = require_google_libs()
    scopes = SCOPES[scope_preset]
    RUNTIME.mkdir(parents=True, exist_ok=True)

    tpath = token_path(profile)
    creds = None

    if tpath.exists():
        creds = Credentials.from_authorized_user_file(str(tpath), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not interactive:
                raise SystemExit(
                    "[KOS] Gmail nao autorizado ainda. Rode:\n"
                    f"python scripts\\run_gmail_operator.py --mode connect --profile {profile} --scope-preset {scope_preset}"
                )

            if not CLIENT_SECRET_PATH.exists():
                raise SystemExit(
                    "[KOS] client_secret.json nao encontrado.\n"
                    "Baixe o OAuth client JSON do Google Cloud app kaizen-home e salve em:\n"
                    f"{CLIENT_SECRET_PATH}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), scopes)
            creds = flow.run_local_server(port=0)

        tpath.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


def write_json_report(name: str, data: dict[str, Any]) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"{now_stamp()}_{name}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_md_report(name: str, lines: list[str]) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"{now_stamp()}_{name}.md"
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return path


def mode_status(args) -> None:
    data = {
        "status": "KOS_GMAIL_OPERATOR_STATUS",
        "profile": args.profile,
        "client_secret_present": CLIENT_SECRET_PATH.exists(),
        "token_present": token_path(args.profile).exists(),
        "deps": deps_status(),
        "scope_presets": SCOPES,
        "next_step": "connect" if not token_path(args.profile).exists() else "profile/report",
        "paths_redacted": True,
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))


def mode_connect(args) -> None:
    service = load_service(args.profile, args.scope_preset, interactive=True)
    profile = service.users().getProfile(userId="me").execute()
    data = {
        "status": "KOS_GMAIL_CONNECTED",
        "emailAddress": profile.get("emailAddress"),
        "messagesTotal": profile.get("messagesTotal"),
        "threadsTotal": profile.get("threadsTotal"),
        "historyId": profile.get("historyId"),
        "scope_preset": args.scope_preset,
        "token_path": str(token_path(args.profile)),
    }
    write_json_report("connect_profile", data)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def mode_profile(args) -> None:
    service = load_service(args.profile, args.scope_preset, interactive=False)
    profile = service.users().getProfile(userId="me").execute()
    print(json.dumps(profile, ensure_ascii=False, indent=2))


def _headers_to_dict(headers: list[dict[str, str]]) -> dict[str, str]:
    return {h.get("name", ""): h.get("value", "") for h in headers}


def classify_gmail_digest_category(text: str) -> str:
    value = str(text or "").lower()
    categories = [
        (
            "oportunidades/startup/crédito",
            ["render", "credit", "credits", "startup", "grant", "subsidy", "apoio", "programa", "cloud"],
        ),
        (
            "promoções/ofertas",
            ["mercado livre", "promoção", "promocao", "oferta", "desconto", "cupom", "sale"],
        ),
        (
            "serviços/infra/dev",
            ["github", "google cloud", "supabase", "render", "vercel", "openai", "api", "billing"],
        ),
        (
            "financeiro/cobrança",
            ["payment", "invoice", "cobrança", "cobranca", "fatura", "pagamento", "receipt"],
        ),
        (
            "documentos/anexos",
            ["attachment", "anexado", "invoice", "nota fiscal", "documento", "pdf", "contrato"],
        ),
        (
            "pessoal/família",
            ["família", "familia", "fotos", "photos", "drive", "compartilhado"],
        ),
    ]
    for category, words in categories:
        if any(word in value for word in words):
            return category
    return "outros"


def _payload_has_attachments(payload: dict[str, Any]) -> bool:
    stack = [payload]
    while stack:
        item = stack.pop()
        filename = str(item.get("filename") or "").strip()
        body = item.get("body") or {}
        if filename or body.get("attachmentId"):
            return True
        for part in item.get("parts") or []:
            if isinstance(part, dict):
                stack.append(part)
    return False


def _short_snippet(value: str, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def mode_report(args) -> None:
    service = load_service(args.profile, args.scope_preset, interactive=False)

    query = args.query or "newer_than:7d"
    result = service.users().messages().list(userId="me", q=query, maxResults=args.max_results).execute()
    messages = result.get("messages", [])

    items = []
    for msg in messages:
        full = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()

        headers = _headers_to_dict(full.get("payload", {}).get("headers", []))
        subject = headers.get("Subject", "")
        sender = headers.get("From", "")
        snippet = _short_snippet(full.get("snippet", ""))
        category = classify_gmail_digest_category(" ".join([sender, subject, snippet, " ".join(full.get("labelIds", []))]))
        items.append({
            "id": full.get("id"),
            "threadId": full.get("threadId"),
            "internalDate": full.get("internalDate"),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": subject,
            "date": headers.get("Date", ""),
            "snippet": snippet,
            "labelIds": full.get("labelIds", []),
            "has_attachments": _payload_has_attachments(full.get("payload", {})),
            "category": category,
            "sizeEstimate": full.get("sizeEstimate"),
        })

    data = {
        "status": "KOS_GMAIL_REPORT_READY",
        "profile": args.profile,
        "query": query,
        "count": len(items),
        "items": items,
    }

    json_path = write_json_report("report_raw", data)

    lines = [
        "# KOS Gmail Report",
        "",
        f"Query: `{query}`",
        f"Mensagens analisadas: {len(items)}",
        "",
        "## Emails",
    ]

    for i, item in enumerate(items, 1):
        lines.extend([
            f"### {i}. {item.get('subject') or '(sem assunto)'}",
            f"- From: {item.get('from')}",
            f"- Date: {item.get('date')}",
            f"- ID: `{item.get('id')}`",
            f"- Labels: {', '.join(item.get('labelIds') or [])}",
            f"- Categoria: {item.get('category')}",
            f"- Anexos: {'sim' if item.get('has_attachments') else 'nao'}",
            f"- Resumo curto: {item.get('snippet')}",
            "",
        ])

    md_path = write_md_report("report", lines)

    print(json.dumps({
        "status": "KOS_GMAIL_REPORT_READY",
        "count": len(items),
        "items": items,
        "json_report": str(json_path),
        "md_report": str(md_path),
    }, ensure_ascii=False, indent=2))


def mode_read(args) -> None:
    if not args.message_id:
        raise SystemExit("[KOS] --message-id obrigatorio para read")

    service = load_service(args.profile, args.scope_preset, interactive=False)
    msg = service.users().messages().get(userId="me", id=args.message_id, format="full").execute()

    data = {
        "status": "KOS_GMAIL_MESSAGE_READ",
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "labelIds": msg.get("labelIds", []),
        "snippet": msg.get("snippet", ""),
        "payload_headers": _headers_to_dict(msg.get("payload", {}).get("headers", [])),
    }
    path = write_json_report("message_read_raw", data)
    print(json.dumps({"status": data["status"], "report": str(path), "snippet": data["snippet"]}, ensure_ascii=False, indent=2))


def _mime_message(to: str, subject: str, body: str) -> dict[str, str]:
    message = MIMEText(body, "plain", "utf-8")
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw}


def mode_send(args) -> None:
    if args.confirm != "SEND_GMAIL":
        raise SystemExit("[KOS] Envio bloqueado. Use --confirm SEND_GMAIL")

    if not args.to or not args.subject or not args.body:
        raise SystemExit("[KOS] --to, --subject e --body sao obrigatorios para send")

    service = load_service(args.profile, args.scope_preset, interactive=False)
    sent = service.users().messages().send(
        userId="me",
        body=_mime_message(args.to, args.subject, args.body)
    ).execute()

    print(json.dumps({"status": "KOS_GMAIL_SENT", "id": sent.get("id"), "threadId": sent.get("threadId")}, ensure_ascii=False, indent=2))


def mode_trash(args) -> None:
    if args.confirm != "TRASH_GMAIL":
        raise SystemExit("[KOS] Lixeira bloqueada. Use --confirm TRASH_GMAIL")
    if not args.message_id:
        raise SystemExit("[KOS] --message-id obrigatorio para trash")

    service = load_service(args.profile, args.scope_preset, interactive=False)
    result = service.users().messages().trash(userId="me", id=args.message_id).execute()
    print(json.dumps({"status": "KOS_GMAIL_TRASHED", "id": result.get("id"), "labelIds": result.get("labelIds", [])}, ensure_ascii=False, indent=2))


def mode_delete(args) -> None:
    if not args.allow_permanent_delete or args.confirm != "PERMANENT_DELETE_GMAIL":
        raise SystemExit("[KOS] Delete permanente bloqueado. Prefira --mode trash. Para forcar: --allow-permanent-delete --confirm PERMANENT_DELETE_GMAIL")
    if args.scope_preset != "full_delete":
        raise SystemExit("[KOS] Delete permanente exige --scope-preset full_delete")
    if not args.message_id:
        raise SystemExit("[KOS] --message-id obrigatorio para delete")

    service = load_service(args.profile, args.scope_preset, interactive=False)
    service.users().messages().delete(userId="me", id=args.message_id).execute()
    print(json.dumps({"status": "KOS_GMAIL_PERMANENTLY_DELETED", "id": args.message_id}, ensure_ascii=False, indent=2))


def mode_modify(args) -> None:
    if not args.message_id:
        raise SystemExit("[KOS] --message-id obrigatorio para modify")

    add = [x.strip() for x in (args.add_labels or "").split(",") if x.strip()]
    remove = [x.strip() for x in (args.remove_labels or "").split(",") if x.strip()]

    if not add and not remove:
        raise SystemExit("[KOS] Use --add-labels ou --remove-labels")

    service = load_service(args.profile, args.scope_preset, interactive=False)
    result = service.users().messages().modify(
        userId="me",
        id=args.message_id,
        body={"addLabelIds": add, "removeLabelIds": remove},
    ).execute()

    print(json.dumps({"status": "KOS_GMAIL_MODIFIED", "id": result.get("id"), "labelIds": result.get("labelIds", [])}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="K-OS Gmail Operator Bridge")
    parser.add_argument("--mode", required=True, choices=["status", "connect", "profile", "report", "read", "send", "trash", "delete", "modify"])
    parser.add_argument("--profile", default="default")
    parser.add_argument("--scope-preset", default="operator", choices=list(SCOPES.keys()))
    parser.add_argument("--query", default="")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--message-id", default="")
    parser.add_argument("--to", default="")
    parser.add_argument("--subject", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--confirm", default="")
    parser.add_argument("--allow-permanent-delete", action="store_true")
    parser.add_argument("--add-labels", default="")
    parser.add_argument("--remove-labels", default="")
    args = parser.parse_args()

    if args.mode == "status":
        mode_status(args)
    elif args.mode == "connect":
        mode_connect(args)
    elif args.mode == "profile":
        mode_profile(args)
    elif args.mode == "report":
        mode_report(args)
    elif args.mode == "read":
        mode_read(args)
    elif args.mode == "send":
        mode_send(args)
    elif args.mode == "trash":
        mode_trash(args)
    elif args.mode == "delete":
        mode_delete(args)
    elif args.mode == "modify":
        mode_modify(args)


if __name__ == "__main__":
    main()
