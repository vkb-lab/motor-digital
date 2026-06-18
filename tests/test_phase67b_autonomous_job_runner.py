from __future__ import annotations

import json
from pathlib import Path

from k_atlas.kaizen.autonomous_job_runner import process_inbox

def test_phase67b_autonomous_job_runner_executes_safe_write_job(tmp_path):
    inbox = tmp_path / "local_runtime" / "kos_autonomous_jobs" / "inbox"
    inbox.mkdir(parents=True)
    job = {
        "status": "PENDING",
        "job_id": "TEST_JOB",
        "action": "write_json_report",
        "output_relpath": "local_runtime/kos_autonomous_jobs/output/TEST_JOB.json",
        "payload": {"message": "ok"},
    }
    (inbox / "TEST_JOB.json").write_text(json.dumps(job), encoding="utf-8")

    result = process_inbox(root=tmp_path)

    assert result["processed_count"] == 1
    assert result["processed"][0]["status"] == "KOS_AUTONOMOUS_JOB_EXECUTED"
    assert result["processed"][0]["returncode"] == 0
    assert (tmp_path / "local_runtime" / "kos_autonomous_jobs" / "output" / "TEST_JOB.json").exists()

def test_phase67b_blocks_when_kill_switch_engaged(tmp_path):
    control = tmp_path / "local_runtime" / "kos_control"
    control.mkdir(parents=True)
    (control / "AUTONOMY_KILL_SWITCH.json").write_text(
        json.dumps({"status": "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"}),
        encoding="utf-8",
    )

    inbox = tmp_path / "local_runtime" / "kos_autonomous_jobs" / "inbox"
    inbox.mkdir(parents=True)
    job = {
        "status": "PENDING",
        "job_id": "BLOCKED_JOB",
        "action": "write_json_report",
        "output_relpath": "local_runtime/kos_autonomous_jobs/output/BLOCKED_JOB.json",
        "payload": {"message": "blocked"},
    }
    (inbox / "BLOCKED_JOB.json").write_text(json.dumps(job), encoding="utf-8")

    result = process_inbox(root=tmp_path)

    assert result["processed_count"] == 1
    assert result["processed"][0]["status"] == "KOS_AUTONOMOUS_JOB_FAILED"
    assert result["processed"][0]["reason"] == "blocked_by_kill_switch"
