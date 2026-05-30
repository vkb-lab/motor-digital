from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CoworkPilotStudio:
    def __init__(
        self,
        root: str | Path = ".",
        reports_dir: str | Path = "reports/cowork_pilot_studio",
    ) -> None:
        self.root = Path(root)
        self.reports_dir = self.root / reports_dir

    def latest_file(self, folder: str, pattern: str = "*") -> Path | None:
        target = self.root / folder
        if not target.exists():
            return None

        files = [item for item in target.glob(pattern) if item.is_file()]
        if not files:
            return None

        return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[0]

    def read_text(self, path: Path | None, limit: int = 20000) -> str:
        if path is None or not path.exists():
            return ""

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            if len(text) > limit:
                return text[-limit:]
            return text
        except Exception as exc:
            return f"read_error: {type(exc).__name__}: {exc}"

    def load_json(self, path: str) -> dict[str, Any]:
        target = self.root / path

        if not target.exists():
            return {
                "exists": False,
                "path": path,
                "status": "missing",
            }

        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            return {
                "exists": True,
                "path": path,
                "status": data.get("status", "loaded"),
                "ok": data.get("ok"),
                "checkpoint": data.get("checkpoint"),
                "name": data.get("name"),
                "summary": data.get("summary", {}),
            }
        except Exception as exc:
            return {
                "exists": True,
                "path": path,
                "status": "read_error",
                "error": f"{type(exc).__name__}: {exc}",
            }

    def run_git(self, args: list[str]) -> str:
        try:
            result = subprocess.run(
                args,
                cwd=self.root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
            )
            return (result.stdout + result.stderr).strip()
        except Exception as exc:
            return f"git_error: {type(exc).__name__}: {exc}"

    def collect_state(self) -> dict[str, Any]:
        latest_script = self.latest_file("memory/local_clipboard_runner/approved_scripts", "*.ps1")
        latest_log = self.latest_file("memory/local_clipboard_runner/logs", "*.log")
        latest_rejected = self.latest_file("memory/local_clipboard_runner/rejected_clipboard", "*.txt")

        report_paths = [
            "reports/autoprogramming_apply_package_builder/latest_autoprogramming_apply_package_builder.json",
            "reports/autoprogramming_proposal_reviewer/latest_autoprogramming_proposal_reviewer.json",
            "reports/assisted_autoprogramming/latest_assisted_autoprogramming.json",
            "reports/local_clipboard_runner/latest_local_clipboard_runner.json",
            "reports/executor_package_builder/stage_064_smoke_report.json",
            "reports/human_decision_center/stage_063_smoke_report.json",
        ]

        return {
            "ok": True,
            "checkpoint": "67.5",
            "name": "K-Atlas Cowork Pilot Studio",
            "generated_at": utc_now(),
            "status": "operational",
            "layout": {
                "left_panel": "comando_plano_prompt",
                "right_panel": "retorno_logs_status",
                "bottom_panel": "timeline_story",
                "recording_layer": "manual_or_ffmpeg_optional",
            },
            "latest_runner_script_path": str(latest_script).replace("\\", "/") if latest_script else None,
            "latest_runner_log_path": str(latest_log).replace("\\", "/") if latest_log else None,
            "latest_rejected_clipboard_path": str(latest_rejected).replace("\\", "/") if latest_rejected else None,
            "latest_runner_script": self.read_text(latest_script),
            "latest_runner_log": self.read_text(latest_log),
            "latest_rejected_clipboard": self.read_text(latest_rejected, limit=6000),
            "git_status": self.run_git(["git", "status", "--short"]),
            "git_log": self.run_git(["git", "log", "--oneline", "-10"]),
            "report_signals": [self.load_json(path) for path in report_paths],
            "guardrails": [
                "estudio nao executa comandos",
                "estudio apenas observa e organiza",
                "gravacao e camada separada",
                "sem API externa",
                "sem publicacao",
                "sem deploy",
                "sem envio automatico",
            ],
        }

    def save_report(self) -> dict[str, Any]:
        report = self.collect_state()

        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_cowork_pilot_studio.json"
        md_path = self.reports_dir / "latest_cowork_pilot_studio.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas Cowork Pilot Studio",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Layout operacional",
            "",
            "- Esquerda: comando, plano e prompt",
            "- Direita: retorno, logs e status",
            "- Base: timeline da historia operacional",
            "- Gravacao: camada supervisionada separada",
            "",
            "## Ultimo script",
            "",
            str(report.get("latest_runner_script_path")),
            "",
            "## Ultimo log",
            "",
            str(report.get("latest_runner_log_path")),
            "",
            "## Git status",
            "",
            report.get("git_status") or "limpo",
            "",
            "## Guardrails",
            "",
        ]

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
