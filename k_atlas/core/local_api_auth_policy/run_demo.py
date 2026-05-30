from __future__ import annotations

import json

from .policy import validate_local_api_runtime_request


if __name__ == "__main__":
    result = validate_local_api_runtime_request({
        "bind_host": "127.0.0.1",
        "port": 8787,
        "auto_execute": False,
        "remote_control_enabled": False,
        "external_public_access": False,
    })
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
