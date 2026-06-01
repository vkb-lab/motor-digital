def local_env_policy():
    return {
        "status": "ACTIVE",
        "values_must_not_be_committed": True,
        "local_paths": ["local_runtime/", ".env", ".env.local"],
    }
