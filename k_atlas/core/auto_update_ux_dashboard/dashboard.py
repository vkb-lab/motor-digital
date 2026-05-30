from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from k_atlas.core.silent_update_status_center.status_center import SilentUpdateStatusCenter
from k_atlas.core.download_cleanup_policy.policy import DownloadCleanupPolicy
from k_atlas.core.operator_clipboard_return.clipboard_return import OperatorClipboardReturn
from k_atlas.core.auto_update_notification_bridge.notification_bridge import AutoUpdateNotificationBridge


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AutoUpdateUXDashboard:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/auto_update_ux_dashboard",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir

    def build_report(self) -> dict[str, Any]:
        status = SilentUpdateStatusCenter(project_root=self.project_root).build_report()
        cleanup = DownloadCleanupPolicy(project_root=self.project_root).build_report()
        clipboard = OperatorClipboardReturn(project_root=self.project_root).build_return("ok", "dashboard build")
        notification = AutoUpdateNotificationBridge(project_root=self.project_root).build_notification("info", "dashboard build")

        report = {
            "ok": True,
            "checkpoint": "122",
            "name": "Auto Update UX Dashboard",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "silent_status_center": status.get("status"),
                "download_cleanup_policy": cleanup.get("status"),
                "clipboard_return": clipboard.get("status"),
                "notification_bridge": notification.get("status"),
                "ux_mode": "download -> hidden watcher -> popup -> clipboard return",
                "execution_enabled": False,
                "external_side_effects": "reports_only",
            },
            "components": {
                "status": status.get("summary"),
                "cleanup": cleanup.get("summary"),
                "clipboard": clipboard,
                "notification": notification,
            },
        }
        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_auto_update_ux_dashboard.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_auto_update_ux_dashboard.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        return "\n".join([
            "# K-Atlas Auto Update UX Dashboard",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## UX Mode",
            "",
            f"- {summary.get('ux_mode')}",
            "",
            "## Components",
            "",
            f"- Silent status center: {summary.get('silent_status_center')}",
            f"- Download cleanup policy: {summary.get('download_cleanup_policy')}",
            f"- Clipboard return: {summary.get('clipboard_return')}",
            f"- Notification bridge: {summary.get('notification_bridge')}",
        ])
