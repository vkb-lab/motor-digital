from pathlib import Path
import json

from scripts.run_kos_brain_provider_status import (
    build_status,
    choose_provider,
    load_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_brain_provider_priority_registry_exists():
    path = ROOT / "memory" / "kos_governance" / "KOS_BRAIN_PROVIDER_PRIORITY_REGISTRY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_BRAIN_PROVIDER_PRIORITY_ACTIVE"
    order = [item["id"] for item in data["routing_order"]]
    assert order[0] == "kos_internal_evolutionary"
    assert "ollama_local" in order
    assert "gemini_free_guarded" in order
    assert order.index("ollama_local") < order.index("gemini_free_guarded")
    assert order[-1] == "external_paid_locked"


def test_brain_provider_skill_exists():
    path = ROOT / "memory" / "kos_skills" / "KOS_SKILL_BRAIN_PROVIDER_PRIORITY_V1.md"
    text = path.read_text(encoding="utf-8")
    assert "Inteligência interna evolutiva" in text
    assert "IA local gratuita" in text
    assert "Gemini Free Guarded" in text
    assert "paid/external bloqueado" in text.lower() or "bloqueado" in text.lower()


def test_brain_provider_status_builds_without_secret_leak():
    status = build_status()
    assert status["status"] == "KOS_BRAIN_PROVIDER_STATUS_READY"
    assert "providers" in status
    assert "GEMINI_API_KEY" not in json.dumps(status)
    assert status["decision"]["paid_provider_used"] is False


def test_choose_provider_prefers_internal_then_local_then_free_cloud():
    fake = {
        "providers": {
            "kos_internal_evolutionary": {"active": False},
            "ollama_local": {"active": True},
            "lmstudio_local": {"active": False},
            "localai_or_vllm": {"active": False},
            "gemini_free_guarded": {"active": True},
        }
    }
    decision = choose_provider(fake)
    assert decision["selected_provider"] == "ollama_local"
    assert decision["paid_provider_used"] is False
