from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DownloadIntakeUX:
    def __init__(
        self,
        project_root: str | Path = ".",
        memory_dir: str | Path = "memory/download_intake",
        reports_dir: str | Path = "reports/download_intake_ux",
    ) -> None:
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.state_path = self.memory_dir / "state.json"
        self.latest_command_path = self.memory_dir / "latest_command.txt"
        self.latest_download_path = self.memory_dir / "latest_download.json"
        self.executed_path = self.memory_dir / "executed_installers.jsonl"

    def load_json(self, path: Path, default: Any = None) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return default

    def count_jsonl(self, path: Path) -> int:
        if not path.exists():
            return 0
        return len([line for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()])

    def summary(self) -> dict[str, Any]:
        state = self.load_json(self.state_path, {})
        latest_download = self.load_json(self.latest_download_path, None)
        fixed_command = state.get(
            "fixed_command",
            'cd "C:\\Users\\oi\\Desktop\\motor-digital"; powershell -ExecutionPolicy Bypass -File ".\\ops\\k_next.ps1"',
        )

        report = {
            "ok": True,
            "checkpoint": "106",
            "name": "Download Intake UX Fix",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "fixed_command_available": bool(fixed_command),
                "latest_download_available": latest_download is not None,
                "executed_installers": self.count_jsonl(self.executed_path),
                "ux_goal": "baixar arquivo e executar sempre o mesmo comando no PowerShell principal",
                "extra_windows_required": False,
            },
            "state": state,
            "latest_download": latest_download,
            "fixed_command": fixed_command,
            "guardrails": [
                "nao executa automaticamente sem comando humano",
                "nao abre acesso remoto",
                "nao chama API externa",
                "nao publica",
                "nao envia mensagens",
                "apenas prepara e executa instaladores K_ATLAS locais quando operador roda k_next",
            ],
        }
        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_download_intake_ux.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_download_intake_ux.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Download Intake UX Fix",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Fixed command available: {summary.get('fixed_command_available')}",
            f"- Latest download available: {summary.get('latest_download_available')}",
            f"- Executed installers: {summary.get('executed_installers')}",
            f"- Extra windows required: {summary.get('extra_windows_required')}",
            "",
            "## Fixed command",
            "",
            "```powershell",
            str(report.get("fixed_command", "")),
            "```",
        ]
        return "\n".join(lines)
