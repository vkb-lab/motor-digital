from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class OperatorClipboardReturn:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/operator_clipboard_return",
        reports_dir: str | Path = "reports/operator_clipboard_return",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.reports_dir = self.project_root / reports_dir
        self.return_path = self.live_dir / "latest_clipboard_return.json"

    def build_return(self, status: str = "ok", details: str = "") -> dict[str, Any]:
        text = "ok" if status == "ok" else "erro"

        result = {
            "ok": True,
            "checkpoint": "121",
            "name": "Operator Clipboard Return",
            "generated_at": utc_now(),
            "status": status,
            "clipboard_text": text,
            "details": details,
            "operator_instruction": "apos popup, clicar OK e colar no chat com Ctrl+V",
            "external_side_effects": "clipboard_text_only_when_used_by_watcher",
        }

        self.live_dir.mkdir(parents=True, exist_ok=True)
        self.return_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        self.save_report(result)
        return result

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_operator_clipboard_return.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
