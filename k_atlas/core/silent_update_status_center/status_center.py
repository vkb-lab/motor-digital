from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SilentUpdateStatusCenter:
    def __init__(
        self,
        project_root: str | Path = ".",
        memory_dir: str | Path = "memory/auto_update_watcher",
        reports_dir: str | Path = "reports/silent_update_status_center",
    ) -> None:
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.events_path = self.memory_dir / "events.jsonl"
        self.latest_run_log = self.memory_dir / "latest_run.log"

    def read_events(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.events_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
        return rows[-limit:]

    def latest_log_tail(self, lines: int = 80) -> str:
        if not self.latest_run_log.exists():
            return ""
        content = self.latest_run_log.read_text(encoding="utf-8", errors="ignore").splitlines()
        return "\n".join(content[-lines:])

    def build_report(self) -> dict[str, Any]:
        events = self.read_events()
        last_event = events[-1] if events else None
        ok_events = [item for item in events if item.get("event_type") == "installer_ok"]
        error_events = [item for item in events if "error" in str(item.get("event_type", "")) or "exception" in str(item.get("event_type", ""))]

        report = {
            "ok": True,
            "checkpoint": "118",
            "name": "Silent Update Status Center",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "events_loaded": len(events),
                "ok_events": len(ok_events),
                "error_events": len(error_events),
                "latest_event_type": last_event.get("event_type") if isinstance(last_event, dict) else None,
                "latest_run_log_exists": self.latest_run_log.exists(),
                "execution_enabled": False,
                "external_side_effects": "read_only",
            },
            "latest_event": last_event,
            "latest_log_tail": self.latest_log_tail(),
        }
        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_silent_update_status_center.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_silent_update_status_center.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        return "\n".join([
            "# K-Atlas Silent Update Status Center",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Events loaded: {summary.get('events_loaded')}",
            f"- OK events: {summary.get('ok_events')}",
            f"- Error events: {summary.get('error_events')}",
            f"- Latest event type: {summary.get('latest_event_type')}",
        ])
