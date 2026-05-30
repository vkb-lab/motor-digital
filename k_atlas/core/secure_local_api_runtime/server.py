from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4


ROOT = Path.cwd()
APPROVAL_QUEUE = ROOT / "live" / "local_api_approval_bridge" / "api_approval_queue.json"
AUDIT_LEDGER = ROOT / "memory" / "local_api_audit_ledger" / "events.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_list(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def audit(event_type: str, payload: dict[str, Any]) -> None:
    AUDIT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
    with AUDIT_LEDGER.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


class LocalApiHandler(BaseHTTPRequestHandler):
    server_version = "KAtlasSecureLocalAPI/0.1"

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_json(200, {
                "ok": True,
                "service": "k_atlas_secure_local_api",
                "status": "healthy",
                "generated_at": utc_now(),
                "execution_enabled": False,
                "remote_control_enabled": False,
            })
            return

        if self.path == "/state":
            self.send_json(200, {
                "ok": True,
                "service": "k_atlas_secure_local_api",
                "status": "read_only",
                "approval_queue_total": len(load_list(APPROVAL_QUEUE)),
                "external_side_effects": "none",
            })
            return

        self.send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/approval-request":
            self.send_json(404, {"ok": False, "error": "not_found"})
            return

        content_length = int(self.headers.get("Content-Length", "0") or "0")
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"

        try:
            payload = json.loads(raw_body)
        except Exception:
            self.send_json(400, {"ok": False, "error": "invalid_json"})
            return

        item = {
            "approval_request_id": str(uuid4()),
            "created_at": utc_now(),
            "status": "waiting_human_approval",
            "payload": payload,
            "automatic_execution_allowed": False,
            "real_execution_enabled": False,
            "external_side_effects": "queue_only",
        }

        queue = load_list(APPROVAL_QUEUE)
        queue.append(item)
        save_list(APPROVAL_QUEUE, queue)
        audit("secure_local_api.approval_request_queued", item)

        self.send_json(202, item)

    def log_message(self, format: str, *args: Any) -> None:
        audit("secure_local_api.http_log", {"client": self.address_string(), "message": format % args})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    if args.host not in {"127.0.0.1", "localhost"}:
        raise SystemExit("Host bloqueado. Use 127.0.0.1 nesta fase.")

    server = HTTPServer((args.host, args.port), LocalApiHandler)
    print(f"K-Atlas Secure Local API Runtime em http://{args.host}:{args.port}")
    print("Somente localhost. Sem execucao automatica.")
    server.serve_forever()


if __name__ == "__main__":
    main()
