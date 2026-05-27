from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class CoworkResponse:
    understanding: str
    plan: List[str] = field(default_factory=list)
    executed: List[str] = field(default_factory=list)
    blocked: List[str] = field(default_factory=list)
    next_step: str = ""
    intent: str = "unknown"
    action: str = "none"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        lines = []

        lines.append("### Entendimento")
        lines.append(self.understanding or "Ainda não entendi completamente o pedido.")
        lines.append("")

        if self.plan:
            lines.append("### Plano")
            for item in self.plan:
                lines.append(f"- {item}")
            lines.append("")

        if self.executed:
            lines.append("### Ação executada")
            for item in self.executed:
                lines.append(f"- {item}")
            lines.append("")

        if self.blocked:
            lines.append("### Bloqueios / Limites")
            for item in self.blocked:
                lines.append(f"- {item}")
            lines.append("")

        if self.next_step:
            lines.append("### Próximo passo")
            lines.append(self.next_step)
            lines.append("")

        return "\n".join(lines)
