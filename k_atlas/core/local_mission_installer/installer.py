from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import (
    sha256_text,
    validate_manual_install_request,
    validate_mission_package,
    validate_mission_step,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LocalMissionInstaller:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/local_mission_installer",
        memory_dir: str | Path = "memory/local_mission_installer",
        reports_dir: str | Path = "reports/local_mission_installer",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.mission_queue_path = self.live_dir / "mission_queue.json"
        self.install_manifest_path = self.memory_dir / "install_manifest.json"
        self.events_path = self.memory_dir / "events.jsonl"
        self.inbox_dir = self.live_dir / "inbox"

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

    def build_demo_mission(self) -> dict[str, Any]:
        content = "# K-Atlas Local Mission Demo\n\nMissao demonstrativa instalada pelo Local Mission Installer.\n"
        mission = {
            "schema_version": "k_atlas.local_mission.v1",
            "mission_id": f"mission_demo_{uuid4()}",
            "mission_name": "Local Mission Installer Demo",
            "created_at": utc_now(),
            "created_by": "k_atlas",
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
            "objective": "Demonstrar instalacao local declarativa sem blocos gigantes no chat.",
            "steps": [
                {
                    "action": "write_file",
                    "path": "reports/autoprog_generated/local_mission_demo.md",
                    "purpose": "arquivo demo seguro",
                    "content": content,
                    "content_sha256": sha256_text(content),
                }
            ],
        }

        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        path = self.inbox_dir / f"{mission['mission_id']}.kmission.json"
        path.write_text(json.dumps(mission, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

        return {
            "ok": True,
            "mission": mission,
            "mission_path": str(path).replace("\\", "/"),
        }

    def import_mission_package(self, package: Mapping[str, Any]) -> dict[str, Any]:
        validation = validate_mission_package(package)
        mission = dict(package or {})
        mission_id = str(mission.get("mission_id", "")).strip()

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "generated_at": utc_now(),
                "status": "mission_import_blocked_by_policy",
                "validation": validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        queue = self.load_list(self.mission_queue_path)

        for item in queue:
            if item.get("mission_id") == mission_id:
                report = {
                    "ok": True,
                    "checkpoint": "73",
                    "name": "Local Mission Installer",
                    "generated_at": utc_now(),
                    "status": "mission_already_imported",
                    "mission_id": mission_id,
                    "validation": validation,
                    "external_side_effects": "none",
                }
                self.save_report(report)
                return report

        item = {
            "mission_queue_id": str(uuid4()),
            "mission_id": mission_id,
            "mission_name": mission.get("mission_name"),
            "imported_at": utc_now(),
            "status": "waiting_human_mission_approval",
            "validation": validation,
            "mission_snapshot": mission,
            "automatic_execution_allowed": False,
            "human_approval_required": True,
            "external_side_effects": "none",
        }

        queue.append(item)
        self.save_list(self.mission_queue_path, queue)

        report = {
            "ok": True,
            "checkpoint": "73",
            "name": "Local Mission Installer",
            "generated_at": utc_now(),
            "status": "mission_imported",
            "mission_id": mission_id,
            "mission_queue_id": item["mission_queue_id"],
            "validation": validation,
            "external_side_effects": "none",
        }

        self.save_report(report)
        self.event("local_mission_installer.mission_imported", {
            "mission_id": mission_id,
            "mission_queue_id": item["mission_queue_id"],
        })

        return report

    def import_mission_file(self, path: str | Path) -> dict[str, Any]:
        target = Path(path)
        if not target.is_absolute():
            target = self.project_root / target

        if not target.exists():
            report = {
                "ok": False,
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "generated_at": utc_now(),
                "status": "mission_file_not_found",
                "mission_path": str(target).replace("\\", "/"),
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        data = json.loads(target.read_text(encoding="utf-8"))
        return self.import_mission_package(data)

    def find_mission(self, mission_id: str | None = None, allowed_statuses: set[str] | None = None) -> dict[str, Any] | None:
        queue = self.load_list(self.mission_queue_path)
        statuses = allowed_statuses or {"waiting_human_mission_approval", "approved_for_manual_install"}

        candidates = [
            item for item in queue
            if item.get("status") in statuses
            and item.get("automatic_execution_allowed") is not True
        ]

        if mission_id:
            for item in candidates:
                if item.get("mission_id") == mission_id:
                    return item
            return None

        return candidates[0] if candidates else None

    def approve_mission(self, mission_id: str | None = None, approved_by: str = "human_operator", notes: str = "") -> dict[str, Any]:
        queue = self.load_list(self.mission_queue_path)
        target_index = None

        for index, item in enumerate(queue):
            if item.get("status") != "waiting_human_mission_approval":
                continue
            if mission_id and item.get("mission_id") != mission_id:
                continue
            target_index = index
            break

        if target_index is None:
            report = {
                "ok": False,
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "generated_at": utc_now(),
                "status": "no_mission_waiting_approval",
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        item = queue[target_index]
        validation = item.get("validation", {})

        if not isinstance(validation, dict) or validation.get("ok") is not True:
            report = {
                "ok": False,
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "generated_at": utc_now(),
                "status": "mission_not_valid_for_approval",
                "mission_id": item.get("mission_id"),
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        item["status"] = "approved_for_manual_install"
        item["approved_at"] = utc_now()
        item["approved_by"] = approved_by
        item["approval_notes"] = notes
        queue[target_index] = item
        self.save_list(self.mission_queue_path, queue)

        report = {
            "ok": True,
            "checkpoint": "73",
            "name": "Local Mission Installer",
            "generated_at": utc_now(),
            "status": "mission_approved_for_manual_install",
            "mission_id": item.get("mission_id"),
            "mission_queue_id": item.get("mission_queue_id"),
            "external_side_effects": "none",
        }

        self.save_report(report)
        self.event("local_mission_installer.mission_approved", {
            "mission_id": item.get("mission_id"),
            "approved_by": approved_by,
        })

        return report

    def dry_run(self, mission_id: str | None = None) -> dict[str, Any]:
        mission_item = self.find_mission(mission_id, {"waiting_human_mission_approval", "approved_for_manual_install"})

        if mission_item is None:
            report = {
                "ok": False,
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "generated_at": utc_now(),
                "status": "no_mission_available",
                "summary": {
                    "planned_steps": 0,
                    "real_execution_enabled": False,
                    "external_side_effects": "none",
                },
            }
            self.save_report(report)
            return report

        mission = mission_item.get("mission_snapshot", {})
        validation = validate_mission_package(mission)

        plan: list[dict[str, Any]] = []

        for step in mission.get("steps", []) if isinstance(mission, dict) else []:
            step_validation = validate_mission_step(step)
            path = step_validation["path"]
            target = self.project_root / path
            plan.append({
                "action": step_validation["action"],
                "path": path,
                "target_exists": target.exists(),
                "target_sha256": sha256_file(target),
                "content_sha256": step_validation["content_sha256"],
                "status": "ready" if step_validation["ok"] else "blocked",
                "reasons": step_validation["reasons"],
            })

        report = {
            "ok": validation["ok"] and all(item["status"] == "ready" for item in plan),
            "checkpoint": "73",
            "name": "Local Mission Installer",
            "generated_at": utc_now(),
            "status": "mission_dry_run_completed",
            "mission_id": mission_item.get("mission_id"),
            "mission_status": mission_item.get("status"),
            "validation": validation,
            "plan": plan,
            "summary": {
                "planned_steps": len(plan),
                "ready_steps": len([item for item in plan if item["status"] == "ready"]),
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "human_approval_required": True,
            },
        }

        self.save_report(report)
        self.event("local_mission_installer.dry_run_completed", {
            "mission_id": mission_item.get("mission_id"),
            "planned_steps": len(plan),
        })

        return report

    def make_backup(self, target: Path, run_dir: Path) -> str | None:
        if not target.exists() or not target.is_file():
            return None

        backup_dir = run_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        safe_name = str(target.relative_to(self.project_root)).replace("\\", "__").replace("/", "__")
        backup = backup_dir / safe_name
        shutil.copy2(target, backup)
        return str(backup).replace("\\", "/")

    def install_manual(self, request: Mapping[str, Any], mission_id: str | None = None) -> dict[str, Any]:
        request_validation = validate_manual_install_request(request)

        if not request_validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "generated_at": utc_now(),
                "status": "manual_install_blocked_by_policy",
                "request_validation": request_validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        mission_item = self.find_mission(mission_id, {"approved_for_manual_install"})

        if mission_item is None:
            report = {
                "ok": False,
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "generated_at": utc_now(),
                "status": "no_approved_mission_available",
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        dry = self.dry_run(mission_item.get("mission_id"))

        if not dry.get("ok"):
            report = {
                "ok": False,
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "generated_at": utc_now(),
                "status": "manual_install_blocked_by_dry_run",
                "dry_run": dry,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        install_run_id = str(uuid4())
        run_dir = self.memory_dir / "runs" / install_run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        mission = mission_item.get("mission_snapshot", {})
        installed_steps: list[dict[str, Any]] = []

        for step in mission.get("steps", []):
            action = str(step.get("action"))
            relative_path = str(step.get("path", "")).replace("\\", "/")
            content = str(step.get("content", ""))
            target = self.project_root / relative_path
            backup_path = self.make_backup(target, run_dir)
            before_hash = sha256_file(target)

            target.parent.mkdir(parents=True, exist_ok=True)

            if action == "write_file":
                target.write_text(content, encoding="utf-8")
                result_action = "file_written"
            elif action == "append_file":
                existing = target.read_text(encoding="utf-8") if target.exists() else ""
                if content not in existing:
                    target.write_text(existing + content, encoding="utf-8")
                    result_action = "content_appended"
                else:
                    result_action = "content_already_present"
            else:
                result_action = "skipped"

            installed_steps.append({
                "action": action,
                "result_action": result_action,
                "path": relative_path,
                "backup_path": backup_path,
                "before_sha256": before_hash,
                "after_sha256": sha256_file(target),
                "installed_at": utc_now(),
            })

        manifest = self.load_list(self.install_manifest_path)
        manifest_item = {
            "install_run_id": install_run_id,
            "mission_id": mission_item.get("mission_id"),
            "mission_queue_id": mission_item.get("mission_queue_id"),
            "installed_at": utc_now(),
            "human_approved": True,
            "install_mode": "manual",
            "installed_steps": installed_steps,
            "rollback_data_available": True,
        }

        manifest.append(manifest_item)
        self.save_list(self.install_manifest_path, manifest)

        queue = self.load_list(self.mission_queue_path)
        for item in queue:
            if item.get("mission_id") == mission_item.get("mission_id"):
                item["status"] = "installed_manual"
                item["installed_at"] = utc_now()
                item["install_run_id"] = install_run_id
        self.save_list(self.mission_queue_path, queue)

        report = {
            "ok": True,
            "checkpoint": "73",
            "name": "Local Mission Installer",
            "generated_at": utc_now(),
            "status": "manual_install_completed",
            "manifest_item": manifest_item,
            "summary": {
                "installed_steps": len(installed_steps),
                "real_execution_enabled": True,
                "external_side_effects": "local_files_only",
                "auto_publish": False,
                "auto_send": False,
                "auto_deploy": False,
            },
        }

        self.save_report(report)
        self.event("local_mission_installer.manual_install_completed", {
            "mission_id": mission_item.get("mission_id"),
            "install_run_id": install_run_id,
            "installed_steps": len(installed_steps),
        })

        return report

    def summary(self) -> dict[str, Any]:
        queue = self.load_list(self.mission_queue_path)
        manifest = self.load_list(self.install_manifest_path)

        return {
            "ok": True,
            "checkpoint": "73",
            "name": "Local Mission Installer",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "mission_queue_total": len(queue),
                "waiting_human_mission_approval": len([item for item in queue if item.get("status") == "waiting_human_mission_approval"]),
                "approved_for_manual_install": len([item for item in queue if item.get("status") == "approved_for_manual_install"]),
                "installed_manual": len([item for item in queue if item.get("status") == "installed_manual"]),
                "install_manifest_total": len(manifest),
                "automatic_execution_allowed": False,
                "real_execution_enabled": False,
            },
            "latest_mission": queue[-1] if queue else None,
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_local_mission_installer.json"
        md_path = self.reports_dir / "latest_local_mission_installer.md"

        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {}) or {}

        lines = [
            "# K-Atlas Local Mission Installer",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Mission queue total: {summary.get('mission_queue_total')}",
            f"- Waiting approval: {summary.get('waiting_human_mission_approval')}",
            f"- Approved: {summary.get('approved_for_manual_install')}",
            f"- Installed: {summary.get('installed_manual')}",
            f"- Installed steps: {summary.get('installed_steps')}",
            f"- External side effects: {summary.get('external_side_effects')}",
            "",
            "## Guardrails",
            "",
            "- Declarative missions only",
            "- No shell execution",
            "- No API calls",
            "- No deploy",
            "- No publish",
            "- Human approval required",
        ]

        return "\n".join(lines)
