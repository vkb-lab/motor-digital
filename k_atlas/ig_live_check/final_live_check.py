import os
from k_atlas.ig_live_check.env_plan import REQUIRED_NAMES, FINAL_FLAGS
from k_atlas.ig_live_check.runtime_loader import load_local_runtime_values
from k_atlas.ig_real_gate.readiness import inspect_ig_real_readiness
from k_atlas.ig_first_post.arming_gate import inspect_phase12_arming

def build_final_live_check(load_runtime: bool = True):
    runtime = load_local_runtime_values() if load_runtime else {"status": "SKIPPED"}

    missing = [name for name in REQUIRED_NAMES if not os.getenv(name)]
    flags = {name: os.getenv(name, "") == expected for name, expected in FINAL_FLAGS.items()}

    readiness = inspect_ig_real_readiness()
    phase12 = inspect_phase12_arming()

    ready_for_real = (
        not missing
        and readiness.get("can_run_real") is True
        and phase12.get("armed") is True
        and flags.get("KOS_PHASE13_REAL_RUN") is True
    )

    return {
        "status": "READY_FOR_REAL_FIRST_POST" if ready_for_real else "LIVE_CHECK_LOCKED",
        "runtime": runtime,
        "missing": missing,
        "flags": flags,
        "instagram_readiness": readiness,
        "phase12": phase12,
        "ready_for_real_first_post": ready_for_real,
        "real_action_executed": False,
        "external_call_executed": False,
    }
