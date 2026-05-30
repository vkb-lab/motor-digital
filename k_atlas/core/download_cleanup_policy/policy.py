from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DownloadCleanupPolicy:
    def __init__(
        self,
        downloads_dir: str | Path | None = None,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/download_cleanup_policy",
    ) -> None:
        self.project_root = Path(project_root)
        self.downloads_dir = Path(downloads_dir) if downloads_dir else Path.home() / "Downloads"
        self.reports_dir = self.project_root / reports_dir

    def scan(self) -> list[dict[str, Any]]:
        if not self.downloads_dir.exists():
            return []
        rows: list[dict[str, Any]] = []
        for item in self.downloads_dir.glob("*.ps1"):
            if item.name.upper().startswith("K_ATLAS_"):
                rows.append({
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size,
                    "last_write": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    "cleanup_recommended": True,
                })
        return rows

    def build_report(self) -> dict[str, Any]:
        files = self.scan()
        report = {
            "ok": True,
            "checkpoint": "120",
            "name": "Download Cleanup Policy",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "download_installers_found": len(files),
                "cleanup_mode": "move_not_copy",
                "delete_mode_enabled": False,
                "external_side_effects": "read_only",
            },
            "files": files,
            "policy": [
                "watcher deve mover instaladores para motor-digital",
                "watcher nao deve deixar duplicatas em Downloads",
                "arquivos processados devem ir para memory/auto_update_watcher/processed_installers",
                "limpeza destrutiva exige aprovacao humana",
            ],
        }
        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_download_cleanup_policy.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
