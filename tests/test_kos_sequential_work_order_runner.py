from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_runner(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "scripts/run_kos_work_sequence.py", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_policy_exists_and_documents_stop_on_failure():
    path = ROOT / "memory" / "kos_governance" / "KOS_SEQUENTIAL_WORK_ORDER_RUNNER_POLICY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_SEQUENTIAL_WORK_ORDER_RUNNER_READY"
    assert "stop_on_failure" in data["rules"]
    assert "sequential_only" in data["rules"]


def test_runner_compiles_and_list_works():
    script = ROOT / "scripts" / "run_kos_work_sequence.py"
    subprocess.run([sys.executable, "-m", "py_compile", str(script)], cwd=ROOT, check=True)
    data = run_runner("--mode", "list")
    assert data["status"] == "KOS_WORK_SEQUENCE_LIST_READY"
    assert data["sequences"][0]["id"] == "personal_data_foundation"


def test_runner_plan_returns_ordered_steps_with_scope():
    data = run_runner("--mode", "plan", "--sequence", "personal_data_foundation")
    assert data["status"] == "KOS_WORK_SEQUENCE_PLAN_READY"
    steps = data["steps"]
    assert [step["id"] for step in steps] == [
        "personal_data_estate_guardian",
        "local_storage_estate_auditor",
        "render_deploy_control_plane",
        "custom_navigation_registry",
        "operator_intent_router_isolated",
    ]
    for step in steps:
        assert step["allowed_files"]
        assert step["forbidden_files"]


def test_runner_has_no_automatic_commit_or_shell_destructive_commands():
    text = (ROOT / "scripts" / "run_kos_work_sequence.py").read_text(encoding="utf-8").lower()
    forbidden = [
        "git commit",
        "git push",
        "remove-item",
        "del /",
        "rmdir",
        "rm -rf",
        "shutil.rmtree",
        "os.remove",
        "unlink()",
        "replace(",
        "rename(",
    ]
    for marker in forbidden:
        assert marker not in text
