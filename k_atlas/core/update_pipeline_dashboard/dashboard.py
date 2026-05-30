from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UpdatePipelineDashboard:
    def __init__(self, reports_dir: str | Path = "reports/update_pipeline_dashboard") -> None:
        self.reports_dir = Path(reports_dir)

    def load_json(self, path: str) -> Any:
        target = Path(path)
        if not target.exists():
            return None
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return None

    def count_list(self, path: str) -> int:
        data = self.load_json(path)
        return len(data) if isinstance(data, list) else 0

    def build_report(self) -> dict[str, Any]:
        report = {
            "ok": True,
            "checkpoint": "117",
            "name": "Update Pipeline Dashboard",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "intake_queue": self.count_list("live/update_intake_queue/update_queue.json"),
                "verified_updates": self.count_list("live/update_verification_gate/verified_updates.json"),
                "apply_records": self.count_list("memory/update_apply_runner/apply_manifest.json"),
                "rollback_hooks": self.count_list("memory/update_rollback_hook/rollback_hooks.json"),
                "real_execution_enabled": False,
                "automatic_execution_allowed": False,
                "external_side_effects": "local_files_only",
            },
            "guardrails": [
                "updates passam por fila",
                "gate verifica instalador antes de aplicar",
                "runner nao executa automaticamente",
                "rollback hook exige aprovacao humana",
                "sem porta publica",
                "sem API externa",
            ],
        }

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_update_pipeline_dashboard.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return report
