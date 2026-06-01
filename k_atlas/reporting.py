"""Markdown report generation for K-Atlas OS."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .events import emit_event, read_events
from .paths import REPORTS_DIR, ensure_dirs


def generate_report(title: str = "K-OS Operational Report", data: dict[str, Any] | None = None) -> Path:
    ensure_dirs()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"kos_report_{stamp}.md"
    payload = data or {}
    events = read_events(limit=10)
    lines = [
        f"# {title}",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Data",
        "",
    ]
    if payload:
        for key, value in payload.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- status: local fallback")
    lines.extend(["", "## Recent Events", ""])
    if events:
        for event in events:
            lines.append(f"- {event.get('ts', '')} | {event.get('type', '')}")
    else:
        lines.append("- No events recorded")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    emit_event("report_generated", {"path": str(path)})
    return path

