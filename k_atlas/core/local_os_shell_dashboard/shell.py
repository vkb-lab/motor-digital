from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from k_atlas.core.secure_local_api_readiness.api import SecureLocalApiReadiness
from k_atlas.core.operator_approval_console.console import OperatorApprovalConsole
from k_atlas.core.lan_cockpit_access.lan import LANCockpitAccess
from k_atlas.core.remote_tunnel_gate.gate import RemoteTunnelGate


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalOSShellDashboard:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/local_os_shell_dashboard",
        memory_dir: str | Path = "memory/local_os_shell_dashboard",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir
        self.memory_dir = self.project_root / memory_dir

    def exists(self, path: str) -> bool:
        return (self.project_root / path).exists()

    def build_components(self) -> list[dict[str, Any]]:
        rows = [
            {"checkpoint": "77", "name": "Local Control Plane", "path": "k_atlas/core/local_control_plane", "role": "control plane local"},
            {"checkpoint": "78", "name": "Remote Assist Readiness", "path": "k_atlas/core/remote_assist_readiness", "role": "readiness remoto seguro"},
            {"checkpoint": "79", "name": "Secure Local API Readiness", "path": "k_atlas/core/secure_local_api_readiness", "role": "base para API local"},
            {"checkpoint": "80", "name": "Operator Approval Console", "path": "k_atlas/core/operator_approval_console", "role": "aprovacao humana"},
            {"checkpoint": "81", "name": "LAN Cockpit Access", "path": "k_atlas/core/lan_cockpit_access", "role": "acesso LAN planejado"},
            {"checkpoint": "82", "name": "Remote Tunnel Gate", "path": "k_atlas/core/remote_tunnel_gate", "role": "gate remoto sem tunel real"},
        ]
        final = []
        for row in rows:
            ok = self.exists(row["path"])
            final.append({**row, "status": "operational" if ok else "missing"})
        return final

    def build_report(self) -> dict[str, Any]:
        api = SecureLocalApiReadiness(project_root=self.project_root).build_report({"mode": "readiness", "bind_address": "127.0.0.1"})
        approvals = OperatorApprovalConsole(project_root=self.project_root).summary()
        lan = LANCockpitAccess(project_root=self.project_root).build_plan({"mode": "readiness", "port": 8506})
        tunnel = RemoteTunnelGate(project_root=self.project_root).summary()
        components = self.build_components()
        operational = len([x for x in components if x["status"] == "operational"])

        report = {
            "ok": operational >= 4,
            "checkpoint": "83",
            "name": "K-Atlas Local OS Shell Dashboard",
            "generated_at": utc_now(),
            "status": "operational" if operational >= 4 else "partial",
            "summary": {
                "components_total": len(components),
                "components_operational": operational,
                "local_os_ready": operational >= 4,
                "remote_control_enabled": False,
                "external_side_effects": "local_files_only",
                "next_checkpoint": "84 - Local OS Action Router",
            },
            "components": components,
            "secure_local_api": api,
            "operator_approval_console": approvals.get("summary"),
            "lan_cockpit_access": lan.get("network"),
            "remote_tunnel_gate": tunnel.get("summary"),
            "guardrails": [
                "shell apenas observa e organiza",
                "shell nao controla mouse",
                "shell nao captura senha",
                "shell nao abre porta publica",
                "shell nao executa missao sem aprovacao",
            ],
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_local_os_shell_dashboard.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        (self.reports_dir / "latest_local_os_shell_dashboard.md").write_text(self.to_markdown(report), encoding="utf-8")

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Local OS Shell Dashboard",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Components total: {summary.get('components_total')}",
            f"- Components operational: {summary.get('components_operational')}",
            f"- Local OS ready: {summary.get('local_os_ready')}",
            f"- Remote control enabled: {summary.get('remote_control_enabled')}",
            f"- Next checkpoint: {summary.get('next_checkpoint')}",
            "",
            "## Components",
            "",
        ]
        for item in report.get("components", []):
            lines.append(f"- {item.get('checkpoint')} - {item.get('name')} - {item.get('status')}")
        return "\n".join(lines)
