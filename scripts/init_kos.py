from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.agent_registry import register_default_agents
from k_atlas.events import emit_event
from k_atlas.paths import ensure_dirs


def main() -> int:
    ensure_dirs()
    registry = register_default_agents()
    emit_event("kos_initialized", {"agents": registry.names()})
    print("K-OS inicializado")
    print("Agentes:", ", ".join(registry.names()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

