from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from k_atlas.core.local_api_auth_policy.policy import validate_local_api_runtime_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SecureLocalApiRuntime:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/secure_local_api_runtime",
        memory_dir: str | Path = "memory/secure_local_api_runtime",
        reports_dir: str | Path = "reports/secure_local_api_runtime",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.config_path = self.live_dir / "server_config.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_config(self, host: str = "127.0.0.1", port: int = 8787) -> dict[str, Any]:
        request = {
            "bind_host": host,
            "port": port,
            "auto_execute": False,
            "remote_control_enabled": False,
            "external_public_access": False,
            "mouse_automation": False,
            "browser_automation": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
        }
        validation = validate_local_api_runtime_request(request)

        config = {
            "ok": validation["ok"],
            "checkpoint": "89",
            "name": "Secure Local API Runtime",
            "generated_at": utc_now(),
            "runtime_id": str(uuid4()),
            "host": host,
            "port": port,
            "base_url": f"http://{host}:{port}",
            "status": "ready_to_start" if validation["ok"] else "blocked_by_policy",
            "validation": validation,
            "endpoints": [
                {"method": "GET", "path": "/health", "effect": "read_only"},
                {"method": "GET", "path": "/state", "effect": "read_only"},
                {"method": "POST", "path": "/approval-request", "effect": "queue_only"},
            ],
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "local_files_only",
            "guardrails": [
                "bind padrao somente em 127.0.0.1",
                "sem acesso publico direto",
                "sem controle de mouse",
                "sem automacao de navegador",
                "sem execucao automatica",
                "toda acao real exige aprovacao humana",
            ],
        }

        self.live_dir.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        self.save_report(config)
        self.event("secure_local_api_runtime.config_built", {"host": host, "port": port, "ok": validation["ok"]})
        return config

    def status(self) -> dict[str, Any]:
        if self.config_path.exists():
            try:
                config = json.loads(self.config_path.read_text(encoding="utf-8"))
            except Exception:
                config = None
        else:
            config = None

        if config is None:
            config = self.build_config()

        return {
            "ok": True,
            "checkpoint": "89",
            "name": "Secure Local API Runtime",
            "generated_at": utc_now(),
            "status": "operational",
            "config": config,
            "start_command": "powershell -ExecutionPolicy Bypass -File .\\ops\\start_secure_local_api_runtime.ps1",
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_secure_local_api_runtime.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_secure_local_api_runtime.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas Secure Local API Runtime",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Base URL: {report.get('base_url')}",
            "",
            "## Guardrails",
            "",
        ]
        for item in report.get("guardrails", []):
            lines.append(f"- {item}")
        return "\n".join(lines)
