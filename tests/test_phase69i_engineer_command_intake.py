from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase69i_engineer_command_intake.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase69i_intake", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase69i_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "scripts" / "submit_kos_engineer_command_intake.ps1").exists()
    assert (ROOT / "KOS_Engineer_Command_Intake.cmd").exists()
    assert (ROOT / "config" / "kos_engineer_command_intake_bridge_policy.json").exists()
    assert (ROOT / "docs" / "KOS_ENGINEER_COMMAND_INTAKE_BRIDGE_V069I.md").exists()


def test_phase69i_stages_safe_packet():
    mod = load_module()
    raw = """KOS_ENGINEER_PACKET_START
{"id":"test-safe","title":"safe","objective":"stage","action":"stage_command","mode":"stage_only","command":"Write-Host test"}
KOS_ENGINEER_PACKET_END"""
    result = mod.process_raw_packet(raw)
    assert result["status"] == "KOS_ENGINEER_COMMAND_INTAKE_STAGED"
    assert result["safe_for_auto_execution"] is False
    assert result["operator_review_required"] is True


def test_phase69i_blocks_real_publish_packet():
    mod = load_module()
    raw = """KOS_ENGINEER_PACKET_START
{"id":"test-block","title":"block","objective":"publish","action":"stage_command","mode":"stage_only","command":"$env:KOS_REAL_HUPMIX_PUBLISH_ENABLED='true'; --execute-real-publish"}
KOS_ENGINEER_PACKET_END"""
    result = mod.process_raw_packet(raw)
    assert result["status"] == "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED"
    assert result["reason"] == "blocked_pattern_detected"


def test_phase69i_blocks_secret_packet():
    mod = load_module()
    raw = """KOS_ENGINEER_PACKET_START
{"id":"test-secret","title":"secret","objective":"bad","action":"stage_command","mode":"stage_only","command":"access_token=abc"}
KOS_ENGINEER_PACKET_END"""
    result = mod.process_raw_packet(raw)
    assert result["status"] == "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED"
    assert result["reason"] == "blocked_pattern_detected"
