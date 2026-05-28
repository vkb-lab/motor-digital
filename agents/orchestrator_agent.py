# -*- coding: utf-8 -*-
"""
K-Atlas OS - Orchestrator Agent

Agente coordenador inicial do K-Atlas OS.
Responsavel por transformar objetivos em tarefas e memorias operacionais.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.base_agent import AgentContext, BaseAgent


class OrchestratorAgent(BaseAgent):
    agent_id = "orchestrator_agent"
    name = "Orchestrator Agent"
    description = "Agente coordenador multiagente inicial do K-Atlas OS."
    version = "0.1.0"
    capabilities = [
        "orchestration",
        "planning",
        "coordination",
        "multiagent",
        "tasks",
        "memory",
    ]
    permissions = [
        "agent.execute",
        "kernel.status",
        "registry.read",
        "events.read",
        "task.read",
        "task.write",
        "memory.read",
        "memory.write",
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
            "type": "orchestrator",
            "created_for": "K-Atlas OS",
            "module_role": "multiagent_coordination",
        }

    def required_permission(self, context: AgentContext) -> str:
        return "agent.execute"

    def run(self, context: AgentContext) -> Dict[str, Any]:
        action = self._action(context.command)

        if action == "ping":
            return self._ping()

        if action in ["help", "commands"]:
            return self._help()

        if action in ["status", "overview"]:
            return self._status()

        if action in ["plan", "goal"]:
            return self._plan(context.payload)

        if action == "handoff":
            return self._handoff(context.payload)

        if action == "daily_start":
            return self._daily_start(context.payload)

        return {
            "success": False,
            "message": "Comando nao reconhecido pelo OrchestratorAgent.",
            "action": action,
            "available_actions": [
                "ping",
                "help",
                "status",
                "plan",
                "handoff",
                "daily_start",
            ],
        }

    def _action(self, command: str) -> str:
        clean = str(command).strip().lower()
        if "." in clean:
            return clean.split(".", 1)[1]
        return clean

    def _require_kernel(self) -> None:
        if self.kernel is None:
            raise RuntimeError("OrchestratorAgent precisa receber uma instancia do kernel.")

    def _ping(self) -> Dict[str, Any]:
        return {
            "success": True,
            "agent_id": self.agent_id,
            "message": "OrchestratorAgent operacional.",
        }

    def _help(self) -> Dict[str, Any]:
        return {
            "success": True,
            "commands": {
                "orchestrator_agent.ping": "Verifica se o orquestrador esta ativo.",
                "orchestrator_agent.status": "Mostra visao geral do sistema.",
                "orchestrator_agent.plan": "Transforma objetivo em tarefa e memoria.",
                "orchestrator_agent.handoff": "Cria tarefa para outro agente.",
                "orchestrator_agent.daily_start": "Cria memoria de inicio de operacao diaria.",
            },
            "example_plan": {
                "goal": "Criar campanha da semana",
                "priority": "high",
                "tags": ["campaign", "weekly"],
            },
        }

    def _status(self) -> Dict[str, Any]:
        self._require_kernel()

        kernel_status = self.kernel.execute("system_agent.status").to_dict()
        agents = self.kernel.execute("system_agent.agents").to_dict()
        task_stats = self.kernel.execute("task_agent.stats").to_dict()
        memory_stats = self.kernel.execute("memory_agent.stats").to_dict()

        return {
            "success": True,
            "message": "Visao geral do K-Atlas OS.",
            "kernel_status": kernel_status.get("output"),
            "agents": agents.get("output"),
            "task_stats": task_stats.get("output"),
            "memory_stats": memory_stats.get("output"),
        }

    def _plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._require_kernel()

        goal = str(payload.get("goal", "")).strip()
        if not goal:
            raise ValueError("Campo obrigatorio ausente: goal")

        priority = str(payload.get("priority", "normal")).strip().lower()
        tags = self._as_list(payload.get("tags", []))
        assigned_agent_id = payload.get("assigned_agent_id", "task_agent")

        memory_result = self.kernel.execute(
            "memory_agent.remember",
            payload={
                "title": "Plano operacional criado",
                "content": goal,
                "type": "decision",
                "tags": ["orchestrator", "plan"] + tags,
                "source": "orchestrator_agent",
                "visibility": "internal",
                "importance": int(payload.get("importance", 2)),
            },
        ).to_dict()

        task_result = self.kernel.execute(
            "task_agent.create",
            payload={
                "title": goal,
                "description": str(payload.get("description", "Tarefa criada pelo OrchestratorAgent.")),
                "priority": priority,
                "tags": ["orchestrator"] + tags,
                "assigned_agent_id": assigned_agent_id,
                "payload": {
                    "origin": "orchestrator_agent",
                    "goal": goal,
                },
            },
        ).to_dict()

        return {
            "success": bool(memory_result.get("success")) and bool(task_result.get("success")),
            "message": "Objetivo convertido em memoria e tarefa.",
            "goal": goal,
            "memory_result": memory_result,
            "task_result": task_result,
        }

    def _handoff(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._require_kernel()

        target_agent_id = str(payload.get("target_agent_id", "")).strip()
        title = str(payload.get("title", "")).strip()

        if not target_agent_id:
            raise ValueError("Campo obrigatorio ausente: target_agent_id")

        if not title:
            raise ValueError("Campo obrigatorio ausente: title")

        result = self.kernel.execute(
            "task_agent.create",
            payload={
                "title": title,
                "description": str(payload.get("description", "")),
                "priority": str(payload.get("priority", "normal")),
                "tags": ["handoff", target_agent_id] + self._as_list(payload.get("tags", [])),
                "assigned_agent_id": target_agent_id,
                "payload": {
                    "origin": "orchestrator_agent",
                    "target_agent_id": target_agent_id,
                    "handoff_payload": payload.get("payload", {}),
                },
            },
        ).to_dict()

        return {
            "success": bool(result.get("success")),
            "message": "Handoff criado.",
            "target_agent_id": target_agent_id,
            "task_result": result,
        }

    def _daily_start(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._require_kernel()

        focus = str(payload.get("focus", "Operacao diaria do K-Atlas OS")).strip()
        tags = self._as_list(payload.get("tags", ["daily", "operations"]))

        memory_result = self.kernel.execute(
            "memory_agent.remember",
            payload={
                "title": "Inicio de operacao diaria",
                "content": focus,
                "type": "context",
                "tags": ["daily_start", "orchestrator"] + tags,
                "source": "orchestrator_agent",
                "visibility": "internal",
                "importance": int(payload.get("importance", 1)),
            },
        ).to_dict()

        task_result = self.kernel.execute(
            "task_agent.create",
            payload={
                "title": "Revisar prioridades do dia",
                "description": focus,
                "priority": str(payload.get("priority", "normal")),
                "tags": ["daily_start", "operations"],
                "assigned_agent_id": "orchestrator_agent",
            },
        ).to_dict()

        return {
            "success": bool(memory_result.get("success")) and bool(task_result.get("success")),
            "message": "Operacao diaria iniciada.",
            "memory_result": memory_result,
            "task_result": task_result,
        }

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [value]
