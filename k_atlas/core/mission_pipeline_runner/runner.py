from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_pipeline_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MissionPipelineRunner:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/mission_pipeline_runner",
        memory_dir: str | Path = "memory/mission_pipeline_runner",
        reports_dir: str | Path = "reports/mission_pipeline_runner",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.events_path = self.memory_dir / "events.jsonl"
        self.pipeline_runs_path = self.live_dir / "pipeline_runs.json"

    def exists(self, path: str) -> bool:
        return (self.project_root / path).exists()

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
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
        path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def discover_components(self) -> dict[str, Any]:
        components = {
            "mission_pack_generator": {
                "module": "k_atlas/core/mission_pack_generator",
                "page": "pages/74_K_Atlas_Mission_Pack_Generator.py",
                "demo_script_candidates": [
                    "ops/run_mission_pack_generator_demo.ps1",
                    "ops/generate_local_mission_pack.ps1",
                    "ops/generate_mission_pack_demo.ps1",
                ],
            },
            "mission_pack_bridge": {
                "module": "k_atlas/core/mission_pack_bridge",
                "page": "pages/75_K_Atlas_Mission_Pack_Bridge.py",
                "demo_script_candidates": [
                    "ops/run_mission_pack_bridge_demo.ps1",
                    "ops/bridge_latest_mission_pack.ps1",
                ],
            },
            "local_mission_installer": {
                "module": "k_atlas/core/local_mission_installer",
                "page": "pages/73_K_Atlas_Local_Mission_Installer.py",
                "demo_script_candidates": [
                    "ops/install_local_mission.ps1",
                    "ops/run_local_mission_installer_demo.ps1",
                ],
            },
        }

        final: dict[str, Any] = {}

        for name, data in components.items():
            scripts = [
                candidate for candidate in data["demo_script_candidates"]
                if self.exists(candidate)
            ]

            final[name] = {
                "module": data["module"],
                "module_exists": self.exists(data["module"]),
                "page": data["page"],
                "page_exists": self.exists(data["page"]),
                "scripts_found": scripts,
                "ready": self.exists(data["module"]) and len(scripts) > 0,
            }

        return final

    def build_plan(self) -> dict[str, Any]:
        components = self.discover_components()

        steps = [
            {
                "order": 1,
                "name": "generate_mission_pack",
                "component": "mission_pack_generator",
                "ready": components["mission_pack_generator"]["ready"],
                "instruction": "Gerar mission pack declarativo local.",
            },
            {
                "order": 2,
                "name": "bridge_mission_pack_to_local_mission",
                "component": "mission_pack_bridge",
                "ready": components["mission_pack_bridge"]["ready"],
                "instruction": "Converter mission pack para formato .kmission.json.",
            },
            {
                "order": 3,
                "name": "install_local_mission_with_human_approval",
                "component": "local_mission_installer",
                "ready": components["local_mission_installer"]["ready"],
                "instruction": "Instalar missao local somente com aprovacao humana.",
            },
        ]

        return {
            "ok": all(step["ready"] for step in steps),
            "generated_at": utc_now(),
            "components": components,
            "steps": steps,
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
        }

    def dry_run(self, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
        request_data = dict(request or {"mode": "dry_run"})
        validation = validate_pipeline_request(request_data)
        run_id = str(uuid4())

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "76",
                "name": "Mission Pipeline Runner",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "blocked_by_policy",
                "request_validation": validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        plan = self.build_plan()

        report = {
            "ok": plan["ok"],
            "checkpoint": "76",
            "name": "Mission Pipeline Runner",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "dry_run_completed" if plan["ok"] else "dry_run_partial",
            "request_validation": validation,
            "plan": plan,
            "summary": {
                "steps_total": len(plan["steps"]),
                "steps_ready": len([step for step in plan["steps"] if step["ready"]]),
                "pipeline_ready": plan["ok"],
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "Executar ops/run_mission_pipeline.ps1 -Approve -Install apenas quando o operador aprovar.",
            },
            "guardrails": [
                "dry-run nao instala nada",
                "execucao real exige -Approve -Install no script local",
                "sem API externa",
                "sem envio automatico",
                "sem deploy automatico",
                "sem navegador automatico",
            ],
        }

        self.save_report(report)
        self.event("mission_pipeline_runner.dry_run_completed", {
            "run_id": run_id,
            "pipeline_ready": plan["ok"],
        })

        return report

    def run_supervised(self, request: Mapping[str, Any]) -> dict[str, Any]:
        request_data = dict(request or {})
        request_data.setdefault("mode", "supervised")
        validation = validate_pipeline_request(request_data)
        run_id = str(uuid4())

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "76",
                "name": "Mission Pipeline Runner",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "blocked_by_policy",
                "request_validation": validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        plan = self.build_plan()
        if not plan["ok"]:
            report = {
                "ok": False,
                "checkpoint": "76",
                "name": "Mission Pipeline Runner",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "pipeline_not_ready",
                "plan": plan,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        installed = bool(request_data.get("install"))
        report = {
            "ok": True,
            "checkpoint": "76",
            "name": "Mission Pipeline Runner",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "supervised_pipeline_registered",
            "plan": plan,
            "summary": {
                "install_requested": installed,
                "human_approved": request_data.get("human_approved") is True,
                "execution_enabled": installed,
                "real_execution_enabled": installed,
                "external_side_effects": "local_files_only" if installed else "none",
                "note": "Execucao operacional real ocorre pelo script ops/run_mission_pipeline.ps1.",
            },
        }

        runs = self.load_list(self.pipeline_runs_path)
        runs.append(report)
        self.save_list(self.pipeline_runs_path, runs)

        self.save_report(report)
        self.event("mission_pipeline_runner.supervised_pipeline_registered", {
            "run_id": run_id,
            "install_requested": installed,
        })

        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_mission_pipeline_runner.json"
        md_path = self.reports_dir / "latest_mission_pipeline_runner.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        md_path.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {}) or {}

        lines = [
            "# K-Atlas Mission Pipeline Runner",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Pipeline ready: {summary.get('pipeline_ready')}",
            f"- Steps total: {summary.get('steps_total')}",
            f"- Steps ready: {summary.get('steps_ready')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Real execution enabled: {summary.get('real_execution_enabled')}",
            f"- External side effects: {summary.get('external_side_effects')}",
            f"- Next action: {summary.get('next_action')}",
        ]

        if report.get("guardrails"):
            lines.extend(["", "## Guardrails", ""])
            for item in report.get("guardrails", []):
                lines.append(f"- {item}")

        return "\n".join(lines)
