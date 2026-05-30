from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.local_mission_installer.policy import validate_mission_package
from k_atlas.core.mission_pack_generator.policy import validate_mission_pack


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MissionPackBridge:
    def __init__(
        self,
        project_root: str | Path = ".",
        source_pack_path: str | Path = "live/mission_pack_generator/latest_mission_pack.json",
        live_dir: str | Path = "live/mission_pack_bridge",
        memory_dir: str | Path = "memory/mission_pack_bridge",
        reports_dir: str | Path = "reports/mission_pack_bridge",
    ) -> None:
        self.project_root = Path(project_root)
        self.source_pack_path = self.project_root / source_pack_path
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.generated_dir = self.live_dir / "generated_local_missions"
        self.latest_local_mission_path = self.live_dir / "latest_local_mission.kmission.json"
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

    def load_json(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def normalize_step(self, step: Mapping[str, Any]) -> dict[str, Any]:
        data = dict(step or {})
        return {
            "action": str(data.get("action", "")).strip(),
            "path": str(data.get("path", "")).replace("\\", "/").strip(),
            "purpose": str(data.get("purpose", "mission_pack_bridge_step")),
            "content": str(data.get("content", "")),
            "content_sha256": str(data.get("content_sha256", "")).strip(),
        }

    def convert_pack_to_local_mission(self, pack: Mapping[str, Any]) -> dict[str, Any]:
        data = dict(pack or {})
        steps = [self.normalize_step(step) for step in data.get("steps", []) if isinstance(step, dict)]

        local_mission = {
            "schema_version": "k_atlas.local_mission.v1",
            "mission_id": f"bridge_{data.get('mission_id') or uuid4()}",
            "mission_name": f"Bridged Mission - {data.get('objective') or 'sem objetivo'}",
            "created_at": utc_now(),
            "created_by": "k_atlas_mission_pack_bridge",
            "status": "draft_ready_for_local_review",
            "install_mode": "manual_only",
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
            "source": "mission_pack_bridge",
            "source_checkpoint": data.get("checkpoint"),
            "source_mission_pack_id": data.get("mission_pack_id"),
            "source_mission_id": data.get("mission_id"),
            "objective": data.get("objective"),
            "steps": steps,
            "guardrails": [
                "bridge apenas converte mission pack para local mission",
                "bridge nao instala automaticamente",
                "bridge nao executa codigo",
                "bridge nao chama API externa",
                "bridge exige Local Mission Installer para aplicacao manual",
            ],
        }

        return local_mission

    def bridge_latest(self, source_path: str | Path | None = None) -> dict[str, Any]:
        bridge_id = str(uuid4())
        source = self.project_root / source_path if source_path else self.source_pack_path
        pack = self.load_json(source)

        if pack is None:
            report = {
                "ok": False,
                "checkpoint": "75",
                "name": "Mission Pack Bridge",
                "bridge_id": bridge_id,
                "generated_at": utc_now(),
                "status": "source_pack_not_found_or_invalid_json",
                "source_path": str(source).replace("\\", "/"),
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        pack_validation = validate_mission_pack(pack)
        local_mission = self.convert_pack_to_local_mission(pack)
        local_validation = validate_mission_package(local_mission)

        self.generated_dir.mkdir(parents=True, exist_ok=True)
        mission_id = str(local_mission.get("mission_id", "local_mission")).replace("/", "_").replace("\\", "_")
        output_path = self.generated_dir / f"{mission_id}.kmission.json"

        output_path.write_text(
            json.dumps(local_mission, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        self.latest_local_mission_path.parent.mkdir(parents=True, exist_ok=True)
        self.latest_local_mission_path.write_text(
            json.dumps(local_mission, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        report = {
            "ok": pack_validation.get("ok") is True and local_validation.get("ok") is True,
            "checkpoint": "75",
            "name": "Mission Pack Bridge",
            "bridge_id": bridge_id,
            "generated_at": utc_now(),
            "status": "local_mission_generated" if local_validation.get("ok") else "local_mission_generated_but_blocked",
            "source_path": str(source).replace("\\", "/"),
            "output_path": str(output_path).replace("\\", "/"),
            "latest_local_mission_path": str(self.latest_local_mission_path).replace("\\", "/"),
            "pack_validation": pack_validation,
            "local_mission_validation": local_validation,
            "summary": {
                "steps_total": len(local_mission.get("steps", [])),
                "ready_for_local_installer": bool(local_validation.get("ok")),
                "automatic_execution_allowed": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_files_only",
                "next_action": "rodar ops/install_local_mission.ps1 com o caminho do .kmission gerado",
            },
            "guardrails": [
                "nao instala automaticamente",
                "nao executa comandos",
                "nao publica",
                "nao envia mensagens",
                "nao faz deploy",
            ],
        }

        self.save_report(report)
        self.event("mission_pack_bridge.local_mission_generated", {
            "bridge_id": bridge_id,
            "output_path": str(output_path).replace("\\", "/"),
            "ready_for_local_installer": bool(local_validation.get("ok")),
        })

        return report

    def summary(self) -> dict[str, Any]:
        generated = []
        if self.generated_dir.exists():
            generated = sorted(self.generated_dir.glob("*.kmission.json"), key=lambda p: p.stat().st_mtime, reverse=True)

        latest = self.load_json(self.latest_local_mission_path)

        return {
            "ok": True,
            "checkpoint": "75",
            "name": "Mission Pack Bridge",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "generated_local_missions_total": len(generated),
                "latest_local_mission_exists": self.latest_local_mission_path.exists(),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
            },
            "latest_local_mission": latest,
            "generated_paths": [str(path).replace("\\", "/") for path in generated[:10]],
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.reports_dir / "latest_mission_pack_bridge.json"
        md_path = self.reports_dir / "latest_mission_pack_bridge.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {}) or {}
        lines = [
            "# K-Atlas Mission Pack Bridge",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Steps total: {summary.get('steps_total')}",
            f"- Ready for local installer: {summary.get('ready_for_local_installer')}",
            f"- External side effects: {summary.get('external_side_effects')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Output",
            "",
            f"- Local mission: {report.get('output_path')}",
        ]
        return "\n".join(lines)
