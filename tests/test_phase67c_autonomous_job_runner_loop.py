from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase67c_loop_script_exists():
    assert (ROOT / "scripts" / "start_kos_autonomous_job_runner_loop.ps1").exists()

def test_phase67c_startup_profile_has_loop_block():
    text = (ROOT / "scripts" / "start_kos_startup_operational_profile.ps1").read_text(encoding="utf-8")
    assert "KOS_PHASE67C_AUTONOMOUS_JOB_RUNNER_LOOP_START" in text
    assert "start_kos_autonomous_job_runner_loop.ps1" in text

def test_phase67c_runtime_status_knows_loop_role():
    text = (ROOT / "scripts" / "run_phase49_runtime_control_status.py").read_text(encoding="utf-8")
    assert "autonomous_job_runner_loop" in text
    assert "start_kos_autonomous_job_runner_loop.ps1" in text
