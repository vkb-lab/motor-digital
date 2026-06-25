from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_google_ai_toolbelt_registry_exists():
    path = ROOT / "memory" / "kos_governance" / "KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_GOOGLE_AI_TOOLBELT_READY"
    ids = {tool["id"] for tool in data["tools"]}
    expected = {
        "google_ai_studio",
        "stitch",
        "pomelli",
        "opal",
        "mixboard",
        "flow",
        "flow_music_producerai",
        "antigravity",
        "notebooklm",
    }
    assert expected.issubset(ids)


def test_google_ai_toolbelt_skill_exists():
    path = ROOT / "memory" / "kos_skills" / "KOS_SKILL_GOOGLE_AI_TOOLBELT_OPERATOR_V1.md"
    text = path.read_text(encoding="utf-8")
    assert "GOOGLE AI TOOLBELT" in text
    assert "Stitch" in text
    assert "Pomelli" in text
    assert "NotebookLM" in text
    assert "Antigravity" in text
    assert "subsidio" in text.lower() or "startup" in text.lower()


def test_google_ai_toolbelt_has_guardrails():
    path = ROOT / "memory" / "kos_governance" / "KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = " ".join(data["security_rules"])
    assert "do_not_commit_api_keys" in rules
    assert "do_not_commit_oauth_tokens" in rules
    assert "do_not_claim_api_access_when_tool_is_browser_only" in rules
