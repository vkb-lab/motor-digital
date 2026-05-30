from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .snapshot import build_system_snapshot


class AutoReporterCentral:
    def __init__(self, output_dir: str | Path = "reports/autoreporter") -> None:
        self.output_dir = Path(output_dir)

    def generate(self) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        snapshot = build_system_snapshot()

        json_path = self.output_dir / "k_atlas_central_report.json"
        md_path = self.output_dir / "k_atlas_central_report.md"

        json_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        md_path.write_text(self.to_markdown(snapshot), encoding="utf-8")

        return {
            "ok": True,
            "status": "report_generated",
            "json_path": str(json_path).replace("\\", "/"),
            "md_path": str(md_path).replace("\\", "/"),
            "snapshot": snapshot,
        }

    def to_markdown(self, snapshot: dict[str, Any]) -> str:
        modules = snapshot.get("modules", {})
        metrics = snapshot.get("metrics", {})
        git = snapshot.get("git", {})
        autonomy = snapshot.get("autonomy_status", {})

        lines = [
            "# K-Atlas Central Report",
            "",
            f"Generated at: {snapshot.get('generated_at')}",
            f"Checkpoint: {snapshot.get('checkpoint')} - {snapshot.get('module')}",
            "",
            "## Status",
            "",
            f"- Current autonomy level: {autonomy.get('current_level')}",
            f"- Next target: {autonomy.get('next_target')}",
            f"- Modules OK: {metrics.get('modules_ok')} / {metrics.get('modules_total')}",
            f"- Streamlit pages: {metrics.get('streamlit_pages')}",
            f"- Control Plane events: {metrics.get('control_plane_events')}",
            f"- Supervisor queue items: {metrics.get('supervisor_queue_items')}",
            "",
            "## Modules",
            "",
        ]

        for key, value in modules.items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in autonomy.get("guardrails", []):
            lines.append(f"- {item}")

        lines.extend([
            "",
            "## Git",
            "",
            f"- Branch: {git.get('branch')}",
            "",
            "### Last commits",
            "",
            "```text",
            git.get("last_commits", ""),
            "```",
            "",
            "### Status",
            "",
            "```text",
            git.get("status_short", ""),
            "```",
            "",
            "## Next checkpoints",
            "",
        ])

        for item in snapshot.get("next_checkpoints", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
