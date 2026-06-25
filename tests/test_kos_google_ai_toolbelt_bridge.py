from pathlib import Path
import json

from scripts.run_google_ai_toolbelt_bridge import (
    load_registry,
    make_subsidy_pack,
    make_tool_briefing,
)

ROOT = Path(__file__).resolve().parents[1]


def test_toolbelt_bridge_loads_registry():
    registry = load_registry()
    assert registry["status"] == "KOS_GOOGLE_AI_TOOLBELT_READY"
    assert len(registry["tools"]) >= 8


def test_toolbelt_bridge_generates_stitch_briefing():
    registry = load_registry()
    text = make_tool_briefing(
        registry,
        "stitch",
        "kaizen-home",
        "criar interface do painel principal do K-OS",
    )
    assert "Google Stitch" in text
    assert "kaizen-home" in text
    assert "prompt" in text.lower() or "briefing" in text.lower()
    assert "Do not claim API automation" in text or "browser-assisted" in text


def test_toolbelt_bridge_generates_subsidy_pack():
    registry = load_registry()
    text = make_subsidy_pack(
        registry,
        "kaizen-home",
        "preparar pacote de subsidio com Google Cloud e K-OS",
    )
    assert "Google Cloud" in text
    assert "Gmail Operator" in text
    assert "NotebookLM" in text
    assert "Stitch" in text
    assert "Antigravity" in text
