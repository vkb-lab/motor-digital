from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class KAtlasComponent:
    checkpoint = "472"
    name = "K-Uni Operator Focus Mode"
    batch = "469-473"
    batch_name = "K-Uni Home Operations Layer"

    def summary(self) -> dict[str, Any]:
        return {
            "ok": True,
            "checkpoint": self.checkpoint,
            "name": self.name,
            "batch": self.batch,
            "batch_name": self.batch_name,
            "status": "operational",
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "human_approval_required": True,
            "guardrails": [
                "sem execucao automatica",
                "sem API externa",
                "sem controle remoto real",
                "sem captura de senha",
                "sem deploy automatico",
                "auditoria obrigatoria"
            ],
            "generated_at": utc_now()
        }
