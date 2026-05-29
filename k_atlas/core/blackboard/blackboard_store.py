from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class JsonListStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"Store corrompido: {self.path}")
        return data

    def save(self, rows: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


class BlackboardStore:
    def __init__(
        self,
        messages_path: str | Path = "memory/blackboard/messages.json",
        commands_path: str | Path = "memory/blackboard/command_queue.json",
        results_path: str | Path = "memory/blackboard/command_results.json",
    ) -> None:
        self.messages = JsonListStore(messages_path)
        self.commands = JsonListStore(commands_path)
        self.results = JsonListStore(results_path)

    def add_message(self, author: str, role: str, content: str, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
        rows = self.messages.load()
        item = {
            "message_id": str(uuid4()),
            "created_at": utc_now_iso(),
            "author": author,
            "role": role,
            "content": content,
            "metadata": dict(metadata or {}),
        }
        rows.append(item)
        self.messages.save(rows)
        return item

    def queue_command(
        self,
        title: str,
        command: str,
        requested_by: str = "human_operator",
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        rows = self.commands.load()
        item = {
            "command_id": str(uuid4()),
            "created_at": utc_now_iso(),
            "title": title,
            "command": command,
            "requested_by": requested_by,
            "approval_status": "pending_approval",
            "execution_status": "waiting_approval",
            "metadata": dict(metadata or {}),
        }
        rows.append(item)
        self.commands.save(rows)
        return item

    def approve_command(self, command_id: str, reviewer: str = "k_supervisor") -> dict[str, Any]:
        rows = self.commands.load()
        for item in rows:
            if item.get("command_id") == command_id:
                item["approval_status"] = "approved"
                item["approved_by"] = reviewer
                item["approved_at"] = utc_now_iso()
                item["execution_status"] = "pending_execution"
                self.commands.save(rows)
                return item
        raise KeyError(f"command_id nao encontrado: {command_id}")

    def mark_running(self, command_id: str) -> dict[str, Any]:
        rows = self.commands.load()
        for item in rows:
            if item.get("command_id") == command_id:
                item["execution_status"] = "running"
                item["started_at"] = utc_now_iso()
                self.commands.save(rows)
                return item
        raise KeyError(f"command_id nao encontrado: {command_id}")

    def mark_finished(self, command_id: str, ok: bool, result: Mapping[str, Any]) -> dict[str, Any]:
        rows = self.commands.load()
        for item in rows:
            if item.get("command_id") == command_id:
                item["execution_status"] = "finished" if ok else "failed"
                item["finished_at"] = utc_now_iso()
                item["last_result"] = dict(result)
                self.commands.save(rows)
                return item
        raise KeyError(f"command_id nao encontrado: {command_id}")

    def add_result(self, command_id: str, result: Mapping[str, Any]) -> dict[str, Any]:
        rows = self.results.load()
        item = {
            "result_id": str(uuid4()),
            "command_id": command_id,
            "created_at": utc_now_iso(),
            "result": dict(result),
        }
        rows.append(item)
        self.results.save(rows)
        return item