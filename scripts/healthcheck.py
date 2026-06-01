from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.agent_registry import register_default_agents
from k_atlas.events import EVENTS_FILE, emit_event
from k_atlas.memory_store import MemoryStore
from k_atlas.paths import MEMORY_DIR, REQUIRED_DIRS, ensure_dirs, relative_to_root
from k_atlas.reporting import generate_report


def check(condition: bool, label: str, failures: list[str]) -> None:
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    ensure_dirs()

    register_default_agents()
    check(True, "imports principais", failures)

    for directory in REQUIRED_DIRS:
        check(directory.exists(), f"pasta {relative_to_root(directory)}", failures)

    check((ROOT / "app.py").exists(), "app.py existe", failures)

    memory_probe = MEMORY_DIR / "healthcheck_write.json"
    memory_probe.write_text(json.dumps({"status": "ok"}, ensure_ascii=False), encoding="utf-8")
    check(memory_probe.exists(), "escrita em memory/", failures)

    event = emit_event("healthcheck", {"status": "ok"})
    check(EVENTS_FILE.exists() and event["type"] == "healthcheck", "escrita em logs/events.jsonl", failures)

    store = MemoryStore()
    store.add("healthcheck", "ok", ["healthcheck"])
    check(len(store.find("healthcheck")) >= 1, "memoria operacional JSON", failures)

    report_path = generate_report("K-OS Healthcheck Report", {"status": "ok"})
    check(report_path.exists(), "criacao de relatorio", failures)

    if failures:
        print("STATUS: BLOQUEADO")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("STATUS: PRONTO MVP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

