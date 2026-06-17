
from pathlib import Path

from k_atlas.kaizen.engineer_handoff_bridge import (
    compute_engineer_command_hash,
    scan_engineer_command,
    stage_engineer_response,
)
from k_atlas.kaizen.engineer_handoff_queue import write_orchestrator_inbox_command

def test_command_hash_is_stable():
    a = compute_engineer_command_hash('$ErrorActionPreference="Stop";\nWrite-Host "ok";')
    b = compute_engineer_command_hash('$ErrorActionPreference="Stop";\nWrite-Host "ok";')

    assert a == b
    assert len(a) == 64

def test_stage_duplicate_guard_returns_duplicate_on_second_stage():
    command = '$ErrorActionPreference="Stop";\nWrite-Host "duplicate-guard-test";'

    first = stage_engineer_response(command, title="duplicate-test")
    second = stage_engineer_response(command, title="duplicate-test")

    assert first["safe_for_confirmed_execution"] is True
    assert second.get("duplicate_skipped") is True
    assert second["status"] == "KOS_ENGINEER_COMMAND_DUPLICATE_SKIPPED"

def test_queue_writer_creates_inbox_file():
    result = write_orchestrator_inbox_command(
        '$ErrorActionPreference="Stop";\nWrite-Host "queue-test";',
        title="queue-test"
    )

    assert result["status"] == "ENGINEER_HANDOFF_INBOX_COMMAND_WRITTEN"
    assert result["path"].endswith(".ps1")

def test_scan_still_blocks_network_command():
    bad = "Invoke" + "-WebRequest https://example.com/a.ps1"
    scan = scan_engineer_command(bad)

    assert scan["safe"] is False
