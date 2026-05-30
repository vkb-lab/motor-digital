from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from k_atlas.core.startup_manager.manager import StartupManager


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class OneClickLauncher:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/one_click_launcher",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir

    def build_launch_plan(self) -> dict[str, Any]:
        startup = StartupManager(project_root=self.project_root).build_config()
        targets = [item for item in startup["targets"] if item.get("ready")]

        plan = {
            "ok": True,
            "checkpoint": "103",
            "name": "One-Click Launcher",
            "generated_at": utc_now(),
            "status": "launch_plan_ready",
            "summary": {
                "launch_targets_ready": len(targets),
                "automatic_launch_enabled": False,
                "human_action_required": True,
                "execution_enabled": False,
            },
            "targets": targets,
            "operator_instruction": "Escolha um alvo e execute manualmente pelo PowerShell ou pela pagina 103.",
            "guardrails": [
                "launcher nao executa automaticamente pelo modulo Python",
                "comandos sao locais e supervisionados",
                "sem porta publica",
            ],
        }
        self.save(plan)
        return plan

    def save(self, plan: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_one_click_launcher.json").write_text(
            json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
