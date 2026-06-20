from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase69l_files_exist():
    assert (ROOT / "scripts" / "run_phase69l_engineer_packet_review_console.py").exists()
    assert (ROOT / "scripts" / "open_kos_engineer_packet_review.ps1").exists()
    assert (ROOT / "config" / "kos_engineer_packet_review_console_policy.json").exists()
    assert (ROOT / "docs" / "KOS_ENGINEER_PACKET_REVIEW_CONSOLE_V069L.md").exists()

def test_phase69l_review_is_safe_only():
    script = (ROOT / "scripts" / "run_phase69l_engineer_packet_review_console.py").read_text(encoding="utf-8")
    policy = (ROOT / "config" / "kos_engineer_packet_review_console_policy.json").read_text(encoding="utf-8")

    assert "auto_execution_enabled" in script
    assert "operator_review_required" in script
    assert "execution_requires_existing_approval_pipeline" in script
    assert "instagram_publish_executed" in script
    assert "auto_execution_enabled" in policy
    assert "operator_review_required" in policy
