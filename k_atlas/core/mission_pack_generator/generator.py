from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .policy import sha256_text, validate_mission_pack


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    text = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    text = "_".join(part for part in text.split("_") if part)
    return text[:64] or "mission"


class MissionPackGenerator:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/mission_pack_generator",
        memory_dir: str | Path = "memory/mission_pack_generator",
        reports_dir: str | Path = "reports/mission_pack_generator",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.generated_dir = self.live_dir / "generated_missions"
        self.latest_pack_path = self.live_dir / "latest_mission_pack.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_content(self, objective: str, mission_id: str) -> str:
        return (
            "# K-Atlas Generated Local Mission\n\n"
            f"Mission ID: {mission_id}\n\n"
            f"Objective: {objective}\n\n"
            "Status: generated_by_mission_pack_generator\n\n"
            "This file was produced by the K-Atlas Mission Pack Generator.\n"
        )

    def generate_pack(
        self,
        objective: str,
        target_path: str | None = None,
        mission_type: str = "write_report",
    ) -> dict[str, Any]:
        mission_pack_id = f"mission_pack_{uuid4()}"
        mission_id = f"mission_{slugify(objective)}_{uuid4().hex[:8]}"
        safe_slug = slugify(objective)

        final_target_path = target_path or f"reports/autoprog_generated/{safe_slug}.md"
        content = self.build_content(objective=objective, mission_id=mission_id)

        pack = {
            "ok": True,
            "schema_version": "1.0",
            "checkpoint": "74",
            "name": "K-Atlas Local Mission Pack",
            "mission_pack_id": mission_pack_id,
            "mission_id": mission_id,
            "mission_type": mission_type,
            "objective": objective,
            "created_at": utc_now(),
            "source": "mission_pack_generator",
            "install_mode": "manual",
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
            "external_side_effects": "none",
            "steps": [
                {
                    "step_id": f"step_{uuid4().hex[:12]}",
                    "action": "write_file",
                    "path": final_target_path.replace("\\", "/"),
                    "content": content,
                    "content_sha256": sha256_text(content),
                    "purpose": "create_generated_local_mission_report",
                }
            ],
            "guardrails": [
                "pack apenas descreve a missao",
                "pack nao executa sozinho",
                "pack exige aprovacao humana",
                "pack nao chama API externa",
                "pack nao publica",
                "pack nao envia mensagens",
                "pack nao faz deploy",
            ],
        }

        validation = validate_mission_pack(pack)
        pack["validation"] = validation

        self.generated_dir.mkdir(parents=True, exist_ok=True)
        pack_path = self.generated_dir / f"{mission_pack_id}.json"
        pack_path.write_text(
            json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        self.latest_pack_path.parent.mkdir(parents=True, exist_ok=True)
        self.latest_pack_path.write_text(
            json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        report = {
            "ok": validation["ok"],
            "checkpoint": "74",
            "name": "Mission Pack Generator",
            "generated_at": utc_now(),
            "status": "mission_pack_generated" if validation["ok"] else "mission_pack_generated_but_blocked",
            "mission_pack_path": str(pack_path).replace("\\", "/"),
            "latest_pack_path": str(self.latest_pack_path).replace("\\", "/"),
            "pack": pack,
            "summary": {
                "objective": objective,
                "target_path": final_target_path.replace("\\", "/"),
                "steps_total": len(pack["steps"]),
                "human_approval_required": True,
                "automatic_execution_allowed": False,
                "external_side_effects": "none",
                "next_action": "revisar pack e encaminhar para instalador local no proximo checkpoint",
            },
        }

        self.save_report(report)
        self.event("mission_pack_generator.pack_generated", {
            "mission_pack_id": mission_pack_id,
            "mission_id": mission_id,
            "validation_ok": validation["ok"],
        })

        return report

    def summary(self) -> dict[str, Any]:
        packs = sorted(self.generated_dir.glob("*.json")) if self.generated_dir.exists() else []
        latest = None

        if self.latest_pack_path.exists():
            try:
                latest = json.loads(self.latest_pack_path.read_text(encoding="utf-8"))
            except Exception:
                latest = None

        return {
            "ok": True,
            "checkpoint": "74",
            "name": "Mission Pack Generator",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "generated_packs_total": len(packs),
                "latest_pack_exists": self.latest_pack_path.exists(),
                "automatic_execution_allowed": False,
                "external_side_effects": "none",
            },
            "latest_pack": latest,
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_mission_pack_generator.json"
        md_path = self.reports_dir / "latest_mission_pack_generator.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Mission Pack Generator",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Objective: {summary.get('objective')}",
            f"- Target path: {summary.get('target_path')}",
            f"- Steps total: {summary.get('steps_total')}",
            f"- Human approval required: {summary.get('human_approval_required')}",
            f"- Automatic execution allowed: {summary.get('automatic_execution_allowed')}",
            f"- External side effects: {summary.get('external_side_effects')}",
            f"- Next action: {summary.get('next_action')}",
        ]
        return "\n".join(lines)
