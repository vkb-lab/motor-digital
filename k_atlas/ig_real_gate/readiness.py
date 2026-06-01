import os
from k_atlas.ig_real_gate.env_names import IG_ENV_NAMES, required_env_names

def inspect_ig_real_readiness():
    missing = [name for name in required_env_names() if not os.getenv(name)]
    real_flag = os.getenv(IG_ENV_NAMES["real_flag"], "").strip().lower() == "true"
    human_flag = os.getenv(IG_ENV_NAMES["human_flag"], "").strip().upper() == "OK"

    can_prepare = len(missing) == 0
    can_run_real = can_prepare and real_flag and human_flag

    return {
        "status": "IG_REAL_READY" if can_run_real else "IG_REAL_LOCKED",
        "can_prepare": can_prepare,
        "can_run_real": can_run_real,
        "missing_env": missing,
        "real_flag_enabled": real_flag,
        "human_ok": human_flag,
        "external_call_allowed": can_run_real,
        "real_action_executed": False,
    }
