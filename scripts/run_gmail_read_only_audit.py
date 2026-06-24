from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "local_runtime" / "kos_gmail_read_only" / "latest_gmail_read_only_audit.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATHS = [
    ROOT / "local_runtime" / "kos_secrets" / "gmail_token.json",
    ROOT / "local_runtime" / "secrets" / "gmail_token.json",
    ROOT / "memory" / "kos_governance" / "gmail_token.json",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_report(payload: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_token_payload() -> tuple[dict[str, Any] | None, str]:
    env_json = os.environ.get("KOS_GMAIL_TOKEN_JSON", "").strip() or os.environ.get("GMAIL_TOKEN_JSON", "").strip()
    if env_json:
        if env_json.startswith("{"):
            return json.loads(env_json), "env:KOS_GMAIL_TOKEN_JSON"
        path = Path(env_json)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig")), str(path)

    for path in TOKEN_PATHS:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig")), str(path)

    return None, ""


def header_value(headers: list[dict[str, str]], name: str) -> str:
    for header in headers:
        if str(header.get("name", "")).lower() == name.lower():
            return str(header.get("value", ""))
    return ""


def sanitize_message(message: dict[str, Any]) -> dict[str, str]:
    payload = message.get("payload", {}) or {}
    headers = payload.get("headers", []) or []
    return {
        "id": str(message.get("id", "")),
        "thread_id": str(message.get("threadId", "")),
        "from": header_value(headers, "From")[:180],
        "subject": header_value(headers, "Subject")[:220],
        "date": header_value(headers, "Date")[:120],
        "snippet": str(message.get("snippet", ""))[:240],
    }


def build_missing_token_report(detail: str = "") -> dict[str, Any]:
    return {
        "status": "KOS_GMAIL_READ_ONLY_TOKEN_MISSING",
        "created_at": now_iso(),
        "read_only": True,
        "email_sent": False,
        "email_deleted": False,
        "email_archived": False,
        "token_printed": False,
        "detail": detail,
        "expected_token_locations": [str(path) for path in TOKEN_PATHS],
        "accepted_env": ["KOS_GMAIL_TOKEN_JSON", "GMAIL_TOKEN_JSON"],
        "next_step": "Autorizar Gmail OAuth uma vez e salvar token autorizado em local_runtime/kos_secrets/gmail_token.json.",
    }


def build_audit(limit: int = 10) -> dict[str, Any]:
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except Exception as exc:
        return {
            "status": "KOS_GMAIL_READ_ONLY_DEPENDENCY_MISSING",
            "created_at": now_iso(),
            "error": str(exc),
            "read_only": True,
            "email_sent": False,
            "email_deleted": False,
            "email_archived": False,
        }

    token_payload, source = load_token_payload()
    if not token_payload:
        return build_missing_token_report()

    try:
        creds = Credentials.from_authorized_user_info(token_payload, scopes=SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        if not creds.valid:
            return build_missing_token_report("Token encontrado, mas nao esta valido para Gmail read-only.")

        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        profile = service.users().getProfile(userId="me").execute()
        listed = service.users().messages().list(
            userId="me",
            maxResults=max(1, min(int(limit), 25)),
            q="newer_than:30d",
        ).execute()
        messages = []
        for item in listed.get("messages", []) or []:
            msg = service.users().messages().get(
                userId="me",
                id=item.get("id"),
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()
            messages.append(sanitize_message(msg))

        return {
            "status": "KOS_GMAIL_READ_ONLY_CONNECTED",
            "created_at": now_iso(),
            "token_source": source,
            "email_address": profile.get("emailAddress"),
            "messages_total_estimate": profile.get("messagesTotal"),
            "threads_total_estimate": profile.get("threadsTotal"),
            "messages_returned": len(messages),
            "messages": messages,
            "read_only": True,
            "email_sent": False,
            "email_deleted": False,
            "email_archived": False,
            "token_printed": False,
        }
    except Exception as exc:
        return {
            "status": "KOS_GMAIL_READ_ONLY_ERROR",
            "created_at": now_iso(),
            "error": str(exc)[:900],
            "read_only": True,
            "email_sent": False,
            "email_deleted": False,
            "email_archived": False,
            "token_printed": False,
        }


def main() -> int:
    limit = 10
    if "--limit" in sys.argv:
        try:
            limit = int(sys.argv[sys.argv.index("--limit") + 1])
        except Exception:
            limit = 10

    report = build_audit(limit=limit)
    write_report(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") in {"KOS_GMAIL_READ_ONLY_CONNECTED", "KOS_GMAIL_READ_ONLY_TOKEN_MISSING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
