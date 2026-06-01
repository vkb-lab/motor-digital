REQUIRED_NAMES = [
    "IG_BUSINESS_ACCOUNT_ID",
    "META_ACCESS_KEY",
]

FINAL_FLAGS = {
    "KOS_REAL_IG_PUBLISH_ENABLED": "true",
    "KOS_HUMAN_OK_FOR_IG_REAL": "OK",
    "KOS_PHASE12_REAL_RUN": "YES_I_CONFIRM",
    "KOS_PHASE13_REAL_RUN": "YES_I_CONFIRM",
}

def build_env_plan():
    return {
        "status": "ENV_PLAN_READY",
        "required_names": REQUIRED_NAMES,
        "final_flags": FINAL_FLAGS,
        "local_runtime_file": "local_runtime/ig_runtime.env",
        "do_not_commit_local_runtime": True,
    }
