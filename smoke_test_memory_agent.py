# -*- coding: utf-8 -*-
"""
Smoke test do MemoryAgent.

Uso:
python smoke_test_memory_agent.py
"""

from __future__ import annotations

from pathlib import Path

from agents.memory_agent import MemoryAgent
from core.kernel import create_kernel


ROOT = Path(__file__).resolve().parent


def assert_success(result, label: str) -> None:
    if not result.success:
        print(label)
        print(result.to_dict())
        raise SystemExit(1)


if __name__ == "__main__":
    kernel = create_kernel(root_path=ROOT)
    kernel.start(load_state=True)

    memory_agent = MemoryAgent(storage_path=ROOT / "memory" / "entries.json")
    kernel.register_agent(memory_agent, replace=True, roles=["agent"])

    ping = kernel.execute("memory_agent.ping")
    assert_success(ping, "ping failed")

    created = kernel.execute(
        "memory_agent.remember",
        payload={
            "title": "Validar MemoryAgent",
            "content": "Teste automatico da memoria operacional persistente do K-Atlas OS.",
            "type": "decision",
            "tags": ["smoke_test", "memory_agent", "kernel"],
            "source": "smoke_test",
            "visibility": "internal",
            "importance": 2,
        },
    )
    assert_success(created, "remember failed")

    memory_id = created.output["memory"]["memory_id"]

    listed = kernel.execute("memory_agent.list", payload={"limit": 10})
    assert_success(listed, "list failed")

    loaded = kernel.execute("memory_agent.get", payload={"memory_id": memory_id})
    assert_success(loaded, "get failed")

    searched = kernel.execute("memory_agent.search", payload={"query": "MemoryAgent"})
    assert_success(searched, "search failed")

    stats = kernel.execute("memory_agent.stats")
    assert_success(stats, "stats failed")

    print("MemoryAgent smoke test OK")
    print("memory_id:", memory_id)
    print("total_memories:", stats.output["total"])

    kernel.stop(save_state=True)
