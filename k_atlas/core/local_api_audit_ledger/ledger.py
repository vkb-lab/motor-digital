from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalApiAuditLedger:
    def __init__(
        self,
        project_root: str | Path = ".",
        memory_dir: str | Path = "memory/local_api_audit_ledger",
        reports_dir: str | Path = "reports/local_api_audit_ledger",
    ) -> None:
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.ledger_path = self.memory_dir / "api_audit_ledger.jsonl"

    def append(self, event_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "audit_id": str(uuid4()),
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": dict(payload or {}),
            "external_side_effects": "none",
            "tamper_note": "append_only_jsonl",
        }
        with self.ledger_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        self.save_report()
        return row

    def rows(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        output: list[dict[str, Any]] = []
        for line in self.ledger_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                output.append(json.loads(line))
            except Exception:
                output.append({"ok": False, "raw": line})
        return output

    def summary(self) -> dict[str, Any]:
        rows = self.rows()
        return {
            "ok": True,
            "checkpoint": "92",
            "name": "Local API Audit Ledger",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "audit_events_total": len(rows),
                "external_side_effects": "none",
                "real_execution_enabled": False,
            },
            "events": rows[-20:],
        }

    def save_report(self) -> dict[str, Any]:
        report = self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_local_api_audit_ledger.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_local_api_audit_ledger.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        return "\n".join([
            "# K-Atlas Local API Audit Ledger",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Audit events total: {summary.get('audit_events_total')}",
            f"- External side effects: {summary.get('external_side_effects')}",
        ])
