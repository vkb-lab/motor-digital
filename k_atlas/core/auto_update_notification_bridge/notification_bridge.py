from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AutoUpdateNotificationBridge:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/auto_update_notification_bridge",
        reports_dir: str | Path = "reports/auto_update_notification_bridge",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.reports_dir = self.project_root / reports_dir
        self.notification_path = self.live_dir / "latest_notification.json"

    def build_notification(self, status: str = "ok", message: str = "ok") -> dict[str, Any]:
        status = status if status in {"ok", "erro", "info"} else "info"
        clipboard_text = "ok" if status == "ok" else ("erro" if status == "erro" else message)

        notification = {
            "ok": True,
            "checkpoint": "119",
            "name": "Auto Update Notification Bridge",
            "generated_at": utc_now(),
            "status": status,
            "message": message,
            "clipboard_text": clipboard_text,
            "target": "chatgpt_operator_window",
            "popup_required": True,
            "window_focus_allowed": True,
            "external_side_effects": "clipboard_and_popup_only",
        }

        self.live_dir.mkdir(parents=True, exist_ok=True)
        self.notification_path.write_text(
            json.dumps(notification, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        self.save_report(notification)
        return notification

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_auto_update_notification_bridge.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
