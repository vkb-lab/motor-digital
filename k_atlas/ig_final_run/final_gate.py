import os
from k_atlas.ig_live_check.final_live_check import build_final_live_check

PHASE14_ENV = "KOS_PHASE14_REAL_RUN"
PHASE14_VALUE = "YES_I_CONFIRM"

def inspect_phase14_gate(load_runtime: bool = True):
    live_check = build_final_live_check(load_runtime=load_runtime)
    phase14_armed = os.getenv(PHASE14_ENV, "").strip() == PHASE14_VALUE

    ready = bool(live_check.get("ready_for_real_first_post")) and phase14_armed

    return {
        "status": "READY_FOR_REAL_SEND" if ready else "PHASE14_LOCKED",
        "ready_for_real_send": ready,
        "phase14_armed": phase14_armed,
        "required_env": PHASE14_ENV,
        "required_value": PHASE14_VALUE,
        "live_check": live_check,
        "real_action_executed": False,
        "external_call_executed": False,
    }
