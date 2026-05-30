from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .policy import validate_command_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        result = subprocess.run(
            args,
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return {
            "ok": result.returncode == 0,
            "command": " ".join(args),
            "returncode": result.returncode,
            "stdout": result.stdout[-5000:],
            "stderr": result.stderr[-5000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "command": " ".join(args),
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }


class CommandCenter:
    def __init__(
        self,
        memory_dir: str | Path = "memory/command_center",
        reports_dir: str | Path = "reports/command_center",
    ) -> None:
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.queue_path = self.memory_dir / "command_queue.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def default_plan(self, objective: str = "manter K-Atlas operacional") -> list[dict[str, Any]]:
        return [
            {"action": "health_check", "objective": objective},
            {"action": "check_daemon", "objective": objective},
            {"action": "check_git", "objective": objective},
            {"action": "generate_autoreport", "objective": objective},
            {"action": "sandbox_creative_plan", "objective": "planejar audiovisual K-Atlas sem API real"},
            {"action": "deploy_assisted_check", "objective": "validar readiness sem deploy automatico"},
        ]

    def load_queue(self) -> list[dict[str, Any]]:
        if not self.queue_path.exists():
            return []
        try:
            data = json.loads(self.queue_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_queue(self, rows: list[dict[str, Any]]) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.queue_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def create_cycle(self, objective: str = "manter K-Atlas operacional") -> dict[str, Any]:
        cycle_id = str(uuid4())
        tasks = []

        for item in self.default_plan(objective):
            validation = validate_command_payload(item)
            tasks.append({
                "task_id": str(uuid4()),
                "cycle_id": cycle_id,
                "created_at": utc_now(),
                "status": "pending" if validation["ok"] else "blocked",
                "validation": validation,
                **item,
            })

        queue = self.load_queue()
        queue.extend(tasks)
        self.save_queue(queue)

        result = {
            "ok": True,
            "cycle_id": cycle_id,
            "status": "cycle_created",
            "tasks_created": len(tasks),
            "tasks": tasks,
        }

        self.event("cycle.created", result)
        return result

    def execute_task(self, task: dict[str, Any]) -> dict[str, Any]:
        action = task.get("action")

        if action == "health_check":
            try:
                with urllib.request.urlopen("http://127.0.0.1:8501/_stcore/health", timeout=5) as response:
                    return {"ok": True, "status": "health_ok", "http_status": response.status}
            except Exception as exc:
                return {"ok": False, "status": "health_failed", "error": str(exc)}

        if action == "check_daemon":
            path = Path("memory/local_daemon/heartbeat.json")
            if not path.exists():
                return {"ok": False, "status": "daemon_heartbeat_missing"}
            return {"ok": True, "status": "daemon_heartbeat_found", "heartbeat": json.loads(path.read_text(encoding="utf-8"))}

        if action == "check_git":
            return {
                "ok": True,
                "status": "git_checked",
                "git_status": run_cmd(["git", "status", "--short"]),
                "git_log": run_cmd(["git", "log", "--oneline", "-5"]),
            }

        if action == "generate_autoreport":
            return run_cmd([sys.executable, "-m", "k_atlas.core.autoreporter.run_report"], timeout=180)

        if action == "sandbox_creative_plan":
            return run_cmd([sys.executable, "-m", "k_atlas.core.sandbox_api_adapter.run_demo"], timeout=180)

        if action == "deploy_assisted_check":
            return run_cmd([sys.executable, "-m", "k_atlas.core.deploy_pipeline.run_deploy_check"], timeout=180)

        if action == "saas_factory_plan":
            return run_cmd([sys.executable, "-m", "k_atlas.saas_factory.workflows.run_saas_factory_workflow"], timeout=240)

        return {"ok": False, "status": "unknown_action", "action": action}

    def run_pending_once(self, limit: int = 10) -> dict[str, Any]:
        queue = self.load_queue()
        executed = []

        for task in queue:
            if len(executed) >= limit:
                break

            if task.get("status") != "pending":
                continue

            validation = validate_command_payload(task)
            if not validation["ok"]:
                task["status"] = "blocked"
                task["validation"] = validation
                continue

            task["status"] = "running"
            task["started_at"] = utc_now()
            result = self.execute_task(task)
            task["finished_at"] = utc_now()
            task["status"] = "finished" if result.get("ok") else "failed"
            task["result"] = result
            executed.append(task)

            self.event("task.executed", {
                "task_id": task.get("task_id"),
                "action": task.get("action"),
                "status": task.get("status"),
            })

        self.save_queue(queue)

        report = {
            "ok": True,
            "checkpoint": "42",
            "name": "Command Center Autonomo",
            "generated_at": utc_now(),
            "executed_count": len(executed),
            "executed": executed,
            "queue_total": len(queue),
            "side_effects": "local_reports_checks_only_no_publish_no_deploy",
        }

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_command_center_run.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.event("cycle.executed", report)
        return report
