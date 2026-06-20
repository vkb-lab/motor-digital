from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase69k_files_exist():
    assert (ROOT / "scripts" / "run_kos_engineer_packet_oneclick.ps1").exists()
    assert (ROOT / "KOS_Engineer_Packet_OneClick.cmd").exists()
    assert (ROOT / "config" / "kos_engineer_packet_oneclick_runner_policy.json").exists()
    assert (ROOT / "docs" / "KOS_ENGINEER_PACKET_ONECLICK_RUNNER_V069K.md").exists()

def test_phase69k_runner_is_not_auto_executor():
    script = (ROOT / "scripts" / "run_kos_engineer_packet_oneclick.ps1").read_text(encoding="utf-8")
    policy = (ROOT / "config" / "kos_engineer_packet_oneclick_runner_policy.json").read_text(encoding="utf-8")

    assert "submit_kos_engineer_command_intake.ps1" in script
    assert "run_phase69j_engineer_packet_promotion_bridge.py" in script
    assert "auto_execution_enabled=$false" in script
    assert "execution_requires_existing_approval_pipeline" in script
    assert "auto_execution_enabled" in policy
    assert "operator_review_required" in policy
