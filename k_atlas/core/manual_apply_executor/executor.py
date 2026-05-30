from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_manual_apply_request, validate_target_path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ManualApplyExecutor:
    def __init__(
        self,
        project_root: str | Path = ".",
        gate_queue_path: str | Path = "live/autoprogramming_apply_package_gate/apply_package_gate_queue.json",
        memory_dir: str | Path = "memory/manual_apply_executor",
        reports_dir: str | Path = "reports/manual_apply_executor",
    ) -> None:
        self.project_root = Path(project_root)
        self.gate_queue_path = self.project_root / gate_queue_path
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.events_path = self.memory_dir / "events.jsonl"
        self.apply_manifest_path = self.memory_dir / "apply_manifest.json"

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

    def find_gate_item(self, gate_id: str | None = None) -> dict[str, Any] | None:
        items = self.load_list(self.gate_queue_path)

        candidates = [
            item for item in items
            if item.get("status") == "waiting_human_apply_approval"
            and item.get("manual_apply_allowed_after_approval") is True
            and item.get("automatic_apply_allowed") is not True
            and item.get("real_execution_enabled") is not True
        ]

        if gate_id:
            for item in candidates:
                if item.get("gate_id") == gate_id:
                    return item
            return None

        return candidates[0] if candidates else None

    def load_manifest(self) -> list[dict[str, Any]]:
        return self.load_list(self.apply_manifest_path)

    def save_manifest(self, rows: list[dict[str, Any]]) -> None:
        self.save_list(self.apply_manifest_path, rows)

    def make_backup(self, target_path: Path, run_dir: Path) -> str | None:
        if not target_path.exists():
            return None

        backup_dir = run_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        safe_name = str(target_path).replace(":", "").replace("\\", "__").replace("/", "__")
        backup_path = backup_dir / safe_name

        if target_path.is_file():
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target_path, backup_path)
            return str(backup_path).replace("\\", "/")

        return None

    def validate_gate_item_for_apply(self, gate_item: Mapping[str, Any]) -> dict[str, Any]:
        reasons: list[str] = []

        if gate_item.get("status") != "waiting_human_apply_approval":
            reasons.append(f"invalid_gate_status:{gate_item.get('status')}")

        if gate_item.get("manual_apply_allowed_after_approval") is not True:
            reasons.append("manual_apply_not_allowed")

        validation = gate_item.get("validation", {})
        if not isinstance(validation, dict) or validation.get("ok") is not True:
            reasons.append("gate_validation_not_passed")

        package = gate_item.get("package_snapshot", {})
        if not isinstance(package, dict):
            reasons.append("package_snapshot_required")
            package = {}

        file_plans = package.get("file_plans", [])
        if not isinstance(file_plans, list) or not file_plans:
            reasons.append("file_plans_required")

        file_results: list[dict[str, Any]] = []

        for plan in file_plans if isinstance(file_plans, list) else []:
            path_result = validate_target_path(str(plan.get("path", "")))
            content = str(plan.get("content", ""))
            expected_hash = str(plan.get("content_sha256", "")).strip()
            actual_hash = sha256_text(content)

            local_reasons = list(path_result["reasons"]) if not path_result["ok"] else []

            if expected_hash and expected_hash != actual_hash:
                local_reasons.append("content_hash_mismatch")

            file_result = {
                "ok": len(local_reasons) == 0,
                "path": path_result["path"],
                "content_sha256": actual_hash,
                "reasons": local_reasons or ["file_ready_for_manual_apply"],
            }

            file_results.append(file_result)

            if not file_result["ok"]:
                reasons.append("invalid_file_plan_detected")

        return {
            "ok": len(reasons) == 0,
            "status": "gate_item_ready_for_manual_apply" if not reasons else "gate_item_blocked",
            "reasons": reasons or ["gate_item_ready_for_manual_apply"],
            "file_results": file_results,
        }

    def dry_run(self, gate_id: str | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        gate_item = self.find_gate_item(gate_id)

        if gate_item is None:
            report = {
                "ok": False,
                "checkpoint": "69",
                "name": "Manual Apply Executor",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "no_gate_item_ready",
                "summary": {
                    "planned_files": 0,
                    "execution_enabled": False,
                    "real_execution_enabled": False,
                    "external_side_effects": "none",
                },
            }
            self.save_report(report)
            return report

        validation = self.validate_gate_item_for_apply(gate_item)
        package = gate_item.get("package_snapshot", {})
        file_plans = package.get("file_plans", []) if isinstance(package, dict) else []

        plan = []

        for item in file_plans:
            target_path = self.project_root / str(item.get("path", "")).replace("\\", "/")
            plan.append({
                "path": str(item.get("path", "")).replace("\\", "/"),
                "exists": target_path.exists(),
                "action": "overwrite_with_backup" if target_path.exists() else "create_new_file",
                "content_size": len(str(item.get("content", ""))),
                "content_sha256": sha256_text(str(item.get("content", ""))),
            })

        report = {
            "ok": validation["ok"],
            "checkpoint": "69",
            "name": "Manual Apply Executor",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "dry_run_completed",
            "gate_id": gate_item.get("gate_id"),
            "apply_package_id": gate_item.get("apply_package_id"),
            "validation": validation,
            "plan": plan,
            "summary": {
                "planned_files": len(plan),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "aplicar somente com human_approved true e apply_mode manual",
            },
        }

        self.save_report(report)
        self.event("manual_apply_executor.dry_run_completed", {
            "run_id": run_id,
            "gate_id": gate_item.get("gate_id"),
            "planned_files": len(plan),
        })

        return report

    def apply_manual(self, request: Mapping[str, Any], gate_id: str | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        request_validation = validate_manual_apply_request(request)

        if not request_validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "69",
                "name": "Manual Apply Executor",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "manual_apply_blocked_by_policy",
                "request_validation": request_validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        gate_item = self.find_gate_item(gate_id)

        if gate_item is None:
            report = {
                "ok": False,
                "checkpoint": "69",
                "name": "Manual Apply Executor",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "no_gate_item_ready",
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        gate_validation = self.validate_gate_item_for_apply(gate_item)

        if not gate_validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "69",
                "name": "Manual Apply Executor",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "gate_item_blocked",
                "gate_validation": gate_validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        run_dir = self.memory_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        package = gate_item.get("package_snapshot", {})
        file_plans = package.get("file_plans", []) if isinstance(package, dict) else []

        applied_files: list[dict[str, Any]] = []

        for plan in file_plans:
            relative_path = str(plan.get("path", "")).replace("\\", "/")
            target_path = self.project_root / relative_path
            content = str(plan.get("content", ""))

            backup_path = self.make_backup(target_path, run_dir)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")

            applied_files.append({
                "path": relative_path,
                "backup_path": backup_path,
                "content_sha256": sha256_text(content),
                "applied_at": utc_now(),
            })

        manifest = self.load_manifest()

        manifest_item = {
            "run_id": run_id,
            "gate_id": gate_item.get("gate_id"),
            "apply_package_id": gate_item.get("apply_package_id"),
            "applied_at": utc_now(),
            "applied_files": applied_files,
            "rollback_available": True,
            "human_approved": True,
            "apply_mode": "manual",
        }

        manifest.append(manifest_item)
        self.save_manifest(manifest)

        report = {
            "ok": True,
            "checkpoint": "69",
            "name": "Manual Apply Executor",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "manual_apply_completed",
            "manifest_item": manifest_item,
            "summary": {
                "applied_files": len(applied_files),
                "backup_created": len([item for item in applied_files if item.get("backup_path")]) > 0,
                "rollback_available": True,
                "execution_enabled": True,
                "real_execution_enabled": True,
                "external_side_effects": "local_files_only",
                "auto_publish": False,
                "auto_send": False,
                "auto_deploy": False,
            },
        }

        self.save_report(report)
        self.event("manual_apply_executor.manual_apply_completed", {
            "run_id": run_id,
            "applied_files": len(applied_files),
        })

        return report

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_manual_apply_executor.json"
        md_path = self.reports_dir / "latest_manual_apply_executor.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(report), encoding="utf-8")

        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Manual Apply Executor",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Planned files: {summary.get('planned_files')}",
            f"- Applied files: {summary.get('applied_files')}",
            f"- Backup created: {summary.get('backup_created')}",
            f"- Rollback available: {summary.get('rollback_available')}",
            f"- External side effects: {summary.get('external_side_effects')}",
            f"- Next action: {summary.get('next_action')}",
        ]

        return "\n".join(lines)
