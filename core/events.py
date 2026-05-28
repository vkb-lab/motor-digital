# -*- coding: utf-8 -*-
"""
K-Atlas OS - Event System

Camada responsável por eventos, auditoria básica e publicação interna.
Python puro. Compatível com Windows. Sem dependências externas.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional


def utc_now_iso() -> str:
    """Retorna timestamp UTC em formato ISO-8601."""
    return datetime.now(timezone.utc).isoformat()


class EventLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Event:
    """
    Evento operacional padrão do K-Atlas OS.

    Todo evento importante do sistema deve passar por esta estrutura.
    Isso cria uma base auditável para kernel, agentes, memória, API e workers.
    """

    event_type: str
    source: str
    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    target: Optional[str] = None
    status: EventStatus = EventStatus.PENDING
    level: EventLevel = EventLevel.INFO
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.trace_id is None:
            self.trace_id = self.event_id

        if isinstance(self.status, str):
            self.status = EventStatus(self.status)

        if isinstance(self.level, str):
            self.level = EventLevel(self.level)

    def to_dict(self) -> Dict[str, Any]:
        """Converte o evento para dicionário serializável."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "target": self.target,
            "action": self.action,
            "payload": self.payload,
            "status": self.status.value,
            "level": self.level.value,
            "trace_id": self.trace_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        """Converte o evento para JSON UTF-8 safe."""
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Reconstrói um evento a partir de um dicionário."""
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            event_type=data["event_type"],
            source=data["source"],
            target=data.get("target"),
            action=data["action"],
            payload=data.get("payload", {}),
            status=EventStatus(data.get("status", EventStatus.PENDING.value)),
            level=EventLevel(data.get("level", EventLevel.INFO.value)),
            trace_id=data.get("trace_id"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", utc_now_iso()),
        )


EventCallback = Callable[[Event], None]


class EventBus:
    """
    Barramento simples de eventos.

    Responsabilidades:
    - publicar eventos
    - permitir assinaturas por tipo de evento
    - registrar eventos em arquivo JSONL
    - manter histórico recente em memória
    """

    WILDCARD = "*"

    def __init__(
        self,
        log_dir: str | Path = "logs/events",
        log_to_file: bool = True,
        keep_last: int = 500,
    ) -> None:
        self.log_dir = Path(log_dir)
        self.log_to_file = log_to_file
        self.keep_last = keep_last
        self._subscribers: Dict[str, List[EventCallback]] = {}
        self._history: List[Event] = []
        self._lock = threading.RLock()

        if self.log_to_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def subscribe(self, event_type: str, callback: EventCallback) -> None:
        """Assina um tipo de evento. Use '*' para receber todos."""
        if not callable(callback):
            raise TypeError("callback precisa ser uma função chamável.")

        with self._lock:
            self._subscribers.setdefault(event_type, []).append(callback)

    def unsubscribe(self, event_type: str, callback: EventCallback) -> None:
        """Remove uma assinatura."""
        with self._lock:
            callbacks = self._subscribers.get(event_type, [])
            self._subscribers[event_type] = [item for item in callbacks if item != callback]

    def publish(self, event: Event) -> Event:
        """Publica um evento, grava log e notifica assinantes."""
        with self._lock:
            self._history.append(event)
            if len(self._history) > self.keep_last:
                self._history = self._history[-self.keep_last :]

            if self.log_to_file:
                self._write_event(event)

            callbacks = list(self._subscribers.get(event.event_type, []))
            callbacks.extend(self._subscribers.get(self.WILDCARD, []))

        for callback in callbacks:
            try:
                callback(event)
            except Exception as exc:
                self._write_callback_error(event, exc)

        return event

    def emit(
        self,
        event_type: str,
        source: str,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        target: Optional[str] = None,
        status: EventStatus | str = EventStatus.PENDING,
        level: EventLevel | str = EventLevel.INFO,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """Cria e publica um evento em uma chamada."""
        event = Event(
            event_type=event_type,
            source=source,
            target=target,
            action=action,
            payload=payload or {},
            status=EventStatus(status),
            level=EventLevel(level),
            trace_id=trace_id,
            metadata=metadata or {},
        )
        return self.publish(event)

    def history(
        self,
        event_type: Optional[str] = None,
        level: Optional[EventLevel | str] = None,
        limit: int = 100,
    ) -> List[Event]:
        """Retorna eventos recentes em memória."""
        with self._lock:
            events: Iterable[Event] = list(self._history)

        if event_type is not None:
            events = [event for event in events if event.event_type == event_type]

        if level is not None:
            target_level = EventLevel(level)
            events = [event for event in events if event.level == target_level]

        return list(events)[-limit:]

    def _write_event(self, event: Event) -> None:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        file_path = self.log_dir / f"events-{day}.jsonl"

        with file_path.open("a", encoding="utf-8") as file:
            file.write(event.to_json() + "\n")

    def _write_callback_error(self, original_event: Event, exc: Exception) -> None:
        """Registra erro de subscriber sem quebrar o kernel."""
        if not self.log_to_file:
            return

        error_event = Event(
            event_type="eventbus.callback_error",
            source="event_bus",
            target=original_event.source,
            action="notify_subscriber",
            status=EventStatus.FAILED,
            level=EventLevel.ERROR,
            trace_id=original_event.trace_id,
            payload={
                "original_event_id": original_event.event_id,
                "original_event_type": original_event.event_type,
                "error": str(exc),
            },
        )
        self._write_event(error_event)
