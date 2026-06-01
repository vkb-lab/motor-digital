import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_FILE = ROOT / "local_runtime" / "ig_runtime.env"

def load_local_runtime_values():
    loaded = []
    if not RUNTIME_FILE.exists():
        return {"status": "LOCAL_RUNTIME_FILE_MISSING", "loaded": loaded, "path": str(RUNTIME_FILE)}

    for raw in RUNTIME_FILE.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and value and not os.getenv(key):
            os.environ[key] = value
            loaded.append(key)

    return {"status": "LOCAL_RUNTIME_FILE_LOADED", "loaded": loaded, "path": str(RUNTIME_FILE)}
