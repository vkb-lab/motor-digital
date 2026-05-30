from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_manual_rollback_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ManualApplyRollbackExecutor:
    def __init__(
        self,
        project_root: str | Path = ".",
        apply_manifest_path: str | Path = "memory/manual_apply_executor/apply_manifest.json",
        memory_dir: str | Path = "memory/manual_apply_rollback_executor",
        reports_dir: str | Path = "reports/manual_apply_rollback_executor",
    ) -> None:
        self.project_root = Path(project_root)
        self.apply_manifest_path = self.project_root / apply_manifest_path
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.rollback_manifest_path = self.memory_dir / "rollback_manifest.json"
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

    def resolve_backup_path(self, backup_path: str | None) -> Path | None:
        if not backup_path:
            return None
        path = Path(backup_path)
        if path.is_absolute():
            return path
        return self.project_root / path

    def load_apply_manifest(self) -> list[dict[str, Any]]:
        return self.load_list(self.apply_manifest_path)

    def load_rollback_manifest(self) -> list[dict[str, Any]]:
        return self.load_list(self.rollback_manifest_path)

    def find_apply_run(self, run_id: str | None = None) -> dict[str, Any] | None:
        manifest = self.load_apply_manifest()
        rollback_manifest = self.load_rollback_manifest()

        rolled_back_ids = {
            item.get("source_apply_run_id")
            for item in rollback_manifest
            if item.get("source_apply_run_id")
        }

        candidates = [
            item for item in manifest
            if item.get("rollback_available") is True
            and item.get("run_id") not in rolled_back_ids
        ]

        if run_id:
            for item in candidates:
                if item.get("run_id") == run_id:
                    return item
            return None

        return candidates[-1] if candidates else None

    def dry_run(self, run_id: str | None = None) -> dict[str, Any]:
        operation_id = str(uuid4())
        apply_run = self.find_apply_run(run_id)

        if apply_run is None:
            report = {
                "ok": False,
                "checkpoint": "70",
                "name": "Manual Apply Rollback Executor",
                "operation_id": operation_id,
                "generated_at": utc_now(),
                "status": "no_apply_run_available_for_rollback",
                "summary": {
                    "planned_files": 0,
                    "external_side_effects": "none",
                    "real_execution_enabled": False,
                },
            }
            self.save_report(report)
            return report

        plan: list[dict[str, Any]] = []

        for item in apply_run.get("applied_files", []):
            relative_path = str(item.get("path", "")).replace("\\", "/")
            target_path = self.project_root / relative_path
            backup_path = self.resolve_backup_path(item.get("backup_path"))

            if backup_path and backup_path.exists():
                action = "restore_backup"
                ready = True
            elif backup_path is None:
                action = "delete_created_file"
                ready = target_path.exists()
            else:
                action = "backup_missing"
                ready = False

            plan.append({
                "path": relative_path,
                "target_exists": target_path.exists(),
                "target_sha256": sha256_file(target_path),
                "backup_path": str(backup_path).replace("\\", "/") if backup_path else None,
                "backup_exists": backup_path.exists() if backup_path else None,
                "rollback_action": action,
                "ready": ready,
            })

        report = {
            "ok": all(item["ready"] for item in plan),
            "checkpoint": "70",
            "name": "Manual Apply Rollback Executor",
            "operation_id": operation_id,
            "generated_at": utc_now(),
            "status": "rollback_dry_run_completed",
            "source_apply_run_id": apply_run.get("run_id"),
            "plan": plan,
            "summary": {
                "planned_files": len(plan),
                "ready_files": len([item for item in plan if item["ready"]]),
                "external_side_effects": "none",
                "real_execution_enabled": False,
                "next_action": "executar rollback somente com aprovacao humana explicita",
            },
        }

        self.save_report(report)
        self.event("manual_apply_rollback_executor.dry_run_completed", {
            "operation_id": operation_id,
            "source_apply_run_id": apply_run.get("run_id"),
            "planned_files": len(plan),
        })

        return report

    def rollback_manual(self, request: Mapping[str, Any], run_id: str | None = None) -> dict[str, Any]:
        operation_id = str(uuid4())
        validation = validate_manual_rollback_request(request)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "70",
                "name": "Manual Apply Rollback Executor",
                "operation_id": operation_id,
                "generated_at": utc_now(),
                "status": "manual_rollback_blocked_by_policy",
                "request_validation": validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        dry = self.dry_run(run_id)

        if not dry.get("ok"):
            report = {
                "ok": False,
                "checkpoint": "70",
                "name": "Manual Apply Rollback Executor",
                "operation_id": operation_id,
                "generated_at": utc_now(),
                "status": "manual_rollback_blocked_by_dry_run",
                "dry_run": dry,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        restored_files: list[dict[str, Any]] = []

        for item in dry.get("plan", []):
            target_path = self.project_root / item["path"]
            backup_path = self.resolve_backup_path(item.get("backup_path"))

            before_hash = sha256_file(target_path)

            if item["rollback_action"] == "restore_backup" and backup_path and backup_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(backup_path.read_bytes())
                result_action = "backup_restored"
            elif item["rollback_action"] == "delete_created_file" and target_path.exists():
                target_path.unlink()
                result_action = "created_file_deleted"
            else:
                result_action = "skipped"

            restored_files.append({
                "path": item["path"],
                "rollback_action": result_action,
                "before_sha256": before_hash,
                "after_sha256": sha256_file(target_path),
                "rolled_back_at": utc_now(),
            })

        rollback_manifest = self.load_rollback_manifest()
        manifest_item = {
            "rollback_operation_id": operation_id,
            "source_apply_run_id": dry.get("source_apply_run_id"),
            "rolled_back_at": utc_now(),
            "human_approved": True,
            "rollback_mode": "manual",
            "restored_files": restored_files,
        }

        rollback_manifest.append(manifest_item)
        self.save_list(self.rollback_manifest_path, rollback_manifest)

        report = {
            "ok": True,
            "checkpoint": "70",
            "name": "Manual Apply Rollback Executor",
            "operation_id": operation_id,
            "generated_at": utc_now(),
            "status": "manual_rollback_completed",
            "manifest_item": manifest_item,
            "summary": {
                "rolled_back_files": len(restored_files),
                "external_side_effects": "local_files_only",
                "real_execution_enabled": True,
                "auto_publish": False,
                "auto_send": False,
                "auto_deploy": False,
            },
        }

        self.save_report(report)
        self.event("manual_apply_rollback_executor.manual_rollback_completed", {
            "operation_id": operation_id,
            "rolled_back_files": len(restored_files),
        })

        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_manual_apply_rollback_executor.json"
        md_path = self.reports_dir / "latest_manual_apply_rollback_executor.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Manual Apply Rollback Executor",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Planned files: {summary.get('planned_files')}",
            f"- Ready files: {summary.get('ready_files')}",
            f"- Rolled back files: {summary.get('rolled_back_files')}",
            f"- External side effects: {summary.get('external_side_effects')}",
            f"- Next action: {summary.get('next_action')}",
        ]
        return "\n".join(lines)
