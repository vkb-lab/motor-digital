from __future__ import annotations

import json

from .readiness import RemoteAssistReadiness


if __name__ == "__main__":
    readiness = RemoteAssistReadiness()
    result = readiness.build_readiness({
        "mode": "lan_readiness",
        "network_scope": "lan_only",
        "human_approved": False,
        "public_exposure_enabled": False,
        "remote_control_enabled": False,
        "unattended_access_enabled": False,
        "mouse_automation": False,
        "keyboard_automation": False,
        "credential_capture_enabled": False,
        "password_storage_enabled": False,
        "auto_execute": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
        "external_api_enabled": False,
    })
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
