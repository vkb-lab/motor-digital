from __future__ import annotations

import json

from .runtime import SecureLocalApiRuntime


if __name__ == "__main__":
    runtime = SecureLocalApiRuntime()
    result = runtime.build_config()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
