# -*- coding: utf-8 -*-
"""
K-Atlas OS - Task Agent

Agente operacional para criar, listar, atualizar e concluir tarefas.
Persistencia simples em JSON para evoluir depois para banco de dados, API e workers.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agents.base_agent import AgentContext, BaseAgent


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskAgent(BaseAgent):
    agent_id = "task_agent"
    name = "Task Agent"
    description = "Agente de tarefas operacionais do K-Atlas OS."
    version = "0.1.0"
    capabilities = [
        "task",
        "tasks",
        "operations",
        "workflow",
    ]
    permissions = [
        "agent.execute",
        "task.read",
        "task.write",
        "memory.read",
        "memory.write",
        "events.read",
    ]

    VALID_STATUS = ["pending", "running", "done", "blocked", "cancelled"]
    VALID_PRIORITY = ["low", "normal", "high", "urgent"]

    def __init__(
        self,
        storage_path: Optional[str | Path] = None,
        event_bus: Optional[Any] = None,
        permission_manager: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            permission_manager=permission_manager,
            config=config,
        )
        configured_path = self.config.get("storage_path")
        self.storage_path = Path(storage_path or configured_path or "memory/tasks.json")

    def metadata(self) -> Dict[str, Any]:
        return {
            "base_class": "BaseAgent",
            "type": "operations",
            "created_for": "K-Atlas OS",
            "module_role": "task_management",
            "storage_path": str(self.storage_path),
        }

    def required_permission(self, context: AgentContext) -> str:
        action = self._action(context.command)

        if action in ["create", "update", "complete", "delete", "cancel", "block"]:
            return "task.write"

        return "task.read"

    def run(self, context: AgentContext) -> Dict[str, Any]:
        action = self._action(context.command)

        if action == "ping":
            return self._ping()

        if action in ["help", "commands"]:
            return self._help()

        if action == "create":
            return self._create(context.payload)

        if action in ["list", "all"]:
            return self._list(context.payload)

        if action == "get":
            return self._get(context.payload)

        if action == "update":
            return self._update(context.payload)

        if action == "complete":
            return self._set_status(context.payload, "done")

        if action == "block":
            return self._set_status(context.payload, "blocked")

        if action == "cancel":
            return self._set_status(context.payload, "cancelled")

        if action == "delete":
            return self._delete(context.payload)

        if action == "stats":
            return self._stats()

        return {
            "success": False,
            "message": "Comando nao reconhecido pelo TaskAgent.",
            "action": action,
            "available_actions": [
                "ping",
                "help",
                "create",
                "list",
                "get",
                "update",
                "complete",
                "block",
                "cancel",
                "delete",
                "stats",
            ],
        }

    def _action(self, command: str) -> str:
        clean = str(command).strip().lower()
        if "." in clean:
            return clean.split(".", 1)[1]
        return clean

    def _ping(self) -> Dict[str, Any]:
        return {
            "success": True,
            "agent_id": self.agent_id,
            "message": "TaskAgent operacional.",
            "storage_path": str(self.storage_path),
        }

    def _help(self) -> Dict[str, Any]:
        return {
            "success": True,
            "commands": {
                "task_agent.create": "Cria uma tarefa.",
                "task_agent.list": "Lista tarefas.",
                "task_agent.get": "Busca uma tarefa por task_id.",
                "task_agent.update": "Atualiza campos de uma tarefa.",
                "task_agent.complete": "Marca tarefa como concluida.",
                "task_agent.block": "Marca tarefa como bloqueada.",
                "task_agent.cancel": "Cancela uma tarefa.",
                "task_agent.delete": "Remove uma tarefa.",
                "task_agent.stats": "Mostra resumo das tarefas.",
            },
            "example_create": {
                "title": "Criar campanha",
                "description": "Gerar campanha inicial",
                "priority": "high",
                "tags": ["campaign", "marketing"],
                "assigned_agent_id": "campaign_agent",
            },
        }

    def _create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = str(payload.get("title", "")).strip()
        if not title:
            raise ValueError("Campo obrigatorio ausente: title")

        priority = str(payload.get("priority", "normal")).strip().lower()
        if priority not in self.VALID_PRIORITY:
            priority = "normal"

        status = str(payload.get("status", "pending")).strip().lower()
        if status not in self.VALID_STATUS:
            status = "pending"

        task = {
            "task_id": str(uuid.uuid4()),
            "title": title,
            "description": str(payload.get("description", "")).strip(),
            "status": status,
            "priority": priority,
            "tags": self._as_list(payload.get("tags", [])),
            "assigned_agent_id": payload.get("assigned_agent_id"),
            "payload": payload.get("payload", {}),
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "completed_at": None,
        }

        store = self._read_store()
        store["tasks"].append(task)
        self._write_store(store)

        return {
            "success": True,
            "message": "Tarefa criada.",
            "task": task,
        }

    def _list(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        store = self._read_store()
        tasks = list(store.get("tasks", []))

        status = payload.get("status")
        if status:
            tasks = [task for task in tasks if task.get("status") == str(status).lower()]

        assigned_agent_id = payload.get("assigned_agent_id")
        if assigned_agent_id:
            tasks = [
                task for task in tasks
                if task.get("assigned_agent_id") == assigned_agent_id
            ]

        limit = int(payload.get("limit", 50))
        tasks = tasks[-limit:]

        return {
            "success": True,
            "total": len(tasks),
            "tasks": tasks,
        }

    def _get(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        task_id = self._require_task_id(payload)
        store = self._read_store()
        task, _index = self._find_task(store, task_id)

        return {
            "success": True,
            "task": task,
        }

    def _update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        task_id = self._require_task_id(payload)
        store = self._read_store()
        task, index = self._find_task(store, task_id)

        allowed_fields = [
            "title",
            "description",
            "status",
            "priority",
            "tags",
            "assigned_agent_id",
            "payload",
        ]

        for field in allowed_fields:
            if field not in payload:
                continue

            if field == "status":
                value = str(payload[field]).strip().lower()
                if value not in self.VALID_STATUS:
                    raise ValueError("Status invalido.")
                task[field] = value
                if value == "done":
                    task["completed_at"] = now_iso()

            elif field == "priority":
                value = str(payload[field]).strip().lower()
                if value not in self.VALID_PRIORITY:
                    raise ValueError("Prioridade invalida.")
                task[field] = value

            elif field == "tags":
                task[field] = self._as_list(payload[field])

            else:
                task[field] = payload[field]

        task["updated_at"] = now_iso()
        store["tasks"][index] = task
        self._write_store(store)

        return {
            "success": True,
            "message": "Tarefa atualizada.",
            "task": task,
        }

    def _set_status(self, payload: Dict[str, Any], status: str) -> Dict[str, Any]:
        data = dict(payload)
        data["status"] = status
        return self._update(data)

    def _delete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        task_id = self._require_task_id(payload)
        store = self._read_store()
        task, index = self._find_task(store, task_id)

        del store["tasks"][index]
        self._write_store(store)

        return {
            "success": True,
            "message": "Tarefa removida.",
            "task": task,
        }

    def _stats(self) -> Dict[str, Any]:
        store = self._read_store()
        tasks = list(store.get("tasks", []))

        by_status: Dict[str, int] = {}
        by_priority: Dict[str, int] = {}

        for task in tasks:
            by_status[task.get("status", "unknown")] = by_status.get(task.get("status", "unknown"), 0) + 1
            by_priority[task.get("priority", "unknown")] = by_priority.get(task.get("priority", "unknown"), 0) + 1

        return {
            "success": True,
            "total": len(tasks),
            "by_status": by_status,
            "by_priority": by_priority,
            "storage_path": str(self.storage_path),
        }

    def _read_store(self) -> Dict[str, Any]:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.storage_path.exists():
            return {
                "version": "0.1.0",
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "tasks": [],
            }

        with self.storage_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if "tasks" not in data or not isinstance(data["tasks"], list):
            data["tasks"] = []

        return data

    def _write_store(self, store: Dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        store["updated_at"] = now_iso()

        temp_path = self.storage_path.with_suffix(self.storage_path.suffix + ".tmp")
        temp_path.write_text(
            json.dumps(store, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(self.storage_path)

    def _require_task_id(self, payload: Dict[str, Any]) -> str:
        task_id = str(payload.get("task_id", "")).strip()
        if not task_id:
            raise ValueError("Campo obrigatorio ausente: task_id")
        return task_id

    def _find_task(self, store: Dict[str, Any], task_id: str) -> Tuple[Dict[str, Any], int]:
        for index, task in enumerate(store.get("tasks", [])):
            if task.get("task_id") == task_id:
                return task, index

        raise KeyError("Tarefa nao encontrada: " + task_id)

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [value]
