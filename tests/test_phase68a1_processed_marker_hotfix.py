from __future__ import annotations

import json
from pathlib import Path

from k_atlas.kaizen.autonomous_job_runner import process_inbox


def test_phase68a1_processed_marker_is_not_overwritten_by_original_job(tmp_path):
    inbox = tmp_path / "local_runtime" / "kos_autonomous_jobs" / "inbox"
    inbox.mkdir(parents=True)

    job = {
        "status": "PENDING",
        "job_id": "TEST_68A1_MARKER",
        "action": "write_json_report",
        "output_relpath": "local_runtime/kos_autonomous_jobs/output/TEST_68A1_MARKER.json",
        "payload": {"message": "marker hotfix"},
    }

    (inbox / "TEST_68A1_MARKER.json").write_text(json.dumps(job), encoding="utf-8")

    result = process_inbox(root=tmp_path)

    marker_path = tmp_path / "local_runtime" / "kos_autonomous_jobs" / "processed" / "TEST_68A1_MARKER.json"
    source_path = tmp_path / "local_runtime" / "kos_autonomous_jobs" / "processed" / "TEST_68A1_MARKER_source.json"

    marker = json.loads(marker_path.read_text(encoding="utf-8"))

    assert result["processed_count"] == 1
    assert marker["status"] == "KOS_AUTONOMOUS_JOB_EXECUTED"
    assert marker["returncode"] == 0
    assert source_path.exists()
