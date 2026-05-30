from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_lan_access_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LANCockpitAccess:
    def __init__(
        self,
        project_root: str | Path = ".",
        memory_dir: str | Path = "memory/lan_cockpit_access",
        reports_dir: str | Path = "reports/lan_cockpit_access",
    ) -> None:
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir

    def local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return "unknown"

    def build_plan(self, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
        data = dict(request or {"mode": "readiness"})
        validation = validate_lan_access_request(data)
        ip = self.local_ip()
        port = int(data.get("port", 8506))

        report = {
            "ok": validation["ok"],
            "checkpoint": "81",
            "name": "LAN Cockpit Access",
            "plan_id": str(uuid4()),
            "generated_at": utc_now(),
            "status": "lan_readiness_ready" if validation["ok"] else "blocked_by_policy",
            "request_validation": validation,
            "network": {
                "local_ip": ip,
                "recommended_url": f"http://{ip}:{port}",
                "safe_default_url": f"http://127.0.0.1:{port}",
                "bind_for_lan": "0.0.0.0",
                "port": port,
            },
            "execution_enabled": False,
            "server_started": False,
            "firewall_changed": False,
            "public_exposure_allowed": False,
            "guardrails": [
                "nao abre firewall",
                "nao inicia servidor sem aprovacao",
                "nao cria tunel publico",
                "usar apenas em rede confiavel",
            ],
        }
        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_lan_cockpit_access.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        (self.reports_dir / "latest_lan_cockpit_access.md").write_text(self.to_markdown(report), encoding="utf-8")

    def to_markdown(self, report: dict[str, Any]) -> str:
        net = report.get("network", {})
        lines = [
            "# K-Atlas LAN Cockpit Access",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## URLs",
            "",
            f"- Local safe: {net.get('safe_default_url')}",
            f"- LAN: {net.get('recommended_url')}",
            "",
            "## Guardrails",
            "",
        ]
        for item in report.get("guardrails", []):
            lines.append(f"- {item}")
        return "\n".join(lines)
