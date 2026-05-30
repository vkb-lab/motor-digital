from __future__ import annotations

import json
import os
import platform
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .policy import validate_remote_assist_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RemoteAssistReadiness:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/remote_assist_readiness",
        memory_dir: str | Path = "memory/remote_assist_readiness",
        reports_dir: str | Path = "reports/remote_assist_readiness",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.events_path = self.memory_dir / "events.jsonl"
        self.live_state_path = self.live_dir / "readiness_state.json"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def detect_lan_ipv4(self) -> list[str]:
        candidates: set[str] = set()

        try:
            hostname = socket.gethostname()
            for item in socket.getaddrinfo(hostname, None, socket.AF_INET):
                ip = item[4][0]
                if not ip.startswith("127."):
                    candidates.add(ip)
        except Exception:
            pass

        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.settimeout(0.2)
            probe.connect(("8.8.8.8", 80))
            ip = probe.getsockname()[0]
            probe.close()
            if ip and not ip.startswith("127."):
                candidates.add(ip)
        except Exception:
            pass

        return sorted(candidates)

    def check_local_port(self, port: int) -> dict[str, Any]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.15)

        try:
            result = sock.connect_ex(("127.0.0.1", int(port)))
            open_local = result == 0
        except Exception:
            open_local = False
        finally:
            sock.close()

        return {
            "port": int(port),
            "host": "127.0.0.1",
            "open_local": open_local,
            "public_exposure_checked": False,
        }

    def collect_machine_profile(self) -> dict[str, Any]:
        return {
            "hostname": socket.gethostname(),
            "username": os.environ.get("USERNAME") or os.environ.get("USER") or "unknown",
            "platform": platform.platform(),
            "system": platform.system(),
            "lan_ipv4": self.detect_lan_ipv4(),
        }

    def collect_port_profile(self) -> list[dict[str, Any]]:
        ports = [8501, 8502, 8503, 8504, 8505, 8765, 8787]
        return [self.check_local_port(port) for port in ports]

    def build_readiness(self, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
        request_data = dict(request or {
            "mode": "lan_readiness",
            "network_scope": "lan_only",
            "human_approved": False,
            "public_exposure_enabled": False,
            "remote_control_enabled": False,
            "unattended_access_enabled": False,
            "mouse_automation": False,
            "keyboard_automation": False,
            "credential_capture_enabled": False,
            "password_storage_enabled": False,
            "auto_execute": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "external_api_enabled": False,
        })

        policy = validate_remote_assist_request(request_data)
        machine = self.collect_machine_profile()
        ports = self.collect_port_profile()

        lan_available = len(machine.get("lan_ipv4", [])) > 0
        streamlit_ports = [item for item in ports if item["port"] in {8501, 8502, 8503, 8504, 8505}]
        any_streamlit_local = any(item["open_local"] for item in streamlit_ports)

        report = {
            "ok": policy["ok"],
            "checkpoint": "78",
            "name": "K-Atlas Remote Assist Readiness",
            "generated_at": utc_now(),
            "status": "ready_for_lan_assist_design" if policy["ok"] else "blocked_by_policy",
            "policy": policy,
            "machine": machine,
            "ports": ports,
            "summary": {
                "lan_ipv4_detected": lan_available,
                "streamlit_local_detected": any_streamlit_local,
                "remote_control_enabled": False,
                "public_exposure_enabled": False,
                "unattended_access_enabled": False,
                "external_side_effects": "local_inspection_only",
                "next_checkpoint": "79 - Secure Local API",
            },
            "remote_assist_model": {
                "phase": "readiness_only",
                "control_plane": "local_control_plane",
                "allowed_scope_now": "local_only_or_lan_design",
                "future_scope": "approved_tunnel_gate",
                "human_approval_required": True,
                "automatic_remote_control_allowed": False,
            },
            "guardrails": [
                "nao abre porta publica",
                "nao inicia tunel remoto",
                "nao controla mouse",
                "nao digita teclado",
                "nao captura senha",
                "nao salva credenciais",
                "nao executa acao remota",
                "apenas coleta readiness local e LAN",
            ],
        }

        self.save_report(report)
        self.event("remote_assist_readiness.report_built", {
            "status": report["status"],
            "lan_ipv4_detected": lan_available,
            "streamlit_local_detected": any_streamlit_local,
        })

        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.live_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_remote_assist_readiness.json"
        md_path = self.reports_dir / "latest_remote_assist_readiness.md"

        payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)

        json_path.write_text(payload, encoding="utf-8")
        self.live_state_path.write_text(payload, encoding="utf-8")
        md_path.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        machine = report.get("machine", {})
        ports = report.get("ports", [])

        lines = [
            "# K-Atlas Remote Assist Readiness",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Machine",
            "",
            f"- Hostname: {machine.get('hostname')}",
            f"- LAN IPv4: {', '.join(machine.get('lan_ipv4', [])) or 'none'}",
            "",
            "## Summary",
            "",
            f"- LAN IPv4 detected: {summary.get('lan_ipv4_detected')}",
            f"- Streamlit local detected: {summary.get('streamlit_local_detected')}",
            f"- Remote control enabled: {summary.get('remote_control_enabled')}",
            f"- Public exposure enabled: {summary.get('public_exposure_enabled')}",
            f"- Next checkpoint: {summary.get('next_checkpoint')}",
            "",
            "## Local ports",
            "",
        ]

        for item in ports:
            lines.append(f"- {item.get('host')}:{item.get('port')} open_local={item.get('open_local')}")

        lines.extend(["", "## Guardrails", ""])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
