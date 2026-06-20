from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase69j_engineer_packet_promotion_bridge.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase69j_promotion", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def write_staged(packet_id: str, command: str):
    path = ROOT / "local_runtime" / "kos_engineer_command_intake" / "staged" / f"{packet_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "status": "KOS_ENGINEER_COMMAND_INTAKE_STAGED",
        "packet_id": packet_id,
        "title": "test",
        "objective": "test",
        "command": command,
    }), encoding="utf-8")
    return path


def test_phase69j_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_engineer_packet_promotion_bridge_policy.json").exists()
    assert (ROOT / "docs" / "KOS_ENGINEER_PACKET_PROMOTION_BRIDGE_V069J.md").exists()


def test_phase69j_promotes_safe_packet_to_handoff_inbox():
    mod = load_module()
    packet = write_staged("test-69j-safe", "Write-Host test")
    result = mod.promote_packet(packet)
    assert result["status"] == "KOS_ENGINEER_PACKET_PROMOTED_TO_HANDOFF_INBOX"
    assert result["auto_execution_enabled"] is False
    assert result["operator_review_required"] is True
    assert Path(result["handoff_inbox_file"]).exists()


def test_phase69j_blocks_real_publish_packet():
    mod = load_module()
    packet = write_staged("test-69j-block", "--execute-real-publish")
    result = mod.promote_packet(packet)
    assert result["status"] == "KOS_ENGINEER_PACKET_PROMOTION_BLOCKED"
    assert result["reason"] == "blocked_pattern_detected"
