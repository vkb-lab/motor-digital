# -*- coding: utf-8 -*-
"""
K-Atlas OS - System Agent

Agente operacional do sistema.
Responsável por expor status, diagnóstico básico e informações do kernel.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import AgentContext, BaseAgent


class SystemAgent(BaseAgent):
    agent_id = "system_agent"
    name = "System Agent"
    description = "Agente de controle operacional do K-Atlas OS."
    version = "0.1.0"
    capabilities = [
        "system",
        "kernel",
        "status",
        "agents",
        "events",
        "permissions",
        "diagnostics",
    ]
    permissions = [
        "agent.execute",
        "kernel.status",
        "registry.read",
        "events.read",
    ]

    def __init__(
        self,
        kernel: Optional[Any] = None,
        event_bus: Optional[Any] = None,
        permission_manager: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            permission_manager=permission_manager,
            config=config,
        )
        self.kernel = kernel

    def metadata(self) -> Dict[str, Any]:
        return {
            "base_class": "BaseAgent",
            "type": "system",
            "created_for": "K-Atlas OS",
            "module_role": "kernel_operations",
        }

    def run(self, context: AgentContext) -> Dict[str, Any]:
        action = self._extract_action(context.command)

        if action in ["ping", "health"]:
            return self._ping()

        if action in ["help", "commands"]:
            return self._help()

        if action in ["status", "kernel_status"]:
            return self._status()

        if action in ["agents", "list_agents"]:
            return self._agents()

        if action in ["events", "recent_events"]:
            limit = int(context.payload.get("limit", 20))
            return self._events(limit=limit)

        if action in ["permissions", "agent_permissions"]:
            agent_id = str(context.payload.get("agent_id", "system_agent"))
            return self._permissions(agent_id=agent_id)

        return {
            "success": False,
            "message": "Comando nao reconhecido pelo SystemAgent.",
            "command": context.command,
            "action": action,
            "available_actions": [
                "ping",
                "help",
                "status",
                "agents",
                "events",
                "permissions",
            ],
        }

    def _extract_action(self, command: str) -> str:
        clean_command = str(command).strip()

        if "." in clean_command:
            return clean_command.split(".", 1)[1].strip().lower()

        return clean_command.lower()

    def _require_kernel(self) -> None:
        if self.kernel is None:
            raise RuntimeError("SystemAgent precisa receber uma instancia do kernel.")

    def _ping(self) -> Dict[str, Any]:
        return {
            "success": True,
            "agent_id": self.agent_id,
            "message": "SystemAgent operacional.",
        }

    def _help(self) -> Dict[str, Any]:
        return {
            "success": True,
            "agent_id": self.agent_id,
            "commands": {
                "system_agent.ping": "Verifica se o agente esta ativo.",
                "system_agent.status": "Retorna status do kernel.",
                "system_agent.agents": "Lista agentes registrados.",
                "system_agent.events": "Lista eventos recentes.",
                "system_agent.permissions": "Lista permissoes de um agente.",
                "system_agent.help": "Mostra comandos disponiveis.",
            },
            "examples": [
                {
                    "command": "system_agent.status",
                    "payload": {},
                },
                {
                    "command": "system_agent.events",
                    "payload": {
                        "limit": 10
                    },
                },
                {
                    "command": "system_agent.permissions",
                    "payload": {
                        "agent_id": "system_agent"
                    },
                },
            ],
        }

    def _status(self) -> Dict[str, Any]:
        self._require_kernel()
        return {
            "success": True,
            "kernel": self.kernel.status(),
        }

    def _agents(self) -> Dict[str, Any]:
        self._require_kernel()
        return {
            "success": True,
            "agents": self.kernel.list_agents(),
        }

    def _events(self, limit: int = 20) -> Dict[str, Any]:
        self._require_kernel()
        return {
            "success": True,
            "limit": limit,
            "events": self.kernel.recent_events(limit=limit),
        }

    def _permissions(self, agent_id: str) -> Dict[str, Any]:
        self._require_kernel()
        return {
            "success": True,
            "agent_id": agent_id,
            "roles": self.kernel.permissions.roles_for(agent_id),
            "permissions": self.kernel.permissions.permissions_for(agent_id),
        }
