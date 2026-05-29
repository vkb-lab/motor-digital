from __future__ import annotations

from typing import Any, Mapping

from .blackboard_store import BlackboardStore


class BlackboardAgent:
    def __init__(self, store: BlackboardStore | None = None) -> None:
        self.store = store or BlackboardStore()

    def create_safe_plan(self, objective: str, requested_by: str = "human_operator") -> dict[str, Any]:
        objective_clean = objective.strip() or "operacao supervisionada"

        message = self.store.add_message(
            author="k_blackboard_agent",
            role="assistant",
            content=(
                "Plano seguro criado. Primeiro vamos diagnosticar, testar e somente depois preparar commit/deploy. "
                "Nenhum comando destrutivo sera executado sem aprovacao."
            ),
            metadata={"objective": objective_clean},
        )

        commands = [
            self.store.queue_command(
                title="Diagnostico Git",
                command="git status --short",
                requested_by=requested_by,
                metadata={"objective": objective_clean, "stage": "diagnostic"},
            ),
            self.store.queue_command(
                title="Historico recente",
                command="git log --oneline -5",
                requested_by=requested_by,
                metadata={"objective": objective_clean, "stage": "diagnostic"},
            ),
            self.store.queue_command(
                title="Smoke test Control Plane",
                command=".\\venv\\Scripts\\python.exe -m k_atlas.core.control_plane.smoke_test_control_plane",
                requested_by=requested_by,
                metadata={"objective": objective_clean, "stage": "test"},
            ),
        ]

        return {
            "message": message,
            "commands": commands,
        }