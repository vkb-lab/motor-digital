# -*- coding: utf-8 -*-
"""
K-Atlas OS - Base Agent

Classe base para agentes do K-Atlas OS.
Todos os agentes futuros devem herdar desta classe.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, List, Optional

from core.events import EventBus, EventLevel, EventStatus
from core.permissions import PermissionManager
from core.registry import AgentSpec


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentContext:
    """
    Contexto de execução de um agente.

    Preparado para futuro:
    - tenant_id
    - user_id
    - trace_id
    - request_id
    - origem API/cockpit/worker
    """

    command: str
    payload: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    user_id: str = "kernel"
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Resultado padronizado de execução de agente."""

    success: bool
    agent_id: str
    action: str
    output: Any = None
    error: Optional[str] = None
    event_id: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "agent_id": self.agent_id,
            "action": self.action,
            "output": self.output,
            "error": self.error,
            "event_id": self.event_id,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


class BaseAgent:
    """
    Classe base de agente.

    Contrato:
    - declarar identidade e capacidades
    - executar comando via execute()
    - implementar run()
    - emitir eventos
    - retornar AgentResult
    """

    agent_id = "base_agent"
    name = "Base Agent"
    description = "Classe base dos agentes do K-Atlas OS."
    version = "0.1.0"
    capabilities: List[str] = []
    permissions: List[str] = ["agent.execute"]

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        permission_manager: Optional[PermissionManager] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.event_bus = event_bus
        self.permission_manager = permission_manager
        self.config = config or {}
        self.started_at: Optional[str] = None
        self.last_result: Optional[AgentResult] = None

    def spec(self) -> AgentSpec:
        """Retorna AgentSpec para registro no kernel."""
        return AgentSpec(
            agent_id=self.agent_id,
            name=self.name,
            description=self.description,
            version=self.version,
            module=self.__class__.__module__,
            class_name=self.__class__.__name__,
            capabilities=list(self.capabilities),
            permissions=list(self.permissions),
            enabled=True,
            metadata=self.metadata(),
        )

    def metadata(self) -> Dict[str, Any]:
        """Metadados livres do agente. Pode ser sobrescrito."""
        return {
            "base_class": "BaseAgent",
            "created_for": "K-Atlas OS",
        }

    def setup(self) -> None:
        """Hook opcional chamado antes do primeiro uso."""
        self.started_at = utc_now_iso()

    def healthcheck(self) -> Dict[str, Any]:
        """Status básico do agente."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "started_at": self.started_at,
            "capabilities": list(self.capabilities),
            "last_success": None if self.last_result is None else self.last_result.success,
        }

    def required_permission(self, context: AgentContext) -> str:
        """
        Define permissão necessária para execução.

        Agentes especializados podem sobrescrever para permissões específicas:
        - memory.write
        - campaign.create
        - api.call
        """
        return "agent.execute"

    def validate(self, context: AgentContext) -> None:
        """Validação de entrada. Sobrescreva quando necessário."""
        if not context.command:
            raise ValueError("context.command não pode ser vazio.")

    def execute(
        self,
        command: str,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[AgentContext] = None,
    ) -> AgentResult:
        """
        Executa um comando com padrão operacional único.
        Nunca chame run() diretamente pelo kernel; use execute().
        """
        effective_context = context or AgentContext(command=command, payload=payload or {})
        effective_context.command = command
        effective_context.payload = payload or effective_context.payload or {}

        start = perf_counter()
        started_event_id: Optional[str] = None

        try:
            self.validate(effective_context)

            if self.permission_manager is not None:
                self.permission_manager.require(
                    self.agent_id,
                    self.required_permission(effective_context),
                )

            started_event = self.emit_event(
                event_type="agent.execution_started",
                action=command,
                payload={
                    "payload": effective_context.payload,
                    "tenant_id": effective_context.tenant_id,
                    "user_id": effective_context.user_id,
                },
                status=EventStatus.PENDING,
                level=EventLevel.INFO,
                trace_id=effective_context.trace_id,
            )
            started_event_id = None if started_event is None else started_event.event_id

            output = self.run(effective_context)

            duration_ms = round((perf_counter() - start) * 1000, 3)
            result = AgentResult(
                success=True,
                agent_id=self.agent_id,
                action=command,
                output=output,
                event_id=started_event_id,
                duration_ms=duration_ms,
            )
            self.last_result = result

            self.emit_event(
                event_type="agent.execution_finished",
                action=command,
                payload=result.to_dict(),
                status=EventStatus.SUCCESS,
                level=EventLevel.INFO,
                trace_id=effective_context.trace_id,
            )
            return result

        except Exception as exc:
            duration_ms = round((perf_counter() - start) * 1000, 3)
            result = AgentResult(
                success=False,
                agent_id=self.agent_id,
                action=command,
                error=str(exc),
                event_id=started_event_id,
                duration_ms=duration_ms,
                metadata={"traceback": traceback.format_exc()},
            )
            self.last_result = result

            self.emit_event(
                event_type="agent.execution_failed",
                action=command,
                payload=result.to_dict(),
                status=EventStatus.FAILED,
                level=EventLevel.ERROR,
                trace_id=effective_context.trace_id,
            )
            return result

    def run(self, context: AgentContext) -> Any:
        """
        Implementação real do agente.

        Subclasses devem sobrescrever este método.
        """
        raise NotImplementedError("Subclasse precisa implementar run(context).")

    def emit_event(
        self,
        event_type: str,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        status: EventStatus = EventStatus.PENDING,
        level: EventLevel = EventLevel.INFO,
        trace_id: Optional[str] = None,
    ):
        """Emite evento se houver EventBus disponível."""
        if self.event_bus is None:
            return None

        return self.event_bus.emit(
            event_type=event_type,
            source=self.agent_id,
            action=action,
            payload=payload or {},
            status=status,
            level=level,
            trace_id=trace_id,
        )
