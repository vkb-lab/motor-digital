# -*- coding: utf-8 -*-
"""
K-Atlas OS - Kernel

Núcleo inicial do sistema operacional multiagente K-Atlas.
"""

from __future__ import annotations

import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.base_agent import AgentContext, AgentResult, BaseAgent
from core.events import EventBus, EventLevel, EventStatus
from core.permissions import PermissionManager
from core.registry import AgentRegistry
from core.router import Route, Router


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class KernelConfig:
    """
    Configuração básica do kernel.

    Mantida simples para facilitar evolução futura:
    - arquivo de registry
    - logs
    - ambiente
    - metadados operacionais
    """

    app_name: str = "K-Atlas OS"
    environment: str = "local"
    root_path: Path = field(default_factory=lambda: Path.cwd())
    registry_file: Path = field(default_factory=lambda: Path("memory/registry.json"))
    permissions_file: Path = field(default_factory=lambda: Path("memory/permissions.json"))
    kernel_log_dir: Path = field(default_factory=lambda: Path("logs/kernel"))
    event_log_dir: Path = field(default_factory=lambda: Path("logs/events"))

    def resolve_paths(self) -> "KernelConfig":
        """Resolve paths relativos a partir do root_path."""
        self.root_path = Path(self.root_path)

        for attr in ["registry_file", "permissions_file", "kernel_log_dir", "event_log_dir"]:
            value = Path(getattr(self, attr))
            if not value.is_absolute():
                setattr(self, attr, self.root_path / value)

        return self


class KAtlasKernel:
    """
    Kernel operacional do K-Atlas OS.

    Responsabilidades:
    - inicializar serviços centrais
    - registrar agentes
    - aplicar permissões
    - rotear comandos
    - gerar eventos auditáveis
    - persistir registry e permissões
    """

    def __init__(self, config: Optional[KernelConfig] = None) -> None:
        self.config = (config or KernelConfig()).resolve_paths()
        self.kernel_id = str(uuid.uuid4())
        self.started_at: Optional[str] = None
        self.running = False

        self.logger = self._setup_logger()
        self.events = EventBus(log_dir=self.config.event_log_dir, log_to_file=True)
        self.permissions = PermissionManager()
        self.registry = AgentRegistry(event_bus=self.events)
        self.router = Router(
            registry=self.registry,
            event_bus=self.events,
            permission_manager=self.permissions,
        )

    def start(self, load_state: bool = True) -> None:
        """Inicializa o kernel."""
        if self.running:
            return

        self.config.root_path.mkdir(parents=True, exist_ok=True)
        self.config.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.permissions_file.parent.mkdir(parents=True, exist_ok=True)

        if load_state:
            self.registry.load_json(self.config.registry_file)
            self.permissions.load_json(self.config.permissions_file)

        self.started_at = utc_now_iso()
        self.running = True

        self.logger.info("Kernel iniciado: %s", self.kernel_id)
        self.events.emit(
            event_type="kernel.started",
            source="kernel",
            action="start",
            payload=self.status(),
            status=EventStatus.SUCCESS,
            level=EventLevel.INFO,
        )

    def stop(self, save_state: bool = True) -> None:
        """Encerra o kernel com persistência opcional."""
        if not self.running:
            return

        if save_state:
            self.save_state()

        self.running = False

        self.logger.info("Kernel encerrado: %s", self.kernel_id)
        self.events.emit(
            event_type="kernel.stopped",
            source="kernel",
            action="stop",
            payload={"kernel_id": self.kernel_id},
            status=EventStatus.SUCCESS,
            level=EventLevel.INFO,
        )

    def save_state(self) -> None:
        """Persiste registry e permissões."""
        self.registry.save_json(self.config.registry_file)
        self.permissions.save_json(self.config.permissions_file)

        self.events.emit(
            event_type="kernel.state_saved",
            source="kernel",
            action="save_state",
            payload={
                "registry_file": str(self.config.registry_file),
                "permissions_file": str(self.config.permissions_file),
            },
            status=EventStatus.SUCCESS,
            level=EventLevel.INFO,
        )

    def register_agent(
        self,
        agent: BaseAgent,
        replace: bool = False,
        roles: Optional[List[str]] = None,
    ) -> None:
        """Registra uma instância de agente no kernel."""
        self._ensure_running_or_bootstrap_allowed()

        agent.event_bus = self.events
        agent.permission_manager = self.permissions
        agent.setup()

        spec = agent.spec()
        self.registry.register(spec, instance=agent, replace=replace)

        effective_roles = roles or ["agent"]
        for role in effective_roles:
            self.permissions.assign_role(spec.agent_id, role)

        self.permissions.grant_many(spec.agent_id, spec.permissions)

        self.events.emit(
            event_type="kernel.agent_registered",
            source="kernel",
            target=spec.agent_id,
            action="register_agent",
            payload={
                "agent": spec.to_dict(),
                "roles": effective_roles,
                "permissions": self.permissions.permissions_for(spec.agent_id),
            },
            status=EventStatus.SUCCESS,
            level=EventLevel.INFO,
        )

    def add_route(
        self,
        command_pattern: str,
        agent_id: str,
        action: Optional[str] = None,
        capability: Optional[str] = None,
        priority: int = 100,
    ) -> Route:
        """Cria rota explícita."""
        route = Route(
            command_pattern=command_pattern,
            agent_id=agent_id,
            action=action,
            capability=capability,
            priority=priority,
        )
        return self.router.add_route(route)

    def execute(
        self,
        command: str,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[AgentContext] = None,
    ) -> AgentResult:
        """Executa comando via router."""
        if not self.running:
            raise RuntimeError("Kernel não está iniciado. Execute kernel.start().")

        if not command or not str(command).strip():
            raise ValueError("command não pode ser vazio.")

        payload = payload or {}
        trace_id = None if context is None else context.trace_id

        start_event = self.events.emit(
            event_type="kernel.command_received",
            source="kernel",
            action="execute",
            payload={"command": command, "payload": payload},
            status=EventStatus.PENDING,
            level=EventLevel.INFO,
            trace_id=trace_id,
        )

        effective_context = context or AgentContext(
            command=command,
            payload=payload,
            trace_id=start_event.trace_id,
            user_id="kernel",
            metadata={"source": "kernel.execute"},
        )

        result = self.router.dispatch(command, payload=payload, context=effective_context)

        self.events.emit(
            event_type="kernel.command_finished",
            source="kernel",
            action="execute",
            payload=result.to_dict(),
            status=EventStatus.SUCCESS if result.success else EventStatus.FAILED,
            level=EventLevel.INFO if result.success else EventLevel.ERROR,
            trace_id=effective_context.trace_id,
        )
        return result

    def status(self) -> Dict[str, Any]:
        """Retorna status operacional do kernel."""
        agents = self.registry.list_agents(enabled_only=False)

        return {
            "kernel_id": self.kernel_id,
            "app_name": self.config.app_name,
            "environment": self.config.environment,
            "running": self.running,
            "started_at": self.started_at,
            "root_path": str(self.config.root_path),
            "registry_file": str(self.config.registry_file),
            "permissions_file": str(self.config.permissions_file),
            "agents_total": len(agents),
            "agents_enabled": len([agent for agent in agents if agent.enabled]),
            "routes_total": len(self.router.list_routes()),
        }

    def list_agents(self) -> List[Dict[str, Any]]:
        """Lista agentes registrados em formato serializável."""
        return [agent.to_dict() for agent in self.registry.list_agents(enabled_only=False)]

    def recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna eventos recentes."""
        return [event.to_dict() for event in self.events.history(limit=limit)]

    def _ensure_running_or_bootstrap_allowed(self) -> None:
        """
        Permite registrar agentes antes ou depois de start().
        Isso reduz fricção na fase local.
        """
        return

    def _setup_logger(self) -> logging.Logger:
        """Configura logger UTF-8 compatível com Windows."""
        self.config.kernel_log_dir.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger("k_atlas.kernel")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if logger.handlers:
            return logger

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler = logging.FileHandler(
            self.config.kernel_log_dir / "kernel.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger


def create_kernel(root_path: Optional[str | Path] = None) -> KAtlasKernel:
    """Factory simples para uso por cockpit, API ou scripts."""
    config = KernelConfig()
    if root_path is not None:
        config.root_path = Path(root_path)
    return KAtlasKernel(config=config)


if __name__ == "__main__":
    kernel = create_kernel()
    kernel.start(load_state=True)
    print(kernel.status())
    kernel.stop(save_state=True)
