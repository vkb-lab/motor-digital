# -*- coding: utf-8 -*-
"""
K-Atlas OS - Learning Agent

Agente de aprendizado operacional contínuo.

Objetivo:
Transformar memória operacional, erros, boas práticas e padrões em conhecimento treinável
para agentes IA, robôs futuros e sistemas autônomos do ecossistema K-Atlas.

Camadas:
- Lessons: aprendizados operacionais
- Errors: erros, causas e correções
- Playbooks: procedimentos reutilizáveis
- Training: conhecimento estruturado para treinamento futuro

Compatível com:
- Python puro
- Windows
- PowerShell
- UTF-8
- Persistência JSON
- Kernel multiagente K-Atlas OS
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agents.base_agent import AgentContext, BaseAgent


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LearningAgent(BaseAgent):
    agent_id = "learning_agent"
    name = "Learning Agent"
    description = "Agente de aprendizado operacional e conhecimento treinavel do K-Atlas OS."
    version = "0.1.0"

    capabilities = [
        "learning",
        "lessons",
        "errors",
        "playbooks",
        "training",
        "best_practices",
        "patterns",
        "operational_knowledge",
    ]

    permissions = [
        "agent.execute",
        "learning.read",
        "learning.write",
        "memory.read",
        "memory.write",
        "events.read",
    ]

    VALID_LESSON_TYPES = [
        "lesson",
        "best_practice",
        "pattern",
        "decision",
        "procedure",
        "insight",
    ]

    VALID_ERROR_SEVERITY = [
        "low",
        "medium",
        "high",
        "critical",
    ]

    VALID_TRAINING_TYPES = [
        "instruction",
        "example",
        "rule",
        "procedure",
        "correction",
        "pattern",
        "playbook",
    ]

    def __init__(
        self,
        root_path: Optional[str | Path] = None,
        event_bus: Optional[Any] = None,
        permission_manager: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            permission_manager=permission_manager,
            config=config,
        )

        configured_root = self.config.get("root_path")
        self.root_path = Path(root_path or configured_root or ".")

        self.learning_dir = self.root_path / "learning"
        self.lessons_file = self.learning_dir / "lessons" / "lessons.json"
        self.errors_file = self.learning_dir / "errors" / "errors.json"
        self.playbooks_file = self.learning_dir / "playbooks" / "playbooks.json"
        self.training_file = self.learning_dir / "training" / "training_items.json"

        self.logger = logging.getLogger("k_atlas.learning_agent")

    def metadata(self) -> Dict[str, Any]:
        return {
            "base_class": "BaseAgent",
            "type": "learning",
            "created_for": "K-Atlas OS",
            "module_role": "operational_learning_and_training_knowledge",
            "learning_dir": str(self.learning_dir),
            "stores": {
                "lessons": str(self.lessons_file),
                "errors": str(self.errors_file),
                "playbooks": str(self.playbooks_file),
                "training": str(self.training_file),
            },
        }

    def required_permission(self, context: AgentContext) -> str:
        return "agent.execute"

    def run(self, context: AgentContext) -> Dict[str, Any]:
        action = self._action(context.command)

        if action == "ping":
            return self._ping()

        if action in ["help", "commands"]:
            return self._help()

        if action in ["learn", "lesson", "register_lesson"]:
            return self._register_lesson(context.payload)

        if action in ["best_practice", "practice"]:
            payload = dict(context.payload)
            payload["type"] = "best_practice"
            return self._register_lesson(payload)

        if action in ["pattern", "register_pattern"]:
            payload = dict(context.payload)
            payload["type"] = "pattern"
            return self._register_lesson(payload)

        if action in ["error", "register_error"]:
            return self._register_error(context.payload)

        if action in ["playbook", "create_playbook"]:
            return self._create_playbook(context.payload)

        if action in ["memory_to_playbook", "from_memory"]:
            return self._memory_to_playbook(context.payload)

        if action in ["training", "create_training"]:
            return self._create_training_item(context.payload)

        if action in ["list_lessons", "lessons"]:
            return self._list_items(self.lessons_file, "lessons", context.payload)

        if action in ["list_errors", "errors"]:
            return self._list_items(self.errors_file, "errors", context.payload)

        if action in ["list_playbooks", "playbooks"]:
            return self._list_items(self.playbooks_file, "playbooks", context.payload)

        if action in ["list_training", "training_items"]:
            return self._list_items(self.training_file, "training_items", context.payload)

        if action == "search":
            return self._search(context.payload)

        if action == "stats":
            return self._stats()

        if action == "export_training_pack":
            return self._export_training_pack(context.payload)

        return {
            "success": False,
            "message": "Comando nao reconhecido pelo LearningAgent.",
            "action": action,
            "available_actions": [
                "ping",
                "help",
                "learn",
                "best_practice",
                "pattern",
                "error",
                "playbook",
                "memory_to_playbook",
                "training",
                "lessons",
                "errors",
                "playbooks",
                "training_items",
                "search",
                "stats",
                "export_training_pack",
            ],
        }

    def _action(self, command: str) -> str:
        clean = str(command).strip().lower()
        if "." in clean:
            return clean.split(".", 1)[1]
        return clean

    def _ping(self) -> Dict[str, Any]:
        self._ensure_dirs()
        return {
            "success": True,
            "agent_id": self.agent_id,
            "message": "LearningAgent operacional.",
            "learning_dir": str(self.learning_dir),
        }

    def _help(self) -> Dict[str, Any]:
        return {
            "success": True,
            "commands": {
                "learning_agent.learn": "Registra aprendizado operacional.",
                "learning_agent.best_practice": "Registra boa pratica.",
                "learning_agent.pattern": "Registra padrao reutilizavel.",
                "learning_agent.error": "Registra erro operacional com causa e correcao.",
                "learning_agent.playbook": "Cria playbook reutilizavel.",
                "learning_agent.memory_to_playbook": "Transforma memoria em playbook.",
                "learning_agent.training": "Cria item de treinamento.",
                "learning_agent.search": "Busca conhecimento aprendido.",
                "learning_agent.stats": "Mostra estatisticas do aprendizado.",
                "learning_agent.export_training_pack": "Exporta pacote consolidado de treinamento.",
            },
            "example_lesson": {
                "title": "Smoke tests nao devem alterar memoria operacional",
                "content": "Usar TemporaryDirectory em testes para evitar sujeira em memory/*.json.",
                "type": "best_practice",
                "tags": ["tests", "memory", "quality"],
                "source": "operator",
                "importance": 3,
            },
            "example_error": {
                "title": "Teste sujou memoria operacional",
                "symptom": "memory/tasks.json ficou modificado apos smoke test.",
                "cause": "Teste gravava no arquivo real.",
                "fix": "Isolar teste com TemporaryDirectory.",
                "severity": "medium",
                "tags": ["tests", "memory"],
            },
            "example_playbook": {
                "title": "Criar novo agente K-Atlas",
                "objective": "Padronizar criacao de agentes.",
                "steps": [
                    "Criar arquivo em agents/",
                    "Implementar BaseAgent",
                    "Criar smoke test",
                    "Integrar no boot quando aprovado",
                    "Rodar dev_runner",
                    "Commitar checkpoint"
                ],
                "tags": ["agents", "kernel"],
            },
        }

    def _register_lesson(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = self._required_text(payload, "title")
        content = self._required_text(payload, "content")

        lesson_type = str(payload.get("type", "lesson")).strip().lower()
        if lesson_type not in self.VALID_LESSON_TYPES:
            lesson_type = "lesson"

        item = {
            "lesson_id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "type": lesson_type,
            "tags": self._as_list(payload.get("tags", [])),
            "source": str(payload.get("source", "operator")).strip(),
            "importance": int(payload.get("importance", 1)),
            "related_agents": self._as_list(payload.get("related_agents", [])),
            "reusable": bool(payload.get("reusable", True)),
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }

        store = self._read_store(self.lessons_file, "lessons")
        store["lessons"].append(item)
        self._write_store(self.lessons_file, store)

        self._log_info("lesson_registered", item["lesson_id"])

        return {
            "success": True,
            "message": "Aprendizado registrado.",
            "lesson": item,
        }

    def _register_error(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = self._required_text(payload, "title")
        symptom = self._required_text(payload, "symptom")

        severity = str(payload.get("severity", "medium")).strip().lower()
        if severity not in self.VALID_ERROR_SEVERITY:
            severity = "medium"

        item = {
            "error_id": str(uuid.uuid4()),
            "title": title,
            "symptom": symptom,
            "cause": str(payload.get("cause", "")).strip(),
            "fix": str(payload.get("fix", "")).strip(),
            "prevention": str(payload.get("prevention", "")).strip(),
            "severity": severity,
            "tags": self._as_list(payload.get("tags", [])),
            "source": str(payload.get("source", "operator")).strip(),
            "related_agents": self._as_list(payload.get("related_agents", [])),
            "status": str(payload.get("status", "resolved")).strip().lower(),
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }

        store = self._read_store(self.errors_file, "errors")
        store["errors"].append(item)
        self._write_store(self.errors_file, store)

        if item["fix"] or item["prevention"]:
            self._create_training_item(
                {
                    "title": "Correcao aprendida: " + title,
                    "content": self._build_error_training_content(item),
                    "type": "correction",
                    "tags": ["error", "correction"] + item["tags"],
                    "source": "learning_agent",
                    "importance": 2,
                }
            )

        self._log_info("error_registered", item["error_id"])

        return {
            "success": True,
            "message": "Erro operacional registrado.",
            "error": item,
        }

    def _create_playbook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = self._required_text(payload, "title")
        objective = self._required_text(payload, "objective")
        steps = self._as_list(payload.get("steps", []))

        if not steps:
            raise ValueError("Campo obrigatorio ausente: steps")

        item = {
            "playbook_id": str(uuid.uuid4()),
            "title": title,
            "objective": objective,
            "context": str(payload.get("context", "")).strip(),
            "steps": [str(step).strip() for step in steps if str(step).strip()],
            "expected_result": str(payload.get("expected_result", "")).strip(),
            "failure_modes": self._as_list(payload.get("failure_modes", [])),
            "tags": self._as_list(payload.get("tags", [])),
            "source": str(payload.get("source", "operator")).strip(),
            "version": str(payload.get("version", "0.1.0")).strip(),
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }

        store = self._read_store(self.playbooks_file, "playbooks")
        store["playbooks"].append(item)
        self._write_store(self.playbooks_file, store)

        self._create_training_item(
            {
                "title": "Playbook treinavel: " + title,
                "content": self._build_playbook_training_content(item),
                "type": "playbook",
                "tags": ["playbook", "procedure"] + item["tags"],
                "source": "learning_agent",
                "importance": int(payload.get("importance", 2)),
            }
        )

        self._log_info("playbook_created", item["playbook_id"])

        return {
            "success": True,
            "message": "Playbook criado.",
            "playbook": item,
        }

    def _memory_to_playbook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = self._required_text(payload, "title")
        memory_content = self._required_text(payload, "memory_content")

        steps = self._as_list(payload.get("steps", []))
        if not steps:
            steps = self._derive_steps_from_text(memory_content)

        playbook_payload = {
            "title": title,
            "objective": str(payload.get("objective", "Transformar memoria operacional em procedimento reutilizavel.")),
            "context": memory_content,
            "steps": steps,
            "expected_result": str(payload.get("expected_result", "Procedimento reutilizavel criado a partir da memoria.")),
            "failure_modes": self._as_list(payload.get("failure_modes", [])),
            "tags": ["memory_to_playbook"] + self._as_list(payload.get("tags", [])),
            "source": str(payload.get("source", "memory_agent")).strip(),
            "importance": int(payload.get("importance", 2)),
        }

        return self._create_playbook(playbook_payload)

    def _create_training_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = self._required_text(payload, "title")
        content = self._required_text(payload, "content")

        training_type = str(payload.get("type", "instruction")).strip().lower()
        if training_type not in self.VALID_TRAINING_TYPES:
            training_type = "instruction"

        item = {
            "training_id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "type": training_type,
            "tags": self._as_list(payload.get("tags", [])),
            "source": str(payload.get("source", "operator")).strip(),
            "importance": int(payload.get("importance", 1)),
            "target_agents": self._as_list(payload.get("target_agents", [])),
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }

        store = self._read_store(self.training_file, "training_items")
        store["training_items"].append(item)
        self._write_store(self.training_file, store)

        self._log_info("training_item_created", item["training_id"])

        return {
            "success": True,
            "message": "Item de treinamento criado.",
            "training_item": item,
        }

    def _list_items(self, path: Path, key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        store = self._read_store(path, key)
        items = list(store.get(key, []))

        tag = payload.get("tag")
        if tag:
            items = [
                item for item in items
                if str(tag) in item.get("tags", [])
            ]

        item_type = payload.get("type")
        if item_type:
            items = [
                item for item in items
                if item.get("type") == str(item_type).lower()
            ]

        limit = int(payload.get("limit", 50))
        items = items[-limit:]

        return {
            "success": True,
            "store": key,
            "total": len(items),
            key: items,
        }

    def _search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = self._required_text(payload, "query").lower()
        limit = int(payload.get("limit", 50))

        results = []

        search_plan = [
            (self.lessons_file, "lessons", "lesson_id"),
            (self.errors_file, "errors", "error_id"),
            (self.playbooks_file, "playbooks", "playbook_id"),
            (self.training_file, "training_items", "training_id"),
        ]

        for path, key, id_field in search_plan:
            store = self._read_store(path, key)
            for item in store.get(key, []):
                haystack = json.dumps(item, ensure_ascii=False).lower()
                if query in haystack:
                    results.append(
                        {
                            "store": key,
                            "id": item.get(id_field),
                            "item": item,
                        }
                    )

        return {
            "success": True,
            "query": query,
            "total": len(results[-limit:]),
            "results": results[-limit:],
        }

    def _stats(self) -> Dict[str, Any]:
        lessons = self._read_store(self.lessons_file, "lessons").get("lessons", [])
        errors = self._read_store(self.errors_file, "errors").get("errors", [])
        playbooks = self._read_store(self.playbooks_file, "playbooks").get("playbooks", [])
        training_items = self._read_store(self.training_file, "training_items").get("training_items", [])

        return {
            "success": True,
            "learning_dir": str(self.learning_dir),
            "totals": {
                "lessons": len(lessons),
                "errors": len(errors),
                "playbooks": len(playbooks),
                "training_items": len(training_items),
            },
            "by_lesson_type": self._count_by(lessons, "type"),
            "by_error_severity": self._count_by(errors, "severity"),
            "by_training_type": self._count_by(training_items, "type"),
        }

    def _export_training_pack(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        output_path = Path(
            payload.get(
                "output_path",
                self.learning_dir / "training" / "training_pack.json",
            )
        )

        pack = {
            "app": "K-Atlas OS",
            "type": "training_pack",
            "version": "0.1.0",
            "created_at": now_iso(),
            "lessons": self._read_store(self.lessons_file, "lessons").get("lessons", []),
            "errors": self._read_store(self.errors_file, "errors").get("errors", []),
            "playbooks": self._read_store(self.playbooks_file, "playbooks").get("playbooks", []),
            "training_items": self._read_store(self.training_file, "training_items").get("training_items", []),
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(pack, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "success": True,
            "message": "Training pack exportado.",
            "output_path": str(output_path),
            "totals": {
                "lessons": len(pack["lessons"]),
                "errors": len(pack["errors"]),
                "playbooks": len(pack["playbooks"]),
                "training_items": len(pack["training_items"]),
            },
        }

    def _read_store(self, path: Path, key: str) -> Dict[str, Any]:
        self._ensure_dirs()

        if not path.exists():
            return {
                "version": "0.1.0",
                "created_at": now_iso(),
                "updated_at": now_iso(),
                key: [],
            }

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if key not in data or not isinstance(data[key], list):
            data[key] = []

        return data

    def _write_store(self, path: Path, store: Dict[str, Any]) -> None:
        self._ensure_dirs()
        store["updated_at"] = now_iso()

        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(
            json.dumps(store, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(path)

    def _ensure_dirs(self) -> None:
        for directory in [
            self.learning_dir,
            self.learning_dir / "lessons",
            self.learning_dir / "errors",
            self.learning_dir / "playbooks",
            self.learning_dir / "training",
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _required_text(self, payload: Dict[str, Any], field: str) -> str:
        value = str(payload.get(field, "")).strip()
        if not value:
            raise ValueError("Campo obrigatorio ausente: " + field)
        return value

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        return [value]

    def _count_by(self, items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
        output: Dict[str, int] = {}

        for item in items:
            key = str(item.get(field, "unknown"))
            output[key] = output.get(key, 0) + 1

        return output

    def _derive_steps_from_text(self, text: str) -> List[str]:
        lines = [
            line.strip(" -0123456789.").strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if len(lines) >= 2:
            return lines

        return [
            "Ler a memoria operacional original.",
            "Identificar objetivo, contexto e decisao tomada.",
            "Converter a decisao em procedimento reutilizavel.",
            "Registrar o procedimento como playbook.",
            "Validar o playbook em execucao real antes de automatizar.",
        ]

    def _build_error_training_content(self, error: Dict[str, Any]) -> str:
        return "\n".join(
            [
                "Erro operacional aprendido.",
                "Titulo: " + str(error.get("title", "")),
                "Sintoma: " + str(error.get("symptom", "")),
                "Causa: " + str(error.get("cause", "")),
                "Correcao: " + str(error.get("fix", "")),
                "Prevencao: " + str(error.get("prevention", "")),
            ]
        )

    def _build_playbook_training_content(self, playbook: Dict[str, Any]) -> str:
        steps = playbook.get("steps", [])
        step_lines = [
            str(index + 1) + ". " + str(step)
            for index, step in enumerate(steps)
        ]

        return "\n".join(
            [
                "Playbook treinavel.",
                "Titulo: " + str(playbook.get("title", "")),
                "Objetivo: " + str(playbook.get("objective", "")),
                "Contexto: " + str(playbook.get("context", "")),
                "Passos:",
                *step_lines,
                "Resultado esperado: " + str(playbook.get("expected_result", "")),
            ]
        )

    def _log_info(self, action: str, item_id: str) -> None:
        self.logger.info(
            "LearningAgent action=%s item_id=%s",
            action,
            item_id,
        )
