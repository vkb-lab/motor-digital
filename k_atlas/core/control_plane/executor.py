from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .event_bus import EventBus
from .supervisor_queue import SupervisorQueue
from .system_state import SystemState


SAFE_EXECUTION_ACTIONS = {
    "read_events",
    "summarize_state",
    "generate_report",
    "create_content_package",
    "dry_run",
    "run_smoke_test",
    "prepare_deploy",
}


BLOCKED_EXECUTION_ACTIONS = {
    "official_publish",
    "mass_messaging",
    "browser_automation",
    "external_api_without_vault",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_filename(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value)
    return cleaned[:120] or "execution"


class ControlPlaneExecutor:
    def __init__(
        self,
        event_bus: EventBus | None = None,
        supervisor_queue: SupervisorQueue | None = None,
        system_state: SystemState | None = None,
        output_dir: str | Path = "reports/control_plane/executions",
    ) -> None:
        self.event_bus = event_bus or EventBus()
        self.supervisor_queue = supervisor_queue or SupervisorQueue()
        self.system_state = system_state or SystemState()
        self.output_dir = Path(output_dir)

    def execute_approved(
        self,
        approval_id: str,
        executor_id: str = "k_control_plane_executor",
    ) -> dict[str, Any]:
        approvals = self.supervisor_queue.load()

        target_index = None
        target_item: dict[str, Any] | None = None

        for index, item in enumerate(approvals):
            if item.get("approval_id") == approval_id:
                target_index = index
                target_item = item
                break

        if target_item is None or target_index is None:
            raise KeyError(f"approval_id nao encontrado: {approval_id}")

        if target_item.get("status") != "approved":
            result = {
                "ok": False,
                "status": "not_approved",
                "approval_id": approval_id,
                "reasons": ["task_must_be_approved_before_execution"],
            }
            self.event_bus.emit(
                event_type="execution.blocked",
                source="control_plane.executor",
                payload=result,
                severity="warning",
            )
            return result

        if target_item.get("execution_status") == "executed":
            return {
                "ok": True,
                "status": "already_executed",
                "approval_id": approval_id,
                "result": target_item.get("execution_result", {}),
            }

        task = dict(target_item.get("task", {}))
        action = str(task.get("action", "")).strip()

        if action in BLOCKED_EXECUTION_ACTIONS or action not in SAFE_EXECUTION_ACTIONS:
            result = {
                "ok": False,
                "status": "execution_action_blocked",
                "approval_id": approval_id,
                "action": action,
                "reasons": [f"action_not_safe_for_executor:{action}"],
            }
            self.event_bus.emit(
                event_type="execution.blocked",
                source="control_plane.executor",
                payload=result,
                severity="warning",
            )
            target_item["execution_status"] = "blocked"
            target_item["execution_result"] = result
            approvals[target_index] = target_item
            self.supervisor_queue.save(approvals)
            return result

        self.event_bus.emit(
            event_type="execution.started",
            source="control_plane.executor",
            payload={
                "approval_id": approval_id,
                "task": task,
                "executor_id": executor_id,
            },
        )

        result = self._execute_safe_action(task=task, approval_id=approval_id, executor_id=executor_id)

        target_item["status"] = "executed"
        target_item["execution_status"] = "executed"
        target_item["executed_at"] = utc_now_iso()
        target_item["executed_by"] = executor_id
        target_item["execution_result"] = result
        approvals[target_index] = target_item
        self.supervisor_queue.save(approvals)

        self.system_state.set_module_status(
            "control_plane_executor",
            "executed",
            {
                "last_approval_id": approval_id,
                "last_action": action,
                "last_result_status": result.get("status"),
            },
        )

        self.event_bus.emit(
            event_type="execution.finished",
            source="control_plane.executor",
            payload=result,
        )

        return result

    def execute_all_approved(self, executor_id: str = "k_control_plane_executor") -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        for item in self.supervisor_queue.load():
            if item.get("status") == "approved" and item.get("execution_status") != "executed":
                results.append(self.execute_approved(item["approval_id"], executor_id=executor_id))

        return results

    def _execute_safe_action(
        self,
        task: Mapping[str, Any],
        approval_id: str,
        executor_id: str,
    ) -> dict[str, Any]:
        action = str(task.get("action", "")).strip()
        task_id = str(task.get("task_id") or uuid4())
        payload = dict(task.get("payload", {}))

        if action == "read_events":
            return self._write_execution_record(
                action=action,
                task_id=task_id,
                approval_id=approval_id,
                executor_id=executor_id,
                data={
                    "events": self.event_bus.read_events(limit=50),
                },
            )

        if action == "summarize_state":
            return self._write_execution_record(
                action=action,
                task_id=task_id,
                approval_id=approval_id,
                executor_id=executor_id,
                data={
                    "system_state": self.system_state.load(),
                    "recent_events": self.event_bus.read_events(limit=20),
                    "approvals_count": len(self.supervisor_queue.load()),
                },
            )

        if action == "generate_report":
            return self._write_execution_record(
                action=action,
                task_id=task_id,
                approval_id=approval_id,
                executor_id=executor_id,
                data={
                    "title": "K-Atlas Control Plane Report",
                    "summary": "Relatorio gerado por executor supervisionado.",
                    "system_state": self.system_state.load(),
                    "recent_events": self.event_bus.read_events(limit=30),
                    "payload": payload,
                },
            )

        if action == "create_content_package":
            return self._write_execution_record(
                action=action,
                task_id=task_id,
                approval_id=approval_id,
                executor_id=executor_id,
                data={
                    "package_type": "supervised_content_package",
                    "status": "created",
                    "module": payload.get("module", "k_atlas"),
                    "risk": payload.get("risk", "controlled"),
                    "official_publish": False,
                    "items": [
                        {
                            "type": "brief",
                            "title": "Brief operacional supervisionado",
                            "body": "Pacote criado pelo Control Plane Executor para validacao humana.",
                        },
                        {
                            "type": "next_action",
                            "title": "Enviar para modulo especializado",
                            "body": "Este pacote pode seguir para K-Social, SaaS Factory ou Creative Media Gateway.",
                        },
                    ],
                    "payload": payload,
                },
            )

        if action == "dry_run":
            return self._write_execution_record(
                action=action,
                task_id=task_id,
                approval_id=approval_id,
                executor_id=executor_id,
                data={
                    "dry_run": True,
                    "side_effects": "none",
                    "payload": payload,
                },
            )

        if action == "run_smoke_test":
            compiled = []
            targets = [
                "k_atlas/core/control_plane/event_bus.py",
                "k_atlas/core/control_plane/agent_registry.py",
                "k_atlas/core/control_plane/autonomy_policy.py",
                "k_atlas/core/control_plane/task_router.py",
                "k_atlas/core/control_plane/executor.py",
            ]

            for target in targets:
                py_compile.compile(target, doraise=True)
                compiled.append(target)

            return self._write_execution_record(
                action=action,
                task_id=task_id,
                approval_id=approval_id,
                executor_id=executor_id,
                data={
                    "smoke_test": "py_compile_control_plane",
                    "compiled": compiled,
                    "status": "passed",
                },
            )

        if action == "prepare_deploy":
            return self._write_execution_record(
                action=action,
                task_id=task_id,
                approval_id=approval_id,
                executor_id=executor_id,
                data={
                    "deploy_plan": {
                        "target": "render",
                        "mode": "auto_deploy_by_git_push",
                        "requires_manual_confirmation": True,
                        "external_api_enabled": False,
                    },
                    "payload": payload,
                },
            )

        return {
            "ok": False,
            "status": "unknown_safe_action",
            "action": action,
            "approval_id": approval_id,
        }

    def _write_execution_record(
        self,
        action: str,
        task_id: str,
        approval_id: str,
        executor_id: str,
        data: Mapping[str, Any],
    ) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        execution_id = str(uuid4())
        path = self.output_dir / f"{safe_filename(action)}_{safe_filename(task_id)}.json"

        record = {
            "ok": True,
            "status": "executed",
            "execution_id": execution_id,
            "approval_id": approval_id,
            "task_id": task_id,
            "action": action,
            "executor_id": executor_id,
            "executed_at": utc_now_iso(),
            "output_path": str(path).replace("\\", "/"),
            "data": dict(data),
        }

        path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

        return record