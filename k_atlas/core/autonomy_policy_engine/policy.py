from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


BLOCKED_FLAGS = [
    "auto_execute",
    "real_execution_enabled",
    "external_api_enabled",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
    "remote_control_enabled",
    "public_network_enabled",
    "credential_access_enabled",
]

ALLOWED_MODES = {"observe", "plan", "recommend", "queue"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_autonomy_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    mode = str(data.get("mode", "observe")).strip()
    if mode not in ALLOWED_MODES:
        reasons.append(f"invalid_mode:{mode}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    risk = str(data.get("risk_level", "low")).strip().lower()
    if risk not in {"low", "medium"}:
        reasons.append(f"risk_level_blocked:{risk}")

    return {
        "ok": len(reasons) == 0,
        "status": "autonomy_request_allowed" if not reasons else "autonomy_request_blocked",
        "mode": mode,
        "reasons": reasons or ["autonomy_request_allowed"],
        "execution_enabled": False,
        "real_execution_enabled": False,
        "external_side_effects": "none",
        "human_approval_required": True,
    }


class AutonomyPolicyEngine:
    def __init__(
        self,
        memory_dir: str | Path = "memory/autonomy_policy_engine",
        reports_dir: str | Path = "reports/autonomy_policy_engine",
    ) -> None:
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def evaluate(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        request = dict(payload or {"mode": "observe", "risk_level": "low"})
        validation = validate_autonomy_request(request)
        report = {
            "ok": validation["ok"],
            "checkpoint": "94",
            "name": "Autonomy Policy Engine",
            "policy_id": str(uuid4()),
            "generated_at": utc_now(),
            "status": "policy_allowed" if validation["ok"] else "policy_blocked",
            "request": request,
            "validation": validation,
            "guardrails": [
                "no automatic execution",
                "no public network exposure",
                "no credential access",
                "no browser or mouse automation",
                "human approval required",
            ],
        }
        self.save_report(report)
        self.event("autonomy_policy_engine.evaluated", {"status": report["status"]})
        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_autonomy_policy_engine.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        lines = [
            "# K-Atlas Autonomy Policy Engine",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Guardrails",
            "",
        ]
        for item in report.get("guardrails", []):
            lines.append(f"- {item}")
        (self.reports_dir / "latest_autonomy_policy_engine.md").write_text("\n".join(lines), encoding="utf-8")
        return report
