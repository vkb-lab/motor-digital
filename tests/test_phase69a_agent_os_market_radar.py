from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase69a_files_exist():
    assert (ROOT / "scripts" / "run_phase69a_agent_os_market_radar.py").exists()
    assert (ROOT / "config" / "kos_agent_os_market_radar_policy.json").exists()
    assert (ROOT / "docs" / "KOS_AGENT_OS_MARKET_RADAR_V069A.md").exists()

def test_phase69a_market_references_exist():
    text = (ROOT / "scripts" / "run_phase69a_agent_os_market_radar.py").read_text(encoding="utf-8")
    assert "OpenAI ChatGPT Agent" in text
    assert "OpenAI Agents SDK / Codex" in text
    assert "Anthropic Claude Code" in text
    assert "Cursor Agents / CLI" in text
    assert "Replit Agent" in text

def test_phase69a_safe_only():
    text = (ROOT / "scripts" / "run_phase69a_agent_os_market_radar.py").read_text(encoding="utf-8")
    assert "paid_ai_call_executed" in text
    assert "instagram_publish_executed" in text
    assert "browser_logged_account_automation_used" in text
