from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_local_api_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SecureLocalApiReadiness:
    def __init__(
        self,
        project_root: str | Path = ".",
        memory_dir: str | Path = "memory/secure_local_api_readiness",
        reports_dir: str | Path = "reports/secure_local_api_readiness",
    ) -> None:
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def local_ip(self) -> str:
        try:
            host = socket.gethostname()
            return socket.gethostbyname(host)
        except Exception:
            return "unknown"

    def build_report(self, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
        data = dict(request or {"mode": "readiness", "bind_address": "127.0.0.1"})
        validation = validate_local_api_request(data)
        report_id = str(uuid4())

        report = {
            "ok": validation["ok"],
            "checkpoint": "79",
            "name": "Secure Local API Readiness",
            "report_id": report_id,
            "generated_at": utc_now(),
            "status": "ready_for_localhost_api" if validation["ok"] else "blocked_by_policy",
            "request_validation": validation,
            "network": {
                "hostname": socket.gethostname(),
                "local_ip": self.local_ip(),
                "default_safe_bind": "127.0.0.1",
                "lan_bind_requires_human_approval": True,
                "public_bind_allowed": False,
            },
            "allowed_ports": [8501, 8502, 8503, 8504, 8505, 8765],
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "readiness nao abre servidor",
                "readiness nao altera firewall",
                "readiness nao expÃµe porta publica",
                "readiness nao executa comandos remotos",
                "readiness exige aprovacao humana para LAN",
            ],
        }

        self.save_report(report)
        self.event("secure_local_api_readiness.report_built", {"report_id": report_id, "status": report["status"]})
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_secure_local_api_readiness.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        (self.reports_dir / "latest_secure_local_api_readiness.md").write_text(self.to_markdown(report), encoding="utf-8")

    def to_markdown(self, report: dict[str, Any]) -> str:
        network = report.get("network", {})
        lines = [
            "# K-Atlas Secure Local API Readiness",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Network",
            "",
            f"- Hostname: {network.get('hostname')}",
            f"- Local IP: {network.get('local_ip')}",
            f"- Default bind: {network.get('default_safe_bind')}",
            f"- Public bind allowed: {network.get('public_bind_allowed')}",
            "",
            "## Guardrails",
            "",
        ]
        for item in report.get("guardrails", []):
            lines.append(f"- {item}")
        return "\n".join(lines)
