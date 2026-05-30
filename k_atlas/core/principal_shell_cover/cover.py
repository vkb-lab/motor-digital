from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PrincipalShellCover:
    def __init__(
        self,
        project_root: str | Path = ".",
        memory_dir: str | Path = "memory/principal_shell_cover",
        reports_dir: str | Path = "reports/principal_shell_cover",
    ) -> None:
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.events_path = self.memory_dir / "events.jsonl"

    def exists(self, path: str) -> bool:
        return (self.project_root / path).exists()

    def load_json(self, path: str) -> Any:
        target = self.project_root / path
        if not target.exists():
            return None
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return None

    def count_list(self, path: str) -> int:
        data = self.load_json(path)
        return len(data) if isinstance(data, list) else 0

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_status(self) -> dict[str, Any]:
        modules = {
            "local_os_release_capsule": "k_atlas/core/local_os_release_capsule",
            "local_control_plane": "k_atlas/core/local_control_plane",
            "local_mission_installer": "k_atlas/core/local_mission_installer",
            "mission_pipeline_runner": "k_atlas/core/mission_pipeline_runner",
            "remote_assist_readiness": "k_atlas/core/remote_assist_readiness",
            "secure_local_api_runtime": "k_atlas/core/secure_local_api_runtime",
            "supervised_autonomy_dashboard": "k_atlas/core/supervised_autonomy_dashboard",
            "auto_update_watcher": "ops/start_k_atlas_auto_update_watcher_hidden.ps1",
        }

        module_rows = []
        for name, path in modules.items():
            module_rows.append({
                "name": name,
                "path": path,
                "exists": self.exists(path),
            })

        ready_count = len([item for item in module_rows if item["exists"]])

        status = {
            "ok": ready_count == len(module_rows),
            "checkpoint": "123",
            "name": "Principal Shell Cover",
            "generated_at": utc_now(),
            "status": "operational" if ready_count == len(module_rows) else "partial",
            "summary": {
                "modules_total": len(module_rows),
                "modules_ready": ready_count,
                "principal_shell_ready": ready_count >= 6,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_status_only",
                "purpose": "transformar o PowerShell principal em home operacional do K-Atlas Local OS",
            },
            "modules": module_rows,
            "queues": {
                "update_events": self.count_list("memory/auto_update_watcher/events.jsonl"),
                "mission_pipeline_runs": self.count_list("live/mission_pipeline_runner/pipeline_runs.json"),
                "local_mission_installs": self.count_list("memory/local_mission_installer/install_manifest.json"),
            },
            "quick_commands": [
                {
                    "label": "Abrir Local Control Plane",
                    "command": "powershell -ExecutionPolicy Bypass -File .\\ops\\open_local_control_plane.ps1",
                },
                {
                    "label": "Abrir Release Capsule",
                    "command": "streamlit run pages/100_K_Atlas_Local_OS_Release_Capsule.py --server.port 8510 --server.address 127.0.0.1",
                },
                {
                    "label": "Executar proximo update manualmente",
                    "command": "powershell -ExecutionPolicy Bypass -File .\\ops\\k_next.ps1",
                },
                {
                    "label": "Ver status Git",
                    "command": "git status --short",
                },
            ],
            "guardrails": [
                "shell cover nao executa updates automaticamente",
                "shell cover nao captura senhas",
                "shell cover nao abre acesso remoto",
                "shell cover apenas exibe estado e atalhos",
            ],
        }

        self.save_report(status)
        self.event("principal_shell_cover.status_built", {
            "status": status["status"],
            "modules_ready": ready_count,
        })
        return status

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.reports_dir / "latest_principal_shell_cover.json"
        md_path = self.reports_dir / "latest_principal_shell_cover.md"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self.to_markdown(report), encoding="utf-8")

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Principal Shell Cover",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Modules ready: {summary.get('modules_ready')}/{summary.get('modules_total')}",
            f"- Principal shell ready: {summary.get('principal_shell_ready')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            "",
            "## Quick commands",
            "",
        ]

        for item in report.get("quick_commands", []):
            lines.append(f"- {item.get('label')}: `{item.get('command')}`")

        return "\n".join(lines)

    def render_text(self) -> str:
        status = self.build_status()
        summary = status.get("summary", {})
        modules_ready = f"{summary.get('modules_ready')}/{summary.get('modules_total')}"
        ready = summary.get("principal_shell_ready")
        lines = [
            "",
            "============================================================",
            " K-ATLAS LOCAL OS - PRINCIPAL SHELL",
            "============================================================",
            "",
            f" Status.............: {status.get('status')}",
            f" Modules ready......: {modules_ready}",
            f" Principal ready....: {ready}",
            f" Execucao real......: {summary.get('real_execution_enabled')}",
            f" Side effects.......: {summary.get('external_side_effects')}",
            "",
            " Atalhos principais:",
            "  1. Abrir Local Control Plane:  powershell -ExecutionPolicy Bypass -File .\\ops\\open_local_control_plane.ps1",
            "  2. Proximo update manual:     powershell -ExecutionPolicy Bypass -File .\\ops\\k_next.ps1",
            "  3. Git status:                git status --short",
            "",
            " Regra operacional:",
            "  Baixe K_ATLAS_*.ps1 e aguarde o watcher executar.",
            "  Ao popup finalizar, cole aqui no chat o retorno do clipboard.",
            "",
            "============================================================",
            "",
        ]
        return "\n".join(lines)
