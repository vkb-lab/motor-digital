# -*- coding: utf-8 -*-
"""
K-Atlas OS - Router

Camada de roteamento entre comandos e agentes.
"""

from __future__ import annotations

import fnmatch
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agents.base_agent import AgentContext, AgentResult
from core.events import EventBus, EventLevel, EventStatus
from core.permissions import PermissionManager
from core.registry import AgentRegistry, AgentSpec


@dataclass
class Route:
    """
    Rota explícita para comandos.

    Exemplos:
    - command_pattern="campaign.*", agent_id="campaign_agent"
    - command_pattern="memory.write", agent_id="memory_agent"
    """

    agent_id: str
    command_pattern: str
    action: Optional[str] = None
    capability: Optional[str] = None
    priority: int = 100
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    route_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def matches(self, command: str) -> bool:
        return self.enabled and fnmatch.fnmatchcase(command, self.command_pattern)


class Router:
    """
    Roteador operacional do K-Atlas OS.

    Estratégia de resolução:
    1. payload["target_agent"], se informado
    2. comando no formato "agent_id.action"
    3. rota explícita por pattern
    4. capability informada no payload
    5. capability igual ao primeiro segmento do comando
    """

    def __init__(
        self,
        registry: AgentRegistry,
        event_bus: Optional[EventBus] = None,
        permission_manager: Optional[PermissionManager] = None,
    ) -> None:
        self.registry = registry
        self.event_bus = event_bus
        self.permission_manager = permission_manager
        self._routes: List[Route] = []

    def add_route(self, route: Route) -> Route:
        """Adiciona rota explícita."""
        if not self.registry.has_agent(route.agent_id):
            raise KeyError(f"Agente da rota não registrado: {route.agent_id}")

        self._routes.append(route)
        self._routes.sort(key=lambda item: item.priority)

        self._emit(
            event_type="router.route_added",
            action="add_route",
            payload={
                "route_id": route.route_id,
                "agent_id": route.agent_id,
                "command_pattern": route.command_pattern,
                "priority": route.priority,
            },
            status=EventStatus.SUCCESS,
        )
        return route

    def remove_route(self, route_id: str) -> None:
        """Remove rota por ID."""
        before = len(self._routes)
        self._routes = [route for route in self._routes if route.route_id != route_id]

        self._emit(
            event_type="router.route_removed",
            action="remove_route",
            payload={"route_id": route_id, "removed": before != len(self._routes)},
            status=EventStatus.SUCCESS,
        )

    def list_routes(self) -> List[Dict[str, Any]]:
        """Lista rotas serializáveis."""
        return [
            {
                "route_id": route.route_id,
                "agent_id": route.agent_id,
                "command_pattern": route.command_pattern,
                "action": route.action,
                "capability": route.capability,
                "priority": route.priority,
                "enabled": route.enabled,
                "metadata": route.metadata,
            }
            for route in self._routes
        ]

    def resolve(self, command: str, payload: Optional[Dict[str, Any]] = None) -> AgentSpec:
        """Resolve qual agente deve receber o comando."""
        payload = payload or {}

        target_agent = payload.get("target_agent")
        if target_agent:
            spec = self.registry.get_spec(str(target_agent))
            self._ensure_enabled(spec)
            return spec

        if "." in command:
            possible_agent_id, _action = command.split(".", 1)
            if self.registry.has_agent(possible_agent_id):
                spec = self.registry.get_spec(possible_agent_id)
                self._ensure_enabled(spec)
                return spec

        for route in self._routes:
            if route.matches(command):
                spec = self.registry.get_spec(route.agent_id)
                self._ensure_enabled(spec)
                return spec

        capability = payload.get("capability")
        if not capability and "." in command:
            capability = command.split(".", 1)[0]

        if capability:
            matches = self.registry.find_by_capability(str(capability), enabled_only=True)
            if matches:
                return matches[0]

        raise LookupError(f"Nenhum agente encontrado para o comando: {command}")

    def dispatch(
        self,
        command: str,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[AgentContext] = None,
    ) -> AgentResult:
        """Roteia e executa comando em um agente."""
        payload = payload or {}

        if self.permission_manager is not None:
            actor = "kernel"
            if context is not None:
                actor = context.user_id or "kernel"
            self.permission_manager.require(actor, "router.dispatch")

        spec = self.resolve(command, payload)
        agent = self.registry.get_instance(spec.agent_id)

        action = self._extract_action(command, spec.agent_id)
        effective_context = context or AgentContext(command=action, payload=payload)
        effective_context.command = action
        effective_context.payload = payload

        self._emit(
            event_type="router.dispatch_started",
            action="dispatch",
            target=spec.agent_id,
            payload={
                "command": command,
                "action": action,
                "agent_id": spec.agent_id,
                "trace_id": effective_context.trace_id,
            },
            status=EventStatus.PENDING,
        )

        result = agent.execute(action, payload=payload, context=effective_context)

        self._emit(
            event_type="router.dispatch_finished",
            action="dispatch",
            target=spec.agent_id,
            payload=result.to_dict(),
            status=EventStatus.SUCCESS if result.success else EventStatus.FAILED,
            level=EventLevel.INFO if result.success else EventLevel.ERROR,
        )
        return result

    @staticmethod
    def _extract_action(command: str, agent_id: str) -> str:
        prefix = f"{agent_id}."
        if command.startswith(prefix):
            return command[len(prefix) :]
        return command

    @staticmethod
    def _ensure_enabled(spec: AgentSpec) -> None:
        if not spec.enabled:
            raise RuntimeError(f"Agente desativado: {spec.agent_id}")

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
            source="router",
            target=target,
            action=action,
            payload=payload or {},
            status=status,
            level=level,
        )
