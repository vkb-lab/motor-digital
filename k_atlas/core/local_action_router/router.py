from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.local_action_contracts.contracts import LocalActionContractRegistry, validate_action_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalActionRouter:
    def __init__(
        self,
        live_dir: str | Path = "live/local_action_router",
        reports_dir: str | Path = "reports/local_action_router",
        memory_dir: str | Path = "memory/local_action_router",
    ) -> None:
        self.live_dir = Path(live_dir)
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.route_queue_path = self.live_dir / "action_route_queue.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def load_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_list(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def route(self, request: Mapping[str, Any]) -> dict[str, Any]:
        registry = LocalActionContractRegistry()
        contracts = registry.load_contracts()
        validation = validate_action_request(request, contracts)
        route_id = str(uuid4())

        route = {
            "ok": validation["ok"],
            "checkpoint": "85",
            "name": "Local Action Router",
            "route_id": route_id,
            "generated_at": utc_now(),
            "status": "route_ready" if validation["ok"] else "route_blocked",
            "request": dict(request or {}),
            "validation": validation,
            "action_type": validation.get("action_type"),
            "contract": validation.get("contract"),
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "real_execution_enabled": False,
            "external_side_effects": validation.get("external_side_effects", "none"),
            "suggested_command": (validation.get("contract") or {}).get("suggested_command"),
        }

        queue = self.load_list(self.route_queue_path)
        queue.append(route)
        self.save_list(self.route_queue_path, queue)
        self.save_report(route)
        self.event("local_action_router.route_created", {"route_id": route_id, "ok": route["ok"]})
        return route

    def summary(self) -> dict[str, Any]:
        routes = self.load_list(self.route_queue_path)
        return {
            "ok": True,
            "checkpoint": "85",
            "name": "Local Action Router",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "routes_total": len(routes),
                "ready_routes": len([item for item in routes if item.get("status") == "route_ready"]),
                "blocked_routes": len([item for item in routes if item.get("status") == "route_blocked"]),
                "automatic_execution_allowed": False,
                "real_execution_enabled": False,
            },
            "latest_route": routes[-1] if routes else None,
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.reports_dir / "latest_local_action_router.json"
        md_path = self.reports_dir / "latest_local_action_router.md"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        validation = report.get("validation", {}) or {}
        return "\n".join([
            "# K-Atlas Local Action Router",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Action type: {report.get('action_type')}",
            f"Suggested command: {report.get('suggested_command')}",
            f"Reasons: {validation.get('reasons')}",
        ])
