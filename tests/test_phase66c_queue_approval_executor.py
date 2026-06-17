from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase66c_files_exist():
    assert (ROOT / "config" / "kos_queue_approval_executor_policy.json").exists()
    assert (ROOT / "k_atlas" / "kaizen" / "queue_approval_executor.py").exists()
    assert (ROOT / "scripts" / "run_phase66c_queue_approval_executor.py").exists()
    assert (ROOT / "scripts" / "start_kos_queue_approval_executor_loop.ps1").exists()
    assert (ROOT / "pages" / "KOS_Queue_Approval_Executor.py").exists()

def test_phase66c_policy_blocks_external_actions():
    data = json.loads((ROOT / "config" / "kos_queue_approval_executor_policy.json").read_text(encoding="utf-8"))
    forbidden = set(data["forbidden_actions"])
    assert "instagram_publish" in forbidden
    assert "paid_ai_call" in forbidden
    assert "external_deploy" in forbidden
    assert "browser_logged_account_automation" in forbidden

def test_phase66c_executor_requires_confirmation_and_duplicate_guard():
    text = (ROOT / "k_atlas" / "kaizen" / "queue_approval_executor.py").read_text(encoding="utf-8")
    assert "YES_EXECUTE_K_ATLAS_ENGINEER_COMMAND_LOCAL_ONLY" in text
    assert "DUPLICATE_SKIPPED" in text
    assert "safe_for_confirmed_execution" in text
    assert "run_phase66_engineer_command_confirmed.ps1" in text
