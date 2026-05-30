from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from k_atlas.core.local_os_health_check.health import LocalOSHealthCheck
from k_atlas.core.one_click_launcher.launcher import OneClickLauncher


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class OperatorHome:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/operator_home",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir

    def build_home(self) -> dict[str, Any]:
        health = LocalOSHealthCheck(project_root=self.project_root).collect()
        launcher = OneClickLauncher(project_root=self.project_root).build_launch_plan()

        home = {
            "ok": True,
            "checkpoint": "104",
            "name": "Operator Home",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "health_readiness": health.get("summary", {}).get("readiness"),
                "launch_targets_ready": launcher.get("summary", {}).get("launch_targets_ready"),
                "real_execution_enabled": False,
                "next_action": "usar Operator Home como pagina inicial do K-Atlas Local OS",
            },
            "health": health.get("summary", {}),
            "launch_targets": launcher.get("targets", []),
            "guardrails": [
                "operator home apenas centraliza",
                "acoes reais exigem clique ou comando humano",
                "sem automacao oculta",
            ],
        }
        self.save(home)
        return home

    def save(self, home: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_operator_home.json").write_text(
            json.dumps(home, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
