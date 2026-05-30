from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .center import CommandCenter


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CommandCenterScheduler:
    def __init__(
        self,
        state_dir: str | Path = "memory/command_center_scheduler",
        command_center: CommandCenter | None = None,
        interval_seconds: int = 900,
    ) -> None:
        self.state_dir = Path(state_dir)
        self.state_path = self.state_dir / "scheduler_state.json"
        self.events_path = self.state_dir / "events.jsonl"
        self.pid_path = self.state_dir / "pids.json"
        self.interval_seconds = interval_seconds
        self.command_center = command_center or CommandCenter()

    def write_event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.state_dir.mkdir(parents=True, exist_ok=True)

        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }

        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

        return row

    def save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {}

        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_pid(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.pid_path.write_text(
            json.dumps({
                "scheduler_pid": os.getpid(),
                "updated_at": utc_now(),
            }, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def run_once(
        self,
        objective: str = "ciclo automatico supervisionado do K-Atlas",
        execute_tasks: bool = True,
    ) -> dict[str, Any]:
        run_id = str(uuid4())

        created = self.command_center.create_cycle(objective)

        if execute_tasks:
            executed = self.command_center.run_pending_once(limit=10)
        else:
            executed = {
                "ok": True,
                "status": "execution_skipped_for_test",
                "executed_count": 0,
            }

        state = {
            "ok": True,
            "checkpoint": "43",
            "name": "Command Center Scheduler 24/7",
            "run_id": run_id,
            "timestamp": utc_now(),
            "status": "cycle_completed",
            "objective": objective,
            "execute_tasks": execute_tasks,
            "created": created,
            "executed": executed,
            "next_interval_seconds": self.interval_seconds,
            "guardrails": [
                "sem publicacao automatica",
                "sem deploy automatico",
                "sem mensagem em massa",
                "sem token em texto puro",
                "sem API externa real",
                "somente ciclos locais supervisionados",
            ],
        }

        self.save_state(state)
        self.write_event("scheduler.cycle.completed", state)
        return state

    def run_forever(self) -> None:
        self.save_pid()

        print("K-Atlas Command Center Scheduler 24/7 iniciado.")
        print("Sem publicacao. Sem deploy automatico. Pressione Ctrl+C para parar.")

        while True:
            result = self.run_once(
                objective="manter K-Atlas operacional, auditado e reportado",
                execute_tasks=True,
            )

            print(json.dumps({
                "timestamp": result["timestamp"],
                "status": result["status"],
                "executed_count": result["executed"].get("executed_count"),
            }, ensure_ascii=False))

            time.sleep(self.interval_seconds)
