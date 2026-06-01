from __future__ import annotations

from pathlib import Path

from agents.base_agent import BaseAgent
from k_atlas.agent_registry import AgentRegistry
from k_atlas.campaign_engine import generate_campaign
from k_atlas.events import emit_event, read_events
from k_atlas.memory_store import MemoryStore
from k_atlas.paths import REQUIRED_DIRS, ensure_dirs
from k_atlas.reporting import generate_report
from k_atlas.task_runner import TaskRunner


def test_paths_exist_after_bootstrap() -> None:
    ensure_dirs()
    assert all(path.exists() for path in REQUIRED_DIRS)


def test_memory_json(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    item = store.add("key", {"value": 1}, ["test"])
    assert item["key"] == "key"
    assert store.find("key")[0]["value"]["value"] == 1


def test_events(tmp_path: Path) -> None:
    event_path = tmp_path / "events.jsonl"
    emit_event("test_event", {"ok": True}, event_path)
    events = read_events(path=event_path)
    assert events[-1]["type"] == "test_event"
    assert events[-1]["payload"]["ok"] is True


def test_agent_registry() -> None:
    registry = AgentRegistry()
    registry.register(BaseAgent())
    assert "base" in registry.names()
    assert registry.get("base").name == "base"


def test_basic_agent_execution() -> None:
    registry = AgentRegistry()
    registry.register(BaseAgent())
    result = TaskRunner(registry).run("base", "ping")
    assert result["status"] == "ok"
    assert result["task"] == "ping"


def test_campaign_generation() -> None:
    campaign = generate_campaign("Teste MVP", "Validar campanha", "time interno")
    assert campaign["name"] == "Teste MVP"
    assert campaign["content_plan"]


def test_report_generation() -> None:
    path = generate_report("Teste Report", {"status": "ok"})
    assert path.exists()
    assert "Teste Report" in path.read_text(encoding="utf-8")

