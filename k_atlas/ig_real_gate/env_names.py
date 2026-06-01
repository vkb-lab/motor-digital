IG_ENV_NAMES = {
    "ig_account": "IG_BUSINESS_ACCOUNT_ID",
    "meta_key": "META_ACCESS_KEY",
    "real_flag": "KOS_REAL_IG_PUBLISH_ENABLED",
    "human_flag": "KOS_HUMAN_OK_FOR_IG_REAL",
}

def required_env_names():
    return [IG_ENV_NAMES["ig_account"], IG_ENV_NAMES["meta_key"]]
