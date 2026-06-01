import os

ARMING_ENV = "KOS_PHASE12_REAL_RUN"
ARMING_VALUE = "YES_I_CONFIRM"

def inspect_phase12_arming():
    armed = os.getenv(ARMING_ENV, "").strip() == ARMING_VALUE
    return {
        "status": "PHASE12_ARMED" if armed else "PHASE12_LOCKED",
        "armed": armed,
        "required_env": ARMING_ENV,
        "required_value": ARMING_VALUE,
        "real_action_allowed_by_phase12": armed,
    }
