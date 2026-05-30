from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


CORE_COMPONENTS = [
    {"id": "73", "name": "Local Mission Installer", "path": "k_atlas/core/local_mission_installer"},
    {"id": "74", "name": "Mission Pack Generator", "path": "k_atlas/core/mission_pack_generator"},
    {"id": "75", "name": "Mission Pack Bridge", "path": "k_atlas/core/mission_pack_bridge"},
    {"id": "76", "name": "Mission Pipeline Runner", "path": "k_atlas/core/mission_pipeline_runner"},
    {"id": "77", "name": "Local Control Plane", "path": "k_atlas/core/local_control_plane"},
    {"id": "78", "name": "Remote Assist Readiness", "path": "k_atlas/core/remote_assist_readiness"},
    {"id": "79", "name": "Secure Local API Readiness", "path": "pages/79_K_Atlas_Secure_Local_API_Readiness.py"},
    {"id": "80", "name": "Operator Approval Console", "path": "pages/80_K_Atlas_Operator_Approval_Console.py"},
    {"id": "81", "name": "LAN Cockpit Access", "path": "pages/81_K_Atlas_LAN_Cockpit_Access.py"},
    {"id": "82", "name": "Remote Tunnel Gate", "path": "pages/82_K_Atlas_Remote_Tunnel_Gate.py"},
    {"id": "83", "name": "Local OS Shell", "path": "pages/83_K_Atlas_Local_OS_Shell.py"},
    {"id": "84", "name": "Local Action Contracts", "path": "pages/84_K_Atlas_Local_Action_Contracts.py"},
    {"id": "85", "name": "Local Action Router", "path": "pages/85_K_Atlas_Local_Action_Router.py"},
    {"id": "86", "name": "Local Execution Queue", "path": "pages/86_K_Atlas_Local_Execution_Queue.py"},
    {"id": "87", "name": "Local Action Audit Ledger", "path": "pages/87_K_Atlas_Local_Action_Audit_Ledger.py"},
    {"id": "88", "name": "Assisted Execution Dashboard", "path": "pages/88_K_Atlas_Assisted_Execution_Dashboard.py"},
    {"id": "89", "name": "Secure Local API Runtime", "path": "pages/89_K_Atlas_Secure_Local_API_Runtime.py"},
    {"id": "90", "name": "Local API Auth Policy", "path": "pages/90_K_Atlas_Local_API_Auth_Policy.py"},
    {"id": "91", "name": "API Approval Bridge", "path": "pages/91_K_Atlas_API_Approval_Bridge.py"},
    {"id": "92", "name": "API Audit Ledger", "path": "pages/92_K_Atlas_API_Audit_Ledger.py"},
    {"id": "93", "name": "Secure Local API Dashboard", "path": "pages/93_K_Atlas_Secure_Local_API_Dashboard.py"},
    {"id": "94", "name": "Autonomy Policy Engine", "path": "pages/94_K_Atlas_Autonomy_Policy_Engine.py"},
    {"id": "95", "name": "Safe Task Planner", "path": "pages/95_K_Atlas_Safe_Task_Planner.py"},
    {"id": "96", "name": "Supervised Autonomy Queue", "path": "pages/96_K_Atlas_Supervised_Autonomy_Queue.py"},
    {"id": "97", "name": "Autonomy Audit Monitor", "path": "pages/97_K_Atlas_Autonomy_Audit_Monitor.py"},
    {"id": "98", "name": "Supervised Autonomy Dashboard", "path": "pages/98_K_Atlas_Supervised_Autonomy_Dashboard.py"},
    {"id": "99", "name": "Local OS MVP Readiness", "path": "pages/99_K_Atlas_Local_OS_MVP_Readiness.py"},
    {"id": "100", "name": "Local OS Release Capsule", "path": "pages/100_K_Atlas_Local_OS_Release_Capsule.py"},
]


class LocalOSHealthCheck:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/local_os_health_check",
        memory_dir: str | Path = "memory/local_os_health_check",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir
        self.memory_dir = self.project_root / memory_dir
        self.events_path = self.memory_dir / "events.jsonl"

    def exists(self, path: str) -> bool:
        return (self.project_root / path).exists()

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def collect(self) -> dict[str, Any]:
        rows = []
        for item in CORE_COMPONENTS:
            ready = self.exists(item["path"])
            rows.append({**item, "ready": ready, "status": "ok" if ready else "missing"})

        ready_count = len([item for item in rows if item["ready"]])
        total = len(rows)
        readiness = round((ready_count / total) * 100, 2) if total else 0.0

        report = {
            "ok": True,
            "checkpoint": "101",
            "name": "Local OS Health Check",
            "generated_at": utc_now(),
            "status": "healthy" if readiness >= 80 else "attention_required",
            "summary": {
                "components_total": total,
                "components_ready": ready_count,
                "readiness": readiness,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_files_only",
                "python_version": platform.python_version(),
                "platform": platform.platform(),
            },
            "components": rows,
            "guardrails": [
                "health check apenas observa",
                "nao executa acoes reais",
                "nao publica",
                "nao abre porta publica",
                "nao move mouse",
            ],
        }

        self.save_report(report)
        self.event("local_os_health_check.collected", report["summary"])
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_local_os_health_check.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_local_os_health_check.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Local OS Health Check",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Readiness: {summary.get('readiness')}",
            "",
            "## Components",
            "",
        ]
        for item in report.get("components", []):
            lines.append(f"- {item.get('id')} - {item.get('name')} - {item.get('status')}")
        return "\n".join(lines)
