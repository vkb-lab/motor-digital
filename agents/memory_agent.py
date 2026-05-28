# -*- coding: utf-8 -*-
"""
K-Atlas OS - Memory Agent

Agente de memoria operacional persistente.
Responsavel por registrar, listar, buscar e classificar memorias simples em JSON.
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


class MemoryAgent(BaseAgent):
    agent_id = "memory_agent"
    name = "Memory Agent"
    description = "Agente de memoria operacional do K-Atlas OS."
    version = "0.1.0"
    capabilities = [
        "memory",
        "context",
        "notes",
        "knowledge",
        "persistence",
    ]
    permissions = [
        "agent.execute",
        "memory.read",
        "memory.write",
        "events.read",
    ]

    VALID_TYPES = [
        "note",
        "decision",
        "context",
        "task",
        "system",
        "campaign",
        "learning",
    ]

    VALID_VISIBILITY = [
        "private",
        "internal",
        "system",
    ]

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
        self.storage_path = Path(storage_path or configured_path or "memory/entries.json")

    def metadata(self) -> Dict[str, Any]:
        return {
            "base_class": "BaseAgent",
            "type": "memory",
            "created_for": "K-Atlas OS",
            "module_role": "persistent_operational_memory",
            "storage_path": str(self.storage_path),
        }

    def required_permission(self, context: AgentContext) -> str:
        action = self._action(context.command)

        if action in ["remember", "create", "update", "delete"]:
            return "memory.write"

        return "memory.read"

    def run(self, context: AgentContext) -> Dict[str, Any]:
        action = self._action(context.command)

        if action == "ping":
            return self._ping()

        if action in ["help", "commands"]:
            return self._help()

        if action in ["remember", "create"]:
            return self._create(context.payload)

        if action in ["list", "all"]:
            return self._list(context.payload)

        if action == "get":
            return self._get(context.payload)

        if action == "search":
            return self._search(context.payload)

        if action == "update":
            return self._update(context.payload)

        if action == "delete":
            return self._delete(context.payload)

        if action == "stats":
            return self._stats()

        return {
            "success": False,
            "message": "Comando nao reconhecido pelo MemoryAgent.",
            "action": action,
            "available_actions": [
                "ping",
                "help",
                "remember",
                "list",
                "get",
                "search",
                "update",
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
            "message": "MemoryAgent operacional.",
            "storage_path": str(self.storage_path),
        }

    def _help(self) -> Dict[str, Any]:
        return {
            "success": True,
            "commands": {
                "memory_agent.remember": "Registra uma memoria.",
                "memory_agent.list": "Lista memorias.",
                "memory_agent.get": "Busca memoria por memory_id.",
                "memory_agent.search": "Busca memorias por texto.",
                "memory_agent.update": "Atualiza memoria.",
                "memory_agent.delete": "Remove memoria.",
                "memory_agent.stats": "Mostra resumo da memoria.",
            },
            "example_remember": {
                "title": "Decisao de arquitetura",
                "content": "O K-Atlas usa kernel modular com agentes registrados.",
                "type": "decision",
                "tags": ["kernel", "arquitetura"],
                "source": "operator",
                "visibility": "internal",
            },
        }

    def _create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = str(payload.get("title", "")).strip()
        content = str(payload.get("content", "")).strip()

        if not title:
            raise ValueError("Campo obrigatorio ausente: title")

        if not content:
            raise ValueError("Campo obrigatorio ausente: content")

        memory_type = str(payload.get("type", "note")).strip().lower()
        if memory_type not in self.VALID_TYPES:
            memory_type = "note"

        visibility = str(payload.get("visibility", "internal")).strip().lower()
        if visibility not in self.VALID_VISIBILITY:
            visibility = "internal"

        entry = {
            "memory_id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "type": memory_type,
            "tags": self._as_list(payload.get("tags", [])),
            "source": str(payload.get("source", "operator")).strip(),
            "visibility": visibility,
            "importance": int(payload.get("importance", 1)),
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }

        store = self._read_store()
        store["entries"].append(entry)
        self._write_store(store)

        return {
            "success": True,
            "message": "Memoria registrada.",
            "memory": entry,
        }

    def _list(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        store = self._read_store()
        entries = list(store.get("entries", []))

        memory_type = payload.get("type")
        if memory_type:
            entries = [
                item for item in entries
                if item.get("type") == str(memory_type).lower()
            ]

        tag = payload.get("tag")
        if tag:
            entries = [
                item for item in entries
                if str(tag) in item.get("tags", [])
            ]

        limit = int(payload.get("limit", 50))
        entries = entries[-limit:]

        return {
            "success": True,
            "total": len(entries),
            "entries": entries,
        }

    def _get(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        memory_id = self._require_memory_id(payload)
        store = self._read_store()
        entry, _index = self._find_memory(store, memory_id)

        return {
            "success": True,
            "memory": entry,
        }

    def _search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = str(payload.get("query", "")).strip().lower()
        if not query:
            raise ValueError("Campo obrigatorio ausente: query")

        store = self._read_store()
        results = []

        for entry in store.get("entries", []):
            haystack = " ".join([
                str(entry.get("title", "")),
                str(entry.get("content", "")),
                " ".join([str(tag) for tag in entry.get("tags", [])]),
                str(entry.get("type", "")),
                str(entry.get("source", "")),
            ]).lower()

            if query in haystack:
                results.append(entry)

        limit = int(payload.get("limit", 50))

        return {
            "success": True,
            "query": query,
            "total": len(results[-limit:]),
            "entries": results[-limit:],
        }

    def _update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        memory_id = self._require_memory_id(payload)
        store = self._read_store()
        entry, index = self._find_memory(store, memory_id)

        allowed_fields = [
            "title",
            "content",
            "type",
            "tags",
            "source",
            "visibility",
            "importance",
        ]

        for field in allowed_fields:
            if field not in payload:
                continue

            if field == "type":
                value = str(payload[field]).strip().lower()
                if value not in self.VALID_TYPES:
                    raise ValueError("Tipo de memoria invalido.")
                entry[field] = value

            elif field == "visibility":
                value = str(payload[field]).strip().lower()
                if value not in self.VALID_VISIBILITY:
                    raise ValueError("Visibilidade invalida.")
                entry[field] = value

            elif field == "tags":
                entry[field] = self._as_list(payload[field])

            elif field == "importance":
                entry[field] = int(payload[field])

            else:
                entry[field] = payload[field]

        entry["updated_at"] = now_iso()
        store["entries"][index] = entry
        self._write_store(store)

        return {
            "success": True,
            "message": "Memoria atualizada.",
            "memory": entry,
        }

    def _delete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        memory_id = self._require_memory_id(payload)
        store = self._read_store()
        entry, index = self._find_memory(store, memory_id)

        del store["entries"][index]
        self._write_store(store)

        return {
            "success": True,
            "message": "Memoria removida.",
            "memory": entry,
        }

    def _stats(self) -> Dict[str, Any]:
        store = self._read_store()
        entries = list(store.get("entries", []))

        by_type: Dict[str, int] = {}
        by_visibility: Dict[str, int] = {}

        for entry in entries:
            entry_type = entry.get("type", "unknown")
            visibility = entry.get("visibility", "unknown")
            by_type[entry_type] = by_type.get(entry_type, 0) + 1
            by_visibility[visibility] = by_visibility.get(visibility, 0) + 1

        return {
            "success": True,
            "total": len(entries),
            "by_type": by_type,
            "by_visibility": by_visibility,
            "storage_path": str(self.storage_path),
        }

    def _read_store(self) -> Dict[str, Any]:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.storage_path.exists():
            return {
                "version": "0.1.0",
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "entries": [],
            }

        with self.storage_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if "entries" not in data or not isinstance(data["entries"], list):
            data["entries"] = []

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

    def _require_memory_id(self, payload: Dict[str, Any]) -> str:
        memory_id = str(payload.get("memory_id", "")).strip()
        if not memory_id:
            raise ValueError("Campo obrigatorio ausente: memory_id")
        return memory_id

    def _find_memory(self, store: Dict[str, Any], memory_id: str) -> Tuple[Dict[str, Any], int]:
        for index, entry in enumerate(store.get("entries", [])):
            if entry.get("memory_id") == memory_id:
                return entry, index

        raise KeyError("Memoria nao encontrada: " + memory_id)

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [value]
