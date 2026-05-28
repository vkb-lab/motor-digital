# -*- coding: utf-8 -*-
"""
K-Atlas OS - Agent Registry

Registro central de agentes.
Mantém metadados, instâncias em memória e base para persistência futura.
"""

from __future__ import annotations

import importlib
import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.events import EventBus, EventLevel, EventStatus


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentSpec:
    """
    Descrição operacional de um agente.

    A spec pode existir mesmo sem instância carregada.
    Isso permite futura execução via worker, API ou cloud.
    """

    agent_id: str
    name: str
    description: str = ""
    version: str = "0.1.0"
    module: Optional[str] = None
    class_name: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        self.agent_id = self.agent_id.strip()
        if not self.agent_id:
            raise ValueError("agent_id não pode ser vazio.")

        self.capabilities = sorted(set(self.capabilities))
        self.permissions = sorted(set(self.permissions))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "module": self.module,
            "class_name": self.class_name,
            "capabilities": self.capabilities,
            "permissions": self.permissions,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "registered_at": self.registered_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentSpec":
        return cls(
            agent_id=data["agent_id"],
            name=data.get("name", data["agent_id"]),
            description=data.get("description", ""),
            version=data.get("version", "0.1.0"),
            module=data.get("module"),
            class_name=data.get("class_name"),
            capabilities=list(data.get("capabilities", [])),
            permissions=list(data.get("permissions", [])),
            enabled=bool(data.get("enabled", True)),
            metadata=dict(data.get("metadata", {})),
            registered_at=data.get("registered_at", utc_now_iso()),
        )


class AgentRegistry:
    """
    Registro operacional dos agentes.

    Responsabilidades:
    - registrar specs
    - associar instâncias locais
    - buscar por capacidade
    - persistir e carregar registry.json
    - carregar agente por module/class_name quando necessário
    """

    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        self.event_bus = event_bus
        self._specs: Dict[str, AgentSpec] = {}
        self._instances: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def register(
        self,
        spec: AgentSpec,
        instance: Optional[Any] = None,
        replace: bool = False,
    ) -> AgentSpec:
        """Registra um agente."""
        with self._lock:
            exists = spec.agent_id in self._specs
            if exists and not replace:
                raise ValueError(f"Agente já registrado: {spec.agent_id}")

            self._specs[spec.agent_id] = spec

            if instance is not None:
                self._instances[spec.agent_id] = instance

        self._emit(
            event_type="registry.agent_registered",
            action="register",
            target=spec.agent_id,
            payload={"agent": spec.to_dict(), "replace": replace},
            status=EventStatus.SUCCESS,
        )
        return spec

    def unregister(self, agent_id: str) -> None:
        """Remove um agente do registro."""
        with self._lock:
            if agent_id not in self._specs:
                raise KeyError(f"Agente não encontrado: {agent_id}")

            self._specs.pop(agent_id, None)
            self._instances.pop(agent_id, None)

        self._emit(
            event_type="registry.agent_unregistered",
            action="unregister",
            target=agent_id,
            payload={"agent_id": agent_id},
            status=EventStatus.SUCCESS,
        )

    def get_spec(self, agent_id: str) -> AgentSpec:
        """Retorna spec do agente."""
        with self._lock:
            if agent_id not in self._specs:
                raise KeyError(f"Agente não registrado: {agent_id}")
            return self._specs[agent_id]

    def get_instance(self, agent_id: str) -> Any:
        """
        Retorna instância local do agente.
        Se não estiver carregada, tenta carregar por module/class_name.
        """
        with self._lock:
            if agent_id in self._instances:
                return self._instances[agent_id]

            if agent_id not in self._specs:
                raise KeyError(f"Agente não registrado: {agent_id}")

            spec = self._specs[agent_id]

        instance = self._load_instance_from_spec(spec)

        with self._lock:
            self._instances[agent_id] = instance

        self._emit(
            event_type="registry.agent_loaded",
            action="load_instance",
            target=agent_id,
            payload={"agent_id": agent_id},
            status=EventStatus.SUCCESS,
        )
        return instance

    def attach_instance(self, agent_id: str, instance: Any) -> None:
        """Anexa uma instância local a uma spec já registrada."""
        with self._lock:
            if agent_id not in self._specs:
                raise KeyError(f"Agente não registrado: {agent_id}")
            self._instances[agent_id] = instance

    def list_agents(self, enabled_only: bool = False) -> List[AgentSpec]:
        """Lista specs registradas."""
        with self._lock:
            specs = list(self._specs.values())

        if enabled_only:
            specs = [spec for spec in specs if spec.enabled]

        return sorted(specs, key=lambda item: item.agent_id)

    def has_agent(self, agent_id: str) -> bool:
        with self._lock:
            return agent_id in self._specs

    def set_enabled(self, agent_id: str, enabled: bool) -> None:
        """Ativa ou desativa agente."""
        with self._lock:
            if agent_id not in self._specs:
                raise KeyError(f"Agente não registrado: {agent_id}")
            self._specs[agent_id].enabled = enabled

        self._emit(
            event_type="registry.agent_status_changed",
            action="set_enabled",
            target=agent_id,
            payload={"agent_id": agent_id, "enabled": enabled},
            status=EventStatus.SUCCESS,
        )

    def find_by_capability(self, capability: str, enabled_only: bool = True) -> List[AgentSpec]:
        """Busca agentes por capacidade declarada."""
        with self._lock:
            specs = list(self._specs.values())

        result = [
            spec for spec in specs
            if capability in spec.capabilities and (spec.enabled or not enabled_only)
        ]
        return sorted(result, key=lambda item: item.agent_id)

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "registry_id": str(uuid.uuid4()),
                "exported_at": utc_now_iso(),
                "agents": [spec.to_dict() for spec in self.list_agents(enabled_only=False)],
            }

    def save_json(self, path: str | Path) -> None:
        """Persiste registro em JSON."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=2, sort_keys=True)

        self._emit(
            event_type="registry.saved",
            action="save_json",
            payload={"path": str(file_path)},
            status=EventStatus.SUCCESS,
        )

    def load_json(self, path: str | Path, replace: bool = True) -> None:
        """Carrega registro a partir de JSON."""
        file_path = Path(path)
        if not file_path.exists():
            return

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        specs = [AgentSpec.from_dict(item) for item in data.get("agents", [])]

        with self._lock:
            if replace:
                self._specs.clear()
                self._instances.clear()

            for spec in specs:
                self._specs[spec.agent_id] = spec

        self._emit(
            event_type="registry.loaded",
            action="load_json",
            payload={"path": str(file_path), "count": len(specs), "replace": replace},
            status=EventStatus.SUCCESS,
        )

    def _load_instance_from_spec(self, spec: AgentSpec) -> Any:
        if not spec.module or not spec.class_name:
            raise RuntimeError(
                f"Agente '{spec.agent_id}' não possui module/class_name para carregamento."
            )

        module = importlib.import_module(spec.module)
        agent_class = getattr(module, spec.class_name)
        return agent_class()

    def _emit(
        self,
        event_type: str,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        target: Optional[str] = None,
        status: EventStatus = EventStatus.PENDING,
        level: EventLevel = EventLevel.INFO,
    ) -> None:
        if self.event_bus is None:
            return

        self.event_bus.emit(
            event_type=event_type,
            source="registry",
            target=target,
            action=action,
            payload=payload or {},
            status=status,
            level=level,
        )
