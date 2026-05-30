from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


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
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_contracts() -> list[dict[str, Any]]:
    return [
        {
            "action_type": "create_local_report",
            "name": "Create Local Report",
            "checkpoint": "84",
            "description": "Cria arquivo local dentro de reports/autoprog_generated.",
            "allowed_paths": ["reports/autoprog_generated/"],
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "external_side_effects": "local_files_only",
            "suggested_command": "powershell -ExecutionPolicy Bypass -File .\\ops\\install_local_mission.ps1 -Approve -Install",
        },
        {
            "action_type": "install_local_mission",
            "name": "Install Local Mission",
            "checkpoint": "84",
            "description": "Instala uma missao local validada pelo Local Mission Installer.",
            "allowed_paths": ["live/local_mission_installer/", "reports/autoprog_generated/"],
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "external_side_effects": "local_files_only",
            "suggested_command": "powershell -ExecutionPolicy Bypass -File .\\ops\\install_local_mission.ps1 -Approve -Install",
        },
        {
            "action_type": "run_mission_pipeline",
            "name": "Run Mission Pipeline",
            "checkpoint": "84",
            "description": "Executa pipeline 74-75-73 somente com aprovacao humana.",
            "allowed_paths": ["live/mission_pipeline_runner/", "reports/mission_pipeline_runner/"],
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "external_side_effects": "local_files_only",
            "suggested_command": "powershell -ExecutionPolicy Bypass -File .\\ops\\run_mission_pipeline.ps1 -Approve -Install",
        },
    ]


def validate_action_request(payload: Mapping[str, Any], contracts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    data = dict(payload or {})
    catalog = contracts or default_contracts()
    reasons: list[str] = []

    action_type = str(data.get("action_type", "")).strip()
    contract = next((item for item in catalog if item.get("action_type") == action_type), None)

    if not action_type:
        reasons.append("action_type_required")

    if action_type and contract is None:
        reasons.append(f"unknown_action_type:{action_type}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    if data.get("human_approved") is not True:
        reasons.append("human_approval_required")

    return {
        "ok": len(reasons) == 0,
        "status": "action_request_allowed" if not reasons else "action_request_blocked",
        "action_type": action_type,
        "contract": contract,
        "reasons": reasons or ["action_request_allowed"],
        "automatic_execution_allowed": False,
        "real_execution_enabled": False,
        "external_side_effects": "local_files_only" if contract else "none",
    }


class LocalActionContractRegistry:
    def __init__(
        self,
        live_dir: str | Path = "live/local_action_contracts",
        reports_dir: str | Path = "reports/local_action_contracts",
        memory_dir: str | Path = "memory/local_action_contracts",
    ) -> None:
        self.live_dir = Path(live_dir)
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.contracts_path = self.live_dir / "action_contracts.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_contracts(self) -> dict[str, Any]:
        contracts = default_contracts()
        self.live_dir.mkdir(parents=True, exist_ok=True)
        self.contracts_path.write_text(json.dumps(contracts, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

        report = {
            "ok": True,
            "checkpoint": "84",
            "name": "Local Action Contract Registry",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "contracts_total": len(contracts),
                "automatic_execution_allowed": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_files_only",
            },
            "contracts": contracts,
        }
        self.save_report(report)
        self.event("local_action_contracts.built", {"contracts_total": len(contracts)})
        return report

    def load_contracts(self) -> list[dict[str, Any]]:
        if not self.contracts_path.exists():
            self.build_contracts()
        try:
            data = json.loads(self.contracts_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else default_contracts()
        except Exception:
            return default_contracts()

    def summary(self) -> dict[str, Any]:
        contracts = self.load_contracts()
        return {
            "ok": True,
            "checkpoint": "84",
            "name": "Local Action Contract Registry",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "contracts_total": len(contracts),
                "automatic_execution_allowed": False,
                "real_execution_enabled": False,
            },
            "contracts": contracts,
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.reports_dir / "latest_local_action_contracts.json"
        md_path = self.reports_dir / "latest_local_action_contracts.md"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas Local Action Contract Registry",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Contracts",
            "",
        ]
        for item in report.get("contracts", []):
            lines.append(f"- {item.get('action_type')} - approval_required={item.get('human_approval_required')}")
        return "\n".join(lines)
