
from k_atlas.kaizen.engineer_handoff_bridge import (
    extract_powershell_command,
    scan_engineer_command,
    build_engineer_prompt_from_review,
    validate_engineer_command_file,
)

def test_extract_command_from_response():
    text = 'texto antes\n$ErrorActionPreference="Stop";\nWrite-Host "ok";'
    command = extract_powershell_command(text)

    assert command.startswith("$ErrorActionPreference")
    assert "Write-Host" in command

def test_scan_allows_local_safe_command():
    command = """
$ErrorActionPreference="Stop";
Set-Location "C:\\Users\\oi\\Desktop\\motor-digital";
git --no-pager status --short;
python -m pytest tests\\test_phase61h_work_order_route_registry.py -q;
Write-Host "paid_ai_allowed=false";
Write-Host "instagram_publish_allowed=false";
"""
    scan = scan_engineer_command(command)

    assert scan["safe"] is True
    assert scan["status"] == "ENGINEER_COMMAND_SCAN_SAFE"

def test_scan_blocks_network_download():
    bad = "Invoke" + "-WebRequest https://example.com/a.ps1"
    scan = scan_engineer_command(bad)

    assert scan["safe"] is False
    assert scan["status"] == "ENGINEER_COMMAND_SCAN_BLOCKED"

def test_prompt_ready():
    prompt = build_engineer_prompt_from_review()

    assert prompt["status"] == "KOS_ENGINEER_PROMPT_READY"
    assert "K-Atlas Engineer" in prompt["prompt_text"]

def test_validate_blocks_file_outside_staged_dir(tmp_path):
    command_file = tmp_path / "command.ps1"
    command_file.write_text("Write-Host ok", encoding="utf-8")

    result = validate_engineer_command_file(str(command_file))

    assert result["valid"] is False
    assert result["reason"] == "outside_staged_dir"
