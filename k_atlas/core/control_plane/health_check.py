from __future__ import annotations

from pathlib import Path
from typing import Any

from .agent_registry import build_default_agent_registry
from .event_bus import EventBus
from .supervisor_queue import SupervisorQueue
from .system_state import SystemState


def run_control_plane_health_check() -> dict[str, Any]:
    registry = build_default_agent_registry()
    event_bus = EventBus()
    supervisor_queue = SupervisorQueue()
    system_state = SystemState()

    state = system_state.set_module_status(
        "control_plane",
        "healthy",
        {
            "agents_registered": len(registry.list_agents()),
            "event_bus_path": str(event_bus.path),
            "supervisor_queue_path": str(supervisor_queue.path),
        },
    )

    return {
        "ok": True,
        "agents_registered": len(registry.list_agents()),
        "events_path_exists": Path(event_bus.path).parent.exists(),
        "supervisor_queue_path": str(supervisor_queue.path),
        "system_state": state,
    }