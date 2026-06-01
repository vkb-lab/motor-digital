import os

def env_present(name: str) -> bool:
    return bool(os.getenv(name))

def read_env_presence(names):
    return {name: env_present(name) for name in names}
