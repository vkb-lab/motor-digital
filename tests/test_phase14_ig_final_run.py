from k_atlas.ig_final_run.final_gate import inspect_phase14_gate
from k_atlas.ig_final_run.final_runner import build_phase14_final_package, execute_phase14_if_confirmed

def test_phase14_locked_by_default(monkeypatch):
    for key in [
        "KOS_REAL_IG_PUBLISH_ENABLED",
        "KOS_HUMAN_OK_FOR_IG_REAL",
        "KOS_PHASE12_REAL_RUN",
        "KOS_PHASE13_REAL_RUN",
        "KOS_PHASE14_REAL_RUN",
    ]:
        monkeypatch.delenv(key, raising=False)

    gate = inspect_phase14_gate(load_runtime=False)
    assert gate["status"] == "PHASE14_LOCKED"
    assert gate["ready_for_real_send"] is False

def test_phase14_package_does_not_execute_real(monkeypatch):
    monkeypatch.delenv("KOS_PHASE14_REAL_RUN", raising=False)
    package = build_phase14_final_package(load_runtime=False)
    assert package["real_action_executed"] is False
    assert package["external_call_executed"] is False

def test_phase14_blocks_without_execute_switch(monkeypatch):
    monkeypatch.delenv("KOS_PHASE14_REAL_RUN", raising=False)
    package = build_phase14_final_package(load_runtime=False)
    result = execute_phase14_if_confirmed(package)
    assert result["status"] == "BLOCKED_BY_EXECUTE_SWITCH"
    assert result["real_action_executed"] is False
    assert result["external_call_executed"] is False
