from k_atlas.ig_first_post.first_post_runner import build_first_post_package, execute_first_post_if_armed
from k_atlas.ig_first_post.arming_gate import inspect_phase12_arming

def test_phase12_package_ready_but_not_real(monkeypatch):
    monkeypatch.delenv("KOS_PHASE12_REAL_RUN", raising=False)
    package = build_first_post_package()
    assert package["status"] == "READY_FOR_FINAL_ARMING"
    assert package["real_action_executed"] is False
    assert package["external_call_executed"] is False

def test_phase12_blocks_without_extra_arming(monkeypatch):
    monkeypatch.delenv("KOS_PHASE12_REAL_RUN", raising=False)
    package = build_first_post_package()
    result = execute_first_post_if_armed(package)
    assert result["status"] == "BLOCKED_BY_PHASE12_ARMING"
    assert result["real_action_executed"] is False
    assert result["external_call_executed"] is False

def test_phase12_arming_default_locked(monkeypatch):
    monkeypatch.delenv("KOS_PHASE12_REAL_RUN", raising=False)
    arming = inspect_phase12_arming()
    assert arming["status"] == "PHASE12_LOCKED"
    assert arming["armed"] is False
